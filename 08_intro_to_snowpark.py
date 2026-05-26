# ==============================================================================
# MODULE 8: INTRODUCTION TO SNOWPARK
# ==============================================================================
# Level: Intermediate
# Time: 30 minutes
# Prerequisites: Module 01-07 completed
# ==============================================================================

# ==============================================================================
# SECTION 1: WHAT IS SNOWPARK?
# ==============================================================================

# Snowpark = Snowflake's Python API for data processing.
#
# Think of it as: "Write Python, execute on Snowflake's compute."
#
# KEY INSIGHT: Your Python code does NOT pull data to your laptop.
#   Instead, Snowpark converts your Python into SQL and runs it INSIDE Snowflake.
#   Your data never leaves the warehouse!
#
# ┌──────────────────────────────────────────────────────────────────┐
# │  YOUR PYTHON CODE                                                │
# │  df = session.table("ORDERS")                                    │
# │  df = df.filter(col("TOTAL") > 100)                             │
# │  df = df.group_by("STATUS").agg(sum("TOTAL"))                   │
# │                      │                                           │
# │                      ▼                                           │
# │  SNOWPARK TRANSLATES TO SQL:                                     │
# │  SELECT STATUS, SUM(TOTAL)                                       │
# │  FROM ORDERS                                                     │
# │  WHERE TOTAL > 100                                               │
# │  GROUP BY STATUS                                                 │
# │                      │                                           │
# │                      ▼                                           │
# │  EXECUTES ON SNOWFLAKE WAREHOUSE (not your machine!)             │
# └──────────────────────────────────────────────────────────────────┘
#
# WHY use Snowpark instead of SQL?
#   1. Complex logic is easier in Python (loops, conditionals, ML)
#   2. Reusable functions (UDFs) you can test locally
#   3. Integration with Python libraries (pandas, scikit-learn)
#   4. Programmatic pipelines (dynamic SQL is messy; Python is clean)
#   5. One language for ETL + ML + orchestration

# ==============================================================================
# SECTION 2: THE SESSION — Your Connection to Snowflake
# ==============================================================================

# The Session is your gateway. Everything starts here.
# In a Snowflake Notebook or Stored Procedure, it's available automatically.

from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, lit, sum, avg, count, max, min
from snowflake.snowpark.functions import when, upper, lower, trim, concat
from snowflake.snowpark.types import IntegerType, StringType, FloatType

# IN A SNOWFLAKE NOTEBOOK (session is pre-created):
# session = get_active_session()

# LOCALLY (for development — you'd create it like this):
# connection_params = {
#     "account": "myorg-myaccount",
#     "user": "myuser",
#     "password": "mypass",
#     "role": "DATA_ENGINEER",
#     "warehouse": "COMPUTE_WH",
#     "database": "ANALYTICS",
#     "schema": "DEV",
# }
# session = Session.builder.configs(connection_params).create()

# IMPORTANT: In Snowflake Notebooks/Stored Procedures, session is given to you.
# You'll almost never create it manually in production.

# ==============================================================================
# SECTION 3: CREATING DATAFRAMES
# ==============================================================================

# A Snowpark DataFrame = a reference to data in Snowflake.
# It does NOT load data into Python. It builds a QUERY PLAN.

# Method 1: From existing table
# df = session.table("SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS")

# Method 2: From SQL query
# df = session.sql("SELECT * FROM ORDERS WHERE O_ORDERDATE > '1998-01-01'")

# Method 3: From Python data (for small data / testing)
# from snowflake.snowpark import Row
# df = session.create_dataframe(
#     [Row(1, "Alice", 100.0), Row(2, "Bob", 200.0)],
#     schema=["id", "name", "amount"]
# )

# Method 4: From pandas DataFrame
# import pandas as pd
# pandas_df = pd.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"]})
# df = session.create_dataframe(pandas_df)

# ==============================================================================
# SECTION 4: LAZY EVALUATION (Critical Concept!)
# ==============================================================================

# Snowpark is LAZY — operations build a plan but DON'T execute until triggered.
#
# THESE DO NOT HIT SNOWFLAKE (just build a plan):
#   df.filter(...)
#   df.select(...)
#   df.group_by(...)
#   df.join(...)
#   df.sort(...)
#
# THESE TRIGGER EXECUTION (called "actions"):
#   df.collect()      → Returns all rows as Python list
#   df.show()         → Prints first 10 rows
#   df.count()        → Returns row count (integer)
#   df.to_pandas()    → Converts to pandas DataFrame
#   df.first()        → Returns first row
#   df.write.save_as_table()  → Writes to Snowflake table
#
# WHY lazy?
#   Snowpark can OPTIMIZE the entire plan before executing.
#   It sends ONE optimized SQL query instead of multiple.
#
# ANALOGY:
#   Eager (pandas): Cook each ingredient as you go
#   Lazy (Snowpark): Plan the full recipe, then cook everything efficiently

