# ==============================================================================
# MODULE 10: SNOWPARK WINDOW FUNCTIONS & ADVANCED TRANSFORMATIONS
# ==============================================================================
# Level: Intermediate → Advanced
# Time: 25 minutes
# Prerequisites: Module 01-09 completed
# ==============================================================================

from snowflake.snowpark import Session
from snowflake.snowpark.functions import (
    col, lit, sum, avg, count, min, max,
    when, row_number, rank, dense_rank, lag, lead,
    year, month, datediff, round as round_,
    count_distinct, ntile, percent_rank
)
from snowflake.snowpark import Window

# session = get_active_session()

# ==============================================================================
# SECTION 1: WHAT ARE WINDOW FUNCTIONS?
# ==============================================================================

# Window functions compute values ACROSS a set of rows related to the current row.
# Unlike GROUP BY, they DON'T collapse rows — each row keeps its own identity.
#
# SQL equivalent:
#   ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC)
#
# USE CASES:
#   - Ranking (top N per group)
#   - Running totals (cumulative sum)
#   - Previous/next row values (lag/lead)
#   - Percentiles and distributions
#   - Moving averages

# ==============================================================================
# SECTION 2: WINDOW SPECIFICATION
# ==============================================================================

# A Window defines:
#   PARTITION BY = groups (like GROUP BY, but rows are not collapsed)
#   ORDER BY     = order within each partition
#   FRAME        = which surrounding rows to include (for running totals)

# Define windows:
window_by_customer = Window.partition_by("O_CUSTKEY").order_by(col("O_ORDERDATE").desc())
window_by_status = Window.partition_by("O_ORDERSTATUS").order_by("O_TOTALPRICE")
window_all = Window.order_by(col("O_TOTALPRICE").desc())  # No partition = entire table

# ==============================================================================
# SECTION 3: ROW_NUMBER — Ranking Within Groups
# ==============================================================================

# "For each customer, number their orders from most recent to oldest"
orders = session.table("SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS")

orders_ranked = orders.with_column(
    "ORDER_RANK",
    row_number().over(
        Window.partition_by("O_CUSTKEY").order_by(col("O_ORDERDATE").desc())
    )
)

# Get LATEST order for each customer (rank = 1):
latest_orders = (
    orders_ranked
    .filter(col("ORDER_RANK") == 1)
    .select(
        col("O_CUSTKEY").alias("CUSTOMER_ID"),
        col("O_ORDERKEY").alias("LATEST_ORDER_ID"),
        col("O_ORDERDATE").alias("LATEST_ORDER_DATE"),
        col("O_TOTALPRICE").alias("LATEST_ORDER_TOTAL")
    )
)
latest_orders.show(10)

# SQL equivalent:
# SELECT * FROM (
#   SELECT *, ROW_NUMBER() OVER (PARTITION BY O_CUSTKEY ORDER BY O_ORDERDATE DESC) AS rn
#   FROM ORDERS
# ) WHERE rn = 1

# ==============================================================================
# SECTION 4: RANK vs DENSE_RANK vs ROW_NUMBER
# ==============================================================================

# row_number(): Always unique (1, 2, 3, 4, 5) — ties get arbitrary order
# rank():       Ties get same rank, skips next (1, 2, 2, 4, 5)
# dense_rank(): Ties get same rank, no skip (1, 2, 2, 3, 4)

# Top 5 orders by total price (globally):
top_orders = (
    orders
    .with_column("GLOBAL_RANK", rank().over(Window.order_by(col("O_TOTALPRICE").desc())))
    .filter(col("GLOBAL_RANK") <= 5)
    .select("O_ORDERKEY", "O_TOTALPRICE", "GLOBAL_RANK")
)
top_orders.show()

# Top 3 orders PER status:
top_per_status = (
    orders
    .with_column("RANK_IN_STATUS",
        row_number().over(
            Window.partition_by("O_ORDERSTATUS").order_by(col("O_TOTALPRICE").desc())
        )
    )
    .filter(col("RANK_IN_STATUS") <= 3)
    .select("O_ORDERSTATUS", "O_ORDERKEY", "O_TOTALPRICE", "RANK_IN_STATUS")
    .sort("O_ORDERSTATUS", "RANK_IN_STATUS")
)
top_per_status.show()

# ==============================================================================
# SECTION 5: LAG AND LEAD — Previous/Next Row
# ==============================================================================

# lag() = value from PREVIOUS row
# lead() = value from NEXT row
# Useful for: comparing to previous period, calculating changes

# "For each customer's orders, what was the previous order total?"
orders_with_prev = (
    orders
    .with_column("PREV_ORDER_TOTAL",
        lag(col("O_TOTALPRICE"), 1).over(
            Window.partition_by("O_CUSTKEY").order_by("O_ORDERDATE")
        )
    )
    .with_column("ORDER_CHANGE",
        col("O_TOTALPRICE") - col("PREV_ORDER_TOTAL")
    )
    .filter(col("PREV_ORDER_TOTAL").is_not_null())
    .select("O_CUSTKEY", "O_ORDERDATE", "O_TOTALPRICE", "PREV_ORDER_TOTAL", "ORDER_CHANGE")
)
orders_with_prev.show(10)

# ==============================================================================
# SECTION 6: RUNNING TOTALS (Cumulative Sum)
# ==============================================================================

