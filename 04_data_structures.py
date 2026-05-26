# ==============================================================================
# MODULE 4: DATA STRUCTURES — Lists, Dicts, Sets, Tuples
# ==============================================================================
# Level: Beginner → Intermediate
# Time: 30 minutes
# Prerequisites: Module 01-03 completed
# ==============================================================================

# ==============================================================================
# SECTION 1: LISTS — Ordered, Mutable Collections
# ==============================================================================

# A list = ordered collection of items. Like a result set from a query.
# Created with square brackets [].

# Create lists:
numbers = [10, 20, 30, 40, 50]
names = ["Alice", "Bob", "Charlie"]
mixed = [1, "hello", 3.14, True, None]   # Can mix types (but avoid this)

# Access by index (0-based):
print(names[0])               # Alice (first)
print(names[-1])              # Charlie (last)
print(names[1:3])             # ['Bob', 'Charlie'] (slice)

# Modify (lists are MUTABLE — they can change):
names[0] = "Alicia"           # Replace first item
names.append("Diana")         # Add to end
names.insert(1, "Brandon")    # Insert at position 1
names.remove("Bob")           # Remove by value
popped = names.pop()          # Remove & return last item
print(names)

# Common operations:
numbers = [3, 1, 4, 1, 5, 9, 2, 6]
print(len(numbers))           # 8
print(sum(numbers))           # 31
print(sorted(numbers))        # [1, 1, 2, 3, 4, 5, 6, 9] (new list)
numbers.sort()                # Sorts IN PLACE (modifies original)
print(5 in numbers)           # True (membership check)
print(numbers.count(1))       # 2 (count occurrences)
print(numbers.index(5))       # Index of first occurrence of 5

# REAL-WORLD: Column list for SQL
columns = ["order_id", "customer_id", "total_price", "order_date"]
select_clause = ", ".join(columns)
print(f"SELECT {select_clause} FROM orders")

# ==============================================================================
# SECTION 2: DICTIONARIES — Key-Value Pairs (Most Important!)
# ==============================================================================

# A dict = key:value pairs. Like a JSON object or a single row.
# Created with curly braces {}.
# THIS IS THE MOST USED DATA STRUCTURE IN PYTHON.

# Create:
customer = {
    "id": 101,
    "name": "Alice Smith",
    "email": "alice@email.com",
    "balance": 5432.10,
    "is_active": True
}

# Access values by key:
print(customer["name"])       # Alice Smith
print(customer["balance"])    # 5432.10

# Safe access (returns None if key doesn't exist):
print(customer.get("phone"))          # None (no error!)
print(customer.get("phone", "N/A"))   # N/A (with default)

# Modify:
customer["balance"] = 6000.00         # Update
customer["phone"] = "555-1234"        # Add new key
del customer["is_active"]             # Delete a key

# Useful methods:
print(customer.keys())        # dict_keys(['id', 'name', 'email', ...])
print(customer.values())      # dict_values([101, 'Alice Smith', ...])
print(customer.items())       # dict_items([('id', 101), ('name', 'Alice'), ...])
print(len(customer))          # Number of keys
print("email" in customer)    # True (check if key exists)

# Loop through a dict:
for key, value in customer.items():
    print(f"{key}: {value}")

# REAL-WORLD: Config dictionary
config = {
    "database": "ANALYTICS",
    "schema": "DEV",
    "warehouse": "COMPUTE_WH",
    "role": "DATA_ENGINEER",
}

# Build connection string:
for key, value in config.items():
    print(f"  {key} = {value}")

# REAL-WORLD: List of dictionaries = table of data!
orders = [
    {"id": 1, "customer": "Alice", "total": 150.00},
    {"id": 2, "customer": "Bob", "total": 89.50},
    {"id": 3, "customer": "Alice", "total": 220.00},
]

# Sum totals for Alice:
alice_total = sum(o["total"] for o in orders if o["customer"] == "Alice")
print(f"Alice's total: ${alice_total}")  # $370.0

# ==============================================================================
# SECTION 3: TUPLES — Immutable Ordered Collections
# ==============================================================================

# A tuple = like a list, but CANNOT be changed after creation.
# Created with parentheses () or just commas.

# Create:
coordinates = (10.5, 20.3)
rgb_color = (255, 128, 0)
single = (42,)                # Single-item tuple needs trailing comma

# Access (same as list):
print(coordinates[0])         # 10.5
print(rgb_color[1])           # 128

# CANNOT modify:
# coordinates[0] = 99         # ❌ TypeError! Tuples are immutable.

# WHY use tuples?
# 1. Signal that data shouldn't change (function returns, constants)
# 2. Can be used as dictionary keys (lists cannot!)
# 3. Slightly faster than lists

# REAL-WORLD: Function returning multiple values
def get_table_stats(table_name):
    row_count = 1500000
    col_count = 12
    size_mb = 256
    return (row_count, col_count, size_mb)   # Returns a tuple

rows, cols, size = get_table_stats("orders")
print(f"Table has {rows:,} rows, {cols} columns, {size}MB")

# Tuple unpacking:
point = (3, 7)
x, y = point                  # x=3, y=7

# ==============================================================================
# SECTION 4: SETS — Unique, Unordered Collections
# ==============================================================================

# A set = collection of UNIQUE items. No duplicates. No order.
# Like SELECT DISTINCT in SQL.

# Create:
unique_ids = {1, 2, 3, 4, 5}
colors = {"red", "green", "blue"}

# Remove duplicates from a list:
raw_data = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
unique_data = set(raw_data)
print(unique_data)            # {1, 2, 3, 4}
print(list(unique_data))      # [1, 2, 3, 4] (convert back to list)

