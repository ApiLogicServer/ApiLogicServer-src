---
title: Security - Role-Based Access Control
description: Translate NL security requirements into declare_security.py declarations
source: Generic training for ApiLogicServer projects
usage: AI assistants read this before implementing security declarations
version: 1.0
date: Apr 21, 2026
related:
  - logic_bank_patterns.md (analogous pattern for logic declarations)
changelog:
  - 1.0 (Apr 21, 2026): Initial - roles, DefaultRolePermission, Grant, GlobalFilter
---

# Security — Role-Based Access Control

Security declarations in `security/declare_security.py` are a **declarative DSL** — the same
philosophy as LogicBank rules. You declare *what* access looks like; the engine enforces it
automatically on every API request, Admin UI operation, and MCP query.

---

## Bootstrap (CLI — not AI)

Security requires a one-time infrastructure setup before declarations can be made.
These are CLI commands, not AI-generated:

```bash
# 1. Start Keycloak (or use SQL provider)
cd devops/keycloak
docker compose up

# 2. Activate security in the project
genai-logic add-auth --provider-type=keycloak --db-url=localhost

# Alternative: SQL-based auth (no Keycloak needed)
genai-logic add-auth --provider-type=sql --db-url=sqlite:///database/db.sqlite

# To disable
genai-logic add-auth --provider-type=None
```

After `add-auth`, `config/default.env` will contain `SECURITY_ENABLED = True`.

---

## Declaration DSL — `security/declare_security.py`

All security logic lives in this one file. The four building blocks:

---

### 1. Roles

Define a `Roles` class for code completion — the auth database is the source of truth,
this just enables IDE autocomplete:

```python
class Roles():
    tenant  = "tenant"    # row-level tenant isolation
    manager = "manager"   # full read/write, no delete
    sales   = "sales"     # read-only with row filters
    admin   = "admin"     # full access
```

---

### 2. DefaultRolePermission — table-level CRUD defaults

Grants a role blanket permission across ALL tables. Most projects define one per role.

```python
DefaultRolePermission(to_role=Roles.admin,   can_read=True, can_insert=True,  can_update=True,  can_delete=True)
DefaultRolePermission(to_role=Roles.manager, can_read=True, can_insert=True,  can_update=True,  can_delete=False)
DefaultRolePermission(to_role=Roles.sales,   can_read=True, can_insert=False, can_update=False, can_delete=False)
DefaultRolePermission(to_role=Roles.tenant,  can_read=True, can_insert=True,  can_update=True,  can_delete=True)
```

**NL → DSL mapping:**

| Natural language | Declaration |
|---|---|
| "managers can read and write but not delete" | `DefaultRolePermission(to_role=Roles.manager, can_read=True, can_insert=True, can_update=True, can_delete=False)` |
| "read-only role" | `DefaultRolePermission(to_role=Roles.read_only, can_read=True, can_insert=False, can_update=False, can_delete=False)` |
| "admin has full access" | `DefaultRolePermission(to_role=Roles.admin, can_read=True, can_insert=True, can_update=True, can_delete=True)` |

---

### 3. Grant — row-level filters per entity

Restricts which **rows** a role can see for a specific entity. Multiple Grants for the same
role are **OR'd** — the user sees rows matching ANY of their grants.

```python
# Sales sees only customers with credit_limit >= 3000 ...
Grant(  on_entity = models.Customer,
        to_role   = Roles.sales,
        filter    = lambda: models.Customer.credit_limit >= 3000,
        filter_debug = "credit_limit >= 3000")

# ... OR customers with a positive balance (grants are OR'd)
Grant(  on_entity = models.Customer,
        to_role   = Roles.sales,
        filter    = lambda: models.Customer.balance > 0,
        filter_debug = "balance > 0")

# Tenant isolation — each user sees only their own rows
Grant(  on_entity = models.Order,
        to_role   = Roles.tenant,
        filter    = lambda: models.Order.customer_id == Security.current_user_id(),
        filter_debug = "tenant isolation: own orders only")
```

**NL → DSL mapping:**

