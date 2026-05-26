# ==============================================================================
# MODULE 9: SNOWPARK DATAFRAMES — Hands-On Operations
# ==============================================================================
# Level: Intermediate
# Time: 30 minutes
# Prerequisites: Module 01-08 completed
# NOTE: Run this in a Snowflake Notebook (Python) to execute the code!
# ==============================================================================

# ==============================================================================
# SETUP — Run this cell first in a Snowflake Notebook
# ==============================================================================

from snowflake.snowpark import Session
from snowflake.snowpark.functions import (
    col, lit, sum, avg, count, min, max,
    when, upper, lower, trim, concat, length,
    year, month, datediff, current_date,
    round as round_,
    count_distinct
)
from snowflake.snowpark.types import IntegerType, StringType, FloatType

# In Snowflake Notebook:
# session = get_active_session()

# ==============================================================================
# SECTION 1: READING TABLES
# ==============================================================================

# Read the TPCH sample data:
orders = session.table("SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS")
customers = session.table("SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.CUSTOMER")
line_items = session.table("SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.LINEITEM")
nations = session.table("SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.NATION")

# Check schema (like DESC TABLE):
orders.schema
# Or print column names:
print(orders.columns)

# Preview data:
orders.show(5)

# Row count:
print(f"Orders: {orders.count():,} rows")

# ==============================================================================
# SECTION 2: SELECT — Choosing Columns
# ==============================================================================

# Select specific columns with rename:
order_subset = orders.select(
    col("O_ORDERKEY").alias("ORDER_ID"),
    col("O_CUSTKEY").alias("CUSTOMER_ID"),
    col("O_ORDERDATE").alias("ORDER_DATE"),
    col("O_TOTALPRICE").alias("TOTAL_PRICE"),
    col("O_ORDERSTATUS").alias("STATUS")
)
order_subset.show(5)

# Add computed columns:
orders_enhanced = orders.select(
    col("O_ORDERKEY").alias("ORDER_ID"),
    col("O_TOTALPRICE").alias("TOTAL"),
    (col("O_TOTALPRICE") * lit(0.08)).alias("TAX"),
    (col("O_TOTALPRICE") * lit(1.08)).alias("TOTAL_WITH_TAX"),
    year(col("O_ORDERDATE")).alias("ORDER_YEAR"),
    month(col("O_ORDERDATE")).alias("ORDER_MONTH")
)
orders_enhanced.show(5)

# ==============================================================================
# SECTION 3: FILTER — Row Selection (WHERE)
# ==============================================================================

# Simple filter:
large_orders = orders.filter(col("O_TOTALPRICE") > 300000)
large_orders.show(5)
print(f"Large orders: {large_orders.count()}")

# Multiple conditions (AND):
urgent_large = orders.filter(
    (col("O_ORDERPRIORITY") == "1-URGENT") &
    (col("O_TOTALPRICE") > 200000)
)
urgent_large.show(5)

# OR condition:
open_or_pending = orders.filter(
    (col("O_ORDERSTATUS") == "O") | (col("O_ORDERSTATUS") == "P")
)

# IN clause:
specific_statuses = orders.filter(col("O_ORDERSTATUS").isin(["O", "P"]))

# BETWEEN (date range):
orders_1998 = orders.filter(
    (col("O_ORDERDATE") >= "1998-01-01") &
    (col("O_ORDERDATE") < "1999-01-01")
)
print(f"1998 orders: {orders_1998.count():,}")

# LIKE pattern matching:
high_priority = orders.filter(col("O_ORDERPRIORITY").like("1%"))

# IS NULL / IS NOT NULL:
# orders.filter(col("SOME_COL").is_null())
# orders.filter(col("SOME_COL").is_not_null())

# ==============================================================================
# SECTION 4: WITH_COLUMN — Adding/Replacing Columns
# ==============================================================================

# Add a new column:
orders_with_tax = orders.with_column(
    "TOTAL_WITH_TAX",
    round_(col("O_TOTALPRICE") * lit(1.08), 2)
)

# Add conditional column (CASE WHEN):
orders_categorized = orders.with_column(
    "ORDER_SIZE",
    when(col("O_TOTALPRICE") > 200000, lit("LARGE"))
    .when(col("O_TOTALPRICE") > 50000, lit("MEDIUM"))
    .otherwise(lit("SMALL"))
)
orders_categorized.select("O_ORDERKEY", "O_TOTALPRICE", "ORDER_SIZE").show(10)

# Multiple with_column calls (chaining):
result = (
    orders
    .with_column("ORDER_YEAR", year(col("O_ORDERDATE")))
    .with_column("PRICE_CATEGORY",
        when(col("O_TOTALPRICE") > 100000, lit("HIGH"))
        .otherwise(lit("STANDARD"))
    )
)

# ==============================================================================
# SECTION 5: AGGREGATIONS — GROUP BY
# ==============================================================================

# Count by status:
status_counts = orders.group_by("O_ORDERSTATUS").agg(
    count("*").alias("ORDER_COUNT"),
    sum("O_TOTALPRICE").alias("TOTAL_REVENUE"),
    avg("O_TOTALPRICE").alias("AVG_ORDER_VALUE"),
    min("O_TOTALPRICE").alias("MIN_ORDER"),
    max("O_TOTALPRICE").alias("MAX_ORDER")
)
status_counts.show()

# Group by multiple columns:
yearly_status = (
    orders
    .with_column("ORDER_YEAR", year(col("O_ORDERDATE")))
    .group_by("ORDER_YEAR", "O_ORDERSTATUS")
    .agg(
        count("*").alias("CNT"),
        sum("O_TOTALPRICE").alias("REVENUE")
    )
    .sort("ORDER_YEAR", "O_ORDERSTATUS")
)
yearly_status.show(20)

