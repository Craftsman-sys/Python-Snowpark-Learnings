# Python + Snowpark: From Zero to Industry-Ready

A complete, structured learning course that takes you from zero Python knowledge to building production-ready Snowpark pipelines on Snowflake.

## 📋 Prerequisites

- No programming experience required (we start from absolute scratch)
- A Snowflake account for Snowpark modules (free trial works)
- For Python-only modules (01-07): any Python environment (or Snowflake Notebook)

## 🗂️ Repository Structure

```
├── 01_python_basics.py             # Variables, types, operators, strings
├── 02_control_flow.py              # if/else, for/while loops, comprehensions
├── 03_functions_and_modules.py     # Functions, lambdas, imports, built-ins
├── 04_data_structures.py           # Lists, dicts, sets, tuples, nesting
├── 05_file_io_and_errors.py        # File reading, JSON, try/except, logging
├── 06_oop_classes.py               # Classes, inheritance, dataclasses
├── 07_pandas_basics.py             # DataFrames, filter, group, join (bridge to Snowpark)
├── 08_intro_to_snowpark.py         # Session, lazy evaluation, basic ops
├── 09_snowpark_dataframes.py       # Hands-on: select, filter, join, aggregate
├── 10_window_functions.py          # rank, lag/lead, running totals, ntile
├── 11_udfs_and_stored_procedures.py # UDFs, vectorized UDFs, SPROCs, UDTFs
├── 12_snowpark_ml_advanced.py      # ML, dynamic pipelines, quality frameworks
├── 13_real_world_project.py        # Complete ETL pipeline (staging→facts→dims→KPIs)
├── 14_interview_prep.py            # Top 25 Python + Snowpark interview Q&A
└── 15_reading_modifying_procedures.py  # Reading & modifying existing stored procs
```

## 📚 Learning Path

### Phase 1: Python Foundations (Week 1-2)
| Module | Topic | Time |
|--------|-------|------|
| 01 | Python Basics — variables, types, operators | 30 min |
| 02 | Control Flow — if/else, loops, comprehensions | 25 min |
| 03 | Functions & Modules — def, lambda, imports | 25 min |
| 04 | Data Structures — lists, dicts, sets, tuples | 30 min |
| 05 | File I/O & Errors — files, JSON, try/except | 20 min |
| 06 | OOP — classes, inheritance, dataclasses | 25 min |

### Phase 2: Data Manipulation (Week 3)
| Module | Topic | Time |
|--------|-------|------|
| 07 | Pandas Basics — the bridge to Snowpark | 25 min |

### Phase 3: Snowpark Core (Week 4-5)
| Module | Topic | Time |
|--------|-------|------|
| 08 | Intro to Snowpark — session, lazy eval, concepts | 30 min |
| 09 | Snowpark DataFrames — hands-on operations | 30 min |
| 10 | Window Functions — rank, lag, running totals | 25 min |

### Phase 4: Production Skills (Week 6-7)
| Module | Topic | Time |
|--------|-------|------|
| 11 | UDFs & Stored Procedures — custom logic | 25 min |
| 12 | Snowpark ML & Advanced Patterns | 25 min |
| 13 | Real-World ETL Project | 30 min |

### Phase 5: Interview Prep & Real Skills (Week 8)
| Module | Topic | Time |
|--------|-------|------|
| 14 | Top 25 Interview Q&A | 30 min |
| 15 | Reading & Modifying Existing Stored Procedures | 35 min |

**Total: ~6 hours of structured learning**

## 🎯 What You'll Be Able to Do After

- ✅ Write Python confidently (variables, functions, classes, error handling)
- ✅ Manipulate data with pandas and Snowpark DataFrames
- ✅ Build ETL pipelines that run inside Snowflake
- ✅ Create UDFs for custom row-level logic
- ✅ Write stored procedures for orchestrated workflows
- ✅ Use window functions for analytics (ranking, running totals)
- ✅ Design production-ready data pipelines
- ✅ Answer 25+ common interview questions with confidence

## 🔑 Key Concepts Covered

| Python | Snowpark |
|--------|----------|
| Variables & Types | Session & Connection |
| Control Flow | Lazy Evaluation |
| Functions & Lambdas | DataFrame API |
| Data Structures | Column Expressions |
| Error Handling | UDFs (scalar & vectorized) |
| OOP / Classes | Stored Procedures |
| Pandas DataFrames | Window Functions |
| File I/O & JSON | Write to Tables |

## 💡 How to Use This Course

1. **Read each module top-to-bottom** — explanations come before code
2. **Run the examples** — in a Python environment or Snowflake Notebook
3. **Do the exercises** — marked "TRY IT YOURSELF" in each module
4. **Build Module 13** — run the complete ETL pipeline in a Snowflake Notebook
5. **Practice Module 14** — answer questions without looking at the answers first

## 🏗️ The Real-World Project (Module 13)

```
Source (TPCH) → Staging → Fact Tables → Dimensions → KPIs → Quality Checks
                  │             │              │           │          │
           Clean/rename    Aggregated     Customer 360  Daily     Validation
           columns         metrics        + segments    trends    assertions
```

## ⚙️ Running in Snowflake

For Modules 08-13, create a Snowflake Notebook and paste the code. The session is automatically available:

```python
from snowflake.snowpark import Session
session = get_active_session()  # Auto-provided in notebooks
```

## License

Open source — use for learning and reference.