# Set operations (like SQL set operations):
a = {1, 2, 3, 4, 5}
b = {4, 5, 6, 7, 8}

print(a | b)                  # Union: {1,2,3,4,5,6,7,8} (UNION)
print(a & b)                  # Intersection: {4, 5} (INTERSECT)
print(a - b)                  # Difference: {1, 2, 3} (EXCEPT/MINUS)
print(a ^ b)                  # Symmetric diff: {1,2,3,6,7,8}

# REAL-WORLD: Find tables in source but not in staging:
source_tables = {"orders", "customers", "products", "inventory"}
staged_tables = {"orders", "customers"}
missing = source_tables - staged_tables
print(f"Need to create staging for: {missing}")  # {'products', 'inventory'}

# Add/remove:
colors.add("yellow")
colors.discard("red")         # Remove (no error if not found)

# ==============================================================================
# SECTION 5: NESTED DATA STRUCTURES
# ==============================================================================

# Real-world data is often nested (dicts inside lists, lists inside dicts).

# API response (typical):
api_response = {
    "status": "success",
    "data": {
        "customers": [
            {"id": 1, "name": "Alice", "orders": [101, 102, 103]},
            {"id": 2, "name": "Bob", "orders": [201]},
        ],
        "total_count": 2
    }
}

# Navigate nested structure:
print(api_response["status"])                          # success
print(api_response["data"]["total_count"])             # 2
print(api_response["data"]["customers"][0]["name"])    # Alice
print(api_response["data"]["customers"][0]["orders"])  # [101, 102, 103]

# Loop through nested data:
for customer in api_response["data"]["customers"]:
    order_count = len(customer["orders"])
    print(f"{customer['name']}: {order_count} orders")

# ==============================================================================
# SECTION 6: DICTIONARY COMPREHENSIONS
# ==============================================================================

# Like list comprehensions, but creates dicts:
# {key_expr: value_expr for item in iterable if condition}

# Create a mapping:
names = ["Alice", "Bob", "Charlie"]
name_lengths = {name: len(name) for name in names}
print(name_lengths)           # {'Alice': 5, 'Bob': 3, 'Charlie': 7}

# REAL-WORLD: Column type mapping
columns = ["order_id", "total_price", "order_date", "status"]
types = ["INT", "FLOAT", "DATE", "VARCHAR"]
schema = {col: dtype for col, dtype in zip(columns, types)}
print(schema)
# {'order_id': 'INT', 'total_price': 'FLOAT', 'order_date': 'DATE', 'status': 'VARCHAR'}

# Filter a dict:
prices = {"apple": 1.20, "banana": 0.50, "steak": 15.00, "water": 1.00}
expensive = {item: price for item, price in prices.items() if price > 1.00}
print(expensive)              # {'apple': 1.2, 'steak': 15.0}

# ==============================================================================
# SECTION 7: WHEN TO USE WHAT?
# ==============================================================================

# ┌───────────┬────────────────┬────────────────────────────────────────────┐
# │ Structure │ Use When       │ Data Engineering Example                    │
# ├───────────┼────────────────┼────────────────────────────────────────────┤
# │ List []   │ Ordered items, │ Column names, query results, batch of      │
# │           │ may have dups  │ records to process                         │
# ├───────────┼────────────────┼────────────────────────────────────────────┤
# │ Dict {}   │ Key→Value      │ Config, row as object, API response,       │
# │           │ lookup         │ metadata, JSON parsing                     │
# ├───────────┼────────────────┼────────────────────────────────────────────┤
# │ Tuple ()  │ Fixed data,    │ Function returns, DB credentials,          │
# │           │ immutable      │ coordinate pairs, composite keys           │
# ├───────────┼────────────────┼────────────────────────────────────────────┤
# │ Set {}    │ Unique items,  │ Deduplication, finding differences,        │
# │           │ set operations │ membership testing (fast!)                  │
# └───────────┴────────────────┴────────────────────────────────────────────┘

# ==============================================================================
# SECTION 8: TRY IT YOURSELF
# ==============================================================================

# Exercise 1: Given this list of orders, find the order with highest total:
orders = [
    {"id": 1, "total": 150},
    {"id": 2, "total": 320},
    {"id": 3, "total": 89},
    {"id": 4, "total": 445},
]
# Hint: Use max() with key=lambda



# Exercise 2: Create a dict that counts how many times each status appears:
statuses = ["active", "inactive", "active", "active", "inactive", "pending"]
# Expected: {"active": 3, "inactive": 2, "pending": 1}



# Exercise 3: Find columns that are in table_a but NOT in table_b:
table_a_cols = ["id", "name", "email", "phone", "created_at"]
table_b_cols = ["id", "name", "email", "updated_at"]
# Expected: columns only in table_a



# ==============================================================================
# SECTION 9: KEY TAKEAWAYS
# ==============================================================================

# 1. Lists [] = ordered, mutable, allows duplicates. Most common for sequences.
# 2. Dicts {} = key:value pairs. Most common overall. Used for config, records.
# 3. Tuples () = ordered, immutable. For fixed data and function returns.
# 4. Sets {} = unique, unordered. For deduplication and set math.
# 5. List of dicts = how tables/datasets are represented in Python
# 6. .get(key, default) for safe dict access (no KeyError)
# 7. Comprehensions work for lists, dicts, and sets
# 8. Nested structures: navigate with chained [] brackets

# ==============================================================================
# NEXT: Module 05 — File I/O and Error Handling
# ==============================================================================
