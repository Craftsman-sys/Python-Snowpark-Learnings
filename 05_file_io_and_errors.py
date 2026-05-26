# ==============================================================================
# MODULE 5: FILE I/O AND ERROR HANDLING
# ==============================================================================
# Level: Intermediate
# Time: 20 minutes
# Prerequisites: Module 01-04 completed
# ==============================================================================

# ==============================================================================
# SECTION 1: READING FILES
# ==============================================================================

# Python reads/writes files using the open() function + context manager (with).
# Pattern: with open(filepath, mode) as variable:

# MODES:
#   'r'  = read (default)
#   'w'  = write (overwrites!)
#   'a'  = append (adds to end)
#   'rb' = read binary (for images, parquet, etc.)

# Read entire file:
# with open("data.txt", "r") as f:
#     content = f.read()        # Entire file as one string
#     print(content)

# Read line by line (memory efficient for large files):
# with open("data.csv", "r") as f:
#     for line in f:
#         print(line.strip())   # .strip() removes trailing newline

# Read all lines into a list:
# with open("data.txt", "r") as f:
#     lines = f.readlines()     # ['line1\n', 'line2\n', ...]

# WHY 'with'? It automatically closes the file when done.
# Without 'with', you'd need: f = open(...) ... f.close()

# ==============================================================================
# SECTION 2: WRITING FILES
# ==============================================================================

# Write (creates new or OVERWRITES existing):
# with open("output.txt", "w") as f:
#     f.write("Line 1\n")
#     f.write("Line 2\n")

# Append (adds to end of existing file):
# with open("log.txt", "a") as f:
#     f.write("New log entry\n")

# Write multiple lines at once:
# lines = ["Alice,100\n", "Bob,200\n", "Charlie,300\n"]
# with open("data.csv", "w") as f:
#     f.writelines(lines)

# ==============================================================================
# SECTION 3: CSV FILES (Common in Data Engineering)
# ==============================================================================

import csv

# Reading CSV:
# with open("orders.csv", "r") as f:
#     reader = csv.DictReader(f)    # Each row becomes a dict!
#     for row in reader:
#         print(row["order_id"], row["total"])

# Writing CSV:
# orders = [
#     {"id": 1, "customer": "Alice", "total": 150},
#     {"id": 2, "customer": "Bob", "total": 89},
# ]
# with open("output.csv", "w", newline="") as f:
#     writer = csv.DictWriter(f, fieldnames=["id", "customer", "total"])
#     writer.writeheader()
#     writer.writerows(orders)

# ==============================================================================
# SECTION 4: JSON FILES (APIs and Config)
# ==============================================================================

import json

# JSON = JavaScript Object Notation. Looks just like Python dicts!
# Used for: API responses, config files, Snowflake metadata.

# Parse JSON string:
json_string = '{"name": "Alice", "age": 30, "city": "NYC"}'
data = json.loads(json_string)    # String → Python dict
print(data["name"])               # Alice
print(type(data))                 # <class 'dict'>

# Convert Python dict to JSON string:
config = {"database": "ANALYTICS", "schema": "DEV", "threads": 4}
json_output = json.dumps(config, indent=2)  # Pretty-printed
print(json_output)

# Read JSON file:
# with open("config.json", "r") as f:
#     config = json.load(f)        # File → Python dict

# Write JSON file:
# with open("config.json", "w") as f:
#     json.dump(config, f, indent=2)  # Python dict → File

# ==============================================================================
# SECTION 5: ERROR HANDLING — try/except
# ==============================================================================

# Errors (exceptions) crash your program. try/except catches them.
# Like TRY...CATCH in other languages.

# WITHOUT error handling:
# result = 10 / 0              # ❌ ZeroDivisionError — program crashes!

# WITH error handling:
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")
    result = 0

print(f"Result: {result}")    # Result: 0 (program continues!)

# MULTIPLE exception types:
def safe_convert(value):
    try:
        return int(value)
    except ValueError:
        print(f"Cannot convert '{value}' to int")
        return None
    except TypeError:
        print(f"Invalid type: {type(value)}")
        return None

print(safe_convert("42"))     # 42
print(safe_convert("hello"))  # Cannot convert 'hello' to int → None
print(safe_convert(None))     # Invalid type → None

