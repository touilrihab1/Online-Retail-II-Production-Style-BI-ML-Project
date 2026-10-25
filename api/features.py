
import pandas as pd


def customer_feature_engineering(conn, customer_id, observation_date):
    observation_date = pd.to_datetime(observation_date)

    next_day = (
        observation_date + pd.Timedelta(days=1)
    ).strftime("%Y-%m-%d")

    # 1. RFM features
    rfm_query = """
        SELECT
            MAX(invoicedate) AS last_purchase,
            COUNT(DISTINCT invoice) AS frequency,
            SUM(revenue) AS monetary
        FROM transactions
        WHERE customer_id = ?
          AND invoicedate < ?
          AND NOT is_return
          AND NOT is_non_product
          AND NOT is_guest
    """

    rfm = pd.read_sql_query(
        rfm_query, conn, params=[customer_id, next_day]
    )

    if rfm.empty or pd.isna(rfm.loc[0, "last_purchase"]):
        return None

    rfm["last_purchase"] = pd.to_datetime(rfm["last_purchase"])

    recency = (
        observation_date - rfm.loc[0, "last_purchase"]
    ).days

    frequency = int(rfm.loc[0, "frequency"])
    monetary = float(rfm.loc[0, "monetary"] or 0.0)

    # 2. First purchase and cohort
    first_query = """
        SELECT MIN(invoicedate) AS first_purchase
        FROM transactions
        WHERE customer_id = ?
          AND invoicedate < ?
          AND NOT is_return
          AND NOT is_non_product
          AND NOT is_guest
    """

    first = pd.read_sql_query(
        first_query, conn, params=[customer_id, next_day]
    )

    if pd.isna(first.loc[0, "first_purchase"]):
        return None

    first_purchase = pd.to_datetime(first.loc[0, "first_purchase"])

    cohort_month = (
        first_purchase.to_period("M").ordinal
    )

    days_since_first_purchase = (
        observation_date - first_purchase
    ).days

    # 3. Average order value
    aov_query = """
        SELECT
            COUNT(DISTINCT invoice) AS number_of_orders,
            SUM(revenue) AS total_revenue
        FROM transactions
        WHERE customer_id = ?
          AND invoicedate < ?
          AND NOT is_return
          AND NOT is_non_product
          AND NOT is_guest
    """

    aov = pd.read_sql_query(
        aov_query, conn, params=[customer_id, next_day]
    )

    number_of_orders = aov.loc[0, "number_of_orders"]
    total_revenue = aov.loc[0, "total_revenue"] or 0.0

    average_order_value = (
        float(total_revenue) / number_of_orders
        if number_of_orders else 0.0
    )

    # 4. Product diversity
    diversity_query = """
        SELECT COUNT(DISTINCT stockcode) AS distinct_products_bought
        FROM transactions
        WHERE customer_id = ?
          AND invoicedate < ?
          AND NOT is_return
          AND NOT is_non_product
          AND NOT is_guest
    """

    diversity = pd.read_sql_query(
        diversity_query, conn, params=[customer_id, next_day]
    )

    distinct_products_bought = int(
        diversity.loc[0, "distinct_products_bought"] or 0
    )

    # Keep exactly the feature order used during model training
    return pd.DataFrame([{
        "recency": recency,
        "frequency": frequency,
        "monetary": monetary,
        "cohort_month": cohort_month,
        "days_since_first_purchase": days_since_first_purchase,
        "average_order_value": average_order_value,
        "distinct_products_bought": distinct_products_bought
    }])
