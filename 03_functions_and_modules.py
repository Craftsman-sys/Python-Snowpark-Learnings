# ==============================================================================
# MODULE 3: FUNCTIONS AND MODULES — Reusable Code
# ==============================================================================
# Level: Beginner → Intermediate
# Time: 25 minutes
# Prerequisites: Module 01-02 completed
# ==============================================================================

# ==============================================================================
# SECTION 1: WHAT IS A FUNCTION?
# ==============================================================================

# A function = a reusable block of code with a name.
# Like a SQL stored procedure or a dbt macro.
#
# WHY functions?
#   - Write once, use many times (DRY: Don't Repeat Yourself)
#   - Makes code readable (name describes what it does)
#   - Easier to test and debug (test one function at a time)
#
# ANATOMY:
#   def function_name(parameters):
#       """Docstring: describes what the function does"""
#       code here
#       return result

# ==============================================================================
# SECTION 2: DEFINING AND CALLING FUNCTIONS
# ==============================================================================

# BASIC function (no parameters, no return):
def say_hello():
    print("Hello, World!")

say_hello()                   # Output: Hello, World!
say_hello()                   # Can call it as many times as you want

# Function WITH parameters (inputs):
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")                # Hello, Alice!
greet("Bob")                  # Hello, Bob!

# Function WITH return value (output):
def add(a, b):
    return a + b

result = add(3, 5)
print(result)                 # 8
print(add(10, 20))            # 30

# MULTIPLE parameters:
def calculate_tax(price, tax_rate):
    tax_amount = price * tax_rate
    total = price + tax_amount
    return total

final_price = calculate_tax(100, 0.08)
print(f"Total: ${final_price}")  # Total: $108.0

# ==============================================================================
# SECTION 3: DEFAULT PARAMETERS
# ==============================================================================

# Parameters can have default values (used when not provided):

def connect_to_db(database, schema="PUBLIC", warehouse="COMPUTE_WH"):
    print(f"Connecting to {database}.{schema} using {warehouse}")

connect_to_db("ANALYTICS")
# Output: Connecting to ANALYTICS.PUBLIC using COMPUTE_WH

connect_to_db("ANALYTICS", "STAGING")
# Output: Connecting to ANALYTICS.STAGING using COMPUTE_WH

connect_to_db("ANALYTICS", "STAGING", "LARGE_WH")
# Output: Connecting to ANALYTICS.STAGING using LARGE_WH

# Named arguments (keyword arguments) — order doesn't matter:
connect_to_db(database="RAW", warehouse="TINY_WH", schema="EVENTS")
# Output: Connecting to RAW.EVENTS using TINY_WH

# ==============================================================================
# SECTION 4: RETURN VALUES
# ==============================================================================

# return sends a value back to the caller.
# A function WITHOUT return gives back None.

def multiply(a, b):
    return a * b

result = multiply(4, 5)       # result = 20

# MULTIPLE return values (Python specialty!):
def get_min_max(numbers):
    return min(numbers), max(numbers)

minimum, maximum = get_min_max([5, 2, 8, 1, 9])
print(f"Min: {minimum}, Max: {maximum}")  # Min: 1, Max: 9

# Early return (exit function when condition met):
def find_first_null(records):
    for i, record in enumerate(records):
        if record is None:
            return i          # Return immediately when found
    return -1                 # Only reached if no None found

data = ["a", "b", None, "d"]
print(find_first_null(data))  # 2

# ==============================================================================
# SECTION 5: SCOPE — Where Variables Live
# ==============================================================================

# Variables inside a function are LOCAL (only exist inside that function).
# Variables outside are GLOBAL.

global_var = "I'm global"

def my_function():
    local_var = "I'm local"
    print(global_var)         # ✅ Can READ global variables
    print(local_var)          # ✅ Can use local variables

my_function()
# print(local_var)           # ❌ ERROR! local_var doesn't exist here

# BEST PRACTICE: Don't use global variables. Pass data as parameters.

# ==============================================================================
# SECTION 6: LAMBDA FUNCTIONS (Anonymous Functions)
# ==============================================================================

# Lambda = a tiny function in one line (no name needed).
# Pattern: lambda parameters: expression

# Regular function:
def double(x):
    return x * 2

# Same thing as lambda:
double = lambda x: x * 2
print(double(5))              # 10

# WHERE lambdas shine — as arguments to other functions:
numbers = [3, 1, 4, 1, 5, 9, 2]

# Sort by value:
numbers.sort()
print(numbers)                # [1, 1, 2, 3, 4, 5, 9]

# Sort strings by length:
words = ["banana", "pie", "apple", "a"]
words.sort(key=lambda w: len(w))
print(words)                  # ['a', 'pie', 'apple', 'banana']

# REAL-WORLD: Sort records by a field:
customers = [
    {"name": "Alice", "revenue": 5000},
    {"name": "Bob", "revenue": 8000},
    {"name": "Charlie", "revenue": 3000},
]
customers.sort(key=lambda c: c["revenue"], reverse=True)
print(customers[0]["name"])   # Bob (highest revenue)

# ==============================================================================
# SECTION 7: BUILT-IN FUNCTIONS (Know These!)
# ==============================================================================

