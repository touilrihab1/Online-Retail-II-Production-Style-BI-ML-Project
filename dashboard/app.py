
import streamlit as st

st.set_page_config(
    page_title="Online Retail Analytics",
    page_icon="📊",
    layout="wide"
)

# Main title
st.title("📊 Online Retail Analytics Dashboard")
st.markdown(
    "Business Intelligence | Revenue Analysis | Customer Analytics"
)

st.divider()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Choose a page:",
    [
        "Overview",
        "Revenue Leakage",
        "RFM Explorer",
        "Churn Risk",
        "Cohort Retention"
    ]
)

# Overview page
if page == "Overview":
    st.header("Business Overview")
    st.write(
        "Welcome to the Online Retail Analytics Dashboard."
    )
    st.info(
        "Use the sidebar to explore revenue leakage, "
        "customer segments, churn risk, and retention."
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Gross Revenue", "—")
    col2.metric("Revenue Lost", "—")
    col3.metric("Leakage Rate", "—")

    st.caption(
        "KPIs will be loaded from the FastAPI backend."
    )

elif page == "Revenue Leakage":
    st.header("Revenue Leakage Analysis")
    st.write("Revenue leakage KPIs and charts will appear here.")

elif page == "RFM Explorer":
    st.header("RFM & Customer Segments")
    st.write("Customer RFM values and segments will appear here.")

elif page == "Churn Risk":
    st.header("Customer Churn Risk")
    st.write("Enter a customer ID to explore churn probability.")

elif page == "Cohort Retention":
    st.header("Cohort Retention")
    st.write("Retention curves and cohort charts will appear here.")
