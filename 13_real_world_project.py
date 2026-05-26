# ==============================================================================
# MODULE 13: REAL-WORLD PROJECT — Complete ETL Pipeline with Snowpark
# ==============================================================================
# Level: Advanced (Putting It All Together)
# Time: 30 minutes
# Prerequisites: Module 01-12 completed
# ==============================================================================

# ==============================================================================
# PROJECT: E-Commerce Analytics Pipeline
# ==============================================================================
#
# BUSINESS REQUIREMENT:
#   Build an automated analytics pipeline that:
#   1. Reads raw order data from TPCH
#   2. Cleans and stages the data
#   3. Builds fact and dimension tables
#   4. Generates daily KPI metrics
#   5. Flags data quality issues
#   6. Is deployable as a stored procedure and schedulable
#
# ARCHITECTURE:
#   Source (TPCH) → Staging → Facts/Dims → KPIs → Quality Checks
#
# This mirrors what you'd build at a real company!

from snowflake.snowpark import Session
from snowflake.snowpark.functions import (
    col, lit, sum, avg, count, min, max, when,
    year, month, quarter, datediff, current_timestamp,
    row_number, rank, lag, round as round_,
    count_distinct, concat
)
from snowflake.snowpark import Window
from snowflake.snowpark.types import IntegerType, StringType, FloatType
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("etl_pipeline")

# session = get_active_session()

# ==============================================================================
# SECTION 1: CONFIGURATION
# ==============================================================================

CONFIG = {
    "source_database": "SNOWFLAKE_SAMPLE_DATA",
    "source_schema": "TPCH_SF1",
    "target_database": "TPCH_ANALYTICS_DB",
    "target_schema": "DEV",
    "tables": {
        "orders": "ORDERS",
        "customers": "CUSTOMER",
        "line_items": "LINEITEM",
        "nations": "NATION",
        "regions": "REGION",
    }
}

def source_table(name):
    """Get fully qualified source table name."""
    return f"{CONFIG['source_database']}.{CONFIG['source_schema']}.{CONFIG['tables'][name]}"

def target_table(name):
    """Get fully qualified target table name."""
    return f"{CONFIG['target_database']}.{CONFIG['target_schema']}.{name}"

# ==============================================================================
# SECTION 2: STAGING LAYER
# ==============================================================================

def build_staging(session):
    """Build staging views with clean, renamed columns."""
    logger.info("Building staging layer...")

    # Staged Orders
    stg_orders = (
        session.table(source_table("orders"))
        .select(
            col("O_ORDERKEY").alias("ORDER_ID"),
            col("O_CUSTKEY").alias("CUSTOMER_ID"),
            col("O_ORDERSTATUS").alias("ORDER_STATUS"),
            col("O_TOTALPRICE").alias("TOTAL_PRICE"),
            col("O_ORDERDATE").alias("ORDER_DATE"),
            col("O_ORDERPRIORITY").alias("ORDER_PRIORITY"),
        )
    )

    # Staged Customers
    stg_customers = (
        session.table(source_table("customers"))
        .select(
            col("C_CUSTKEY").alias("CUSTOMER_ID"),
            col("C_NAME").alias("CUSTOMER_NAME"),
            col("C_NATIONKEY").alias("NATION_KEY"),
            col("C_ACCTBAL").alias("ACCOUNT_BALANCE"),
            col("C_MKTSEGMENT").alias("MARKET_SEGMENT"),
        )
    )

    # Staged Line Items
    stg_line_items = (
        session.table(source_table("line_items"))
        .select(
            col("L_ORDERKEY").alias("ORDER_ID"),
            col("L_LINENUMBER").alias("LINE_NUMBER"),
            col("L_QUANTITY").alias("QUANTITY"),
            col("L_EXTENDEDPRICE").alias("EXTENDED_PRICE"),
            col("L_DISCOUNT").alias("DISCOUNT_PCT"),
            col("L_TAX").alias("TAX_PCT"),
            col("L_SHIPDATE").alias("SHIP_DATE"),
            col("L_RETURNFLAG").alias("RETURN_FLAG"),
            (col("L_EXTENDEDPRICE") * (lit(1) - col("L_DISCOUNT"))).alias("NET_PRICE"),
        )
    )

    # Staged Nations + Regions (joined)
    stg_geo = (
        session.table(source_table("nations"))
        .join(
            session.table(source_table("regions")),
            col("N_REGIONKEY") == col("R_REGIONKEY")
        )
        .select(
            col("N_NATIONKEY").alias("NATION_KEY"),
            col("N_NAME").alias("NATION_NAME"),
            col("R_NAME").alias("REGION_NAME"),
        )
    )

    logger.info("Staging layer built successfully")
    return stg_orders, stg_customers, stg_line_items, stg_geo

# ==============================================================================
# SECTION 3: FACT TABLE — Order Summary
# ==============================================================================

