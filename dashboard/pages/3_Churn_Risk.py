
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Customer Churn Risk",
    page_icon="📉",
    layout="wide"
)

st.title("Customer Churn Risk")
st.caption("Estimate the probability that a customer will churn.")

customer_id = st.number_input(
    "Enter Customer ID",
    min_value=1,
    step=1
)

if st.button("Predict Churn Risk"):
    try:
        response = requests.get(
            f"{API_URL}/customers/{customer_id}/churn-risk",
            timeout=30
        )

        if response.status_code == 404:
            st.warning("Customer not found. Please check the ID.")
        else:
            response.raise_for_status()
            data = response.json()

            probability = float(data["churn_probability"])

            if not 0 <= probability <= 1:
                st.error("The API returned an invalid probability.")
            else:
                st.subheader(f"Customer {data['customer_id']}")

                col1, col2 = st.columns(2)

                col1.metric(
                    "Churn Probability",
                    f"{probability:.1%}"
                )

                col2.metric(
                    "Churn Score",
                    f"{probability:.4f}"
                )

                st.progress(probability)

                if probability >= 0.7:
                    st.error("High predicted churn probability")
                elif probability >= 0.4:
                    st.warning("Moderate predicted churn probability")
                else:
                    st.success("Low predicted churn probability")

                st.caption(
                    "Risk bands are illustrative thresholds, "
                    "not validated business decision boundaries."
                )

    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to the API: {e}")

    except (KeyError, ValueError, TypeError):
        st.error("The API returned an unexpected response.")
