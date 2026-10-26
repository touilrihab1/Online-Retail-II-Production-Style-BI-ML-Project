import requests
import pandas as pd
import plotly.express as px
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Cohort Retention",
    page_icon="📈",
    layout="wide"
)

st.title("Cohort Retention Analysis")
st.caption(
    "Understand how customer retention evolves across acquisition cohorts."
)

# ---------- Styling ----------
st.markdown("""
<style>
div[data-testid="stMetric"] {
    background: #DCDCDC;
    border: 1px solid #475569;
    padding: 1.2rem;
    border-radius: 14px;
    color: #FFFFFF;
    
}

div[data-testid="stMetricLabel"] {
    color: #CBD5E1 !important;
    font-size: 0.95rem;
}

div[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-size: 1.8rem;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ---------- Fetch data ----------
try:
    response = requests.get(
        f"{API_URL}/cohorts/retention",
        timeout=30
    )
    response.raise_for_status()
    data = response.json()

    cohorts = data.get("cohorts", [])

    if not cohorts:
        st.warning("No cohort retention data available.")

    else:
        # ---------- Prepare data ----------
        rows = []

        for cohort in cohorts:
            row = {"Cohort": cohort["cohort_month"]}
            row.update({
                int(period): float(rate)
                for period, rate in cohort["retention"].items()
            })
            rows.append(row)

        retention_df = (
            pd.DataFrame(rows)
            .set_index("Cohort")
            .sort_index()
        )

        # ---------- Cohort selection ----------
        st.subheader("Retention Overview")

        col1, col2 = st.columns(2)

        with col1:
            selected_cohort = st.selectbox(
                "Select acquisition cohort",
                retention_df.index.tolist(),
                index=len(retention_df.index) - 1
            )

        available_months = sorted(
            int(col) for col in retention_df.columns
            if pd.notna(retention_df.loc[selected_cohort, col])
        )

        with col2:
            selected_month = st.selectbox(
                "Select period",
                available_months,
                format_func=lambda x: (
                    "Month 0 (Acquisition)" if x == 0
                    else f"Month {x}"
                )
            )

        retention_rate = float(
            retention_df.loc[selected_cohort, selected_month]
        )
        churn_rate = max(0.0, 100.0 - retention_rate)

        # ---------- KPI cards ----------
        k1, k2, k3 = st.columns(3)

        k1.metric("Acquisition Cohort", selected_cohort)
        k2.metric("Retention Rate", f"{retention_rate:.1f}%")
        k3.metric("Not Retained", f"{churn_rate:.1f}%")

        # ---------- Donut chart ----------
        st.subheader("Customer Retention Distribution")
        st.caption(
            f"Cohort: {selected_cohort} · "
            f"{'Acquisition month' if selected_month == 0 else f'Month {selected_month}'}"
        )

        donut_df = pd.DataFrame({
            "Status": ["Retained", "Not retained"],
            "Percentage": [retention_rate, churn_rate]
        })

        fig = px.pie(
            donut_df,
            names="Status",
            values="Percentage",
            hole=0.68,
            color="Status",
            color_discrete_map={
                "Retained": "#38BDF8",
                "Not retained": "#334155"
            }
        )

        fig.update_traces(
            textposition="outside",
            texttemplate="%{label}<br>%{value:.1f}%",
            hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
            marker=dict(line=dict(color="#0E1117", width=3))
        )

        fig.update_layout(
            height=400,
            showlegend=False,
            margin=dict(t=30, b=30, l=30, r=30),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            annotations=[
                dict(
                    text=f"{retention_rate:.1f}%",
                    x=0.5,
                    y=0.5,
                    font_size=28,
                    font_color="#F8FAFC",
                    showarrow=False
                )
            ]
        )

        st.plotly_chart(fig, use_container_width=True)

        # ---------- Retention trend ----------
        st.subheader("Retention Trend")
        st.caption(
            "Compare retention across periods for the selected cohort."
        )

        trend = (
            retention_df.loc[selected_cohort]
            .dropna()
            .rename_axis("Month")
            .reset_index(name="Retention Rate")
        )

        trend["Month"] = trend["Month"].astype(int)

        line_fig = px.line(
            trend,
            x="Month",
            y="Retention Rate",
            markers=True,
            labels={
                "Month": "Months Since Acquisition",
                "Retention Rate": "Retention (%)"
            }
        )

        line_fig.update_traces(
            line=dict(width=3),
            marker=dict(size=7)
        )

        line_fig.update_layout(
            height=350,
            yaxis=dict(range=[0, 100], ticksuffix="%"),
            xaxis=dict(dtick=1),
            margin=dict(t=30, b=30),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(line_fig, use_container_width=True)

        # ---------- Detailed table ----------
        with st.expander("View detailed cohort retention table"):
            display_df = retention_df.copy()
            display_df.columns = [
                f"Month {int(c)}" for c in display_df.columns
            ]

            st.dataframe(
                display_df.style.format("{:.1f}%"),
                use_container_width=True
            )

except requests.exceptions.RequestException:
    st.error(
        "Could not connect to the API. Make sure FastAPI is running."
    )

except (KeyError, ValueError, TypeError):
    st.error("The API returned data in an unexpected format.")
