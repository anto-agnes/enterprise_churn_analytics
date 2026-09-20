-- analytics_queries.sql

-- 1. Monthly Recurring Revenue (MRR) Growth Trend
WITH monthly_mrr AS (
    SELECT 
        d.year,
        d.month,
        SUM(f.amount_paid) AS total_mrr,
        COUNT(DISTINCT f.customer_id) AS active_customers
    FROM fact_transactions f
    JOIN dim_dates d ON f.date_key = d.date_key
    WHERE f.is_churned = 0
    GROUP BY d.year, d.month
)
SELECT 
    year,
    month,
    total_mrr,
    active_customers,
    LAG(total_mrr) OVER (ORDER BY year, month) AS prev_month_mrr,
    ROUND(
        ((total_mrr - LAG(total_mrr) OVER (ORDER BY year, month)) / 
        NULLIF(LAG(total_mrr) OVER (ORDER BY year, month), 0)) * 100, 2
    ) AS mrr_growth_percentage
FROM monthly_mrr;

-- 2. Customer Lifetime Value (LTV) by Region
WITH customer_revenue AS (
    SELECT 
        c.customer_id,
        c.region,
        p.plan_name,
        SUM(f.amount_paid) AS total_lifetime_spend,
        COUNT(f.transaction_id) AS active_months
    FROM dim_customers c
    JOIN fact_transactions f ON c.customer_id = f.customer_id
    JOIN dim_plans p ON f.plan_id = p.plan_id
    GROUP BY c.customer_id, c.region, p.plan_name
)
SELECT 
    region,
    plan_name,
    COUNT(customer_id) AS total_customers,
    ROUND(AVG(total_lifetime_spend), 2) AS avg_ltv,
    ROUND(AVG(active_months), 1) AS avg_retention_months
FROM customer_revenue
GROUP BY region, plan_name
ORDER BY avg_ltv DESC;