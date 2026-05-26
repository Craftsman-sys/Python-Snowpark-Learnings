# ==============================================================================
# MODULE 15: READING & MODIFYING EXISTING STORED PROCEDURES
# ==============================================================================
# Level: Practical / Real-World
# Time: 35 minutes
# PURPOSE: You just joined a team. There are existing Python stored procedures
#          in Snowflake. Your manager says "go fix the bug in that proc" or
#          "add a new column to the output." THIS module teaches you how.
# ==============================================================================

# ==============================================================================
# SECTION 1: HOW STORED PROCEDURES LOOK IN SNOWFLAKE
# ==============================================================================

# When you run DESCRIBE PROCEDURE or look at a proc in Snowsight, you see SQL
# that WRAPS Python code. Here's the anatomy:
#
# ┌────────────────────────────────────────────────────────────────────────────┐
# │ CREATE OR REPLACE PROCEDURE my_database.my_schema.my_procedure(           │
# │     param1 VARCHAR,                    ← Input parameters (typed)          │
# │     param2 NUMBER                                                          │
# │ )                                                                          │
# │ RETURNS VARCHAR                         ← What it gives back              │
# │ LANGUAGE PYTHON                         ← Could be Java/Scala too         │
# │ RUNTIME_VERSION = '3.9'                 ← Python version                  │
# │ PACKAGES = ('snowflake-snowpark-python', 'pandas')  ← Libraries used     │
# │ HANDLER = 'main'                        ← Which Python function to call   │
# │ AS                                                                         │
# │ $$                                      ← Python code starts here         │
# │ def main(session, param1, param2):      ← MUST match handler name         │
# │     # ... Python code ...                                                  │
# │     return "Done"                                                          │
# │ $$;                                     ← Python code ends here           │
# └────────────────────────────────────────────────────────────────────────────┘
#
# KEY THINGS TO NOTICE:
#   1. HANDLER = 'main' → the function named 'main' is what runs
#   2. First parameter is ALWAYS 'session' (Snowflake gives it to you)
#   3. Remaining parameters match the SQL parameter list (param1, param2)
#   4. PACKAGES lists what's available (you can't import unlisted packages)
#   5. Code lives between $$ ... $$ (dollar-sign delimiters)
#   6. RETURNS type must match what the Python function returns

# ==============================================================================
# SECTION 2: REAL EXAMPLE — Understand This Stored Procedure
# ==============================================================================

# Here's a REAL stored procedure you might find at work.
# Let's break it down line by line.

# -- SQL WRAPPER (you'd see this in Snowflake):
# CREATE OR REPLACE PROCEDURE ANALYTICS.PROD.REFRESH_DAILY_METRICS(
#     target_date VARCHAR DEFAULT NULL
# )
# RETURNS VARCHAR
# LANGUAGE PYTHON
# RUNTIME_VERSION = '3.9'
# PACKAGES = ('snowflake-snowpark-python')
# HANDLER = 'run'
# AS
# $$

def run(session, target_date=None):
    """Refresh daily metrics table for a given date (or yesterday)."""
    from snowflake.snowpark.functions import col, sum, count, avg, lit, current_date
    from datetime import date, timedelta

    # If no date provided, use yesterday
    if target_date is None:
        target_date = str(date.today() - timedelta(days=1))

    # Read orders for that date
    orders = session.table("RAW.SHOPIFY.ORDERS")
    daily_orders = orders.filter(col("ORDER_DATE") == lit(target_date))

    # Calculate metrics
    metrics = daily_orders.agg(
        lit(target_date).alias("METRIC_DATE"),
        count("*").alias("TOTAL_ORDERS"),
        sum("TOTAL_PRICE").alias("TOTAL_REVENUE"),
        avg("TOTAL_PRICE").alias("AVG_ORDER_VALUE"),
    )

    # Write to metrics table (append — one row per day)
    metrics.write.mode("append").save_as_table("ANALYTICS.PROD.DAILY_METRICS")

    row_count = daily_orders.count()
    return f"SUCCESS: Processed {row_count} orders for {target_date}"

# $$;

# LINE-BY-LINE BREAKDOWN:
#
# def run(session, target_date=None):
#   └─ 'session' = Snowflake connection (auto-provided)
#   └─ 'target_date=None' = optional parameter (defaults to None)
#
# from snowflake.snowpark.functions import ...
#   └─ Imports INSIDE the function (common pattern in stored procs)
#   └─ This is because the code lives inside $$ delimiters
#
# if target_date is None:
#   └─ Python logic: compute default value if not provided
#
# session.table("RAW.SHOPIFY.ORDERS")
#   └─ Opens a reference to the table (lazy — no data loaded yet)
#
# .filter(col("ORDER_DATE") == lit(target_date))
#   └─ WHERE ORDER_DATE = '2024-01-15' (the date we want)
#   └─ lit() wraps a Python value for use in Snowpark expressions
#
# .agg(...)
#   └─ GROUP BY with no group_by = aggregate entire dataset
#
# .write.mode("append").save_as_table(...)
#   └─ INSERT INTO the target table
#
# return f"SUCCESS: ..."
#   └─ Stored procs must return something (status message)