def build_fact_orders(session, stg_orders, stg_line_items):
    """Build fact table: one row per order with aggregated metrics."""
    logger.info("Building fact_orders...")

    fact_orders = (
        stg_orders
        .join(stg_line_items, on="ORDER_ID")
        .group_by(
            stg_orders["ORDER_ID"],
            stg_orders["CUSTOMER_ID"],
            stg_orders["ORDER_DATE"],
            stg_orders["ORDER_STATUS"],
            stg_orders["ORDER_PRIORITY"]
        )
        .agg(
            count("LINE_NUMBER").alias("TOTAL_ITEMS"),
            sum("QUANTITY").alias("TOTAL_QUANTITY"),
            sum("EXTENDED_PRICE").alias("GROSS_REVENUE"),
            sum("NET_PRICE").alias("NET_REVENUE"),
            sum(col("EXTENDED_PRICE") * col("DISCOUNT_PCT")).alias("TOTAL_DISCOUNT"),
        )
        .with_column("ORDER_YEAR", year(col("ORDER_DATE")))
        .with_column("ORDER_QUARTER", quarter(col("ORDER_DATE")))
        .with_column("ORDER_MONTH", month(col("ORDER_DATE")))
    )

    # Save to Snowflake
    fact_orders.write.mode("overwrite").save_as_table(target_table("FACT_ORDERS"))
    row_count = fact_orders.count()
    logger.info(f"fact_orders: {row_count:,} rows written")
    return fact_orders

# ==============================================================================
# SECTION 4: DIMENSION TABLE — Customer 360
# ==============================================================================

def build_dim_customers(session, stg_customers, stg_geo, fact_orders):
    """Build dimension table: customer profile + lifetime metrics."""
    logger.info("Building dim_customers...")

    # Customer lifetime metrics from fact table
    customer_metrics = (
        fact_orders
        .group_by("CUSTOMER_ID")
        .agg(
            count("*").alias("LIFETIME_ORDERS"),
            sum("NET_REVENUE").alias("LIFETIME_REVENUE"),
            avg("NET_REVENUE").alias("AVG_ORDER_VALUE"),
            min("ORDER_DATE").alias("FIRST_ORDER_DATE"),
            max("ORDER_DATE").alias("LAST_ORDER_DATE"),
        )
        .with_column("CUSTOMER_TENURE_DAYS",
            datediff("day", col("FIRST_ORDER_DATE"), col("LAST_ORDER_DATE"))
        )
    )

    # Join customer profile + geography + metrics
    dim_customers = (
        stg_customers
        .join(stg_geo, on="NATION_KEY")
        .join(customer_metrics, on="CUSTOMER_ID", join_type="left")
        .with_column("VALUE_SEGMENT",
            when(col("LIFETIME_REVENUE") > 500000, lit("PLATINUM"))
            .when(col("LIFETIME_REVENUE") > 200000, lit("GOLD"))
            .when(col("LIFETIME_REVENUE") > 50000, lit("SILVER"))
            .otherwise(lit("BRONZE"))
        )
        .select(
            "CUSTOMER_ID", "CUSTOMER_NAME", "MARKET_SEGMENT",
            "NATION_NAME", "REGION_NAME", "ACCOUNT_BALANCE",
            "LIFETIME_ORDERS", "LIFETIME_REVENUE", "AVG_ORDER_VALUE",
            "FIRST_ORDER_DATE", "LAST_ORDER_DATE", "CUSTOMER_TENURE_DAYS",
            "VALUE_SEGMENT"
        )
    )

    dim_customers.write.mode("overwrite").save_as_table(target_table("DIM_CUSTOMERS"))
    row_count = dim_customers.count()
    logger.info(f"dim_customers: {row_count:,} rows written")
    return dim_customers

# ==============================================================================
# SECTION 5: KPI TABLE — Daily Business Metrics
# ==============================================================================

def build_daily_kpis(session, fact_orders):
    """Build daily KPI summary table."""
    logger.info("Building daily_kpis...")

    daily_kpis = (
        fact_orders
        .group_by("ORDER_DATE")
        .agg(
            count("*").alias("ORDERS"),
            count_distinct("CUSTOMER_ID").alias("UNIQUE_CUSTOMERS"),
            sum("NET_REVENUE").alias("REVENUE"),
            avg("NET_REVENUE").alias("AOV"),
            sum("TOTAL_QUANTITY").alias("ITEMS_SOLD"),
        )
        .with_column("PREV_DAY_REVENUE",
            lag(col("REVENUE"), 1).over(Window.order_by("ORDER_DATE"))
        )
        .with_column("REVENUE_CHANGE_PCT",
            when(col("PREV_DAY_REVENUE").is_not_null(),
                round_((col("REVENUE") - col("PREV_DAY_REVENUE")) / col("PREV_DAY_REVENUE") * 100, 2)
            )
        )
        .with_column("RUNNING_REVENUE",
            sum("REVENUE").over(
                Window.order_by("ORDER_DATE")
                .rows_between(Window.UNBOUNDED_PRECEDING, Window.CURRENT_ROW)
            )
        )
        .sort("ORDER_DATE")
    )

    daily_kpis.write.mode("overwrite").save_as_table(target_table("DAILY_KPIS"))
    logger.info(f"daily_kpis: {daily_kpis.count():,} rows written")
    return daily_kpis

