# Team Development

Status: draft, 2026-11-21.

&nbsp;

## 1. SQLite for dev, Postgres for prod

**Why SQLite for dev:** no server, a database per developer, fast resets, and the whole project runs from a clone.

**Why it mostly works:** rules run at the ORM level (SQLAlchemy), and the API and rules issue no database-specific
SQL. Moving from SQLite to Postgres is a database URL, not a code change.

**Where SQLAlchemy does not hide the difference:**

| Area | SQLite (dev) | Postgres (prod) |
|---|---|---|
| Types | Loose: a string fits an INTEGER, VARCHAR length ignored, `Numeric` stored as float | Enforced; `Numeric` exact |
| Dates | Stored as text; `date('now')` is UTC | Native date / timestamp types |
| Raw SQL | `strftime`, `date()` work | Not portable: use the ORM |
| Foreign keys | Enforced only with `PRAGMA foreign_keys=ON` (not set by default) | Always enforced |
| Sequences | Explicit-id inserts are fine | Explicit-id seeds leave sequences behind: "duplicate key" on the next insert |
| Concurrency | One writer at a time | Real concurrency: lost updates and lock waits show up here only |
| DDL | Limited `ALTER TABLE` | Full |

**Practices:**

1. **SQLite for the inner loop, Postgres in CI.** CI runs the same Behave suite against Postgres on every merge. The
   tests call the API, so they don't depend on the database; this catches nearly every row above.
2. **Schema in git as code.** `models.py` plus Alembic migrations (`database/alembic/`) are the source of truth. Don't
   merge `db.sqlite` (binary): rebuild it from migrations and a seed script.
3. **Seed through the ORM, without explicit ids** (as `database/test_data/seed_order_flow.py` in `basic_demo_eai`): the
   rules fire and sequences stay right.
4. **The portable subset:** `Numeric` for money; no raw SQL in logic or APIs; SQLite foreign keys on in dev.
5. **Concurrency and locking:** test on Postgres only (the Manager's Postgres container, or CI).

Open: the CE teaches the one-developer flow (SQLite DDL, then `rebuild-from-database`). A team mode would make 1-2 the
default.

&nbsp;

## 2. Configuring a project for dev, pre-prod and prod

One code base; each environment differs only in **environment variables**. They override `config/default.env`, which
overrides `config/config.py`.

| Setting | Dev | Pre-prod (CI, staging) | Prod |
|---|---|---|---|
| `SQLALCHEMY_DATABASE_URI` | default: `database/db.sqlite` | `postgresql://...` (test database) | `postgresql://...` |
| `SQLALCHEMY_DATABASE_URI_AUTHENTICATION` | default: `database/authentication_db.sqlite` | Postgres, or Keycloak (no auth db) | Keycloak, or Postgres |
| `SECURITY_ENABLED` | `true` (SQL provider) or `false` | `true` | `true` |
| `KAFKA_SERVER`, `KAFKA_CONSUMER_GROUP` | unset (simulated), or local broker | test broker; group unique per environment | prod broker; own group |
| `APILOGICPROJECT_CONSUME_DEBUG` | `true` | `true` for test runs | **`false`** (the debug services have no login) |
| `APILOGICPROJECT_KAFKA_COMMIT_OFFSETS` | default (`true`) | default | default; never `false` |

**How to set them:**

- **Dev:** `config/default.env` (committed), with personal overrides exported in the shell, never committed.
- **Pre-prod and prod:** set by the deployment (container environment, CI secrets), not in files. The container
  image is the same for both; `devops/` has the Docker files.
- **Secrets** (database passwords, Keycloak client secrets) come only from the environment or a secrets manager; keep
  them out of `default.env` and git.

**Schema per environment:** dev builds its SQLite database from the migrations; pre-prod and prod apply the same
Alembic migrations (`database/alembic/`, see `readme_alembic.md`) before the new image starts.

**Postgres on Python 3.13+:** `config.py` rewrites `postgresql://` to `postgresql+psycopg://` itself; use either form.

&nbsp;

## 3. Security testing

Tests need known users, passwords and roles; production uses the organization's identity provider. Keep the two apart
the same way as Kafka: **a test identity server in a container, with its test data in git.**

- **Keycloak container (recommended for teams):** `devops/keycloak/` starts Keycloak with a realm imported from
  `devops/keycloak/import/` (`kcals-realm.json`, `kcals-users-0.json`: users such as `admin`, roles). Replace those
  files with a realm that has **the production role names** and test users, and commit them. Every developer and CI
  then logs in the same way, and the grants in `security/declare_security.py` are tested against the real roles.
- **SQL provider (simplest):** users and roles in `database/authentication_db.sqlite`; no container. Fine for solo dev;
  the role names must still match production.
- **Production:** point at the real identity provider by environment: `KEYCLOAK_BASE`, `KEYCLOAK_REALM`,
  `KEYCLOAK_CLIENT_ID` (see `config/config.py`). The grants don't change; only the user source does.

Custom APIs (`api/api_discovery/`) don't require a login by default, and the debug services have none. Check both
before production (Section 2: `APILOGICPROJECT_CONSUME_DEBUG = false`).

&nbsp;

## 4. Kafka testing

**Dev and CI: nothing to set up beyond a broker.** The project manages its own topics: the reset script
(`integration/kafka/<topic>_reset.sh`) creates them on a local broker container, the debug service
(`/consume_debug/<topic>`) sends a test message live or simulated, and `/reset` empties the queue. With no broker at
all, the same tests run simulated.

**Pre-prod and prod: not do-nothing.** Shared clusters are usually run by a platform team, with topic auto-creation
off. Ask them for:
- **Every topic the project uses, including the internal ones:** each subscribe pipeline needs its entry topic *and*
  `<topic>_processed` (the 2-message pattern's second hop). Publish topics too.
- **A consumer group per project and environment** (`KAFKA_CONSUMER_GROUP`).
- **Connection settings:** TLS/SASL and ACLs go in the full consumer and producer configs,
  `APILOGICPROJECT_KAFKA_CONSUMER` and `APILOGICPROJECT_KAFKA_PRODUCER` (`config/default.env` shows the shape).

The reset script and `/reset` are for dev and test only: they delete or purge topics.

&nbsp;

## 5. Extending the context engineering (CE) and projects

An organization can add its own standards to every project it creates, without forking the product:

| What | Where | Applied |
|---|---|---|
| **Scaffold overlay** | A git repo (or directory) of files, passed as `genai-logic create --from-git=<url>`; a default in the Manager's `system/config/default_from_git.txt` | At creation: overlays the base scaffold (organization docs, devops files, config) |
| **CE overlay** | The Manager's `system/project_context_engineering/` | At creation: copied into each project's `docs/training/`, on top of the scaffold and any `--from-git` overlay (add or override training files) |
| **Assistant instructions** | `*.instructions.md` files in a project's `.github/` | Loaded by the IDE assistant (VS Code Copilot) automatically |

Typical uses: naming conventions, the organization's DDL rules for Postgres (Section 1), a standard Keycloak realm
(Section 3), the Kafka connection pattern (Section 4).

Documented today only briefly, in the Docs pages
[AI-Enabled Projects, "Extend Context Engineering"](https://apilogicserver.github.io/Docs/Project-AI-Enabled/#extend-context-engineering)
and [Existing DB, "Extensible Scaffold"](https://apilogicserver.github.io/Docs/Project-Existing-DB/#extensible-scaffold-context-engineering).
Open: a worked example (an overlay repo with one added training file), and whether the Manager CE should point to it.
