import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="RFM Explorer",
    page_icon="👥",
    layout="wide"
)

# ---------- Custom styling ----------
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    .hero {
        padding: 1.8rem 2rem;
        border-radius: 16px;
        background: linear-gradient(120deg, #172554, #1e40af);
        color: white;
        margin-bottom: 1.5rem;
    }

    .hero h1 {
        color: white;
        font-size: 2.1rem;
        margin-bottom: 0.4rem;
    }

    .hero p {
        color: #dbeafe;
        font-size: 1rem;
        margin-bottom: 0;
    }

    div[data-testid="stMetric"] {
        background: #151b2b;
        border: 1px solid #2d3748;
        padding: 1.2rem;
        border-radius: 12px;
    }

    div[data-testid="stMetricLabel"] {
        color: #a8b5cc;
    }

    div[data-testid="stMetricValue"] {
        color: #f8fafc;
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 650;
        margin: 1.5rem 0 0.8rem 0;
    }

    .profile-card {
        background: #151b2b;
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        margin-top: 0.5rem;
    }

    .profile-label {
        color: #a8b5cc;
        font-size: 0.85rem;
        margin-bottom: 0.4rem;
    }

    .profile-value {
        color: #f8fafc;
        font-size: 1.15rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown("""
<div class="hero">
    <h1>👥 RFM & Customer Intelligence</h1>
    <p>Explore customer purchasing behaviour, monetary value and segmentation.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Customer search ----------
st.markdown('<div class="section-title">Customer Lookup</div>',
            unsafe_allow_html=True)

left, right = st.columns([3, 1])

with left:
    customer_id = st.number_input(
        "Customer ID",
        min_value=1,
        step=1,
        value=1
    )

with right:
    st.write("")
    st.write("")
    analyze = st.button(
        "Analyze Customer",
        type="primary",
        use_container_width=True
    )

# ---------- API request ----------
if analyze:
    try:
        with st.spinner("Retrieving customer insights..."):
            response = requests.get(
                f"{API_URL}/customers/{customer_id}/rfm",
                timeout=10
            )

        if response.status_code == 404:
            st.warning("Customer not found. Please check the Customer ID.")

        else:
            response.raise_for_status()
            data = response.json()

            st.divider()

            st.markdown(
                f"### Customer Profile · {data['customer_id']}"
            )
            st.caption("Key indicators based on the available transaction data")

            # KPI cards
            col1, col2, col3 = st.columns(3)

            col1.metric(
                label="Recency",
                value=f"{data['recency']:,} days",
                help="Days since the customer's last purchase."
            )

            col2.metric(
                label="Frequency",
                value=f"{data['frequency']:,}",
                help="Number of orders recorded for this customer."
            )

            col3.metric(
                label="Monetary Value",
                value=f"{data['monetary']:,.2f}",
                help="Total monetary value recorded for this customer."
            )

            # Segment panel
            st.markdown(
                '<div class="section-title">Segmentation Insights</div>',
                unsafe_allow_html=True
            )

            segment_col, info_col = st.columns([1, 2])

            with segment_col:
                st.markdown(
                    f"""
                    <div class="profile-card">
                        <div class="profile-label">Customer Segment</div>
                        <div class="profile-value">
                            {data['segment']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with info_col:
                st.info(
                    "RFM combines Recency, Frequency and Monetary Value "
                    "to help understand customer behaviour and value."
                )

    except requests.exceptions.RequestException:
        st.error(
            "Could not connect to the API. Make sure FastAPI is running."
        )

    except (KeyError, ValueError, TypeError):
        st.error("The API returned data in an unexpected format.")

else:
    st.markdown("""
    <div class="profile-card">
        <div class="profile-value">Ready to explore customers</div>
        <p style="color:#a8b5cc; margin-top:0.5rem;">
            Enter a Customer ID above to retrieve RFM metrics and
            segmentation information.
        </p>
    </div>
    """, unsafe_allow_html=True)