# ==============================================================================
# SECTION 6: DATA QUALITY CHECKS
# ==============================================================================

def run_quality_checks(session):
    """Run data quality validations on output tables."""
    logger.info("Running data quality checks...")

    checks_passed = 0
    checks_failed = 0
    results = []

    # Check 1: fact_orders has no null ORDER_IDs
    fact = session.table(target_table("FACT_ORDERS"))
    null_orders = fact.filter(col("ORDER_ID").is_null()).count()
    if null_orders == 0:
        checks_passed += 1
        results.append("PASS: fact_orders.ORDER_ID has no NULLs")
    else:
        checks_failed += 1
        results.append(f"FAIL: fact_orders.ORDER_ID has {null_orders} NULLs")

    # Check 2: fact_orders revenue is positive
    neg_revenue = fact.filter(col("NET_REVENUE") <= 0).count()
    if neg_revenue == 0:
        checks_passed += 1
        results.append("PASS: All NET_REVENUE values are positive")
    else:
        checks_failed += 1
        results.append(f"FAIL: {neg_revenue} orders have non-positive revenue")

    # Check 3: dim_customers has unique CUSTOMER_IDs
    dim = session.table(target_table("DIM_CUSTOMERS"))
    total = dim.count()
    distinct = dim.select("CUSTOMER_ID").distinct().count()
    if total == distinct:
        checks_passed += 1
        results.append("PASS: dim_customers.CUSTOMER_ID is unique")
    else:
        checks_failed += 1
        results.append(f"FAIL: {total - distinct} duplicate customer IDs")

    # Check 4: Row count sanity
    if total > 0 and fact.count() > 0:
        checks_passed += 1
        results.append(f"PASS: Tables have data (fact={fact.count():,}, dim={total:,})")
    else:
        checks_failed += 1
        results.append("FAIL: One or more tables are empty!")

    logger.info(f"Quality checks: {checks_passed} passed, {checks_failed} failed")
    return results

# ==============================================================================
# SECTION 7: ORCHESTRATOR — The Main Pipeline
# ==============================================================================

def run_pipeline(session):
    """Execute the complete ETL pipeline."""
    logger.info("=" * 60)
    logger.info("STARTING ETL PIPELINE")
    logger.info("=" * 60)

    # Step 1: Build staging
    stg_orders, stg_customers, stg_line_items, stg_geo = build_staging(session)

    # Step 2: Build fact table
    fact_orders = build_fact_orders(session, stg_orders, stg_line_items)

    # Step 3: Build dimension table
    dim_customers = build_dim_customers(session, stg_customers, stg_geo, fact_orders)

    # Step 4: Build KPIs
    daily_kpis = build_daily_kpis(session, fact_orders)

    # Step 5: Quality checks
    quality_results = run_quality_checks(session)

    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info("=" * 60)

    return {
        "status": "SUCCESS",
        "tables_created": [
            target_table("FACT_ORDERS"),
            target_table("DIM_CUSTOMERS"),
            target_table("DAILY_KPIS"),
        ],
        "quality_checks": quality_results
    }

# ==============================================================================
# SECTION 8: DEPLOY AS STORED PROCEDURE
# ==============================================================================

# To make this schedulable, wrap run_pipeline in a stored procedure:
#
# @sproc(
#     name="TPCH_ANALYTICS_DB.DEV.run_analytics_pipeline",
#     is_permanent=True,
#     stage_location="@TPCH_ANALYTICS_DB.DEV.sproc_stage",
#     replace=True,
#     packages=["snowflake-snowpark-python"]
# )
# def run_analytics_pipeline(session: Session) -> str:
#     result = run_pipeline(session)
#     return str(result)
#
# # Schedule with a Task:
# # CREATE TASK TPCH_ANALYTICS_DB.DEV.daily_analytics
# #   WAREHOUSE = COYOTE02_WH
# #   SCHEDULE = 'USING CRON 0 6 * * * UTC'
# # AS
# #   CALL TPCH_ANALYTICS_DB.DEV.run_analytics_pipeline();
# # ALTER TASK TPCH_ANALYTICS_DB.DEV.daily_analytics RESUME;

# ==============================================================================
# SECTION 9: RUN IT!
# ==============================================================================

# Uncomment to execute:
# result = run_pipeline(session)
# print(result)

# ==============================================================================
# SECTION 10: KEY TAKEAWAYS
# ==============================================================================

# 1. Real pipelines follow: Config → Staging → Facts → Dims → KPIs → Quality
# 2. Functions per layer = testable, reusable, debuggable
# 3. Configuration dict makes pipelines portable (change config, same code)
# 4. Quality checks AFTER building tables catch issues before dashboards see them
# 5. Stored Procedure + Task = scheduled production pipeline
# 6. Logging throughout = observable and debuggable in production
# 7. This pattern scales to any size: just add more staging/fact/dim functions

# ==============================================================================
# NEXT: Module 14 — Interview Preparation
# ==============================================================================