# ==============================================================================
# SECTION 3: COMMON PATTERNS YOU'LL SEE IN EXISTING PROCS
# ==============================================================================

# PATTERN 1: Imports inside the function
# WHY: Code is inside $$ delimiters. Imports must be inside the handler.
def handler(session):
    from snowflake.snowpark.functions import col, sum, count  # ← INSIDE
    from datetime import datetime
    # ... rest of code

# PATTERN 2: SQL mixed with Snowpark
# Many procs use session.sql() for DDL and DataFrames for transforms.
def handler(session):
    # DDL via SQL (create/drop/grant):
    session.sql("CREATE TABLE IF NOT EXISTS DB.SCHEMA.MY_TABLE (ID INT)").collect()

    # Transforms via DataFrame:
    df = session.table("SOURCE_TABLE")
    result = df.filter(col("STATUS") == "ACTIVE")
    result.write.mode("overwrite").save_as_table("TARGET_TABLE")
    return "Done"

# PATTERN 3: Using session.sql() for everything
# Some developers write SQL inside Python (less "Pythonic" but common):
def handler(session):
    session.sql("""
        CREATE OR REPLACE TABLE analytics.summary AS
        SELECT
            customer_id,
            COUNT(*) as order_count,
            SUM(total) as revenue
        FROM raw.orders
        GROUP BY customer_id
    """).collect()     # ← .collect() EXECUTES the SQL!
    return "Done"

# PATTERN 4: Try/except for error handling
def handler(session):
    try:
        df = session.table("SOME_TABLE")
        df.write.mode("overwrite").save_as_table("TARGET")
        return "SUCCESS"
    except Exception as e:
        return f"FAILED: {str(e)}"

# PATTERN 5: Looping over tables or parameters
def handler(session, tables_csv):
    tables = tables_csv.split(",")  # "orders,customers,products" → list
    results = []
    for table in tables:
        count = session.table(f"RAW.{table.strip()}").count()
        results.append(f"{table}: {count} rows")
    return "\n".join(results)

# PATTERN 6: Returning structured results as JSON
def handler(session):
    import json
    results = {"tables_processed": 5, "rows_loaded": 10000, "errors": 0}
    return json.dumps(results)

# ==============================================================================
# SECTION 4: HOW TO READ AN UNFAMILIAR STORED PROCEDURE
# ==============================================================================

# STEP-BY-STEP APPROACH:
#
# 1. IDENTIFY THE HANDLER FUNCTION
#    Look for: HANDLER = 'function_name'
#    Find that function in the Python code.
#
# 2. READ THE PARAMETERS
#    What inputs does it accept? Are there defaults?
#    Match SQL params (VARCHAR, NUMBER) to Python types (str, int/float)
#
# 3. IDENTIFY THE DATA FLOW
#    Where does it READ from? (session.table or session.sql SELECT)
#    What TRANSFORMS does it apply? (.filter, .group_by, .join, .with_column)
#    Where does it WRITE to? (.save_as_table or session.sql INSERT/CREATE)
#
# 4. SPOT THE BUSINESS LOGIC
#    What conditions/filters are applied?
#    What calculations are performed?
#    What makes this proc specific to its business purpose?
#
# 5. CHECK ERROR HANDLING
#    Is there try/except? What happens on failure?
#    Does it return useful error messages?

# ==============================================================================
# SECTION 5: HOW TO MODIFY AN EXISTING STORED PROCEDURE
# ==============================================================================

# SCENARIO: Your manager says "Add customer_name to the output table."
#
# APPROACH:
#
# Step 1: Find where the output is created
#   Look for: .save_as_table() or .write or CREATE TABLE
#
# Step 2: Trace back to see what columns are in the DataFrame at that point
#   Look at: .select() calls, .agg() calls, .join() calls
#
# Step 3: Add the column
#   If it's from a join: add the join if not there, include the column in select
#   If it's computed: add a .with_column() call
#
# Step 4: Test before deploying
#   Run the modified code in a notebook first!

# EXAMPLE — Adding a column to an existing proc:

