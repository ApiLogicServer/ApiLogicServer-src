You can add Role Based Access Control (RBAC) to your project, providing:

* authentication: based on SQL tables (or Keycloak) for users / roles, and
* authorization: declarative row-filters and CRUD permissions per role.

## 1. Bootstrap (CLI — one-time)

```bash
genai-logic add-auth --provider-type=sql                                        # SQL-based, no Keycloak needed
genai-logic add-auth --provider-type=sql --db-url=postgresql://postgres:p@localhost/authdb  # separate auth db

genai-logic add-auth --provider-type=keycloak --db-url=localhost                # local Keycloak
genai-logic add-auth --provider-type=keycloak --db-url=hardened                 # hardened Keycloak

genai-logic add-auth --provider-type=None                                       # disable
```

🚨 For `--provider-type=sql`, never pass `--db-url=sqlite:///database/db.sqlite` (your project's
own domain database) — `--db-url` means "where's the *auth* db," not "which project db." Only
pass it for a genuinely separate auth database.

## 2. Declare — describe it in plain English, AI writes `declare_security.py`

Security declarations are a small DSL (`Roles`, `DefaultRolePermission`, `Grant`,
`GlobalFilter`) — you don't hand-write this. Describe what you want; your coding assistant
translates it. A few examples, in this project's own terms (Customer, Order):

```text
sales role reads Customer and Order, but can't insert, update, or delete
```
```python
DefaultRolePermission(to_role=Roles.sales, can_read=True, can_insert=False, can_update=False, can_delete=False)
```

```text
sales sees only customers with credit_limit >= 3000, or a positive balance
```
```python
Grant(on_entity=models.Customer, to_role=Roles.sales,
      filter=lambda: models.Customer.credit_limit >= 3000, filter_debug="credit_limit >= 3000")
Grant(on_entity=models.Customer, to_role=Roles.sales,
      filter=lambda: models.Customer.balance > 0, filter_debug="balance > 0")
# two Grants for the same role are OR'd — either condition qualifies
```

```text
manager can read, insert, and update everything, but never delete
```
```python
DefaultRolePermission(to_role=Roles.manager, can_read=True, can_insert=True, can_update=True, can_delete=False)
```

```text
no one sees orders for the customer named 'Bob', except manager and admin
```
```python
GlobalFilter(global_filter_attribute_name="name", roles_not_filtered=["sa", "manager", "admin"],
             filter="{entity_class}.name != 'Bob'")
```

You still own the result — `security/declare_security.py` is a real file, reviewed and
version-controlled like any other source, not a black box. Full DSL reference (all four
building blocks, more NL→declaration examples): `docs/training/security.md`.
