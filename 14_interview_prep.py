# ==============================================================================
# MODULE 14: INTERVIEW PREPARATION — Python + Snowpark Q&A
# ==============================================================================
# Level: All Levels (Review & Practice)
# Time: 30 minutes
# Prerequisites: Module 01-13 completed
# ==============================================================================

# ==============================================================================
# PYTHON FUNDAMENTALS (Q1-Q10)
# ==============================================================================

# Q1: What are Python's mutable vs immutable types?
# ANSWER:
# Mutable (can change): list, dict, set
# Immutable (cannot change): int, float, str, tuple, frozenset
# Example:
my_list = [1, 2, 3]
my_list[0] = 99          # ✅ Works (list is mutable)
my_tuple = (1, 2, 3)
# my_tuple[0] = 99       # ❌ TypeError (tuple is immutable)

# Q2: What is the difference between == and 'is'?
# ANSWER:
# == checks VALUE equality
# 'is' checks IDENTITY (same object in memory)
a = [1, 2, 3]
b = [1, 2, 3]
print(a == b)    # True  (same values)
print(a is b)    # False (different objects in memory)
# Use 'is' ONLY for None: if x is None

# Q3: What are *args and **kwargs?
# ANSWER:
# *args = variable number of positional arguments (tuple)
# **kwargs = variable number of keyword arguments (dict)
def flexible_func(*args, **kwargs):
    print(f"Positional: {args}")    # (1, 2, 3)
    print(f"Keyword: {kwargs}")     # {'name': 'Alice', 'age': 30}

flexible_func(1, 2, 3, name="Alice", age=30)

# Q4: Explain list comprehension vs generator expression.
# ANSWER:
# List comprehension: [x**2 for x in range(1000000)] → creates list in memory
# Generator: (x**2 for x in range(1000000)) → yields one item at a time (lazy!)
# Generators are memory-efficient for large data.
squares_list = [x**2 for x in range(10)]         # All in memory now
squares_gen = (x**2 for x in range(10))          # Computed one at a time

# Q5: What is a decorator?
# ANSWER:
# A decorator wraps a function to add behavior without modifying it.
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "done"

# Q6: What's the difference between a shallow copy and deep copy?
# ANSWER:
import copy
original = [[1, 2], [3, 4]]
shallow = original.copy()        # New outer list, SAME inner lists
deep = copy.deepcopy(original)   # New everything
original[0][0] = 99
print(shallow[0][0])  # 99 (shared inner list!)
print(deep[0][0])     # 1  (independent copy)

# Q7: What are context managers (with statement)?
# ANSWER:
# Ensures cleanup happens even if errors occur.
# with open("file.txt") as f: ← auto-closes file
# Custom:
class Timer:
    def __enter__(self):
        self.start = time.time()
        return self
    def __exit__(self, *args):
        print(f"Elapsed: {time.time() - self.start:.2f}s")

# with Timer(): do_something()

# Q8: Explain Python's GIL (Global Interpreter Lock).
# ANSWER:
# GIL prevents true parallel execution of Python threads.
# For CPU-bound tasks: use multiprocessing (separate processes)
# For I/O-bound tasks: threads work fine (GIL released during I/O)
# In Snowpark: doesn't matter because heavy lifting happens in Snowflake!

# Q9: What is the difference between append() and extend()?
a = [1, 2, 3]
a.append([4, 5])    # [1, 2, 3, [4, 5]] — adds as single element
b = [1, 2, 3]
b.extend([4, 5])    # [1, 2, 3, 4, 5] — adds each element individually

# Q10: How does Python handle memory management?
# ANSWER:
# - Reference counting: objects deleted when ref count hits 0
# - Garbage collector: handles circular references
# - del removes a reference (doesn't necessarily free memory immediately)
# - In data engineering: pandas uses lots of memory; Snowpark doesn't (lazy!)

# ==============================================================================
# SNOWPARK QUESTIONS (Q11-Q20)
# ==============================================================================

# Q11: What is Snowpark and how does it differ from running SQL directly?
# ANSWER:
# Snowpark is a Python API that converts DataFrame operations to SQL.
# Differences:
#   - Programmatic (loops, conditionals, functions) vs. static SQL text
#   - Type-safe column references
#   - Reusable logic (Python functions, classes)
#   - Integration with Python ecosystem (ML libraries, file processing)
#   - Same performance (generates SQL that runs on Snowflake warehouse)

# Q12: What is lazy evaluation in Snowpark?
# ANSWER:
# Operations like .filter(), .select(), .join() build a QUERY PLAN but don't execute.
# Execution happens only when an "action" is called:
#   .collect() → returns rows as Python list
#   .show() → prints results
#   .count() → returns integer
#   .write.save_as_table() → writes to Snowflake
# WHY: Allows Snowpark to optimize the entire plan before execution.

