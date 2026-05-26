# ==============================================================================
# MODULE 2: CONTROL FLOW — Making Decisions and Repeating Actions
# ==============================================================================
# Level: Beginner
# Time: 25 minutes
# Prerequisites: Module 01 completed
# ==============================================================================

# ==============================================================================
# SECTION 1: IF / ELIF / ELSE — Making Decisions
# ==============================================================================

# if = "do this ONLY when condition is True"
# Like WHERE in SQL, but for program logic.

# BASIC IF:
temperature = 35

if temperature > 30:
    print("It's hot!")        # This runs because 35 > 30

# IF/ELSE (two paths):
age = 16

if age >= 18:
    print("Adult")
else:
    print("Minor")            # This runs because 16 < 18

# IF/ELIF/ELSE (multiple paths):
score = 75

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"               # This matches (75 >= 70)
elif score >= 60:
    grade = "D"
else:
    grade = "F"

print(f"Grade: {grade}")      # Grade: C

# CRITICAL RULE: Python uses INDENTATION (4 spaces) to define code blocks!
# No curly braces {} like Java/JavaScript. Indentation IS the structure.
#
#   if condition:        ← colon required
#       code here        ← 4 spaces indent = inside the if
#       more code        ← still inside
#   code here            ← back to normal (outside the if)

# SQL COMPARISON:
#   SQL:    CASE WHEN score >= 90 THEN 'A' WHEN score >= 80 THEN 'B' ELSE 'F' END
#   Python: if/elif/else chain (above)

# ==============================================================================
# SECTION 2: REAL-WORLD IF EXAMPLES
# ==============================================================================

# Data validation (common in ETL):
customer_email = "john@email.com"

if customer_email is None or customer_email == "":
    print("ERROR: Email is missing!")
elif "@" not in customer_email:
    print("ERROR: Invalid email format!")
else:
    print(f"Valid email: {customer_email}")

# Choosing behavior based on data size:
row_count = 5000000

if row_count > 1000000:
    strategy = "incremental"
    warehouse_size = "LARGE"
elif row_count > 100000:
    strategy = "full_refresh"
    warehouse_size = "MEDIUM"
else:
    strategy = "full_refresh"
    warehouse_size = "SMALL"

print(f"Strategy: {strategy}, Warehouse: {warehouse_size}")

# ==============================================================================
# SECTION 3: FOR LOOPS — Repeating Actions
# ==============================================================================

# A for loop repeats code for each item in a collection.
# Like processing each row in a result set.

# Loop through a list:
fruits = ["apple", "banana", "cherry"]

for fruit in fruits:
    print(f"I like {fruit}")
# Output:
#   I like apple
#   I like banana
#   I like cherry

# Loop through numbers (range):
for i in range(5):            # 0, 1, 2, 3, 4 (NOT including 5!)
    print(i)

for i in range(1, 6):         # 1, 2, 3, 4, 5
    print(i)

for i in range(0, 10, 2):     # 0, 2, 4, 6, 8 (step by 2)
    print(i)

# REAL-WORLD: Process multiple tables
tables = ["orders", "customers", "products"]

for table in tables:
    sql = f"SELECT COUNT(*) FROM {table}"
    print(f"Running: {sql}")

# Loop with index (enumerate):
columns = ["order_id", "customer_id", "total"]

for index, col_name in enumerate(columns):
    print(f"Column {index}: {col_name}")
# Output:
#   Column 0: order_id
#   Column 1: customer_id
#   Column 2: total

# ==============================================================================
# SECTION 4: WHILE LOOPS — Repeat Until Condition Changes
# ==============================================================================

# while = keep looping AS LONG AS condition is True

counter = 0
while counter < 5:
    print(f"Count: {counter}")
    counter += 1              # counter = counter + 1 (MUST change, or infinite loop!)
# Output: Count: 0, Count: 1, Count: 2, Count: 3, Count: 4

# REAL-WORLD: Retry logic for API calls
max_retries = 3
attempt = 0
success = False

while attempt < max_retries and not success:
    attempt += 1
    print(f"Attempt {attempt}...")
    # Simulate: success on 3rd try
    if attempt == 3:
        success = True
        print("Success!")

# DANGER: Infinite loop (don't do this!)
# while True:
#     print("This never stops!")
# Use Ctrl+C to stop if you accidentally create one.

# ==============================================================================
# SECTION 5: BREAK AND CONTINUE
# ==============================================================================

# break = EXIT the loop immediately
for i in range(10):
    if i == 5:
        break                 # Stop at 5
    print(i)                  # Prints 0, 1, 2, 3, 4

