
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="RFM Explorer",
    page_icon="👥",
    layout="wide"
)

st.title("RFM & Customer Segment Explorer")
st.caption("Explore customer purchasing behaviour and value.")

customer_id = st.number_input(
    "Enter Customer ID",
    min_value=1,
    step=1
)

if st.button("Analyze Customer"):
    try:
        response = requests.get(
            f"{API_URL}/customers/{customer_id}/rfm",
            timeout=10
        )

        if response.status_code == 404:
            st.warning("Customer not found. Please check the ID.")

        else:
            response.raise_for_status()
            data = response.json()

            st.subheader(f"Customer {data['customer_id']}")

            col1, col2, col3 = st.columns(3)

            col1.metric("Recency", f"{data['recency']} days")
            col2.metric("Frequency", f"{data['frequency']} orders")
            col3.metric("Monetary", f"{data['monetary']:,.2f}")

            st.divider()

            st.subheader("Customer Segment")
            st.info(data["segment"])

    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to the API: {e}")

    except (KeyError, ValueError, TypeError):
        st.error("The API returned data in an unexpected format.")