# ==============================================================================
# SECTION 5: BASIC OPERATIONS — SNOWPARK vs SQL
# ==============================================================================

# All examples below assume:
# df = session.table("SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS")

# --- SELECT columns ---
# Snowpark: df.select(col("O_ORDERKEY"), col("O_TOTALPRICE"))
# SQL:      SELECT O_ORDERKEY, O_TOTALPRICE FROM ORDERS

# --- RENAME columns ---
# Snowpark: df.select(col("O_ORDERKEY").alias("order_id"))
# SQL:      SELECT O_ORDERKEY AS order_id FROM ORDERS

# --- FILTER (WHERE) ---
# Snowpark: df.filter(col("O_TOTALPRICE") > 1000)
# SQL:      SELECT * FROM ORDERS WHERE O_TOTALPRICE > 1000

# --- AND / OR conditions ---
# Snowpark: df.filter((col("O_ORDERSTATUS") == "F") & (col("O_TOTALPRICE") > 1000))
# SQL:      WHERE O_ORDERSTATUS = 'F' AND O_TOTALPRICE > 1000

# --- SORT (ORDER BY) ---
# Snowpark: df.sort(col("O_TOTALPRICE").desc())
# SQL:      ORDER BY O_TOTALPRICE DESC

# --- LIMIT ---
# Snowpark: df.limit(10)
# SQL:      LIMIT 10

# --- DISTINCT ---
# Snowpark: df.select("O_ORDERSTATUS").distinct()
# SQL:      SELECT DISTINCT O_ORDERSTATUS FROM ORDERS

# ==============================================================================
# SECTION 6: COLUMN EXPRESSIONS
# ==============================================================================

# col("COLUMN_NAME") references a column.
# You can build expressions with it:

# Arithmetic:
# col("PRICE") * col("QUANTITY")           → PRICE * QUANTITY
# col("PRICE") * lit(1.08)                 → PRICE * 1.08 (add tax)
# col("TOTAL") - col("DISCOUNT")           → TOTAL - DISCOUNT

# String functions:
# upper(col("NAME"))                        → UPPER(NAME)
# lower(col("EMAIL"))                       → LOWER(EMAIL)
# trim(col("ADDRESS"))                      → TRIM(ADDRESS)
# concat(col("FIRST"), lit(" "), col("LAST"))  → CONCAT(FIRST, ' ', LAST)

# Conditional (CASE WHEN):
# when(col("TOTAL") > 1000, lit("HIGH"))
#   .when(col("TOTAL") > 500, lit("MED"))
#   .otherwise(lit("LOW"))
# SQL: CASE WHEN TOTAL > 1000 THEN 'HIGH' WHEN TOTAL > 500 THEN 'MED' ELSE 'LOW' END

# NULL handling:
# col("VALUE").is_null()                    → VALUE IS NULL
# col("VALUE").is_not_null()                → VALUE IS NOT NULL

# ==============================================================================
# SECTION 7: ADDING COLUMNS (with_column)
# ==============================================================================

# df.with_column("NEW_COL", expression) adds/replaces a column.
#
# # Add calculated column:
# df = df.with_column("TOTAL_WITH_TAX", col("O_TOTALPRICE") * lit(1.08))
#
# # Add conditional column:
# df = df.with_column("SIZE_CATEGORY",
#     when(col("O_TOTALPRICE") > 10000, lit("LARGE"))
#     .when(col("O_TOTALPRICE") > 1000, lit("MEDIUM"))
#     .otherwise(lit("SMALL"))
# )
#
# # Rename existing column:
# df = df.with_column_renamed("O_ORDERKEY", "ORDER_ID")

# ==============================================================================
# SECTION 8: AGGREGATIONS (GROUP BY)
# ==============================================================================

# from snowflake.snowpark.functions import sum, avg, count, min, max
#
# # Simple aggregation:
# df.group_by("O_ORDERSTATUS").agg(
#     count("*").alias("ORDER_COUNT"),
#     sum("O_TOTALPRICE").alias("TOTAL_REVENUE"),
#     avg("O_TOTALPRICE").alias("AVG_ORDER_VALUE"),
# )
# SQL: SELECT O_ORDERSTATUS, COUNT(*), SUM(O_TOTALPRICE), AVG(O_TOTALPRICE)
#      FROM ORDERS GROUP BY O_ORDERSTATUS
#
# # Multiple group-by columns:
# df.group_by(["O_ORDERSTATUS", "O_ORDERPRIORITY"]).agg(
#     count("*").alias("CNT")
# )

# ==============================================================================
# SECTION 9: JOINS
# ==============================================================================