# Python has many built-in functions you'll use constantly:

numbers = [10, 20, 30, 40, 50]

print(len(numbers))           # 5 (count of items)
print(sum(numbers))           # 150 (total)
print(min(numbers))           # 10
print(max(numbers))           # 50
print(sorted(numbers, reverse=True))  # [50, 40, 30, 20, 10]

# Type conversion:
print(int("42"))              # 42
print(str(42))                # "42"
print(float("3.14"))          # 3.14
print(bool(1))                # True
print(list(range(5)))         # [0, 1, 2, 3, 4]

# Useful utilities:
print(abs(-5))                # 5 (absolute value)
print(round(3.14159, 2))      # 3.14
print(isinstance(42, int))    # True (type check)

# zip — combine two lists (like a JOIN):
names = ["Alice", "Bob", "Charlie"]
scores = [85, 92, 78]
for name, score in zip(names, scores):
    print(f"{name}: {score}")

# map — apply function to every item:
prices = [10.5, 20.3, 30.7]
rounded = list(map(round, prices))
print(rounded)                # [10, 20, 31]

# filter — keep items that match condition:
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)                  # [2, 4, 6, 8, 10]

# ==============================================================================
# SECTION 8: MODULES AND IMPORTS
# ==============================================================================

# A MODULE = a Python file with reusable code.
# A PACKAGE = a folder of modules.
# import = load code from a module so you can use it.

# Import entire module:
import math
print(math.sqrt(16))          # 4.0
print(math.pi)                # 3.14159...

# Import specific function:
from math import sqrt, pi
print(sqrt(25))               # 5.0
print(pi)                     # 3.14159...

# Import with alias (nickname):
import datetime as dt
today = dt.date.today()
print(today)                  # 2024-01-15 (current date)

# COMMON MODULES for Data Engineering:
# import os                   # File/folder operations
# import json                 # JSON parsing
# import csv                  # CSV reading/writing
# import datetime             # Date/time operations
# import logging              # Production logging
# import pandas as pd         # Data manipulation (Module 07)
# from snowflake.snowpark import Session  # Snowpark! (Module 08)

# ==============================================================================
# SECTION 9: DOCSTRINGS — Documenting Functions
# ==============================================================================

# A docstring explains what your function does. Triple quotes.

def calculate_discount(price, discount_pct, min_price=0):
    """
    Calculate discounted price with a minimum floor.

    Args:
        price (float): Original price
        discount_pct (float): Discount percentage (0.0 to 1.0)
        min_price (float): Minimum allowed price (default 0)

    Returns:
        float: The discounted price (never below min_price)
    """
    discounted = price * (1 - discount_pct)
    return max(discounted, min_price)

result = calculate_discount(100, 0.25)
print(result)                 # 75.0

# View docstring:
help(calculate_discount)

# ==============================================================================
# SECTION 10: REAL-WORLD FUNCTION PATTERNS
# ==============================================================================

# Pattern 1: Data validation
def validate_email(email):
    if email is None:
        return False
    return "@" in email and "." in email

# Pattern 2: SQL builder
def build_select(table, columns, where=None, limit=None):
    cols = ", ".join(columns)
    sql = f"SELECT {cols} FROM {table}"
    if where:
        sql += f" WHERE {where}"
    if limit:
        sql += f" LIMIT {limit}"
    return sql

query = build_select("ORDERS", ["order_id", "total"], where="total > 100", limit=10)
print(query)
# SELECT order_id, total FROM ORDERS WHERE total > 100 LIMIT 10

# Pattern 3: Retry with backoff
import time

def retry_operation(func, max_attempts=3, delay=1):
    for attempt in range(1, max_attempts + 1):
        try:
            return func()
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < max_attempts:
                time.sleep(delay)
    raise Exception(f"All {max_attempts} attempts failed")

# ==============================================================================
# SECTION 11: TRY IT YOURSELF
# ==============================================================================

# Exercise 1: Write a function that converts Fahrenheit to Celsius
# Formula: celsius = (fahrenheit - 32) * 5/9
# Test: fahrenheit_to_celsius(212) should return 100.0



# Exercise 2: Write a function that takes a list of column names
# and returns them as a comma-separated string (for SQL SELECT)
# Example: columns_to_sql(["id", "name", "age"]) → "id, name, age"



# Exercise 3: Write a function that categorizes a value into quartiles:
# Q1 (0-25%), Q2 (25-50%), Q3 (50-75%), Q4 (75-100%)
# Given a value and max_value, return "Q1", "Q2", "Q3", or "Q4"



# ==============================================================================
# SECTION 12: KEY TAKEAWAYS
# ==============================================================================

# 1. def name(params): ... return value — defines a function
# 2. Default parameters: def f(x, y=10) — y is optional
# 3. return sends value back; no return = returns None
# 4. lambda = one-line anonymous function
# 5. Modules: import math, from math import sqrt
# 6. Built-ins to know: len, sum, min, max, sorted, zip, map, filter
# 7. Docstrings document functions (triple-quoted strings)
# 8. Functions keep code DRY, testable, and readable

# ==============================================================================
# NEXT: Module 04 — Data Structures (lists, dicts, sets, tuples)
# ==============================================================================
