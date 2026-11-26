# config

`default.env` holds the **dev** defaults.  It is committed, so it holds no real passwords.

There is no `prod.env` here, by design.  The same code (and container image) runs in every environment, and each environment supplies its own values as **environment variables**, which override `default.env`:

| Environment | Settings | Secrets (`SECRET_KEY`, database password) |
|:--|:--|:--|
| Dev | `default.env` | placeholders in `default.env` |
| Pre-prod, prod | the deployment: `devops/docker-compose-prod/`, or the cloud service's settings | a secrets store, injected as environment variables; locally, a gitignored `secrets.env` |

This is the standard practice for any service, not something specific to GenAI-Logic.  `APILOGICPROJECT_ENV` says which environment this is; outside `dev`, a server with SQL security will not start with the placeholder `SECRET_KEY`.

To try it end to end (dev on SQLite, prod on Postgres, secrets kept out of git), see the [DevOps Quick Start: Dev to Prod](https://apilogicserver.github.io/Docs/DevOps-Quick-Start-Dev-to-Prod/).  For the background, see [Environments and Secrets](https://apilogicserver.github.io/Docs/DevOps-Container-Configuration/#environments-and-secrets-dev-pre-prod-prod).
