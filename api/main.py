
from datetime import date
from fastapi import FastAPI, HTTPException

from api.database import get_connection
import joblib
import pandas as pd
from pathlib import Path
from api.features import customer_feature_engineering


app = FastAPI(title="Online Retail Analytics API")

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "churn_model.joblib"
churn_model = joblib.load(MODEL_PATH)


@app.get("/customers/{customer_id}/rfm")
def get_customer_rfm(customer_id: int):
    conn = get_connection()

    try:
        customer = conn.execute(
            "SELECT customer_id FROM customers WHERE customer_id = ?",
            (customer_id,)
        ).fetchone()

        if customer is None:
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )

        rfm = conn.execute(
            """
            SELECT
                CAST(julianday('now') - julianday(MAX(invoicedate)) AS INTEGER)
                    AS recency,
                COUNT(DISTINCT invoice) AS frequency,
                SUM(revenue) AS monetary
            FROM transactions
            WHERE customer_id = ?
              AND NOT is_return
              AND NOT is_non_product
              AND NOT is_guest
            """,
            (customer_id,)
        ).fetchone()

        return {
            "customer_id": customer_id,
            "recency": rfm["recency"],
            "frequency": rfm["frequency"],
            "monetary": rfm["monetary"] or 0.0,
            "segment": "not_defined"
        }

    finally:
        conn.close()


@app.get("/customers/{customer_id}/churn-risk")
def get_churn_risk(customer_id: int):
    conn = get_connection()

    try:
        customer = conn.execute(
            "SELECT customer_id FROM customers WHERE customer_id = ?",
            (customer_id,)
        ).fetchone()

        if customer is None:
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )


        features = customer_feature_engineering(
            conn=conn,
            customer_id=customer_id,
            observation_date=date(2011, 12, 9)
        )

        probability = churn_model.predict_proba(features)[0, 1]

        return {
            "customer_id": customer_id,
            "churn_probability": round(float(probability), 4)
        }

    finally:
        conn.close()



@app.get("/revenue-leakage/summary")
def get_revenue_leakage_summary():
    conn = get_connection()

    try:
        gross_query = """
            SELECT SUM(revenue) AS gross_revenue
            FROM transactions
            WHERE NOT is_return
              AND NOT is_writeoff
              AND NOT is_non_product
        """
        gross = pd.read_sql_query(gross_query, conn)

        returned_query = """
            SELECT SUM(revenue) AS returned_revenue
            FROM transactions
            WHERE is_return
              AND NOT is_non_product
        """
        returned = pd.read_sql_query(returned_query, conn)

        gross_revenue = gross["gross_revenue"].iloc[0]
        returned_revenue = returned["returned_revenue"].iloc[0]

        gross_revenue = float(gross_revenue or 0.0)
        revenue_lost = abs(float(returned_revenue or 0.0))

        leakage_percentage = (
            (revenue_lost / gross_revenue) * 100
            if gross_revenue > 0
            else 0.0
        )

        return {
            "gross_revenue": round(gross_revenue, 2),
            "revenue_lost": round(revenue_lost, 2),
            "leakage_percentage": round(leakage_percentage, 2)
        }

    finally:
        conn.close()


@app.get("/cohorts/retention")
def get_cohort_retention():
    conn = get_connection()

    try:
        query = """
            WITH first_purchase AS (
                SELECT customer_id, MIN(invoicedate) AS first_date
                FROM transactions
                WHERE customer_id != 0
                  AND NOT is_return
                  AND NOT is_non_product
                  AND NOT is_guest
                GROUP BY customer_id
            )
            SELECT
                strftime('%Y-%m', f.first_date) AS cohort_month,
                (
                    (CAST(strftime('%Y', t.invoicedate) AS INTEGER)
                     - CAST(strftime('%Y', f.first_date) AS INTEGER)) * 12
                    + CAST(strftime('%m', t.invoicedate) AS INTEGER)
                    - CAST(strftime('%m', f.first_date) AS INTEGER)
                ) AS period,
                COUNT(DISTINCT t.customer_id) AS customers
            FROM transactions t
            JOIN first_purchase f ON t.customer_id = f.customer_id
            WHERE t.invoicedate >= f.first_date
              AND NOT t.is_return
              AND NOT t.is_non_product
              AND NOT t.is_guest
            GROUP BY cohort_month, period
            ORDER BY cohort_month, period
        """

        df = pd.read_sql_query(query, conn)

        if df.empty:
            return {"cohorts": []}

        table = df.pivot(
            index="cohort_month",
            columns="period",
            values="customers"
        ).fillna(0)

        rates = table.div(table[0], axis=0).mul(100).round(2)

        return {
            "cohorts": [
                {
                    "cohort_month": month,
                    "retention": {
                        str(int(p)): float(v)
                        for p, v in row.items()
                    }
                }
                for month, row in rates.iterrows()
            ]
        }

    finally:
        conn.close()
