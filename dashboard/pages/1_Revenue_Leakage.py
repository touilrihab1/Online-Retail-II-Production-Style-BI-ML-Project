
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Revenue Leakage",
    page_icon="💸",
    layout="wide"
)

st.title("Revenue Leakage Overview")
st.caption("Understand how much revenue is lost through returns and other leakage.")

try:
    response = requests.get(
        f"{API_URL}/revenue-leakage/summary",
        timeout=10
    )
    response.raise_for_status()
    data = response.json()

    gross_revenue = data["gross_revenue"]
    revenue_lost = data["revenue_lost"]
    leakage_percentage = data["leakage_percentage"]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Gross Revenue",
        f"{gross_revenue:,.2f}"
    )

    col2.metric(
        "Revenue Lost",
        f"{revenue_lost:,.2f}"
    )

    col3.metric(
        "Leakage Rate",
        f"{leakage_percentage:.2f}%"
    )

    st.divider()
    st.subheader("Revenue Overview")

    st.bar_chart({
        "Amount": {
            "Gross Revenue": gross_revenue,
            "Revenue Lost": revenue_lost
        }
    })

except requests.exceptions.RequestException as e:
    st.error(f"Could not connect to the API: {e}")

except (KeyError, ValueError):
    st.error("The API returned data in an unexpected format.")