# Q13: What's the difference between a UDF and a Stored Procedure?
# ANSWER:
# UDF (User-Defined Function):
#   - Runs per ROW (called inside SELECT: SELECT my_udf(column) FROM ...)
#   - Returns a scalar value per row
#   - Stateless (no side effects)
#
# Stored Procedure (SPROC):
#   - Runs ONCE when called (CALL my_proc())
#   - Can execute SQL, create tables, orchestrate workflows
#   - Has access to Session (can do anything)
#   - Returns a single value (status message typically)

# Q14: What is a vectorized UDF and when would you use one?
# ANSWER:
# A vectorized UDF processes BATCHES of rows as pandas Series (not one at a time).
# 10-100x faster than scalar UDFs.
# Use when: applying complex Python logic to large datasets.
# Syntax: @pandas_udf decorator, function takes pd.Series → pd.Series

# Q15: How do you handle NULL values in Snowpark?
# ANSWER:
from snowflake.snowpark.functions import col, coalesce, lit, when, is_null
# Filter nulls:    df.filter(col("X").is_null())
# Filter not null: df.filter(col("X").is_not_null())
# Replace null:    df.with_column("X", coalesce(col("X"), lit(0)))
# Conditional:     when(col("X").is_null(), lit("UNKNOWN")).otherwise(col("X"))

# Q16: How do you optimize Snowpark performance?
# ANSWER:
# 1. Minimize .collect() calls (each triggers execution)
# 2. Push filters early (filter before joins — Snowpark does this too)
# 3. Use built-in functions over UDFs where possible
# 4. Use vectorized UDFs over scalar UDFs for custom logic
# 5. Appropriate warehouse size for the workload
# 6. Cache intermediate results: df.cache_result()
# 7. Avoid .to_pandas() for large datasets (pulls data out of Snowflake)

# Q17: How would you implement a slowly changing dimension in Snowpark?
# ANSWER:
# Use MERGE operation:
# df_source = session.table("SOURCE_CUSTOMERS")
# df_target = session.table("DIM_CUSTOMERS")
# df_target.merge(
#     df_source,
#     df_target["ID"] == df_source["ID"],
#     [
#         when_matched().update({...}),
#         when_not_matched().insert({...})
#     ]
# )
# For SCD Type 2: compare values, close old records, insert new versions.

# Q18: How do you join DataFrames when column names conflict?
# ANSWER:
# Use table references to disambiguate:
# orders = session.table("ORDERS")
# customers = session.table("CUSTOMERS")
# joined = orders.join(customers, orders["CUST_ID"] == customers["CUST_ID"])
# Select with table prefix:
# joined.select(orders["CUST_ID"], customers["NAME"])
# Or rename before joining:
# customers_renamed = customers.with_column_renamed("CUST_ID", "CUSTOMER_ID")

# Q19: Explain the Snowpark DataFrame execution lifecycle.
# ANSWER:
# 1. CREATE: session.table() / session.sql() → creates reference
# 2. TRANSFORM: .filter() / .select() / .join() → builds logical plan
# 3. OPTIMIZE: Snowpark optimizes the plan (pushdown, predicate rewrite)
# 4. COMPILE: Plan is converted to SQL string (.queries to see it)
# 5. EXECUTE: Action triggered → SQL sent to Snowflake warehouse
# 6. RETURN: Results come back as Python objects

# Q20: When would you use Snowpark vs. dbt vs. plain SQL?
# ANSWER:
# Plain SQL:
#   Simple queries, ad-hoc analysis, quick investigations
#
# dbt:
#   SQL-based transformations, dependency management, testing/docs,
#   when your team is SQL-first, standard staging/marts pattern
#
# Snowpark:
#   Complex logic (ML, APIs, custom algorithms), programmatic pipelines,
#   when you need Python libraries, dynamic/parametric processing,
#   UDFs that embed Python logic into queries

# ==============================================================================
# SCENARIO-BASED QUESTIONS (Q21-Q25)
# ==============================================================================

# Q21: Design a data pipeline for daily order processing.
# ANSWER:
# Architecture:
#   1. Stored Procedure: run_daily_pipeline(session, date)
#   2. Reads raw orders for the given date (incremental)
#   3. Joins with customer/product dimensions
#   4. Computes metrics (revenue, items, discounts)
#   5. Writes to fact table (append mode)
#   6. Updates dimension tables (merge for SCD)
#   7. Runs quality checks
#   8. Logs results to audit table
#   9. Scheduled via Snowflake TASK (6 AM UTC daily)