# BEFORE (original proc):
def refresh_summary_BEFORE(session):
    orders = session.table("RAW.ORDERS")
    summary = orders.group_by("CUSTOMER_ID").agg(
        count("*").alias("ORDER_COUNT"),
        sum("TOTAL").alias("REVENUE"),
    )
    summary.write.mode("overwrite").save_as_table("ANALYTICS.CUSTOMER_SUMMARY")
    return "Done"

# AFTER (your modification — added customer_name via JOIN):
def refresh_summary_AFTER(session):
    from snowflake.snowpark.functions import col, count, sum

    orders = session.table("RAW.ORDERS")
    customers = session.table("RAW.CUSTOMERS")  # ← NEW: bring in customer table

    summary = (
        orders
        .group_by("CUSTOMER_ID")
        .agg(
            count("*").alias("ORDER_COUNT"),
            sum("TOTAL").alias("REVENUE"),
        )
        .join(                                   # ← NEW: join customer name
            customers.select("CUSTOMER_ID", "CUSTOMER_NAME"),
            on="CUSTOMER_ID",
            join_type="left"
        )
    )
    summary.write.mode("overwrite").save_as_table("ANALYTICS.CUSTOMER_SUMMARY")
    return "Done"

# ==============================================================================
# SECTION 6: COMMON BUGS AND HOW TO FIX THEM
# ==============================================================================

# BUG 1: "Function not found" / Handler mismatch
# CAUSE: HANDLER = 'main' but function is named 'handler'
# FIX: Make HANDLER match your function name exactly.

# BUG 2: "Package not available"
# CAUSE: Using a library not listed in PACKAGES = (...)
# FIX: Add it to PACKAGES. Check Snowflake conda channel for availability.

# BUG 3: "Column 'X' does not exist"
# CAUSE: Column names are CASE-SENSITIVE in Snowpark (usually UPPERCASE)
# FIX: Use col("UPPER_CASE_NAME") — match what's in the actual table.
# TIP: Run: session.table("MY_TABLE").columns to see exact names.

# BUG 4: ".collect() missing" — SQL doesn't execute
# CAUSE: session.sql("CREATE TABLE ...") without .collect()
# FIX: Add .collect() after session.sql() for DDL/DML statements.
# NOTE: session.table() does NOT need .collect() — it's a reference.

# BUG 5: "Write mode error" — table already exists
# CAUSE: .write.save_as_table() with default mode on existing table
# FIX: Use .write.mode("overwrite") or .write.mode("append")

# BUG 6: "Ambiguous column reference" after JOIN
# CAUSE: Both tables have a column with the same name
# FIX: Use table reference: orders["CUSTOMER_ID"] instead of col("CUSTOMER_ID")
# OR: Rename before joining: df.with_column_renamed("ID", "CUST_ID")

# BUG 7: "Return type mismatch"
# CAUSE: RETURNS VARCHAR but function returns an integer
# FIX: return str(result) — always convert return to match SQL type.

# BUG 8: Nothing seems to happen (lazy evaluation!)
# CAUSE: DataFrame operations are lazy. Without an action, nothing runs.
# FIX: Ensure .collect(), .show(), .count(), or .write.save_as_table() is called.

# ==============================================================================
# SECTION 7: HOW TO VIEW EXISTING PROCEDURES IN SNOWFLAKE
# ==============================================================================

# Find all procedures in a schema:
# SHOW PROCEDURES IN SCHEMA ANALYTICS.PROD;
#
# See the full source code:
# SELECT GET_DDL('PROCEDURE', 'ANALYTICS.PROD.MY_PROC(VARCHAR, NUMBER)');
#
# Describe parameters:
# DESCRIBE PROCEDURE ANALYTICS.PROD.MY_PROC(VARCHAR, NUMBER);
#
# Call a procedure:
# CALL ANALYTICS.PROD.MY_PROC('2024-01-15', 100);
#
# See execution history:
# SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
# WHERE QUERY_TEXT ILIKE '%CALL%MY_PROC%'
# ORDER BY START_TIME DESC;

# ==============================================================================
# SECTION 8: MODIFYING A PROC — COMPLETE WORKFLOW
# ==============================================================================

# Real-world workflow when you need to change a stored procedure:
#
# 1. GET THE CODE
#    SELECT GET_DDL('PROCEDURE', 'DB.SCHEMA.PROC_NAME(VARCHAR)');
#    Copy the result.
#
# 2. UNDERSTAND IT
#    - Find the handler function
#    - Trace the data flow (read → transform → write)
#    - Identify what you need to change
#
# 3. TEST IN A NOTEBOOK
#    - Paste the function into a Snowflake Notebook cell
#    - Modify it
#    - Call it manually: result = my_function(session, "test_param")
#    - Verify the output is correct
#
# 4. DEPLOY THE CHANGE
#    - Update the CREATE OR REPLACE PROCEDURE statement
#    - Run it in a SQL worksheet
#    - The old version is replaced immediately
#
# 5. VERIFY
#    - CALL the procedure with test parameters
#    - Check the output table has the expected changes

