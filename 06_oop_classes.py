# ==============================================================================
# MODULE 6: OBJECT-ORIENTED PROGRAMMING (Classes)
# ==============================================================================
# Level: Intermediate
# Time: 25 minutes
# Prerequisites: Module 01-05 completed
# ==============================================================================

# ==============================================================================
# SECTION 1: WHAT IS OOP?
# ==============================================================================

# OOP = organizing code into "objects" that bundle DATA + BEHAVIOR together.
#
# Without OOP: Functions scattered everywhere, data passed around separately.
# With OOP:    Objects contain their own data AND the functions to manipulate it.
#
# REAL ANALOGY:
#   A Snowflake Session OBJECT has:
#     Data: connection info, warehouse, role, database
#     Behavior: .sql(), .table(), .create_dataframe()
#
# When you write: session.sql("SELECT 1").collect()
#   session = object
#   .sql()  = method (function belonging to the object)
#   .collect() = another method

# ==============================================================================
# SECTION 2: CLASSES AND OBJECTS
# ==============================================================================

# CLASS = blueprint (like a CREATE TABLE definition)
# OBJECT = instance (like an actual row of data)

class Customer:
    """Represents a customer in our system."""

    def __init__(self, customer_id, name, email):
        """Constructor — runs when you create a new Customer."""
        self.customer_id = customer_id   # self.x = instance variable
        self.name = name
        self.email = email
        self.orders = []                  # Empty list, filled later

    def place_order(self, amount):
        """Add an order to this customer."""
        self.orders.append(amount)
        return f"Order ${amount} placed for {self.name}"

    def total_spent(self):
        """Calculate lifetime revenue."""
        return sum(self.orders)

    def __str__(self):
        """How the object looks when printed."""
        return f"Customer({self.customer_id}, {self.name})"


# CREATE objects (instances):
alice = Customer(101, "Alice Smith", "alice@email.com")
bob = Customer(102, "Bob Jones", "bob@email.com")

# USE objects:
print(alice.name)                   # Alice Smith
print(alice.email)                  # alice@email.com

alice.place_order(150.00)
alice.place_order(220.00)
print(alice.total_spent())          # 370.0
print(alice)                        # Customer(101, Alice Smith)

# KEY CONCEPTS:
#   __init__ = constructor (called automatically when creating an object)
#   self     = refers to THIS specific object (like 'this' in Java)
#   Methods  = functions inside a class (always have self as first param)

# ==============================================================================
# SECTION 3: INHERITANCE — Extending Classes
# ==============================================================================

# A child class INHERITS from a parent class (gets all its data + methods).
# Then ADDS or OVERRIDES behavior.

class DataSource:
    """Base class for any data source."""

    def __init__(self, name, connection_string):
        self.name = name
        self.connection_string = connection_string
        self.is_connected = False

    def connect(self):
        self.is_connected = True
        print(f"Connected to {self.name}")

    def disconnect(self):
        self.is_connected = False
        print(f"Disconnected from {self.name}")

    def read(self, query):
        raise NotImplementedError("Subclasses must implement read()")


class SnowflakeSource(DataSource):
    """Snowflake-specific data source."""

    def __init__(self, name, account, warehouse):
        super().__init__(name, f"snowflake://{account}")  # Call parent __init__
        self.warehouse = warehouse

    def read(self, query):
        """Override parent's read() with Snowflake-specific logic."""
        if not self.is_connected:
            raise ConnectionError("Not connected!")
        print(f"Executing on {self.warehouse}: {query}")
        return [{"result": "data"}]


class PostgresSource(DataSource):
    """Postgres-specific data source."""

    def __init__(self, name, host, port=5432):
        super().__init__(name, f"postgres://{host}:{port}")
        self.port = port

    def read(self, query):
        if not self.is_connected:
            raise ConnectionError("Not connected!")
        print(f"Executing on Postgres: {query}")
        return [{"result": "data"}]


# Usage — same interface, different implementations:
sf = SnowflakeSource("Production", "myorg-myaccount", "COMPUTE_WH")
sf.connect()
sf.read("SELECT * FROM orders LIMIT 10")

pg = PostgresSource("Legacy DB", "localhost")
pg.connect()
pg.read("SELECT * FROM users")

# ==============================================================================
# SECTION 4: PROPERTIES AND ENCAPSULATION
# ==============================================================================

# @property makes a method LOOK like an attribute.
# Used to add validation or computation to data access.