# Q22: How would you handle errors in a production Snowpark pipeline?
# ANSWER:
def production_pipeline(session):
    try:
        # Step 1: Extract
        source_df = session.table("RAW.ORDERS")

        # Step 2: Transform
        result = source_df.filter(col("AMOUNT") > 0)

        # Step 3: Load
        result.write.mode("overwrite").save_as_table("ANALYTICS.ORDERS_CLEAN")

        return "SUCCESS"
    except Exception as e:
        # Log error to audit table
        error_msg = str(e)[:1000]
        session.sql(f"""
            INSERT INTO AUDIT.PIPELINE_LOG (TIMESTAMP, STATUS, MESSAGE)
            VALUES (CURRENT_TIMESTAMP(), 'FAILED', '{error_msg}')
        """).collect()
        raise  # Re-raise so task shows as failed

# Q23: How do you unit test Snowpark code?
# ANSWER:
# 1. Extract business logic into pure Python functions (no session dependency)
# 2. Test those functions with pytest locally
# 3. For DataFrame logic: use session.create_dataframe() with test data
# 4. Compare outputs with expected results
# Example:
def categorize_amount(amount):
    """Pure function — easy to test!"""
    if amount > 10000: return "HIGH"
    if amount > 1000: return "MEDIUM"
    return "LOW"

assert categorize_amount(15000) == "HIGH"
assert categorize_amount(5000) == "MEDIUM"
assert categorize_amount(500) == "LOW"

# Q24: Explain how you'd migrate a pandas pipeline to Snowpark.
# ANSWER:
# Step 1: Replace pd.read_csv/pd.read_sql with session.table()
# Step 2: Replace df[condition] with df.filter(col("X") == value)
# Step 3: Replace df.groupby() with df.group_by()
# Step 4: Replace .merge() with .join()
# Step 5: Replace .to_csv() with .write.save_as_table()
# Step 6: Remove .apply() where possible → use built-in functions or UDFs
# KEY: pandas is eager, Snowpark is lazy. Add .show()/.collect() where needed.

# Q25: Design a real-time customer segmentation system.
# ANSWER:
# 1. Feature Engineering (Snowpark):
#    - Calculate RFM metrics (Recency, Frequency, Monetary)
#    - Use window functions for percentile ranks
#    - Build customer_features table (refreshed hourly via Task)
#
# 2. Segmentation (Snowpark ML or UDF):
#    - K-means clustering on RFM features OR
#    - Rule-based segmentation with when/otherwise
#    - Store segment assignments in dim_customers
#
# 3. Deployment:
#    - Register model in Model Registry
#    - Create scoring stored procedure
#    - Schedule with Task (hourly refresh)
#    - Expose via Snowflake view for dashboards

# ==============================================================================
# CODING CHALLENGES (Practice These!)
# ==============================================================================

# Challenge 1: Write a function that finds the top N customers by revenue
# per region (using window functions).

# Challenge 2: Implement a generic data quality check function that accepts
# a table name and a list of rules, returns pass/fail for each.

# Challenge 3: Build a stored procedure that does incremental loading
# with proper error handling and logging.

# Challenge 4: Create a UDF that parses semi-structured JSON data
# and extracts specific fields.

# Challenge 5: Write a pipeline that detects data anomalies
# (orders 3+ standard deviations from the mean).

# ==============================================================================
# RECOMMENDED STUDY ORDER FOR INTERVIEWS
# ==============================================================================

# Week 1: Python basics (types, control flow, functions, data structures)
# Week 2: OOP, error handling, file I/O, pandas
# Week 3: Snowpark fundamentals (session, DataFrame, filter, join, group)
# Week 4: Window functions, UDFs, stored procedures
# Week 5: ML basics, real-world patterns, optimization
# Week 6: Practice coding challenges, mock interviews
#
# KEY TOPICS INTERVIEWERS LOVE:
#   - "Explain lazy evaluation"
#   - "UDF vs SPROC — when to use which?"
#   - "How do you optimize a slow Snowpark pipeline?"
#   - "Design a daily ETL pipeline"
#   - "How do you handle late-arriving data?"
#   - "Write a window function for running total / rank"
#   - "What's the difference between pandas and Snowpark?"

# ==============================================================================
# CONGRATULATIONS! You've completed the full Python + Snowpark course.
# ==============================================================================
# You now know:
#   ✅ Python from scratch (variables → classes)
#   ✅ Data manipulation (pandas)
#   ✅ Snowpark DataFrames (select, filter, join, aggregate, window)
#   ✅ UDFs and Stored Procedures
#   ✅ ML basics with Snowpark
#   ✅ Real-world pipeline architecture
#   ✅ Interview-ready answers
#
# Next steps:
#   1. Run Module 13 as a Snowflake Notebook to see the pipeline work
#   2. Modify it: add new dimensions, change business logic
#   3. Build your own pipeline for a different dataset
#   4. Practice the coding challenges above
# ==============================================================================