# ==============================================================================
# SECTION 9: SQL-BASED VS PYTHON-BASED STORED PROCEDURES
# ==============================================================================

# Snowflake supports stored procedures in MULTIPLE languages:
#
# ┌────────────────────┬──────────────────────────────────────────────────────┐
# │ SQL Stored Proc    │ Python Stored Proc                                   │
# ├────────────────────┼──────────────────────────────────────────────────────┤
# │ LANGUAGE SQL       │ LANGUAGE PYTHON                                      │
# │ Simpler for SQL    │ Better for complex logic                             │
# │ No imports needed  │ Can use pandas, ML libraries, APIs                   │
# │ Uses EXECUTE       │ Uses session.sql() or DataFrame API                  │
# │   IMMEDIATE        │                                                      │
# │ Variables with LET │ Normal Python variables                              │
# │ IF/ELSE/FOR in SQL │ Python if/for/while                                  │
# │ Good for DDL tasks │ Good for ETL + ML + complex transforms              │
# └────────────────────┴──────────────────────────────────────────────────────┘
#
# If you see LANGUAGE SQL → It's pure SQL logic (different syntax!)
# If you see LANGUAGE PYTHON → Use this course to understand it.

# ==============================================================================
# SECTION 10: EXERCISE — READ AND MODIFY THIS PROCEDURE
# ==============================================================================

# EXERCISE: Read this proc and answer the questions below.

def process_returns(session, start_date, end_date):
    from snowflake.snowpark.functions import col, sum, count, avg, lit

    line_items = session.table("SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.LINEITEM")

    returns = (
        line_items
        .filter(col("L_RETURNFLAG") == "R")
        .filter(col("L_SHIPDATE").between(lit(start_date), lit(end_date)))
        .group_by("L_SUPPKEY")
        .agg(
            count("*").alias("RETURN_COUNT"),
            sum("L_EXTENDEDPRICE").alias("RETURN_VALUE"),
            avg("L_QUANTITY").alias("AVG_RETURN_QTY"),
        )
    )

    returns.write.mode("overwrite").save_as_table(
        "TPCH_ANALYTICS_DB.DEV.SUPPLIER_RETURNS"
    )
    return f"Processed returns from {start_date} to {end_date}"

# QUESTIONS:
# 1. What table does this procedure READ from?
# 2. What filter conditions are applied?
# 3. What does it GROUP BY?
# 4. What table does it WRITE to?
# 5. How would you ADD the supplier name to the output?
#    (Hint: JOIN with SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.SUPPLIER on L_SUPPKEY = S_SUPPKEY)

# ANSWERS:
# 1. SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.LINEITEM
# 2. L_RETURNFLAG = 'R' AND L_SHIPDATE BETWEEN start_date AND end_date
# 3. L_SUPPKEY (supplier)
# 4. TPCH_ANALYTICS_DB.DEV.SUPPLIER_RETURNS
# 5. Add: .join(session.table("...SUPPLIER"), col("L_SUPPKEY") == col("S_SUPPKEY"))
#    And include col("S_NAME").alias("SUPPLIER_NAME") in the output

# ==============================================================================
# SECTION 11: KEY TAKEAWAYS
# ==============================================================================

# 1. Stored procs = SQL wrapper ($$ Python code $$) + HANDLER function name
# 2. First param is ALWAYS 'session' (Snowflake provides it)
# 3. To read a proc: find handler → trace data flow → spot business logic
# 4. Column names are UPPERCASE in Snowflake (case-sensitive in Snowpark!)
# 5. session.sql("DDL").collect() for CREATE/DROP/GRANT
# 6. DataFrame API for transforms (filter, join, group_by, write)
# 7. Test changes in a Notebook before deploying
# 8. GET_DDL('PROCEDURE', ...) shows you the source code
# 9. Common bugs: handler mismatch, missing .collect(), case sensitivity
# 10. Always return a string status message from stored procedures

# ==============================================================================
# THIS MODULE COMPLETES YOUR ABILITY TO:
#   ✅ Read ANY Python stored procedure in Snowflake
#   ✅ Understand what it does (trace the data flow)
#   ✅ Find and fix common bugs
#   ✅ Add columns, change filters, modify logic
#   ✅ Test changes safely in a notebook
#   ✅ Deploy modifications
# ==============================================================================