# Count distinct:
distinct_customers = orders.agg(
    count_distinct(col("O_CUSTKEY")).alias("UNIQUE_CUSTOMERS")
)
distinct_customers.show()

# ==============================================================================
# SECTION 6: JOINS
# ==============================================================================

# INNER JOIN: Orders with customer details
orders_with_customer = orders.join(
    customers,
    orders["O_CUSTKEY"] == customers["C_CUSTKEY"],
    join_type="inner"
).select(
    orders["O_ORDERKEY"].alias("ORDER_ID"),
    customers["C_NAME"].alias("CUSTOMER_NAME"),
    customers["C_MKTSEGMENT"].alias("SEGMENT"),
    orders["O_TOTALPRICE"].alias("TOTAL"),
    orders["O_ORDERDATE"].alias("ORDER_DATE")
)
orders_with_customer.show(10)

# LEFT JOIN: All customers, with order info (if any):
customer_orders = customers.join(
    orders,
    customers["C_CUSTKEY"] == orders["O_CUSTKEY"],
    join_type="left"
).select(
    customers["C_NAME"].alias("CUSTOMER"),
    orders["O_ORDERKEY"].alias("ORDER_ID"),
    orders["O_TOTALPRICE"].alias("TOTAL")
)

# JOIN + AGGREGATE (Customer lifetime value):
customer_ltv = (
    orders.join(
        customers,
        orders["O_CUSTKEY"] == customers["C_CUSTKEY"]
    )
    .join(
        nations,
        customers["C_NATIONKEY"] == nations["N_NATIONKEY"]
    )
    .group_by(
        customers["C_CUSTKEY"],
        customers["C_NAME"],
        customers["C_MKTSEGMENT"],
        nations["N_NAME"]
    )
    .agg(
        count("*").alias("TOTAL_ORDERS"),
        sum(orders["O_TOTALPRICE"]).alias("LIFETIME_REVENUE"),
        avg(orders["O_TOTALPRICE"]).alias("AVG_ORDER_VALUE")
    )
    .sort(col("LIFETIME_REVENUE").desc())
    .limit(20)
)
customer_ltv.show()

# ==============================================================================
# SECTION 7: SORTING AND LIMITING
# ==============================================================================

# Sort ascending (default):
orders.sort(col("O_TOTALPRICE")).show(5)

# Sort descending:
orders.sort(col("O_TOTALPRICE").desc()).show(5)

# Multiple sort keys:
orders.sort(
    col("O_ORDERSTATUS").asc(),
    col("O_TOTALPRICE").desc()
).show(10)

# Top N pattern:
top_10_orders = (
    orders
    .sort(col("O_TOTALPRICE").desc())
    .limit(10)
    .select(
        col("O_ORDERKEY").alias("ORDER_ID"),
        col("O_TOTALPRICE").alias("TOTAL")
    )
)
top_10_orders.show()

# ==============================================================================
# SECTION 8: SAVING RESULTS
# ==============================================================================

# Save as a new table:
# customer_ltv.write.mode("overwrite").save_as_table("TPCH_ANALYTICS_DB.DEV.CUSTOMER_LTV")

# Save as view (no data stored):
# customer_ltv.create_or_replace_view("TPCH_ANALYTICS_DB.DEV.V_CUSTOMER_LTV")

# Convert to pandas (for small datasets):
# pdf = customer_ltv.to_pandas()
# print(pdf.head())

# ==============================================================================
# SECTION 9: COMPLETE PIPELINE EXAMPLE
# ==============================================================================

# Real-world scenario: Build an "Order Analytics" summary table

order_analytics = (
    session.table("SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS")
    .join(
        session.table("SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.CUSTOMER"),
        col("O_CUSTKEY") == col("C_CUSTKEY")
    )
    .join(
        session.table("SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.NATION"),
        col("C_NATIONKEY") == col("N_NATIONKEY")
    )
    .with_column("ORDER_YEAR", year(col("O_ORDERDATE")))
    .with_column("ORDER_SIZE",
        when(col("O_TOTALPRICE") > 200000, lit("LARGE"))
        .when(col("O_TOTALPRICE") > 50000, lit("MEDIUM"))
        .otherwise(lit("SMALL"))
    )
    .group_by("ORDER_YEAR", "N_NAME", "C_MKTSEGMENT", "ORDER_SIZE")
    .agg(
        count("*").alias("ORDER_COUNT"),
        sum("O_TOTALPRICE").alias("TOTAL_REVENUE"),
        avg("O_TOTALPRICE").alias("AVG_ORDER_VALUE"),
        count_distinct("O_CUSTKEY").alias("UNIQUE_CUSTOMERS")
    )
    .sort("ORDER_YEAR", col("TOTAL_REVENUE").desc())
)

# Preview:
order_analytics.show(20)

# Save to table:
# order_analytics.write.mode("overwrite").save_as_table(
#     "TPCH_ANALYTICS_DB.DEV.ORDER_ANALYTICS_SUMMARY"
# )

# ==============================================================================
# SECTION 10: KEY TAKEAWAYS
# ==============================================================================

# 1. session.table("TABLE") loads a DataFrame reference (lazy!)
# 2. .select() + .alias() for column selection and renaming
# 3. .filter() for row filtering (WHERE clause)
# 4. .with_column() to add/compute new columns
# 5. .group_by().agg() for aggregations
# 6. .join(other_df, condition, join_type) for joins
# 7. .sort(col.desc()) for ordering
# 8. .write.save_as_table() to persist results
# 9. Chain everything together for readable pipelines
# 10. Nothing executes until .show()/.collect()/.count()/.write

# ==============================================================================
# NEXT: Module 10 — Snowpark Window Functions & Transformations
# ==============================================================================
