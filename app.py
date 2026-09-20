# app.py
import os
import random
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Set page configuration first
st.set_page_config(page_title="Executive SaaS & Churn Analytics", layout="wide")

# Load environment variables from .env file
load_dotenv()

# Strict Environment Variable Validation
REQUIRED_ENV_VARS = ["DB_NAME", "DB_USER", "DB_PASS", "DB_HOST", "DB_PORT"]
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]

if missing_vars:
    st.error(f"⚠️ Missing required environment variables in .env: {', '.join(missing_vars)}")
    st.stop()

# Fetch configuration exclusively from environment variables
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


@st.cache_data
def load_data():
    engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    query_mrr = """
    SELECT 
        d.full_date, 
        f.amount_paid, 
        f.is_churned, 
        c.region, 
        p.plan_name
    FROM fact_transactions f
    JOIN dim_dates d ON f.date_key = d.date_key
    JOIN dim_customers c ON f.customer_id = c.customer_id
    JOIN dim_plans p ON f.plan_id = p.plan_id;
    """
    df = pd.read_sql(query_mrr, engine)
    df['full_date'] = pd.to_datetime(df['full_date'])
    return df


st.title("📈 Enterprise SaaS LTV & Churn Analytics Dashboard")

try:
    df = load_data()

    # Sidebar Filter
    region_filter = st.sidebar.multiselect(
        "Select Region", 
        options=df['region'].unique(), 
        default=df['region'].unique()
    )
    filtered_df = df[df['region'].isin(region_filter)]

    # Key Performance Indicators (KPIs)
    total_mrr = filtered_df[filtered_df['is_churned'] == 0]['amount_paid'].sum()
    total_churned = filtered_df[filtered_df['is_churned'] == 1]['is_churned'].count()
    churn_rate = (total_churned / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Active Revenue Generated", f"${total_mrr:,.2f}")
    col2.metric("Total Churn Events", f"{total_churned}")
    col3.metric("Overall Churn Rate", f"{churn_rate:.2f}%")

    st.markdown("---")

    # Visualizations
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Revenue by Subscription Plan")
        plan_fig = px.pie(
            filtered_df, 
            names='plan_name', 
            values='amount_paid', 
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(plan_fig, use_container_width=True)

    with col_right:
        st.subheader("Regional Revenue Breakdown")
        region_summary = filtered_df.groupby('region')['amount_paid'].sum().reset_index()
        region_fig = px.bar(
            region_summary,
            x='region', 
            y='amount_paid', 
            color='region',
            labels={'amount_paid': 'Revenue ($)', 'region': 'Region'}
        )
        st.plotly_chart(region_fig, use_container_width=True)

except Exception as e:
    st.error(f"Database connection or query failed: {e}")