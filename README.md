# Enterprise Customer LTV & Churn Analytics Engine

An end-to-end modern data analytics warehouse and interactive executive dashboard built to model customer retention, Monthly Recurring Revenue (MRR), and Lifetime Value (LTV) metrics for subscription-based business models.

## 🏗️ System Architecture

1. **Data Warehouse Schema**: STAR Schema implemented in **PostgreSQL** (`dim_customers`, `dim_plans`, `dim_dates`, `fact_transactions`).
2. **Data Pipeline (ELT/ETL)**: Python script (`db_pipeline.py`) utilizing **Faker**, **Pandas**, and **SQLAlchemy** to generate and load 5,000+ transaction records.
3. **Advanced SQL Analytics**: Complex CTEs, Window Functions (`LAG`, `OVER`), and aggregation scripts (`analytics_queries.sql`).
4. **Executive Dashboard**: Interactive BI interface built using **Streamlit** and **Plotly**.

## 🛠️ Tech Stack

* **Database / Data Warehouse**: PostgreSQL
* **Language & Libraries**: Python 3.10+, Pandas, SQLAlchemy, Psycopg2, Faker, Python-Dotenv
* **Business Intelligence / Data Viz**: Streamlit, Plotly
* **Version Control**: Git, GitHub

## 🚀 How to Run Locally

### 1. Prerequisites
Ensure PostgreSQL and Python 3.10+ are installed.

### 2. Setup Environment
```bash
# Clone repository
git clone [https://github.com/anto-agnes/enterprise-churn-analytics.git](https://github.com/anto-agnes/enterprise-churn-analytics.git)
cd enterprise-churn-analytics

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt