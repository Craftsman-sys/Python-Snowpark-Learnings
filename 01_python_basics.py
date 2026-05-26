# ==============================================================================
# MODULE 1: PYTHON BASICS — Your First Steps
# ==============================================================================
# Level: Absolute Beginner
# Time: 30 minutes
# Prerequisites: NONE (we start from zero)
# ==============================================================================

# ==============================================================================
# SECTION 1: WHAT IS PYTHON?
# ==============================================================================

# Python is a programming language — you give it instructions, it executes them.
# Think of it like SQL, but more flexible:
#   SQL:    Talks to databases (SELECT, INSERT, JOIN)
#   Python: Talks to everything (databases, files, APIs, ML models, web apps)
#
# WHY learn Python as a Data Engineer?
#   - Snowpark (Snowflake's Python API) replaces complex SQL with Python
#   - Build ETL/ELT pipelines programmatically
#   - Automate tasks (file processing, API calls, scheduling)
#   - Machine Learning (train & deploy models)
#   - Every data engineering job requires Python
#
# KEY DIFFERENCE from SQL:
#   SQL = declarative (you say WHAT you want, database figures out HOW)
#   Python = imperative (you tell the computer exactly HOW to do things, step by step)

# ==============================================================================
# SECTION 2: VARIABLES — Storing Data
# ==============================================================================

# A variable is a name that holds a value (like a labeled box).
# You create one with: name = value

name = "Snowflake"        # Text (called a "string")
age = 10                  # Whole number (called an "integer" or "int")
price = 99.99             # Decimal number (called a "float")
is_active = True          # True/False (called a "boolean" or "bool")

# Print shows output (like SELECT in SQL)
print(name)               # Output: Snowflake
print(age)                # Output: 10
print(price)              # Output: 99.99
print(is_active)          # Output: True

# RULES for variable names:
#   ✅ starts with letter or underscore: my_var, _count, total_price
#   ❌ cannot start with number: 2name (invalid!)
#   ❌ cannot use spaces: my var (invalid! use my_var)
#   ❌ cannot use reserved words: if, for, class, return

# You can change a variable's value anytime:
counter = 1
print(counter)            # Output: 1
counter = 2
print(counter)            # Output: 2

# ==============================================================================
# SECTION 3: DATA TYPES — The 4 Basic Types
# ==============================================================================

# Python has 4 fundamental data types:

# STRING (str) — Text. Always in quotes.
greeting = "Hello, World!"
query = 'SELECT * FROM orders'   # single or double quotes both work
multi_line = """This is
a multi-line
string"""

# INTEGER (int) — Whole numbers. No quotes, no decimals.
row_count = 1500000
year = 2024
negative = -42

# FLOAT (float) — Decimal numbers.
temperature = 98.6
discount = 0.15
pi = 3.14159

# BOOLEAN (bool) — Only True or False. Used for conditions.
has_data = True
is_empty = False

# Check the type of any variable:
print(type(greeting))     # <class 'str'>
print(type(row_count))    # <class 'int'>
print(type(temperature))  # <class 'float'>
print(type(has_data))     # <class 'bool'>

# ==============================================================================
# SECTION 4: OPERATORS — Math and Comparisons
# ==============================================================================

# ARITHMETIC (math)
a = 10
b = 3
print(a + b)    # 13  (addition)
print(a - b)    # 7   (subtraction)
print(a * b)    # 30  (multiplication)
print(a / b)    # 3.333... (division — always returns float)
print(a // b)   # 3   (floor division — rounds down to int)
print(a % b)    # 1   (modulo — remainder after division)
print(a ** b)   # 1000 (power — 10 raised to 3)

# COMPARISON (returns True or False)
x = 5
print(x == 5)   # True  (equals)
print(x != 3)   # True  (not equals)
print(x > 3)    # True  (greater than)
print(x < 3)    # False (less than)
print(x >= 5)   # True  (greater than or equal)
print(x <= 4)   # False (less than or equal)

# LOGICAL (combine conditions)
age = 25
print(age > 18 and age < 65)   # True  (both must be True)
print(age < 18 or age > 65)    # False (at least one must be True)
print(not (age > 30))          # True  (flips True↔False)

# SQL COMPARISON:
#   SQL:    WHERE age > 18 AND age < 65
#   Python: if age > 18 and age < 65:

# ==============================================================================
# SECTION 5: STRINGS — Working with Text
# ==============================================================================

# Strings are the most common data type in data engineering.

name = "Snowflake"

# Length
print(len(name))              # 9

# Access characters (0-indexed!)
print(name[0])                # S (first character)
print(name[-1])               # e (last character)

# Slicing (substring)
print(name[0:4])              # Snow (characters 0,1,2,3)
print(name[4:])               # flake (from position 4 to end)

# Common methods
text = "  Hello, World!  "
print(text.strip())           # "Hello, World!" (remove whitespace)
print(text.lower())           # "  hello, world!  "
print(text.upper())           # "  HELLO, WORLD!  "
print(text.replace("World", "Python"))  # "  Hello, Python!  "
print("Hello" in text)        # True (contains check)

# SPLITTING (very useful for parsing)
csv_row = "John,25,Engineer"
parts = csv_row.split(",")    # ['John', '25', 'Engineer']
print(parts[0])               # John
print(parts[1])               # 25

# F-STRINGS (inserting variables into text — like string interpolation)
name = "Alice"
age = 30
message = f"My name is {name} and I am {age} years old."
print(message)                # My name is Alice and I am 30 years old.

# This is how you'd build SQL dynamically:
table_name = "ORDERS"
limit = 100
sql = f"SELECT * FROM {table_name} LIMIT {limit}"
print(sql)                    # SELECT * FROM ORDERS LIMIT 100

# ==============================================================================
# SECTION 6: TYPE CONVERSION (Casting)
# ==============================================================================

# Convert between types (like CAST in SQL):

# String to Integer
age_str = "25"
age_int = int(age_str)        # 25 (now a number, can do math)
print(age_int + 5)            # 30

# Integer to String
count = 1500
count_str = str(count)        # "1500" (now text, can concatenate)
print("Count: " + count_str)  # Count: 1500

# String to Float
price_str = "99.99"
price = float(price_str)      # 99.99

# Boolean conversion
print(bool(0))                # False (0 is False)
print(bool(1))                # True  (any non-zero is True)
print(bool(""))               # False (empty string is False)
print(bool("hello"))          # True  (non-empty string is True)
print(bool(None))             # False (None is always False)

# ==============================================================================
# SECTION 7: NONE — Python's NULL
# ==============================================================================

# None = Python's equivalent of NULL in SQL
# It means "no value" or "empty"

result = None
print(result)                 # None
print(result is None)         # True  (use 'is' to check for None)
print(result is not None)     # False

# SQL COMPARISON:
#   SQL:    WHERE column IS NULL
#   Python: if value is None:

# ==============================================================================
# SECTION 8: INPUT/OUTPUT
# ==============================================================================

# OUTPUT: print() displays information
print("Hello!")                          # Simple text
print("Name:", name, "Age:", age)        # Multiple values
print(f"Result: {10 + 20}")             # F-string with expression

# In data engineering, you'll mostly print for debugging:
row_count = 1500000
print(f"Loaded {row_count:,} rows")     # Loaded 1,500,000 rows

# ==============================================================================
# SECTION 9: TRY IT YOURSELF
# ==============================================================================

# Exercise 1: Create variables for a customer record
# customer_id = 101, customer_name = "John Smith", balance = 5432.10, is_vip = True
# Print them all using an f-string.



# Exercise 2: Given this CSV line, split it and extract the email:
csv_line = "101,John Smith,john@email.com,2024-01-15"
# Expected output: john@email.com



# Exercise 3: Calculate the total price with tax
# price = 100.00, tax_rate = 0.08
# Print: "Total: $108.00"



# ==============================================================================
# SECTION 10: KEY TAKEAWAYS
# ==============================================================================

# 1. Variables store values: name = "value"
# 2. Four basic types: str, int, float, bool
# 3. None = Python's NULL
# 4. F-strings for string formatting: f"Hello {name}"
# 5. type() to check a variable's type
# 6. int(), str(), float() to convert between types
# 7. .split() to parse strings (CSV parsing!)
# 8. Python is 0-indexed (first element is [0])

# ==============================================================================
# NEXT: Module 02 — Control Flow (if/else, loops)
# ==============================================================================