# FULL PATTERN: try / except / else / finally
def read_config(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return {}
    except json.JSONDecodeError:
        print(f"Invalid JSON in: {filepath}")
        return {}
    else:
        print("Config loaded successfully!")  # Runs only if NO exception
    finally:
        print("Cleanup complete")             # ALWAYS runs (success or failure)

# ==============================================================================
# SECTION 6: COMMON EXCEPTIONS TO KNOW
# ==============================================================================

# ┌─────────────────────────┬────────────────────────────────────────────────┐
# │ Exception               │ When it happens                                │
# ├─────────────────────────┼────────────────────────────────────────────────┤
# │ ValueError              │ Wrong value: int("hello")                      │
# │ TypeError               │ Wrong type: "hello" + 5                        │
# │ KeyError                │ Dict key not found: d["missing"]               │
# │ IndexError              │ List index out of range: [1,2,3][5]            │
# │ FileNotFoundError       │ File doesn't exist                             │
# │ ZeroDivisionError       │ Division by zero                               │
# │ AttributeError          │ Method doesn't exist: 5.upper()                │
# │ ImportError              │ Module not installed                           │
# │ ConnectionError         │ Network/database connection failed             │
# └─────────────────────────┴────────────────────────────────────────────────┘

# ==============================================================================
# SECTION 7: RAISING EXCEPTIONS (Your Own Errors)
# ==============================================================================

# raise = throw your own error when something is wrong.

def validate_table_name(name):
    if not name:
        raise ValueError("Table name cannot be empty!")
    if " " in name:
        raise ValueError(f"Table name cannot contain spaces: '{name}'")
    if not name[0].isalpha():
        raise ValueError(f"Table name must start with a letter: '{name}'")
    return name.upper()

try:
    result = validate_table_name("my table")
except ValueError as e:
    print(f"Validation error: {e}")

# ==============================================================================
# SECTION 8: LOGGING (Production-Ready Output)
# ==============================================================================

import logging

# Configure logging (do this once at the start of your script):
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Use instead of print() in production code:
logger.debug("Detailed info for debugging")      # Hidden unless level=DEBUG
logger.info("Processing started")                 # Normal progress
logger.warning("Missing data in column X")        # Something concerning
logger.error("Failed to connect to database")     # Something failed
logger.critical("System is down!")                 # Everything is broken

# WHY logging over print?
#   - Levels (debug/info/warning/error) let you filter output
#   - Timestamps included automatically
#   - Can write to files, not just console
#   - Can be turned off in production without removing code

# ==============================================================================
# SECTION 9: REAL-WORLD PATTERN — ETL Error Handling
# ==============================================================================

def process_data_file(filepath):
    """Process a data file with proper error handling."""
    logger.info(f"Starting to process: {filepath}")

    try:
        # Step 1: Read the file
        with open(filepath, "r") as f:
            lines = f.readlines()
        logger.info(f"Read {len(lines)} lines")

    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        return {"status": "error", "message": "File not found"}
    except PermissionError:
        logger.error(f"Permission denied: {filepath}")
        return {"status": "error", "message": "Permission denied"}

    # Step 2: Process records
    valid_records = []
    error_count = 0

    for i, line in enumerate(lines):
        try:
            parts = line.strip().split(",")
            if len(parts) < 3:
                raise ValueError(f"Expected 3+ columns, got {len(parts)}")
            valid_records.append({
                "id": int(parts[0]),
                "name": parts[1],
                "amount": float(parts[2])
            })
        except (ValueError, IndexError) as e:
            error_count += 1
            logger.warning(f"Skipping line {i+1}: {e}")

    logger.info(f"Processed: {len(valid_records)} valid, {error_count} errors")
    return {"status": "success", "records": valid_records, "errors": error_count}

# ==============================================================================
# SECTION 10: KEY TAKEAWAYS
# ==============================================================================

# 1. with open(path, mode) as f: — always use 'with' for files
# 2. CSV: csv.DictReader reads rows as dicts (most useful)
# 3. JSON: json.loads (string→dict), json.dumps (dict→string)
# 4. try/except catches errors and keeps program running
# 5. except SpecificError — always catch specific exceptions
# 6. finally — runs regardless of success/failure (cleanup)
# 7. raise ValueError("message") — throw your own errors
# 8. Use logging module instead of print() in production

# ==============================================================================
# NEXT: Module 06 — Object-Oriented Programming (classes)
# ==============================================================================