class Pipeline:
    """Represents a data pipeline with status tracking."""

    def __init__(self, name):
        self.name = name
        self._status = "idle"         # _ prefix = "private" (convention)
        self._records_processed = 0

    @property
    def status(self):
        """Read the status."""
        return self._status

    @status.setter
    def status(self, value):
        """Set status with validation."""
        valid = ["idle", "running", "completed", "failed"]
        if value not in valid:
            raise ValueError(f"Invalid status: {value}. Must be one of {valid}")
        self._status = value

    @property
    def records_processed(self):
        return self._records_processed

    def process_batch(self, count):
        self._records_processed += count
        print(f"Processed {count} records (total: {self._records_processed})")


pipeline = Pipeline("daily_orders")
pipeline.status = "running"            # Uses the setter (validates!)
print(pipeline.status)                 # Uses the getter
pipeline.process_batch(1000)
pipeline.process_batch(500)
print(pipeline.records_processed)      # 1500

# pipeline.status = "invalid"          # ❌ ValueError!

# ==============================================================================
# SECTION 5: DUNDER METHODS (Magic Methods)
# ==============================================================================

# Methods with double underscores (__xx__) have special meaning in Python.

class Money:
    def __init__(self, amount, currency="USD"):
        self.amount = amount
        self.currency = currency

    def __str__(self):
        """print() and str() use this."""
        return f"${self.amount:.2f} {self.currency}"

    def __repr__(self):
        """Developer representation (debugging)."""
        return f"Money({self.amount}, '{self.currency}')"

    def __add__(self, other):
        """Enable: money1 + money2."""
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies!")
        return Money(self.amount + other.amount, self.currency)

    def __eq__(self, other):
        """Enable: money1 == money2."""
        return self.amount == other.amount and self.currency == other.currency

    def __lt__(self, other):
        """Enable: money1 < money2 (and sorting!)."""
        return self.amount < other.amount


price = Money(99.99)
tax = Money(8.00)
total = price + tax
print(total)                  # $107.99 USD
print(price < total)          # True

# ==============================================================================
# SECTION 6: DATACLASSES (Modern Python — Less Boilerplate)
# ==============================================================================

from dataclasses import dataclass, field
from typing import List

# @dataclass auto-generates __init__, __repr__, __eq__ for you!

@dataclass
class TableMetadata:
    database: str
    schema: str
    name: str
    row_count: int = 0
    columns: List[str] = field(default_factory=list)

    @property
    def full_name(self):
        return f"{self.database}.{self.schema}.{self.name}"


table = TableMetadata("ANALYTICS", "DEV", "ORDERS", 1500000, ["id", "total"])
print(table)                  # TableMetadata(database='ANALYTICS', schema='DEV', ...)
print(table.full_name)        # ANALYTICS.DEV.ORDERS
print(table.row_count)        # 1500000

# Equality works automatically:
table2 = TableMetadata("ANALYTICS", "DEV", "ORDERS", 1500000, ["id", "total"])
print(table == table2)        # True

# ==============================================================================
# SECTION 7: WHEN TO USE OOP IN DATA ENGINEERING
# ==============================================================================

# USE CLASSES WHEN:
#   ✅ Modeling entities with data + behavior (Pipeline, Connection, Table)
#   ✅ Multiple instances with same structure (10 data sources, each with config)
#   ✅ Inheritance for shared interfaces (DataSource → Snowflake, Postgres)
#   ✅ Encapsulation with validation (@property setters)
#
# USE FUNCTIONS WHEN:
#   ✅ Simple transformations (clean_column_name, validate_email)
#   ✅ Stateless operations (no need to remember anything between calls)
#   ✅ Quick scripts and one-off analysis
#
# In Snowpark, you'll use BOTH:
#   - Session object (OOP) — manages your connection
#   - DataFrame methods (OOP) — chainable transformations
#   - UDFs (functions) — custom logic applied to rows

# ==============================================================================
# SECTION 8: KEY TAKEAWAYS
# ==============================================================================

# 1. Class = blueprint. Object = instance.
# 2. __init__(self) = constructor, called when creating objects
# 3. self = reference to the current object instance
# 4. Inheritance: class Child(Parent) — extends and overrides
# 5. @property = computed attribute with optional validation
# 6. Dunder methods (__str__, __add__, __eq__) = operator overloading
# 7. @dataclass = less boilerplate for data-holding classes
# 8. In data engineering: use classes for connections, pipelines, configs

# ==============================================================================
# NEXT: Module 07 — Python for Data (pandas basics)
# ==============================================================================