# orders = session.table("ORDERS")
# customers = session.table("CUSTOMER")
#
# # INNER JOIN:
# joined = orders.join(customers,
#     orders["O_CUSTKEY"] == customers["C_CUSTKEY"],
#     join_type="inner"
# )
#
# # LEFT JOIN:
# joined = orders.join(customers,
#     orders["O_CUSTKEY"] == customers["C_CUSTKEY"],
#     join_type="left"
# )
#
# # After joining, select specific columns:
# result = joined.select(
#     orders["O_ORDERKEY"].alias("ORDER_ID"),
#     customers["C_NAME"].alias("CUSTOMER_NAME"),
#     orders["O_TOTALPRICE"].alias("TOTAL")
# )

# ==============================================================================
# SECTION 10: WRITING RESULTS
# ==============================================================================

# Write DataFrame to a Snowflake table:
# df.write.mode("overwrite").save_as_table("ANALYTICS.DEV.MY_TABLE")
#
# Modes:
#   "overwrite"  → DROP and recreate (like dbt table materialization)
#   "append"     → INSERT INTO existing table
#   "errorifexists" → Fail if table exists (default)
#
# Write to stage (CSV/Parquet):
# df.write.csv("@my_stage/output/data.csv")
# df.write.parquet("@my_stage/output/data.parquet")
#
# Convert to pandas (for small results only!):
# pandas_df = df.to_pandas()

# ==============================================================================
# SECTION 11: METHOD CHAINING (The Power Pattern)
# ==============================================================================

# Chain operations together (like piping in Unix or subqueries in SQL):
#
# result = (
#     session.table("SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS")
#     .filter(col("O_ORDERDATE") >= "1998-01-01")
#     .select(
#         col("O_CUSTKEY").alias("CUSTOMER_ID"),
#         col("O_TOTALPRICE").alias("TOTAL"),
#         col("O_ORDERSTATUS").alias("STATUS"),
#     )
#     .filter(col("TOTAL") > 1000)
#     .sort(col("TOTAL").desc())
#     .limit(100)
# )
# result.show()
#
# This is equivalent to:
# SELECT O_CUSTKEY AS CUSTOMER_ID, O_TOTALPRICE AS TOTAL, O_ORDERSTATUS AS STATUS
# FROM ORDERS
# WHERE O_ORDERDATE >= '1998-01-01' AND O_TOTALPRICE > 1000
# ORDER BY O_TOTALPRICE DESC
# LIMIT 100

# ==============================================================================
# SECTION 12: SEE THE GENERATED SQL
# ==============================================================================

# Want to see what SQL Snowpark generates? Use .queries:
#
# df = session.table("ORDERS").filter(col("O_TOTALPRICE") > 1000)
# print(df.queries)
# Output: {'queries': ['SELECT * FROM ORDERS WHERE O_TOTALPRICE > 1000']}
#
# Or use explain():
# df.explain()
# Shows the query execution plan (like EXPLAIN in SQL)

# ==============================================================================
# SECTION 13: SNOWPARK vs PANDAS SUMMARY
# ==============================================================================

# ┌─────────────────────┬──────────────────────────────────────────────────┐
# │ Feature             │ pandas vs Snowpark                               │
# ├─────────────────────┼──────────────────────────────────────────────────┤
# │ Where runs          │ pandas: your machine | Snowpark: Snowflake       │
# │ Data size           │ pandas: < 10GB | Snowpark: unlimited             │
# │ Evaluation          │ pandas: eager | Snowpark: lazy                   │
# │ Execution trigger   │ pandas: immediate | Snowpark: .collect()/.show() │
# │ Column access       │ pandas: df["col"] | Snowpark: col("COL")         │
# │ Filter              │ pandas: df[df.x>5] | Snowpark: df.filter(...)    │
# │ Group by            │ pandas: .groupby() | Snowpark: .group_by()       │
# │ Output              │ pandas: .to_csv() | Snowpark: .save_as_table()   │
# └─────────────────────┴──────────────────────────────────────────────────┘

# ==============================================================================
# SECTION 14: KEY TAKEAWAYS
# ==============================================================================

# 1. Snowpark = write Python, execute on Snowflake (data stays in warehouse)
# 2. Session = your connection object (given to you in notebooks/procedures)
# 3. DataFrame = lazy query plan (not actual data in memory)
# 4. .collect()/.show()/.count() trigger actual execution
# 5. col("NAME") to reference columns; lit(value) for constants
# 6. Method chaining: df.filter().select().sort() — readable and efficient
# 7. .write.save_as_table() to persist results as Snowflake tables
# 8. .queries property shows you the generated SQL

# ==============================================================================
# NEXT: Module 09 — Snowpark DataFrames (select, filter, join, aggregate)
# ==============================================================================
