# ==============================================================================
# MODULE 7: PYTHON FOR DATA — Pandas Basics
# ==============================================================================
# Level: Intermediate
# Time: 25 minutes
# Prerequisites: Module 01-06 completed
# WHY THIS MODULE: Pandas is the bridge between Python and Snowpark DataFrames.
#                  Snowpark's API is VERY similar to pandas.
# ==============================================================================

# ==============================================================================
# SECTION 1: WHAT IS PANDAS?
# ==============================================================================

# pandas = Python's most popular library for tabular data manipulation.
# Think of it as "SQL inside Python" — SELECT, WHERE, GROUP BY, JOIN.
#
# WHY learn pandas before Snowpark?
#   - Snowpark DataFrames are modeled after pandas (similar methods!)
#   - pandas runs locally (good for small data, prototyping)
#   - Snowpark runs in Snowflake (good for big data, production)
#   - Knowing pandas makes Snowpark 10x easier to learn

import pandas as pd    # Standard alias

# ==============================================================================
# SECTION 2: SERIES AND DATAFRAMES
# ==============================================================================

# SERIES = single column (1D)
ages = pd.Series([25, 30, 35, 40], name="age")
print(ages)

# DATAFRAME = table (2D) — rows and columns
# Like a SQL table or Snowflake result set.

# Create from dictionary:
data = {
    "customer_id": [1, 2, 3, 4, 5],
    "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "city": ["NYC", "LA", "NYC", "Chicago", "LA"],
    "revenue": [5000, 3000, 7500, 2000, 4500],
    "orders": [12, 8, 20, 5, 15],
}
df = pd.DataFrame(data)
print(df)
#    customer_id     name     city  revenue  orders
# 0            1    Alice      NYC     5000      12
# 1            2      Bob       LA     3000       8
# 2            3  Charlie      NYC     7500      20
# 3            4    Diana  Chicago     2000       5
# 4            5      Eve       LA     4500      15

# ==============================================================================
# SECTION 3: EXPLORING DATA (Like DESC TABLE + SELECT)
# ==============================================================================

print(df.shape)               # (5, 5) — 5 rows, 5 columns
print(df.columns.tolist())    # ['customer_id', 'name', 'city', 'revenue', 'orders']
print(df.dtypes)              # Data types per column
print(df.head(3))             # First 3 rows (like LIMIT 3)
print(df.tail(2))             # Last 2 rows
print(df.describe())          # Statistics (count, mean, min, max, etc.)
print(df.info())              # Column types and null counts

# ==============================================================================
# SECTION 4: SELECTING COLUMNS (Like SELECT col1, col2)
# ==============================================================================

# Single column (returns Series):
print(df["name"])

# Multiple columns (returns DataFrame):
print(df[["name", "revenue"]])

# SQL equivalent: SELECT name, revenue FROM customers

# ==============================================================================
# SECTION 5: FILTERING ROWS (Like WHERE)
# ==============================================================================

# Single condition:
high_revenue = df[df["revenue"] > 4000]
print(high_revenue)
# SQL: SELECT * FROM customers WHERE revenue > 4000

# Multiple conditions (use & for AND, | for OR):
nyc_high = df[(df["city"] == "NYC") & (df["revenue"] > 5000)]
print(nyc_high)
# SQL: SELECT * FROM customers WHERE city = 'NYC' AND revenue > 5000

la_or_chicago = df[df["city"].isin(["LA", "Chicago"])]
print(la_or_chicago)
# SQL: SELECT * FROM customers WHERE city IN ('LA', 'Chicago')

# NOT null:
# df[df["column"].notna()]
# SQL: SELECT * FROM customers WHERE column IS NOT NULL

# ==============================================================================
# SECTION 6: ADDING/MODIFYING COLUMNS (Like SELECT col, expression AS new_col)
# ==============================================================================

# New column from calculation:
df["avg_order_value"] = df["revenue"] / df["orders"]
# SQL: SELECT *, revenue / orders AS avg_order_value FROM customers

# Conditional column (like CASE WHEN):
df["tier"] = df["revenue"].apply(
    lambda x: "Gold" if x >= 5000 else "Silver" if x >= 3000 else "Bronze"
)
# SQL: CASE WHEN revenue >= 5000 THEN 'Gold' WHEN >= 3000 THEN 'Silver' ELSE 'Bronze'

print(df[["name", "revenue", "tier"]])

# ==============================================================================
# SECTION 7: SORTING (Like ORDER BY)
# ==============================================================================

# Sort by revenue descending:
sorted_df = df.sort_values("revenue", ascending=False)
print(sorted_df[["name", "revenue"]])
# SQL: SELECT * FROM customers ORDER BY revenue DESC

