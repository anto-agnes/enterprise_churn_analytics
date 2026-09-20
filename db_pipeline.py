# db_pipeline.py
import datetime
import os
import random  # <--- Ensures random module is imported
import psycopg2
from dotenv import load_dotenv
from faker import Faker
import pandas as pd
from sqlalchemy import create_engine

# Load environment variables from .env file
load_dotenv()

# Strict Environment Variable Validation
REQUIRED_ENV_VARS = ["DB_NAME", "DB_USER", "DB_PASS", "DB_HOST", "DB_PORT"]
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"⚠️ Missing required environment variables in .env: {', '.join(missing_vars)}")

# Read configuration exclusively from environment variables
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

fake = Faker()
Faker.seed(42)
random.seed(42)

def get_engine():
    return create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

def setup_database_schema():
    # Connect to default postgres DB first to create target database if needed
    conn = psycopg2.connect(dbname="postgres", user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
    if not cursor.fetchone():
        cursor.execute(f"CREATE DATABASE {DB_NAME}")
    cursor.close()
    conn.close()

    # Connect to target database and set up schema
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
    cursor = conn.cursor()

    cursor.execute("""
    DROP TABLE IF EXISTS fact_transactions CASCADE;
    DROP TABLE IF EXISTS dim_customers CASCADE;
    DROP TABLE IF EXISTS dim_plans CASCADE;
    DROP TABLE IF EXISTS dim_dates CASCADE;

    CREATE TABLE dim_customers (
        customer_id VARCHAR(50) PRIMARY KEY,
        customer_name VARCHAR(100),
        email VARCHAR(100),
        region VARCHAR(50),
        signup_date DATE
    );

    CREATE TABLE dim_plans (
        plan_id INT PRIMARY KEY,
        plan_name VARCHAR(50),
        monthly_cost DECIMAL(10, 2)
    );

    CREATE TABLE dim_dates (
        date_key INT PRIMARY KEY,
        full_date DATE,
        year INT,
        month INT,
        quarter INT
    );

    CREATE TABLE fact_transactions (
        transaction_id SERIAL PRIMARY KEY,
        customer_id VARCHAR(50) REFERENCES dim_customers(customer_id),
        plan_id INT REFERENCES dim_plans(plan_id),
        date_key INT REFERENCES dim_dates(date_key),
        amount_paid DECIMAL(10, 2),
        is_churned INT
    );
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("[SUCCESS] Schema setup complete.")

def populate_data():
    engine = get_engine()

    # 1. Populate dim_plans
    plans = pd.DataFrame([
        {'plan_id': 1, 'plan_name': 'Basic', 'monthly_cost': 29.00},
        {'plan_id': 2, 'plan_name': 'Pro', 'monthly_cost': 79.00},
        {'plan_id': 3, 'plan_name': 'Enterprise', 'monthly_cost': 299.00}
    ])
    plans.to_sql('dim_plans', engine, if_exists='append', index=False)

    # 2. Populate dim_dates (2024 - 2026)
    dates = []
    start_date = datetime.date(2024, 1, 1)
    end_date = datetime.date(2026, 12, 31)
    curr = start_date
    while curr <= end_date:
        dates.append({
            'date_key': int(curr.strftime('%Y%m%d')),
            'full_date': curr,
            'year': curr.year,
            'month': curr.month,
            'quarter': (curr.month - 1) // 3 + 1
        })
        curr += datetime.timedelta(days=1)
    pd.DataFrame(dates).to_sql('dim_dates', engine, if_exists='append', index=False)

    # 3. Populate dim_customers
    regions = ['North America', 'EMEA', 'APAC', 'LATAM']
    customers = []
    for _ in range(1000):
        c_id = f"CUST-{fake.unique.random_number(digits=6)}"
        s_date = fake.date_between(start_date=datetime.date(2024, 1, 1), end_date=datetime.date(2025, 6, 1))
        customers.append({
            'customer_id': c_id,
            'customer_name': fake.name(),
            'email': fake.company_email(),
            'region': random.choice(regions),
            'signup_date': s_date
        })
    df_customers = pd.DataFrame(customers)
    df_customers.to_sql('dim_customers', engine, if_exists='append', index=False)

    # 4. Populate fact_transactions
    transactions = []
    for _, cust in df_customers.iterrows():
        c_id = cust['customer_id']
        s_date = cust['signup_date']
        plan_id = random.choices([1, 2, 3], weights=[0.5, 0.35, 0.15])[0]
        cost = plans.loc[plans['plan_id'] == plan_id, 'monthly_cost'].values[0]

        # Simulate billing history
        months_active = random.randint(1, 18)
        churn_month = random.randint(3, 18) if random.random() < 0.25 else 999

        for m in range(months_active):
            tx_date = s_date + datetime.timedelta(days=30 * m)
            if tx_date > end_date:
                break
            
            is_churn = 1 if m >= churn_month else 0
            date_key = int(tx_date.strftime('%Y%m%d'))

            transactions.append({
                'customer_id': c_id,
                'plan_id': plan_id,
                'date_key': date_key,
                'amount_paid': cost if is_churn == 0 else 0,
                'is_churned': is_churn
            })

            if is_churn == 1:
                break

    pd.DataFrame(transactions).to_sql('fact_transactions', engine, if_exists='append', index=False)
    print("[SUCCESS] Data warehouse populated with realistic records.")

if __name__ == "__main__":
    setup_database_schema()
    populate_data()