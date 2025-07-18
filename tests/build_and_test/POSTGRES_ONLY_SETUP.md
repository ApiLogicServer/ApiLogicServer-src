# PostgreSQL-only BLT Configuration
# Instructions for using the existing env.py configuration system

## The BLT system already has a comprehensive configuration system in `env.py`

### ✅ **Recommended Approach: Use the existing env.py system**

The build_load_and_test.py script uses `env.py` configuration flags to control which tests run.

### 1. **Simple Configuration Swap Method:**

```bash
# Backup your current env.py
cp env.py env_backup.py

# Use the PostgreSQL-only configuration
cp env_postgres_only.py env.py

# Run the normal BLT test (it will only run PostgreSQL tests)
python3 build_load_and_test.py

# Restore your original configuration
cp env_backup.py env.py
```

### 2. **Direct Edit Method:**

Edit `env.py` directly and set:
```python
# Set these to True (PostgreSQL tests)
do_docker_postgres = True
do_docker_postgres_auth = True

# Set these to False (skip non-PostgreSQL tests)
do_docker_mysql = False
do_docker_sqlserver = False
do_allocation_test = False
do_budget_app_test = False
do_other_sqlite_databases = False
do_test_genai = False
do_test_multi_reln = False
do_create_shipping = False
do_run_shipping = False
do_run_nw_kafka = False
do_test_nw_kafka = False
```

### 3. **Use the provided PostgreSQL-only env.py:**

The `env_postgres_only.py` file is a complete configuration that:
- ✅ Enables PostgreSQL tests (`do_docker_postgres = True`)
- ✅ Enables PostgreSQL auth tests (`do_docker_postgres_auth = True`)
- ❌ Disables MySQL tests (`do_docker_mysql = False`)
- ❌ Disables SQLite tests (`do_allocation_test = False`, `do_budget_app_test = False`)
- ❌ Disables other non-essential tests

### 4. Environment variables

Ensure these are set for PostgreSQL testing:
```bash
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=p
export POSTGRES_DB=postgres
export POSTGRES_NW_DB=northwind
```

### 5. PostgreSQL test databases

Make sure these databases exist:
- `postgres` (default PostgreSQL database)
- `northwind` (Northwind sample database)
- `authdb` (authentication database)

You can create them with:
```sql
CREATE DATABASE northwind;
CREATE DATABASE authdb;
```