# continue = SKIP this iteration, go to next
for i in range(10):
    if i % 2 == 0:            # If even number
        continue              # Skip it
    print(i)                  # Prints 1, 3, 5, 7, 9 (odd numbers only)

# REAL-WORLD: Skip invalid records
records = [
    {"id": 1, "name": "Alice", "email": "alice@co.com"},
    {"id": 2, "name": None, "email": "bob@co.com"},
    {"id": 3, "name": "Charlie", "email": None},
    {"id": 4, "name": "Diana", "email": "diana@co.com"},
]

valid_records = []
for record in records:
    if record["name"] is None or record["email"] is None:
        print(f"Skipping invalid record ID: {record['id']}")
        continue
    valid_records.append(record)

print(f"Valid records: {len(valid_records)}")  # 2

# ==============================================================================
# SECTION 6: LIST COMPREHENSIONS — Pythonic Loops (Important!)
# ==============================================================================

# A compact way to create lists. Very common in Python code.
# Pattern: [expression FOR item IN iterable IF condition]

# Traditional loop:
squares = []
for x in range(5):
    squares.append(x ** 2)
print(squares)                # [0, 1, 4, 9, 16]

# Same thing as a list comprehension (one line!):
squares = [x ** 2 for x in range(5)]
print(squares)                # [0, 1, 4, 9, 16]

# With condition (filter):
even_squares = [x ** 2 for x in range(10) if x % 2 == 0]
print(even_squares)           # [0, 4, 16, 36, 64]

# REAL-WORLD: Transform column names
raw_columns = ["Order ID", "Customer Name", "Total Price"]
clean_columns = [col.lower().replace(" ", "_") for col in raw_columns]
print(clean_columns)          # ['order_id', 'customer_name', 'total_price']

# Filter file list:
files = ["data.csv", "report.pdf", "orders.csv", "image.png", "customers.csv"]
csv_files = [f for f in files if f.endswith(".csv")]
print(csv_files)              # ['data.csv', 'orders.csv', 'customers.csv']

# ==============================================================================
# SECTION 7: NESTED LOOPS
# ==============================================================================

# Loop inside a loop (like a cross join in SQL):
databases = ["RAW", "ANALYTICS"]
schemas = ["PUBLIC", "STAGING"]

for db in databases:
    for schema in schemas:
        print(f"{db}.{schema}")
# Output:
#   RAW.PUBLIC
#   RAW.STAGING
#   ANALYTICS.PUBLIC
#   ANALYTICS.STAGING

# ==============================================================================
# SECTION 8: TERNARY EXPRESSION (Inline If)
# ==============================================================================

# One-line if/else for simple cases:
# Pattern: value_if_true IF condition ELSE value_if_false

age = 20
status = "adult" if age >= 18 else "minor"
print(status)                 # adult

# Like SQL's: CASE WHEN age >= 18 THEN 'adult' ELSE 'minor' END

# REAL-WORLD: Default values
warehouse = None
wh_name = warehouse if warehouse is not None else "COMPUTE_WH"
print(wh_name)               # COMPUTE_WH

# ==============================================================================
# SECTION 9: TRY IT YOURSELF
# ==============================================================================

# Exercise 1: Write an if/elif/else that categorizes order_total:
# < 100: "small", 100-999: "medium", >= 1000: "large"
order_total = 450
# YOUR CODE HERE:


# Exercise 2: Loop through this list and print only names starting with 'A':
names = ["Alice", "Bob", "Anna", "Charlie", "Andrew"]
# YOUR CODE HERE:


# Exercise 3: Create a list comprehension that extracts years from these dates:
dates = ["2024-01-15", "2023-06-20", "2022-11-30"]
# Hint: date.split("-")[0] gives the year portion
# Expected: ['2024', '2023', '2022']
# YOUR CODE HERE:


# ==============================================================================
# SECTION 10: KEY TAKEAWAYS
# ==============================================================================

# 1. if/elif/else = decision making (like CASE WHEN in SQL)
# 2. for loop = iterate over a collection (like cursor in SQL)
# 3. while loop = repeat until condition changes
# 4. INDENTATION (4 spaces) defines code blocks — this is NOT optional!
# 5. break = exit loop; continue = skip iteration
# 6. List comprehension: [expr for item in list if condition] — the Pythonic way
# 7. Ternary: value_if_true if condition else value_if_false
# 8. range(start, stop, step) generates number sequences

# ==============================================================================
# NEXT: Module 03 — Functions and Modules
# ==============================================================================