| Natural language | Declaration |
|---|---|
| "sales only sees high-value customers (credit ≥ 3000)" | `Grant(on_entity=models.Customer, to_role=Roles.sales, filter=lambda: models.Customer.credit_limit >= 3000)` |
| "tenants see only their own orders" | `Grant(on_entity=models.Order, to_role=Roles.tenant, filter=lambda: models.Order.customer_id == Security.current_user_id())` |
| "managers see all rows" | No Grant needed — DefaultRolePermission with no filter gives full row access |

**Key rules:**
- `filter` must be a **lambda** returning a SQLAlchemy expression
- Always include `filter_debug` — it appears in logs for diagnosing access issues
- Filters on related entities are applied automatically via SQLAlchemy joins
- `sa` (super-admin) role bypasses all grants — no Grant needed

---

### 4. GlobalFilter — cross-entity filter for a role

Applies the same row filter across ALL entities that have the named attribute. Use for
system-wide policies (e.g., exclude test data, apply tenant ID everywhere).

```python
# Sales role never sees rows where name == 'Bob' (across all entities with a 'name' column)
GlobalFilter(
    global_filter_attribute_name = "name",
    roles_not_filtered = ["sa", "manager", "tenant", "renter"],  # these roles skip the filter
    filter = "{entity_class}.name != 'Bob'"
)
```

**When to use:**
- Cross-cutting data policies ("active records only", "exclude archived")
- Simple tenant isolation on a single discriminator column
- Use `Grant` instead when filter logic varies by entity

---

## Complete Example (basic_demo pattern)

```python
from security.system.authorization import Grant, Security, DefaultRolePermission, GlobalFilter
from database import models

class Roles():
    tenant  = "tenant"
    renter  = "renter"
    manager = "manager"
    sales   = "sales"

DefaultRolePermission(to_role=Roles.tenant,  can_read=True, can_delete=True)
DefaultRolePermission(to_role=Roles.renter,  can_read=True, can_delete=False)
DefaultRolePermission(to_role=Roles.manager, can_read=True, can_delete=False)
DefaultRolePermission(to_role=Roles.sales,   can_read=True, can_delete=False)

GlobalFilter(
    global_filter_attribute_name = "name",
    roles_not_filtered = ["sa", "manager", "tenant", "renter"],
    filter = "{entity_class}.name != 'Bob'"
)

Grant(  on_entity    = models.Customer,
        to_role      = Roles.sales,
        filter       = lambda: models.Customer.credit_limit >= 3000,
        filter_debug = "credit_limit >= 3000")

Grant(  on_entity    = models.Customer,
        to_role      = Roles.sales,
        filter       = lambda: models.Customer.balance > 0,
        filter_debug = "balance > 0")
```

---

## Using in Executable Requirements

In `docs/requirements/<name>/requirements.md`, add a Security section:

```gherkin
## N. Security — Role-Based Access Control

Prerequisite: run `cd devops/keycloak && docker compose up` then
              `genai-logic add-auth --provider-type=keycloak --db-url=localhost`

Feature: RBAC

  Scenario: Role permissions
    Given the following roles: manager, sales, tenant, read_only
    Then manager can read/insert/update but not delete
    And sales can read only
    And tenant can read and delete

  Scenario: Row-level access for sales
    Given a sales user
    Then they see only customers with credit_limit >= 3000 or balance > 0

  Scenario: Tenant isolation
    Given a tenant user
    Then they see only their own orders
```

AI implements this by writing `security/declare_security.py` directly — no CLI needed for the
declarations, only for the initial bootstrap.

---

## MANDATORY WORKFLOW — before implementing security declarations

```
STOP ✋

WHEN USER ASKS TO ADD SECURITY OR AN XR STEP CONTAINS A SECURITY SECTION:

STEP 1: Read this file (security.md) — already done if you're here
STEP 2: Read database/models.py — identify entity class names and key attributes
STEP 3: Check if add-auth has been run (SECURITY_ENABLED in config/default.env)
        If not: tell user to run the CLI bootstrap commands above FIRST
STEP 4: Implement declare_security.py following the patterns above
STEP 5: Restart server and verify grants in logs
```
