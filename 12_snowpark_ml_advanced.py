# ==============================================================================
# MODULE 12: SNOWPARK ML AND ADVANCED PATTERNS
# ==============================================================================
# Level: Advanced
# Time: 25 minutes
# Prerequisites: Module 01-11 completed
# ==============================================================================

from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, lit, sum, avg, count, when, year

# session = get_active_session()

# ==============================================================================
# SECTION 1: SNOWPARK ML OVERVIEW
# ==============================================================================

# Snowpark ML = Machine Learning directly in Snowflake.
# Train models, make predictions, all without moving data out.
#
# COMPONENTS:
#   snowflake.ml.modeling    → Preprocessing + model training (sklearn-compatible)
#   snowflake.ml.registry   → Model versioning and deployment
#   snowflake.ml.feature_store → Feature engineering at scale
#
# WHY use Snowpark ML?
#   - Data stays in Snowflake (security, governance)
#   - Scale: train on billions of rows using warehouse compute
#   - Deploy models that run inside Snowflake (no external serving)
#   - Familiar scikit-learn API

# ==============================================================================
# SECTION 2: DATA PREPARATION PATTERN
# ==============================================================================

# Step 1: Build a training dataset using Snowpark DataFrames

# Example: Predict which customers will place large orders

orders = session.table("SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS")
customers = session.table("SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.CUSTOMER")
nations = session.table("SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.NATION")

# Feature engineering:
customer_features = (
    orders
    .join(customers, orders["O_CUSTKEY"] == customers["C_CUSTKEY"])
    .join(nations, customers["C_NATIONKEY"] == nations["N_NATIONKEY"])
    .group_by(
        customers["C_CUSTKEY"],
        customers["C_MKTSEGMENT"],
        nations["N_NAME"],
        customers["C_ACCTBAL"]
    )
    .agg(
        count("*").alias("ORDER_COUNT"),
        sum("O_TOTALPRICE").alias("TOTAL_REVENUE"),
        avg("O_TOTALPRICE").alias("AVG_ORDER_VALUE"),
    )
    .with_column("IS_HIGH_VALUE",
        when(col("TOTAL_REVENUE") > 500000, lit(1)).otherwise(lit(0))
    )
)
customer_features.show(10)

# Save as training table:
# customer_features.write.mode("overwrite").save_as_table(
#     "TPCH_ANALYTICS_DB.DEV.ML_TRAINING_DATA"
# )

# ==============================================================================
# SECTION 3: PREPROCESSING WITH SNOWPARK ML
# ==============================================================================

# from snowflake.ml.modeling.preprocessing import (
#     OneHotEncoder,
#     StandardScaler,
#     OrdinalEncoder,
#     MinMaxScaler
# )
#
# # Encode categorical columns:
# encoder = OneHotEncoder(
#     input_cols=["C_MKTSEGMENT", "N_NAME"],
#     output_cols=["SEGMENT_ENCODED", "NATION_ENCODED"]
# )
# encoded_df = encoder.fit(customer_features).transform(customer_features)
#
# # Scale numeric columns:
# scaler = StandardScaler(
#     input_cols=["ORDER_COUNT", "TOTAL_REVENUE", "AVG_ORDER_VALUE", "C_ACCTBAL"],
#     output_cols=["ORDER_COUNT_SCALED", "REVENUE_SCALED", "AOV_SCALED", "BALANCE_SCALED"]
# )
# scaled_df = scaler.fit(encoded_df).transform(encoded_df)

# ==============================================================================
# SECTION 4: MODEL TRAINING
# ==============================================================================

# from snowflake.ml.modeling.classification import (
#     LogisticRegression,
#     RandomForestClassifier,
#     XGBClassifier
# )
#
# # Split data:
# train_df, test_df = customer_features.random_split([0.8, 0.2], seed=42)
#
# # Train a model:
# model = RandomForestClassifier(
#     input_cols=["ORDER_COUNT", "TOTAL_REVENUE", "AVG_ORDER_VALUE", "C_ACCTBAL"],
#     label_cols=["IS_HIGH_VALUE"],
#     output_cols=["PREDICTION"]
# )
# model.fit(train_df)
#
# # Predict on test data:
# predictions = model.predict(test_df)
# predictions.select("C_CUSTKEY", "IS_HIGH_VALUE", "PREDICTION").show(10)
#
# # Evaluate:
# from snowflake.ml.modeling.metrics import accuracy_score
# accuracy = accuracy_score(
#     df=predictions,
#     y_true_col_names=["IS_HIGH_VALUE"],
#     y_pred_col_names=["PREDICTION"]
# )
# print(f"Accuracy: {accuracy:.4f}")

# ==============================================================================
# SECTION 5: MODEL REGISTRY
# ==============================================================================

# The Model Registry stores, versions, and deploys models.
#
# from snowflake.ml.registry import Registry
#
# # Connect to registry:
# registry = Registry(session=session)
#
# # Log (save) a model:
# model_ref = registry.log_model(
#     model=model,
#     model_name="customer_high_value_classifier",
#     version_name="v1",
#     metrics={"accuracy": accuracy},
#     comment="Random Forest classifier for customer value prediction"
# )
#
# # List models:
# registry.show_models()
#
# # Load and use a model:
# loaded_model = registry.get_model("customer_high_value_classifier").version("v1")
# new_predictions = loaded_model.run(new_data_df, function_name="predict")

