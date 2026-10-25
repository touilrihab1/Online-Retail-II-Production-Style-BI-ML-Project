
import requests
import pandas as pd
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Cohort Retention",
    page_icon="📈",
    layout="wide"
)

st.title("Cohort Retention Analysis")
st.caption("Explore how customer retention changes over time.")

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
        rows = []

        for cohort in cohorts:
            row = {"Cohort": cohort["cohort_month"]}
            row.update({
                f"Month {period}": rate
                for period, rate in cohort["retention"].items()
            })
            rows.append(row)

        retention_df = pd.DataFrame(rows).set_index("Cohort")
        retention_df = retention_df.sort_index()

        st.subheader("Retention by Cohort")
        st.dataframe(
            retention_df.style.format("{:.1f}%"),
            use_container_width=True
        )

        st.subheader("Retention Heatmap")
        st.caption(
            "Each cell represents the percentage of customers "
            "from a cohort who purchased again in that period."
        )

        chart_df = retention_df.copy()
        chart_df.index.name = "Cohort"

        st.dataframe(
            chart_df.style
            .format("{:.1f}%")
            .background_gradient(cmap="Blues", axis=None),
            use_container_width=True
        )

except requests.exceptions.RequestException as e:
    st.error(f"Could not connect to the API: {e}")

except (KeyError, ValueError, TypeError):
    st.error("The API returned data in an unexpected format.")
