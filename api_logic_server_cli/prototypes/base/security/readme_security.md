You can add Role Based Access Control (RBAC) to your project, providing:

* authentication: based on sql tables for users / roles, and
* authorization: declarative for-filters for roles.

Common commands:

```bash
```
als add-auth --provider-type=sql --db-url=
als add-auth --provider-type=sql --db_url=postgresql://postgres:p@localhost/authdb

als add-auth --provider-type=keycloak --db-url=localhost
als add-auth --provider-type=keycloak --db-url=hardened

als add-auth --provider-type=None # to disable
``` 