# Frame specification for running totals:
# Window.partition_by("X").order_by("Y").rows_between(Window.UNBOUNDED_PRECEDING, Window.CURRENT_ROW)

running_window = (
    Window.partition_by("O_CUSTKEY")
    .order_by("O_ORDERDATE")
    .rows_between(Window.UNBOUNDED_PRECEDING, Window.CURRENT_ROW)
)

orders_cumulative = (
    orders
    .with_column("CUMULATIVE_SPEND", sum("O_TOTALPRICE").over(running_window))
    .with_column("ORDER_NUMBER",
        row_number().over(
            Window.partition_by("O_CUSTKEY").order_by("O_ORDERDATE")
        )
    )
    .filter(col("O_CUSTKEY") == 1)  # Show for one customer
    .select("O_CUSTKEY", "O_ORDERDATE", "O_TOTALPRICE", "CUMULATIVE_SPEND", "ORDER_NUMBER")
    .sort("O_ORDERDATE")
)
orders_cumulative.show(20)

# ==============================================================================
# SECTION 7: NTILE AND PERCENTILES
# ==============================================================================

# ntile(n) divides rows into n equal groups (quartiles, deciles, etc.)

# Divide customers into 4 quartiles by revenue:
customer_quartiles = (
    orders
    .group_by("O_CUSTKEY")
    .agg(sum("O_TOTALPRICE").alias("TOTAL_REVENUE"))
    .with_column("QUARTILE",
        ntile(4).over(Window.order_by(col("TOTAL_REVENUE").desc()))
    )
)
customer_quartiles.show(10)

# Count per quartile:
customer_quartiles.group_by("QUARTILE").agg(
    count("*").alias("CUSTOMER_COUNT"),
    avg("TOTAL_REVENUE").alias("AVG_REVENUE"),
    min("TOTAL_REVENUE").alias("MIN_REVENUE"),
    max("TOTAL_REVENUE").alias("MAX_REVENUE")
).sort("QUARTILE").show()

# ==============================================================================
# SECTION 8: PIVOTING DATA
# ==============================================================================

# Pivot = turn row values into columns (like PIVOT in SQL)

# Orders by year and status → pivot status into columns:
yearly_orders = (
    orders
    .with_column("ORDER_YEAR", year(col("O_ORDERDATE")))
    .group_by("ORDER_YEAR", "O_ORDERSTATUS")
    .agg(count("*").alias("ORDER_COUNT"))
)

# Pivot:
pivoted = yearly_orders.pivot("O_ORDERSTATUS", ["F", "O", "P"]).agg(
    sum("ORDER_COUNT")
).sort("ORDER_YEAR")
pivoted.show()

# ==============================================================================
# SECTION 9: UNION AND SET OPERATIONS
# ==============================================================================

# Combine two DataFrames (like UNION ALL):
orders_1995 = orders.filter(year(col("O_ORDERDATE")) == 1995).select("O_ORDERKEY", "O_TOTALPRICE")
orders_1996 = orders.filter(year(col("O_ORDERDATE")) == 1996).select("O_ORDERKEY", "O_TOTALPRICE")

combined = orders_1995.union_all(orders_1996)
print(f"Combined rows: {combined.count():,}")

# UNION (deduplicates):
# combined_unique = orders_1995.union(orders_1996)

# INTERSECT:
# common = df1.intersect(df2)

# EXCEPT (MINUS):
# only_in_df1 = df1.except_(df2)

# ==============================================================================
# SECTION 10: COMPLETE EXAMPLE — Monthly Revenue with MoM Growth
# ==============================================================================

monthly_revenue = (
    orders
    .with_column("ORDER_MONTH",
        concat(
            year(col("O_ORDERDATE")).cast("string"),
            lit("-"),
            when(month(col("O_ORDERDATE")) < 10,
                concat(lit("0"), month(col("O_ORDERDATE")).cast("string"))
            ).otherwise(month(col("O_ORDERDATE")).cast("string"))
        )
    )
    .group_by("ORDER_MONTH")
    .agg(
        sum("O_TOTALPRICE").alias("REVENUE"),
        count("*").alias("ORDER_COUNT")
    )
    .with_column("PREV_MONTH_REVENUE",
        lag(col("REVENUE"), 1).over(Window.order_by("ORDER_MONTH"))
    )
    .with_column("MOM_GROWTH_PCT",
        when(col("PREV_MONTH_REVENUE").is_not_null(),
            round_((col("REVENUE") - col("PREV_MONTH_REVENUE")) / col("PREV_MONTH_REVENUE") * 100, 2)
        )
    )
    .sort("ORDER_MONTH")
)
monthly_revenue.show(24)

# ==============================================================================
# SECTION 11: KEY TAKEAWAYS
# ==============================================================================

# 1. Window = partition_by + order_by (like GROUP BY but keeps all rows)
# 2. row_number() = unique rank | rank() = ties share rank | dense_rank() = no gaps
# 3. lag(col, n) = previous row value | lead(col, n) = next row value
# 4. Running totals: sum().over(window with UNBOUNDED_PRECEDING to CURRENT_ROW)
# 5. ntile(n) = divide into n equal groups (quartiles, deciles)
# 6. Pivot turns row values into columns
# 7. union_all / intersect / except_ for set operations
# 8. Window functions are ESSENTIAL for analytics and interviews!

# ==============================================================================
# NEXT: Module 11 — UDFs and Stored Procedures
# ==============================================================================