# Sort by multiple columns:
sorted_df = df.sort_values(["city", "revenue"], ascending=[True, False])

# ==============================================================================
# SECTION 8: GROUPING AND AGGREGATION (Like GROUP BY)
# ==============================================================================

# Group by city, calculate totals:
city_stats = df.groupby("city").agg(
    total_revenue=("revenue", "sum"),
    avg_revenue=("revenue", "mean"),
    customer_count=("customer_id", "count"),
).reset_index()
print(city_stats)
# SQL: SELECT city, SUM(revenue), AVG(revenue), COUNT(*) FROM customers GROUP BY city

# Single aggregation:
print(df.groupby("city")["revenue"].sum())

# Multiple aggregations on same column:
print(df.groupby("city")["revenue"].agg(["sum", "mean", "max"]))

# ==============================================================================
# SECTION 9: JOINING (Like SQL JOIN)
# ==============================================================================

# Create a second DataFrame:
orders_df = pd.DataFrame({
    "order_id": [101, 102, 103, 104],
    "customer_id": [1, 2, 1, 3],
    "amount": [500, 300, 200, 800],
})

# INNER JOIN:
merged = df.merge(orders_df, on="customer_id", how="inner")
print(merged[["name", "order_id", "amount"]])
# SQL: SELECT * FROM customers c JOIN orders o ON c.customer_id = o.customer_id

# LEFT JOIN:
merged_left = df.merge(orders_df, on="customer_id", how="left")
# SQL: LEFT JOIN

# Join types: 'inner', 'left', 'right', 'outer' (same as SQL!)

# ==============================================================================
# SECTION 10: OTHER COMMON OPERATIONS
# ==============================================================================

# RENAME columns:
renamed = df.rename(columns={"revenue": "total_revenue", "orders": "order_count"})

# DROP columns:
dropped = df.drop(columns=["avg_order_value", "tier"])

# DROP DUPLICATES:
unique_cities = df.drop_duplicates(subset=["city"])
# SQL: SELECT DISTINCT city FROM customers

# FILL NULLS:
# df["column"].fillna(0)        # Replace NULL with 0
# df["column"].fillna("Unknown") # Replace NULL with text

# VALUE COUNTS (frequency distribution):
print(df["city"].value_counts())
# NYC        2
# LA         2
# Chicago    1

# APPLY (custom function to every row):
df["name_upper"] = df["name"].apply(lambda x: x.upper())

# ==============================================================================
# SECTION 11: PANDAS → SNOWPARK TRANSLATION TABLE
# ==============================================================================

# ┌──────────────────────────┬─────────────────────────────────────────┐
# │ Pandas                   │ Snowpark Equivalent                     │
# ├──────────────────────────┼─────────────────────────────────────────┤
# │ pd.DataFrame(data)       │ session.create_dataframe(data)          │
# │ df["col"]                │ df.col or df["COL"]                     │
# │ df[df["col"] > 5]        │ df.filter(col("COL") > 5)              │
# │ df.sort_values("col")    │ df.sort(col("COL"))                     │
# │ df.groupby("col").sum()  │ df.group_by("COL").agg(sum("COL"))     │
# │ df.merge(df2, on="col")  │ df.join(df2, on="COL")                 │
# │ df.head(5)               │ df.limit(5).collect()                   │
# │ df.rename(columns={})    │ df.with_column_renamed()                │
# │ df.drop(columns=[])      │ df.drop()                               │
# │ df.shape[0]              │ df.count()                              │
# │ df.to_csv("file.csv")   │ df.write.csv("@stage/path")             │
# └──────────────────────────┴─────────────────────────────────────────┘
#
# KEY DIFFERENCE:
#   Pandas executes IMMEDIATELY (eager evaluation)
#   Snowpark builds a PLAN and executes when you call .collect() (lazy evaluation)
#   This is like SQL: the query is compiled first, then executed.

# ==============================================================================
# SECTION 12: KEY TAKEAWAYS
# ==============================================================================

# 1. DataFrame = table (rows + columns). Series = single column.
# 2. df[condition] filters rows (like WHERE)
# 3. df.groupby().agg() for GROUP BY operations
# 4. df.merge() for JOINs (inner, left, right, outer)
# 5. df.sort_values() for ORDER BY
# 6. .apply(lambda) for row-wise custom logic (like CASE WHEN)
# 7. Method chaining: df.filter().sort().groupby() — like SQL subqueries
# 8. Pandas = local/small data. Snowpark = same API but runs on Snowflake!

# ==============================================================================
# NEXT: Module 08 — Introduction to Snowpark!
# ==============================================================================
