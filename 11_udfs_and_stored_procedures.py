# ==============================================================================
# MODULE 11: SNOWPARK UDFs AND STORED PROCEDURES
# ==============================================================================
# Level: Advanced
# Time: 25 minutes
# Prerequisites: Module 01-10 completed
# ==============================================================================

from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, udf, sproc, lit
from snowflake.snowpark.types import (
    IntegerType, StringType, FloatType,
    StructType, StructField, ArrayType, VariantType
)

# session = get_active_session()

# ==============================================================================
# SECTION 1: WHAT ARE UDFs?
# ==============================================================================

# UDF = User-Defined Function
# A Python function that runs INSIDE Snowflake on every row.
#
# Think of it as: Python logic applied at the ROW LEVEL (like a SQL function).
#
# USE CASES:
#   - Complex string parsing (regex, custom formats)
#   - ML model scoring (predict on each row)
#   - Business logic too complex for SQL (multi-step calculations)
#   - API calls per row (geocoding, enrichment)
#
# EXECUTION: The Python code runs on Snowflake's compute (not your machine).

# ==============================================================================
# SECTION 2: INLINE UDFs (Quick & Simple)
# ==============================================================================

# Method 1: @udf decorator (registered in session)

@udf(name="categorize_price", is_permanent=False, replace=True)
def categorize_price(price: float) -> str:
    if price is None:
        return "UNKNOWN"
    elif price > 200000:
        return "ENTERPRISE"
    elif price > 50000:
        return "BUSINESS"
    elif price > 10000:
        return "STANDARD"
    else:
        return "STARTER"

# Use it in a DataFrame:
orders = session.table("SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS")

result = orders.select(
    col("O_ORDERKEY").alias("ORDER_ID"),
    col("O_TOTALPRICE").alias("TOTAL"),
    categorize_price(col("O_TOTALPRICE")).alias("PRICE_TIER")
)
result.show(10)

# Method 2: Lambda-style UDF (for simple transformations)
clean_status = udf(
    lambda s: s.strip().upper() if s else "UNKNOWN",
    return_type=StringType(),
    input_types=[StringType()]
)

# ==============================================================================
# SECTION 3: REGISTERED (PERMANENT) UDFs
# ==============================================================================

# Permanent UDFs persist in Snowflake — callable from SQL too!

@udf(
    name="TPCH_ANALYTICS_DB.DEV.parse_priority_level",
    is_permanent=True,
    stage_location="@TPCH_ANALYTICS_DB.DEV.udf_stage",  # Where to store code
    replace=True
)
def parse_priority_level(priority: str) -> int:
    """Extract numeric priority level from strings like '1-URGENT', '2-HIGH'."""
    if priority is None:
        return 0
    try:
        return int(priority.split("-")[0])
    except (ValueError, IndexError):
        return 0

# Now callable from SQL too:
# SELECT TPCH_ANALYTICS_DB.DEV.parse_priority_level('1-URGENT')  → 1

# ==============================================================================
# SECTION 4: VECTORIZED UDFs (Performance!)
# ==============================================================================

# Vectorized UDFs process BATCHES of rows (pandas Series) instead of one at a time.
# 10-100x faster than regular UDFs for large datasets!

from snowflake.snowpark.functions import pandas_udf
from snowflake.snowpark.types import PandasSeriesType, PandasDataFrameType
import pandas as pd

# Vectorized UDF — processes a pandas Series at a time:
@pandas_udf(
    name="calculate_discount_tier",
    is_permanent=False,
    replace=True
)
def calculate_discount_tier(prices: pd.Series) -> pd.Series:
    """Assign discount tier based on order price (vectorized)."""
    return pd.cut(
        prices,
        bins=[0, 10000, 50000, 200000, float('inf')],
        labels=["NO_DISCOUNT", "5_PERCENT", "10_PERCENT", "15_PERCENT"]
    ).astype(str)

# Usage:
result = orders.with_column(
    "DISCOUNT_TIER",
    calculate_discount_tier(col("O_TOTALPRICE"))
)
result.select("O_ORDERKEY", "O_TOTALPRICE", "DISCOUNT_TIER").show(10)

# ==============================================================================
# SECTION 5: STORED PROCEDURES
# ==============================================================================

# Stored Procedure = A Python function that runs a WORKFLOW (not per-row).
# Can execute SQL, manipulate tables, orchestrate pipelines.
#
# UDF vs Stored Procedure:
#   UDF:   Runs per ROW (like a SQL function: SELECT my_udf(column) FROM table)
#   SPROC: Runs ONCE (like a script: CALL my_procedure())
#
# USE CASES:
#   - ETL pipeline orchestration
#   - Data quality checks
#   - Administrative tasks (cleanup, archival)
#   - ML model training workflows

