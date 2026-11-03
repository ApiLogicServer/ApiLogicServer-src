---
title: Security - Role-Based Access Control
description: Translate NL security requirements into declare_security.py declarations
source: Generic training for ApiLogicServer projects
usage: AI assistants read this before implementing security declarations
version: 1.1
date: Oct 29, 2026
related:
  - logic_bank_patterns.md (analogous pattern for logic declarations)
changelog:
  - 1.1 (Oct 29, 2026): New section "Roles inside business rules": `Security.current_user_has_role(name)` in a rule or event (a role may exceed a limit, approve, bypass). It existed in every generated project but no doc mentioned it for business rules; a blind run found it only by reading security/system/authorization.py. Includes the no-user case (the call raises).
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

# Alternative: SQL-based auth (no Keycloak needed) — uses the project's own pre-built
# User/Role/UserRole schema (database/authentication_db.sqlite), created automatically
# by `genai-logic create`. Omit --db-url for this default case.
genai-logic add-auth --provider-type=sql

# To disable
genai-logic add-auth --provider-type=None
```

**🚨 CRITICAL — for `--provider-type=sql`, do NOT pass `--db-url=sqlite:///database/db.sqlite`
(or any URL pointing at the project's own domain database).** For `add-auth`, `--db-url` means
"where is the *auth* database" — not "which project database to use." Pointing it at your
domain db (which has no `User`/`Role`/`UserRole` tables) makes the CLI regenerate
`authentication_db.sqlite` **from your domain data**, silently overwriting the correct
pre-built auth schema, then crashing (`insert_lines_at`: can't find `UserRoleList` — because
your domain db was never given one) before authentication is ever wired in. Confirmed live,
100% reproducible on a completely fresh project (Sep 2026) — this is a real trap, not a
hypothetical one; the earlier version of this doc's own example was exactly this bug.
Only pass `--db-url` when you have a genuinely separate auth database (e.g.
`--db-url=postgresql://postgres:p@localhost/authdb`, a real database with the User/Role
schema already in it) — never your project's own `database/db.sqlite`.

After `add-auth`, `config/default.env` will contain `SECURITY_ENABLED = True`.

**Using Podman instead of Docker?** Substitute `podman compose up` for `docker compose up` in
step 1 — `devops/keycloak/docker-compose.yml` works unchanged. One-time setup (Podman machine
init, compose plugin wiring): [DevOps-Podman](https://apilogicserver.github.io/Docs/DevOps-Podman/).

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

## Roles inside business rules

Grants control *access* (who may read or write a row). Sometimes the **business rule itself** depends on who the user is:
"a manager may exceed the budget", "only a credit controller may go over the limit", "approvers can skip the check".
Use `Security.current_user_has_role('<role>')` inside the rule. It is generated into every project
(`security/system/authorization.py`) and reads the roles of the signed-in user (Keycloak: the token's realm roles;
SQL provider: the user's role rows).

| Natural language | In the rule |
|---|---|
| "a manager may exceed the budget" | the constraint passes when `Security.current_user_has_role('manager')` is true |
| "only role X can do Y" | the event or constraint rejects unless the role check is true |

```python
from logic_bank.logic_bank import Rule
from database import models


def _current_user_is_manager() -> bool:
    """True only if a request user exists and holds the manager role; no user -> False."""
    try:
        from security.system.authorization import Security   # import here: logic loads before security
        return Security.current_user_has_role('manager')
    except Exception:
        return False        # no request / no signed-in user: not a manager, so the rule is enforced


def _total_salary_within_budget(row, old_row, logic_row):
    if row.total_salary <= row.budget:
        return True
    if _current_user_is_manager():
        logic_row.log(f"over budget ({row.total_salary} > {row.budget}) - allowed for manager role")
        return True
    return False


Rule.constraint(validate=models.Department,
                calling=_total_salary_within_budget,       # calling=, not as_condition=: more than one line
                error_msg="Department total_salary ({row.total_salary}) exceeds budget ({row.budget})")
```

**Rules for this pattern**
- **No user is a real case.** A seed script, a Kafka consumer, a direct insert, or `SECURITY_ENABLED = False` has no signed-in
  user, and `Security.current_user()` then **raises**. Wrap the call as above and decide what no-user means. The safe default is
  "not authorized": the rule is enforced. Record the choice as a 🔴 ad-lib.
- **Use the exact role name from the auth data** (for Keycloak, the realm role; see `devops/keycloak/import`). `sa` and `admin`
  are not "manager". Only the named role is exempt unless the requirement says otherwise.
- **The role belongs to whoever commits the transaction**, not to who created the data. Nothing records that a role holder
  approved an overage, and others may then be blocked from editing the same row until it is back within the limit. The
  requirement rarely says; list it as a 🔴 ad-lib.
- **Keep it small.** A rule that depends on the caller is outside the pure declarative model. One role check in one rule; do
  not scatter it.
- **Tests must log in as both kinds of user** (`test_utils.login('<user>')`), and cover the no-user case where one exists.
- The usual rules for `calling=` apply (a dependency anchor if the body delegates to a helper; never write the literal text
  `row.attr` in a comment).

Verified (Oct 29, 2026, Keycloak provider, `demo_emp_types`): a manager is allowed, a non-manager and `admin` are rejected, and
a write with no user is rejected. The SQL provider uses the same call; it was not separately tested.

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