# ==============================================================================
# SECTION 6: ADVANCED PATTERNS — DYNAMIC PIPELINES
# ==============================================================================

# Pattern: Process multiple tables dynamically

def process_tables(session, table_names, output_schema):
    """Process a list of tables and create summary views."""
    results = []
    for table_name in table_names:
        df = session.table(table_name)
        row_count = df.count()
        col_count = len(df.columns)
        results.append({
            "table": table_name,
            "rows": row_count,
            "columns": col_count
        })
        print(f"Processed {table_name}: {row_count:,} rows, {col_count} cols")
    return results

# Usage:
# tables = ["SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS",
#           "SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.CUSTOMER",
#           "SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.LINEITEM"]
# stats = process_tables(session, tables, "DEV")

# ==============================================================================
# SECTION 7: ADVANCED PATTERN — DATA QUALITY FRAMEWORK
# ==============================================================================

def run_data_quality_checks(session, table_name, checks):
    """
    Run data quality checks on a table.

    Args:
        checks: list of dicts with keys: column, check_type, threshold
    """
    df = session.table(table_name)
    total_rows = df.count()
    results = []

    for check in checks:
        column = check["column"]
        check_type = check["check_type"]

        if check_type == "not_null":
            null_count = df.filter(col(column).is_null()).count()
            passed = null_count == 0
            results.append({
                "check": f"{column} NOT NULL",
                "passed": passed,
                "details": f"{null_count} nulls found"
            })

        elif check_type == "unique":
            distinct_count = df.select(column).distinct().count()
            passed = distinct_count == total_rows
            results.append({
                "check": f"{column} UNIQUE",
                "passed": passed,
                "details": f"{distinct_count} distinct vs {total_rows} total"
            })

        elif check_type == "positive":
            negative_count = df.filter(col(column) <= 0).count()
            passed = negative_count == 0
            results.append({
                "check": f"{column} > 0",
                "passed": passed,
                "details": f"{negative_count} non-positive values"
            })

    return results

# Usage:
# checks = [
#     {"column": "O_ORDERKEY", "check_type": "not_null"},
#     {"column": "O_ORDERKEY", "check_type": "unique"},
#     {"column": "O_TOTALPRICE", "check_type": "positive"},
# ]
# results = run_data_quality_checks(session, "SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS", checks)
# for r in results:
#     status = "✓" if r["passed"] else "✗"
#     print(f"  {status} {r['check']}: {r['details']}")

# ==============================================================================
# SECTION 8: ADVANCED PATTERN — INCREMENTAL PROCESSING
# ==============================================================================

def incremental_load(session, source_table, target_table, timestamp_col):
    """
    Load only new rows from source into target (incremental pattern).
    Like dbt incremental materialization, but in Python.
    """
    source_df = session.table(source_table)

    try:
        target_df = session.table(target_table)
        max_ts = target_df.agg(max(col(timestamp_col)).alias("MAX_TS")).collect()[0]["MAX_TS"]
        new_rows = source_df.filter(col(timestamp_col) > lit(max_ts))
        new_count = new_rows.count()

        if new_count > 0:
            new_rows.write.mode("append").save_as_table(target_table)
            return f"Appended {new_count:,} new rows (after {max_ts})"
        else:
            return "No new rows to process"

    except Exception:
        source_df.write.mode("overwrite").save_as_table(target_table)
        total = source_df.count()
        return f"Initial load: {total:,} rows"

# Usage:
# result = incremental_load(
#     session,
#     "RAW.EVENTS.PAGE_VIEWS",
#     "ANALYTICS.DEV.PAGE_VIEWS_INCREMENTAL",
#     "EVENT_TIMESTAMP"
# )

# ==============================================================================
# SECTION 9: SNOWPARK WITH TASKS (Scheduling)
# ==============================================================================

# Combine Stored Procedures with Snowflake Tasks for scheduled pipelines:
#
# -- Create the stored procedure (Python)
# -- Then schedule it with SQL:
#
# CREATE TASK TPCH_ANALYTICS_DB.DEV.daily_customer_refresh
#   WAREHOUSE = COMPUTE_WH
#   SCHEDULE = 'USING CRON 0 6 * * * UTC'
# AS
#   CALL TPCH_ANALYTICS_DB.DEV.refresh_customer_summary();
#
# ALTER TASK TPCH_ANALYTICS_DB.DEV.daily_customer_refresh RESUME;
#
# This is the Snowpark equivalent of a scheduled dbt job!

# ==============================================================================
# SECTION 10: KEY TAKEAWAYS
# ==============================================================================

# 1. Snowpark ML: sklearn-compatible API, runs entirely in Snowflake
# 2. Preprocessing (OneHotEncoder, StandardScaler) works on Snowpark DataFrames
# 3. Model Registry: version, store, deploy, and serve models
# 4. Dynamic pipelines: loop over tables, parametric processing
# 5. Data quality frameworks: build reusable check functions
# 6. Incremental patterns: max(timestamp) watermark, append new rows
# 7. Schedule with Tasks: SPROC + CREATE TASK = automated pipeline
# 8. Everything stays in Snowflake (security + scale)

# ==============================================================================
# NEXT: Module 13 — Real-World ETL Project
# ==============================================================================