@sproc(
    name="TPCH_ANALYTICS_DB.DEV.refresh_customer_summary",
    is_permanent=True,
    stage_location="@TPCH_ANALYTICS_DB.DEV.sproc_stage",
    replace=True
)
def refresh_customer_summary(session: Session) -> str:
    """Rebuild the customer summary table."""

    # Step 1: Read source data
    orders = session.table("SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS")
    customers = session.table("SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.CUSTOMER")

    # Step 2: Transform
    from snowflake.snowpark.functions import col, sum, count, avg

    summary = (
        orders
        .join(customers, orders["O_CUSTKEY"] == customers["C_CUSTKEY"])
        .group_by(customers["C_CUSTKEY"], customers["C_NAME"], customers["C_MKTSEGMENT"])
        .agg(
            count("*").alias("TOTAL_ORDERS"),
            sum("O_TOTALPRICE").alias("LIFETIME_REVENUE"),
            avg("O_TOTALPRICE").alias("AVG_ORDER_VALUE")
        )
    )

    # Step 3: Write to table
    summary.write.mode("overwrite").save_as_table(
        "TPCH_ANALYTICS_DB.DEV.CUSTOMER_SUMMARY"
    )

    row_count = session.table("TPCH_ANALYTICS_DB.DEV.CUSTOMER_SUMMARY").count()
    return f"SUCCESS: Refreshed CUSTOMER_SUMMARY with {row_count:,} rows"

# Call it:
# session.call("TPCH_ANALYTICS_DB.DEV.refresh_customer_summary")
# Or from SQL: CALL TPCH_ANALYTICS_DB.DEV.refresh_customer_summary();

# ==============================================================================
# SECTION 6: STORED PROCEDURE WITH PARAMETERS
# ==============================================================================

@sproc(
    name="TPCH_ANALYTICS_DB.DEV.build_monthly_report",
    is_permanent=True,
    stage_location="@TPCH_ANALYTICS_DB.DEV.sproc_stage",
    replace=True
)
def build_monthly_report(session: Session, year: int, month: int) -> str:
    """Build a monthly orders report for a specific year/month."""
    from snowflake.snowpark.functions import col, sum, count, year as yr, month as mn

    orders = session.table("SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS")

    monthly_data = (
        orders
        .filter((yr(col("O_ORDERDATE")) == year) & (mn(col("O_ORDERDATE")) == month))
        .group_by("O_ORDERSTATUS")
        .agg(
            count("*").alias("ORDER_COUNT"),
            sum("O_TOTALPRICE").alias("TOTAL_REVENUE")
        )
    )

    table_name = f"TPCH_ANALYTICS_DB.DEV.MONTHLY_REPORT_{year}_{month:02d}"
    monthly_data.write.mode("overwrite").save_as_table(table_name)

    return f"Created {table_name} with {monthly_data.count()} rows"

# Call with parameters:
# session.call("TPCH_ANALYTICS_DB.DEV.build_monthly_report", 1998, 6)
# SQL: CALL TPCH_ANALYTICS_DB.DEV.build_monthly_report(1998, 6);

# ==============================================================================
# SECTION 7: UDTFs (Table Functions — Return Multiple Rows)
# ==============================================================================

# UDTF = User-Defined Table Function
# Returns MULTIPLE rows per input (like LATERAL FLATTEN in SQL)

from snowflake.snowpark.functions import udtf
from snowflake.snowpark.types import StructType, StructField

# Example: Split a comma-separated string into rows
class SplitString:
    def process(self, input_str: str, delimiter: str):
        if input_str:
            for part in input_str.split(delimiter):
                yield (part.strip(),)

split_udtf = udtf(
    SplitString,
    output_schema=StructType([StructField("VALUE", StringType())]),
    input_types=[StringType(), StringType()],
    name="split_to_rows",
    replace=True
)

# Usage:
# SELECT * FROM TABLE(split_to_rows('apple,banana,cherry', ','))
# Returns 3 rows: apple, banana, cherry

# ==============================================================================
# SECTION 8: BEST PRACTICES
# ==============================================================================

# 1. PREFER BUILT-IN FUNCTIONS over UDFs (they're faster):
#    ❌ UDF that does upper() → use Snowpark's upper() instead
#    ✅ UDF for complex regex, ML scoring, custom algorithms
#
# 2. USE VECTORIZED UDFs for large datasets (pandas_udf):
#    Regular UDF: processes 1 row at a time
#    Vectorized:  processes thousands of rows at once (batch)
#
# 3. STORED PROCEDURES for workflows, UDFs for row-level logic:
#    SPROC: "Rebuild the summary table every night"
#    UDF:   "Classify each order into a tier"
#
# 4. TEST LOCALLY before registering:
#    result = categorize_price(150000.0)
#    assert result == "BUSINESS"
#
# 5. USE TYPE HINTS for clarity and debugging:
#    def my_func(x: float) -> str:  ← Snowpark uses these!

# ==============================================================================
# SECTION 9: KEY TAKEAWAYS
# ==============================================================================

# 1. UDF = per-row function (like SQL functions). @udf decorator.
# 2. Vectorized UDF = batch processing with pandas. 10-100x faster.
# 3. Stored Procedure = workflow/script. @sproc decorator. Receives session.
# 4. UDTF = returns multiple rows per input (table function).
# 5. is_permanent=True → persists in Snowflake, callable from SQL.
# 6. stage_location needed for permanent UDFs/SPROCs (stores the code).
# 7. Always prefer built-in functions over UDFs for simple operations.
# 8. UDFs can include any Python library available in Snowflake's conda channel.

# ==============================================================================
# NEXT: Module 12 — Snowpark ML and Advanced Patterns
# ==============================================================================
