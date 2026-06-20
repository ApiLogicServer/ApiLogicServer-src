# GenAI-Logic (API Logic Server)

[![Downloads](https://pepy.tech/badge/apilogicserver)](https://pepy.tech/project/apilogicserver)
[![Latest Version](https://img.shields.io/pypi/v/apilogicserver.svg)](https://pypi.python.org/pypi/apilogicserver/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/apilogicserver.svg)](https://pypi.python.org/pypi/apilogicserver/)

One prompt — or your existing database — builds a working API and Admin App, then you declare business logic in **5 readable rules instead of 200 lines of AI-generated code** to enforce it.

On opening the project (or using Codespaces, below), the readme provides a First Time tour.  You'll see that enforcement yourself in a few minutes: those rules run at **one commit point**, no matter which path the transaction came in on — API, MCP, agent, Kafka. **No bypass.**

And you're not reading alone: your AI assistant is a partner throughout. Ask it anything — architecture, rules, debugging, deployment, or how the system works.

## See it work — no install

**[Open in GitHub Codespaces →](https://codespaces.new/ApiLogicServer/codespaces_mgr)**

This opens a ready-to-go Manager workspace in your browser — no local Python, no clone, nothing to install. Inside, the README walks you through a short guided demo: one prompt creates a real project, you trigger a business rule, then open the 200-line procedural version side-by-side with the 5-line declarative version that replaces it.

If you'd rather work locally, see [Quick Start](#-quick-start-local-install) below.

![API Logic Server Architecture](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/Architecture-What-Is.png)

---

## ⚡ Quick Start (local install)

```bash
# Install (Python 3.10-3.13)
python -m venv venv                      # windows: python -m venv venv
source venv/bin/activate                 # windows: venv\Scripts\activate
python -m pip install ApiLogicServer

# Start the Manager (opens readme with instructions)
genai-logic start

# Create project from your database (or use sample)
genai-logic create --project_name=my_app --db_url=

# Run it
cd my_app
python api_logic_server_run.py
```

**What's in the generated project:**
- **JSON:API** — endpoints for every table, with filtering, sorting, pagination, related data
- **Admin App** — multi-page React UI with automatic joins, runs immediately
- **Logic Engine** — declarative rules (5 lines instead of 200) enforced on every write path, from every caller
- **Security** — row-level authorization, JWT authentication
- **Custom UIs** — use the same API with vibe tools (Cursor, Bolt, Lovable) or GenAI-Logic's own Copilot training
- **Docker-ready** — pre-configured containers for deployment

**[📖 8-minute video demo](https://www.youtube.com/watch?v=Z4_NJIm5rFs&t=323s)** | **[📚 Full Documentation](https://apilogicserver.github.io/Docs/)** | **[🏠 Home](https://www.genai-logic.com)**

---

## Why rules instead of code

| | Without rules | With GenAI-Logic |
|---|---|---|
| Creating API endpoints | Days to weeks | Seconds, automated |
| Multi-table update logic | 200+ lines of procedural code, easy to miss a change path | 5 declarative rules — [see the A/B comparison](https://github.com/ApiLogicServer/basic_demo/blob/main/logic/procedural/declarative-vs-procedural-comparison.md) |
| Screen building | Manual, or proprietary low-code | Automated from the data model, plus vibe-tool custom UIs |
| System integration | Custom glue code per consumer | MCP-discoverable APIs out of the box |
| Auditing what the logic does | Reading procedural code | Reading the rules — they're the documentation |

Rules are declarative: declared once, auto-invoked at every commit from every caller, auto-ordered by the engine. You don't call them, so they can't be forgotten or bypassed — every write, from any path (API, custom endpoint, Kafka consumer, agent), goes through the same commit-time enforcement. No second door.

This isn't new theory — it's the same paradigm (Val Huber, co-inventor with Ron Ross) from Wang Labs PACE and Versata, validated across 6,000+ production deployments over 40 years, now open source and rebuilt for Python/React.

---

## When to use it

**Good fit** — data-centric business applications where the complexity is in multi-table calculations, constraints, and derivations:
- Application integration — instant APIs for legacy databases, modernization without a rewrite
- Rapid prototyping — a working backend in minutes
- GenAI backends — natural language → working microservice
- Backoffice / admin apps, CRUD-heavy systems (orders, inventory, customers)
- Microservice decomposition of a monolith

**Not the right tool** — real-time streaming (use Kafka/Flink), ML pipelines, low-level systems programming, document/content management, or simple static sites. GenAI-Logic can still be the backend in a hybrid architecture for these.

---

## FAQ

**How is this different from low-code platforms (Retool, OutSystems, Hasura)?**
It generates standard Python projects you own, extend, and deploy — not a proprietary screen-painter. Unlike plain API generators, it includes multi-table logic automation. [Detailed comparison →](https://medium.com/@valjhuber/declarative-genai-the-architecture-behind-enterprise-vibe-automation-1b8a4fe4fbd7)

**Is this vendor lock-in?**
No — Apache 2.0 + Commons Clause (free for internal use). Rules sit on top of standard, readable, version-controlled Python and SQLAlchemy events. You can keep using the rules engine as a library, or replace rules with equivalent procedural code at any time.

**Can I customize the generated app?**
Yes. Override the UI, extend the API, add your own logic — standard Python and SQLAlchemy, any vibe tool. The generated project is a starting point, not a black box. [Customization patterns →](https://apilogicserver.github.io/Docs/Logic/)

**What happens when logic doesn't fit the declarative model?**
The engine handles the large majority of typical business logic (calculations, validations, cascading updates). For workflows, state machines, or external integrations, you write standard Python event handlers that coexist with the rules — the engine calls your code at the right time.

**How long until a team is productive?**
Rules can be written immediately in natural language; the DSL itself is intuitive. Understanding the engine's optimization strategy (pruning, chaining) takes a few days. Most teams are productive within a week.

**Where do I get help?**
[Discord](https://discord.gg/fNRTTVFT) for real-time help, [GitHub Discussions](https://github.com/ApiLogicServer/ApiLogicServer-src/discussions), or the [full documentation](https://apilogicserver.github.io/Docs/).

**[→ More FAQs](https://medium.com/@valjhuber/declarative-genai-the-architecture-behind-enterprise-vibe-automation-1b8a4fe4fbd7#faqs)**

---

## Architecture

```
┌─────────────────────────────────────────────┐
│  Natural Language Prompt or Existing DB     │
└───────────────┬─────────────────────────────┘
                │ genai-logic create
                ↓
┌─────────────────────────────────────────────┐
│         Generated Project                    │
├─────────────────────────────────────────────┤
│  Admin App (React)                          │
│  JSON:API (SAFRS)                           │
│  Logic (Rules Engine)                       │
│  ORM (SQLAlchemy)                           │
│  Security (JWT + Row-level)                 │
└─────────────────────────────────────────────┘
                │
                ↓
        Docker Container
```

**Stack:** Python 3.10-3.13, Flask + SQLAlchemy, React + Material-UI, Docker.

**What gets created:**
```
my_app/
├── api/                    # JSON:API endpoints (Admin App AND custom UIs)
│   ├── expose_api_models.py
│   └── customize_api.py    # custom endpoints
├── ui/admin/                # instant Admin App
│   └── admin.yaml
├── logic/                   # business logic, enforced on every write
│   └── declare_logic.py
├── security/
│   └── declare_security.py
├── database/
│   └── models.py
├── tests/                   # BDD tests (Behave)
├── docs/training/           # GenAI-Logic training for Copilot
└── devops/docker/
```

---

## GenAI Integration

Create from natural language:
```bash
genai-logic genai --using=prompt.txt
```

```text
Create a system for customers, orders, items and products.
Customer balance is sum of unshipped order totals.
Order total is sum of item amounts.
Item amount is quantity * unit price.
Copy product price to item unit price.
Constraint: customer balance cannot exceed credit limit.
```

That's a working microservice — database, API, Admin App, and 5 declarative rules enforcing the credit check — in about 10 seconds.

Every created project also includes AI tutoring: open it and your Copilot/Claude assistant explains what's built and what to do next (`.github/.copilot-instructions.md`), backed by training material in `docs/training/`. Ask it to translate a new requirement and it writes the rules, not procedural code, because that training tells it to.

**Living documentation:** `genai-logic add-tests` generates Behave tests from your declared rules; running them produces a report tracing requirement → test → rule → execution — so the rules stay the source of truth, not a Word doc that drifts.

---

## 🎬 Video Overview (8 min)

[![GenAI Automation](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/sample-ai/copilot/genai-automation-video.png)](https://www.youtube.com/watch?v=Z4_NJIm5rFs&t=323s "Microservice Automation")

---

## Examples and Samples

**[See all sample projects](https://apilogicserver.github.io/Docs/Data-Model-Examples/)**

| Sample | Description | Database |
|--------|-------------|----------|
| **basic_demo** | Check credit rules, Behave testing | SQLite (Northwind) |
| **genai_demo** | Created from natural language | SQLite |
| **classicmodels** | Sales, employees, offices | MySQL |
| **chinook** | Music store (artists, albums, tracks) | SQLite/PostgreSQL |
| **postgres-nw** | Northwind on PostgreSQL | PostgreSQL |
| **sqlserver** | Adventure Works | SQL Server |

---

## Supported Databases

SQLite, PostgreSQL, MySQL/MariaDB, SQL Server, Oracle, and any other SQLAlchemy-supported database.

---

## Security

Authentication (SQL-based, Keycloak, or custom providers), role-based authorization with row-level filtering, multi-tenant global filters, JWT tokens, Swagger-integrated security docs. [Security Overview →](https://apilogicserver.github.io/Docs/Security-Overview/)

---

## Contributing

| Area | Current | Ideas for contribution |
|------|---------|----------------------|
| **API** | JSON:API, Swagger | GraphQL, gRPC |
| **Deployment** | Docker, Azure | AWS (ECS/Lambda), Kubernetes/Helm |
| **Logic** | Rules engine | Additional rule types, performance tuning |
| **UI** | Admin App (React) | Custom UI frameworks, mobile SDK |
| **GenAI** | Web version, CLI | Enhanced natural language understanding |

**[See open issues](https://github.com/ApiLogicServer/ApiLogicServer-src/issues)**

**Developing API Logic Server itself:**
```bash
git clone https://github.com/ApiLogicServer/ApiLogicServer-src.git
cd ApiLogicServer-src
python -m pip install -r requirements.txt
python test/build_and_test.py
```
**[Dev installation docs →](https://apilogicserver.github.io/Docs/Architecture-Internals/)**

---

## Documentation

- **[Full Documentation](https://apilogicserver.github.io/Docs/)**
- **[Quick Start Tutorial](https://apilogicserver.github.io/Docs/Tutorial/)** (20 minutes)
- **[Logic: Why](https://apilogicserver.github.io/Docs/Logic-Why/)** — the case for declarative logic
- **[Logic Documentation](https://apilogicserver.github.io/Docs/Logic/)** — rule types and patterns
- **[API Self-Serve](https://apilogicserver.github.io/Docs/API-Self-Serve/)** — consumer-driven APIs
- **[Security Guide](https://apilogicserver.github.io/Docs/Security-Overview/)**
- **[Behave Testing](https://apilogicserver.github.io/Docs/Behave/)**
- **[Natural Language Logic](https://apilogicserver.github.io/Docs/WebGenAI-CLI/)**
- **[Integration Patterns](https://apilogicserver.github.io/Docs/Sample-Integration/)** — Kafka, B2B, MCP
- **[Database Changes](https://apilogicserver.github.io/Docs/Database-Changes/)**
- **[Deployment](https://apilogicserver.github.io/Docs/DevOps-Containers/)**
- **[Architecture](https://apilogicserver.github.io/Docs/Architecture-What-Is/)**
- **[Issue Tracker](https://github.com/ApiLogicServer/ApiLogicServer-src/issues)**

---

## Background

The declarative rules paradigm here has 40+ years of production history:

- **Wang Labs PACE** (1980s-90s) — Val Huber co-invented the paradigm with Ron Ross; 6,000+ production deployments on minicomputers and Visual Basic.
- **Versata** (1990s-2010s) — Val Huber as CTO; evolved the engine for J2EE; Fortune 500 customers; $3.4B company (IPO: VSTA).
- **API Logic Server / GenAI-Logic** (2020-present) — Val Huber, architect and lead developer; modern Python/React, open source, combined with GenAI for natural-language logic authoring.

In-depth context, written by Val Huber on Medium:

| Article | Topic |
|---------|-------|
| **[Welcome to GenAI-Logic](https://medium.com/@valjhuber/welcome-to-genai-logic-a610ba14bd72)** | Vision and overview — start here |
| **[Declarative GenAI Architecture](https://medium.com/@valjhuber/declarative-genai-the-architecture-behind-enterprise-vibe-automation-1b8a4fe4fbd7)** | NL → DSL → Engines, the FrankenCode problem, FAQ |
| **[Declarative Logic: Living in a Procedural World](https://medium.com/@valjhuber/declarative-logic-living-in-a-procedural-world-6c5b20552c6b)** | How declarative rules work inside Python |
| **[Living With Logic in the Enterprise](https://medium.com/@valjhuber/living-with-logic-7e202782d0c5)** | Debugging, testing, performance, real deployments |
| **[Business User / IT Collaboration](https://medium.com/@valjhuber/declarative-genai-business-user-it-collaboration-c5547776ff7d)** | Logic as a contract between business and IT |
| **[Vibe an MCP Server](https://medium.com/@valjhuber/vibe-an-mcp-server-declarative-genai-logic-dec16719c004)** | Creating MCP-enabled services |
| **[Probabilistic and Deterministic Logic](https://medium.com/@valjhuber/probabilistic-and-deterministic-logic-9a38f98d24a8)** | AI at runtime + deterministic rules |
| **[Enterprise Vibe Automation](https://medium.com/@valjhuber/enterprise-vibe-automation-b40c8f750a1d)** | Full-stack automation from prompts |

---

## Connect

- **Home:** [genai-logic.com](https://www.genai-logic.com)
- **Discord:** [Join the community](https://discord.gg/fNRTTVFT)
- **Issues:** [GitHub Issues](https://github.com/ApiLogicServer/ApiLogicServer-src/issues)
- **Discussions:** [GitHub Discussions](https://github.com/ApiLogicServer/ApiLogicServer-src/discussions)
- **Docs:** [apilogicserver.github.io/Docs](https://apilogicserver.github.io/Docs/)
- **Blog:** [Medium](https://medium.com/@valjhuber)

---

## Acknowledgments

Built on Flask, SQLAlchemy, SAFRS, React, Material-UI, and Behave — and on the work of Val Huber and Ron Ross in originating the declarative rules paradigm at Wang Labs PACE, carried forward at Versata. Thanks to everyone who's filed issues, sent PRs, and given feedback.

## License

MIT — see [LICENSE](LICENSE).

---

**[⭐ Star this repo](https://github.com/ApiLogicServer/ApiLogicServer-src)** if you find it useful.
