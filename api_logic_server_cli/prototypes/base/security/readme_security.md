You can add Role Based Access Control (RBAC) to your project, providing:

* authentication: based on sql tables for users / roles, and
* authorization: declarative for-filters for roles.

Common setup commands:

```bash
als add-auth --provider-type=sql --db-url=
als add-auth --provider-type=sql --db_url=postgresql://postgres:p@localhost/authdb

als add-auth --provider-type=keycloak --db-url=localhost
als add-auth --provider-type=keycloak --db-url=hardened

als add-auth --provider-type=None # to disable
``` 

Then, declare grants like this in `declare_security.py`, either by using AI:

```bash
sales role sees only customers with credit_limit ≥ 3000 or positive balance
```

Or, directly in Python:

```python
Grant(  on_entity = models.Customer,
        to_role = Roles.sales,
        filter = lambda : models.Customer.credit_limit >= 3000,
        filter_debug = "credit_limit > 3000")                                   # this eliminates Charlie, but...
```