# API Logic Server

[![Downloads](https://pepy.tech/badge/apilogicserver)](https://pepy.tech/project/apilogicserver)
[![Latest Version](https://img.shields.io/pypi/v/apilogicserver.svg)](https://pypi.python.org/pypi/apilogicserver/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/apilogicserver.svg)](https://pypi.python.org/pypi/apilogicserver/)

**Create instant microservices from your database or natural language prompt** - working API + Admin App + Logic in 5 seconds, with 40X code reduction through declarative rules.

Create **instant microservices** (MCP-enabled API + Admin App + Business Logic) from your database or a natural language prompt:

```bash
ApiLogicServer create --project_name=my_app --db_url=mysql://...
```

![API Logic Server Architecture](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/Architecture-What-Is.png)

---

## ⚡ Quick Start (2 minutes)

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

**What you get in 5 seconds:**
- 🚀 **JSON:API** - Endpoints for every table with filtering, pagination, related data
- 📱 **Instant Admin App UI** - Multi-page React app with automatic joins (runs immediately)
- 🎨 **Custom Apps via API** - Use the API with your favorite vibe tools (Cursor, Bolt, Lovable, etc.) OR leverage GenAI-Logic training for Copilot to build custom UIs ([see this article](https://medium.com/@valjhuber/enterprise-vibe-automation-b40c8f750a1d))
- 🧠 **Logic Engine** - Spreadsheet-like rules (40X more concise than code)
- 🔐 **Security** - Row-level authorization, JWT authentication
- 🐳 **Docker-ready** - Pre-configured containers for deployment

**Mix and match:** Use the instant Admin App for backoffice tasks AND build custom UIs with vibe tools for advanced features like cards and maps - all powered by the same logic-enabled API.

**[📖 8-minute video demo](https://www.youtube.com/watch?v=Z4_NJIm5rFs&t=323s)** | **[📚 Full Documentation](https://apilogicserver.github.io/Docs/)** | **[🏠 Home](https://www.genai-logic.com)**

---

## 🎯 Why API Logic Server?

**Built on 40+ years of proven technology** (Wang PACE → Versata → API Logic Server):
- **6,000+ production deployments** validated the declarative approach
- **Fortune 500 companies** relied on this architecture for mission-critical systems
- Now **open source** and **modernized** for cloud-native Python/React stack

### The Problem It Solves

| Traditional Approach | API Logic Server |
|---------------------|------------------|
| Weeks to create API endpoints | **5 seconds** (automated) |
| 200+ lines of update logic code | **5 rules** (40X reduction - to see an A/B Comparision, [click here](https://github.com/ApiLogicServer/basic_demo/blob/main/logic/procedural/declarative-vs-procedural-comparison.md) |
| Manual screen painting | **Automated** from data model, plus vibe-enabled custom UIs |
| Hard to integrate systems | **MCP-enabled** APIs |
| Opaque procedural code | **Declarative** living documentation |

---

## 💡 When to Use API Logic Server

### ✅ Ideal Use Cases

API Logic Server excels at **data-centric business applications** where the complexity is in multi-table calculations, constraints, and derivations:

- **🔌 Application Integration** - Instant APIs for legacy databases (modernization without rewrite)
- **⚡ Rapid Prototyping** - Working backend in minutes for validation
- **🤖 GenAI Backends** - Natural language → working microservice
- **🏢 Backoffice Apps** - Admin dashboards for data maintenance
- **🔗 Microservices** - Decompose monoliths with instant services
- **📊 Business Rule Automation** - Complex calculations, cascading updates, constraint checking
- **🔄 CRUD-Heavy Applications** - Order management, inventory, customer systems
- **🏛️ Legacy Modernization** - MCP-enable existing databases, create modern API layer while legacy apps continue running

**Sweet Spot:** Applications where business logic complexity >> UI complexity

### ⚠️ Not Recommended For

API Logic Server is optimized for data-centric business logic, but **less suited** for:

- **Real-time streaming systems** - Use Kafka/Flink for high-throughput event processing
- **Complex UI/UX interactions** - Works great as the backend, but not a UI framework
- **Machine learning pipelines** - Use TensorFlow/PyTorch for ML workflows
- **Low-level system programming** - Traditional languages better suited
- **Document/content management** - Use specialized CMS platforms
- **Simple static websites** - Overkill for basic content delivery

**For these scenarios, traditional approaches are more appropriate.** API Logic Server can still serve as the backend for hybrid architectures.

---


## ❓ Frequently Asked Questions

**Q: How is this different from low-code platforms (Retool, OutSystems, Hasura)?**

A: Unlike pure low-code platforms, API Logic Server generates **standard Python projects you own, extend and deploy**. Screen creation is by vibe tools rather than screen painting. Unlike API generators, it includes sophisticated multi-table logic automation (40X code reduction). **[Read detailed comparison →](https://medium.com/@valjhuber/declarative-genai-the-architecture-behind-enterprise-vibe-automation-1b8a4fe4fbd7)**

**Q: Isn't this just vendor lock-in?**

A: It's **free and open source**. The declarative rules sit on top of standard (readable, version-controlled) Python — you can always drop down to procedural code. If you ever need to migrate away, you can either keep using the rules engine (it's just a library) or replace declarative rules with equivalent procedural code using standard SQLAlchemy events.

**Q: Can I customize the generated app?**

A: **Absolutely.** You can override the UI, extend APIs, and plug in your own logic — using standard Python, SQLAlchemy, and any Vibe tool. The generated project is a starting point, not a black box. **[See customization patterns →](https://apilogicserver.github.io/Docs/Logic/)**

**Q: What happens when logic doesn't fit the declarative model?**

A: The declarative engine handles **over 95%** of typical business logic (calculations, validations, cascading updates). For complex workflows, state machines, or external integrations, you write standard Python event handlers that coexist with declarative rules. The engine calls your code at the right time — no conflict, full extensibility.

**Q: How long does it take developers to become productive?**

A: Developers can start writing rules immediately using natural language, and the DSL syntax is intuitive. Understanding the engine's optimization strategies (pruning, chaining) takes a few days of practice. **Most teams are fully productive within a week.**

**Q: What if I have questions or need help?**

A: Join our **[Discord community](https://discord.gg/fNRTTVFT)** for real-time help, check **[GitHub Discussions](https://github.com/ApiLogicServer/ApiLogicServer-src/discussions)**, or browse the **[comprehensive documentation](https://apilogicserver.github.io/Docs/)**.

**[→ More FAQs in detailed article](https://medium.com/@valjhuber/declarative-genai-the-architecture-behind-enterprise-vibe-automation-1b8a4fe4fbd7#faqs)**

---
## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│  Natural Language Prompt or Existing DB     │
└───────────────┬─────────────────────────────┘
                │ ApiLogicServer create
                ↓
┌─────────────────────────────────────────────┐
│         Generated Project                    │
├─────────────────────────────────────────────┤
│  📱 Admin App (React)                       │
│  🔌 JSON:API (SAFRS)                        │
│  🧠 Logic (Rules Engine)                    │
│  💾 ORM (SQLAlchemy)                        │
│  🔐 Security (JWT + Row-level)              │
└─────────────────────────────────────────────┘
                │
                ↓
        🐳 Docker Container
```

**Technology Stack:**
- Python 3.10-3.13
- Flask + SQLAlchemy
- React + Material-UI
- Docker + Docker Compose

---

## 📦 What Gets Created

```
my_app/
├── api/                    # JSON:API endpoints (for Admin App AND custom UIs)
│   ├── expose_api_models.py
│   └── customize_api.py    # Add custom endpoints
├── ui/admin/              # Instant Admin App (ready to run)
│   └── admin.yaml         # Declare UI behavior
├── logic/                 # Business Logic (enforced on ALL API calls)
│   └── declare_logic.py   # Spreadsheet-like rules
├── security/              # Authentication & Authorization
│   └── declare_security.py
├── database/              # SQLAlchemy models
│   └── models.py
├── tests/                 # BDD tests (Behave)
├── docs/
│   └── training/          # GenAI-Logic training for Copilot
└── devops/
    └── docker/            # Deployment configs
```

**Two UI approaches (use both!):**
1. **Instant Admin App** - Runs immediately for backoffice/internal users
2. **Custom UIs** - Build with vibe tools (Cursor, Bolt, etc.) OR use GenAI-Logic Copilot training to create React/Vue/Angular apps that consume the API

---

## 🚀 Key Features

### 1️⃣ Declarative Logic (40X More Concise)

**Before (200+ lines of Python):**
```python
# Manual cascade updates, balance calculations, constraint checking...
# Complex dependency tracking, old_row comparisons...
# Missed corner cases: reassign order, change quantity, delete order...
# (Imagine 200 lines of procedural code here)
```

**After (5 declarative rules):**
```python
Rule.constraint(derive=Customer.Balance <= Customer.CreditLimit)
Rule.sum(derive=Customer.Balance, as_sum_of=Order.AmountTotal, 
         where=lambda row: row.ShippedDate is None)
Rule.sum(derive=Order.AmountTotal, as_sum_of=OrderDetail.Amount)
Rule.formula(derive=OrderDetail.Amount, 
             as_expression=lambda row: row.Quantity * row.UnitPrice)
Rule.copy(derive=OrderDetail.UnitPrice, from_parent=Product.UnitPrice)
```

**Rules automatically handle all dependencies:**
- ✅ Chain up (OrderDetail → Order → Customer)
- ✅ Chain down (Product price change cascades)
- ✅ Old row comparisons (moved orders adjust both customers)
- ✅ All 9 use cases (add, update, delete, reassign...)

### 2️⃣ Self-Serve APIs

Consumers select their own attributes and related data - no custom API development required:

```bash
# Get customer with orders and order details
GET /api/Customer/ALFKI?include=OrderList,OrderList.OrderDetailList&fields[Customer]=CompanyName,Balance

# Filter and sort
GET /api/Customer?filter[Balance][$gt]=1000&sort=-Balance&page[size]=10
```

**Features:**
- Filtering, sorting, pagination
- Related data (automatic joins)
- Optimistic locking
- Swagger documentation
- **Logic enforcement** on all updates

### 3️⃣ GenAI Integration

#### Create from Natural Language
```bash
genai-logic genai --using=prompt.txt
```

**Example prompt:**
```
Create a system for customers, orders, items and products.
Customer balance is sum of unshipped order totals.
Order total is sum of item amounts.
Item amount is quantity * unit price.
Copy product price to item unit price.
Constraint: customer balance cannot exceed credit limit.
```

**Result:** Working microservice with logic in 10 seconds!
#### AI-Assisted Development

Every created project includes **AI tutoring** to help you get oriented and productive quickly:

- 🤖 **Copilot instructions** (`.copilot-instructions.md`) - When you open a project, Copilot presents a friendly welcome message explaining what's already built and what you can do next. Ask Copilot to "read instructions" anytime for guidance.
- 📚 **Training materials** (`docs/training/`) - Comprehensive guides for all features
- 🔍 **Logic from natural language** (translate English → rules)

```python
# Paste into Copilot: "Create logic for check credit"
# Copilot generates the 5 rules above!
```
### 4️⃣ Living Documentation

**Automated test generation** from your rules:
```bash
# Generate Behave tests from declared logic
genai-logic add-tests

# Run tests
behave

# Generate documentation
python behave_logic_report.py
```

**Output:** Complete traceability from requirements → tests → rules → execution trace.

---

## 🎬 Video Overview (8 min)

See how **Microservice Automation** creates and runs a microservice - a multi-page app and an API:

[![GenAI Automation](https://raw.githubusercontent.com/ApiLogicServer/Docs/main/docs/images/sample-ai/copilot/genai-automation-video.png)](https://www.youtube.com/watch?v=Z4_NJIm5rFs&t=323s "Microservice Automation")

---

## 🤝 Contributing

We welcome contributions! Areas of interest:

| Area | Current | Ideas for Contribution |
|------|---------|----------------------|
| **API** | JSON:API, Swagger | GraphQL, gRPC support |
| **Deployment** | Docker, Azure | AWS (ECS/Lambda), Kubernetes/Helm charts |
| **Logic** | Rules engine | Additional rule types, performance tuning |
| **UI** | Admin App (React) | Custom UI frameworks, mobile SDK |
| **GenAI** | Web version, CLI | Enhanced natural language understanding |

**[See issues](https://github.com/ApiLogicServer/ApiLogicServer-src/issues)** for current requests.

### Development Setup

For ***development*** (extending API Logic Server itself):

```bash
# Clone and install dev version
git clone https://github.com/ApiLogicServer/ApiLogicServer-src.git
cd ApiLogicServer-src

# Install dependencies
python -m pip install -r requirements.txt

# Run build/test automation
python test/build_and_test.py
```

**[See dev installation docs](https://apilogicserver.github.io/Docs/Architecture-Internals/)** for complete setup.

---

## 📚 Documentation

- **[📖 Full Documentation](https://apilogicserver.github.io/Docs/)** - Comprehensive guides and reference
- **[🚀 Quick Start Tutorial](https://apilogicserver.github.io/Docs/Tutorial/)** - 20-minute walkthrough
- **[🧠 Logic Documentation](https://apilogicserver.github.io/Docs/Logic/)** - Rule types and patterns
- **[🔐 Security Guide](https://apilogicserver.github.io/Docs/Security-Overview/)** - Authentication and authorization
- **[🐳 Deployment](https://apilogicserver.github.io/Docs/DevOps-Containers/)** - Docker, Azure, containers
- **[🔧 Architecture](https://apilogicserver.github.io/Docs/Architecture-What-Is/)** - How it works
- **[❓ FAQs](https://apilogicserver.github.io/Docs/FAQ-Low-Code/)** - Common questions
- **[🐛 Issue Tracker](https://github.com/ApiLogicServer/ApiLogicServer-src/issues)** - Bug reports and feature requests

---

## 📖 Key Documentation Pages

### Getting Started
- **[Express Install](https://apilogicserver.github.io/Docs/Install-Express/)** - Get running in 10 minutes
- **[Manager Workspace](https://apilogicserver.github.io/Docs/Manager/)** - Project organization and readme
- **[Tutorial](https://apilogicserver.github.io/Docs/Tutorial/)** - Complete walkthrough

### Core Concepts
- **[Logic: Why](https://apilogicserver.github.io/Docs/Logic-Why/)** - The case for declarative logic
- **[API Self-Serve](https://apilogicserver.github.io/Docs/API-Self-Serve/)** - Consumer-driven APIs
- **[Behave Testing](https://apilogicserver.github.io/Docs/Behave/)** - BDD test framework integration

### Advanced Topics
- **[Natural Language Logic](https://apilogicserver.github.io/Docs/WebGenAI-CLI/)** - GenAI logic translation
- **[Integration Patterns](https://apilogicserver.github.io/Docs/Sample-Integration/)** - Kafka, B2B, MCP
- **[Database Changes](https://apilogicserver.github.io/Docs/Database-Changes/)** - Schema evolution

---

## 🌟 Examples and Samples

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

## 🏆 Technology Lineage

API Logic Server builds on proven technology with **40+ years** of production validation:

### Wang Labs PACE (1980s-1990s)
- **Inventor:** Val Huber (Designer and Co-inventor with Ron Ross of declarative rules)
- **Scale:** 6,000+ production deployments
- **Innovation:** First commercial declarative business rules system
- **Platform:** Minicomputers → Visual Basic

### Versata (1990s-2010s)
- **Leadership:** Val Huber (CTO)
- **Customers:** Fortune 500 companies
- **Scale:** $3.4 billion company (IPO: VSTA)
- **Innovation:** Evolved rules for J2EE enterprise applications
- **Platform:** Java Enterprise Edition

### API Logic Server (2020-present)
- **Leadership:** Val Huber (Architect and Lead Developer)
- **Innovation:** Modern cloud-native Python/React implementation
- **Platform:** Open source, Docker, microservices architecture
- **Unique:** Combined with GenAI for natural language logic

**The same declarative rules paradigm, proven at scale, now open source and AI-enhanced.**

---

## 📊 Comparison: Frameworks vs Low Code vs API Logic Server

| Aspect | Frameworks<br>(Django, Flask) | Low Code<br>(Retool, Appsmith) | API Logic Server |
|--------|------------------------------|-------------------------------|------------------|
| **API Creation** | Manual (weeks) | Limited/proprietary | ✅ Automated (5 sec) |
| **Logic Automation** | ❌ Manual code | ❌ Limited | ✅ Rules (40X) |
| **App Automation** | ❌ Manual | ✅ GUI builder | ✅ From data model |
| **Customization** | ✅ Full Python | ⚠️ Proprietary | ✅ Python + Rules |
| **IDE** | ✅ Standard tools | ❌ Proprietary | ✅ VSCode, PyCharm |
| **Deployment** | ✅ Any platform | ⚠️ Vendor lock-in | ✅ Docker, any cloud |
| **GenAI Integration** | ❌ None | ⚠️ Limited | ✅ Full (DB + Logic) |
| **Testing** | Manual | Limited | ✅ Auto-generated |

---

## 💾 Supported Databases

- **SQLite** (included samples)
- **PostgreSQL**
- **MySQL / MariaDB**
- **SQL Server**
- **Oracle**
- Any SQLAlchemy-supported database

---

## 🔐 Security Features

- **Authentication:** SQL-based, Keycloak, or custom providers
- **Authorization:** Role-based grants with row-level filtering
- **Multi-tenant:** Global filters based on user attributes
- **JWT Tokens:** Standard authentication flow
- **Swagger Security:** Integrated with API documentation

**[See Security Overview](https://apilogicserver.github.io/Docs/Security-Overview/)**

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

Built on the shoulders of giants:

**Technology Pioneers:**
- **Wang Labs PACE** (1980s) - Original declarative rules concept (Val Huber, designer/co-inventor)
- **Versata** (1990s-2010s) - $3.4B company, Fortune 500 deployments (Val Huber, CTO)
- **Ron Ross** - Co-inventor of declarative rules paradigm

**Open Source Foundation:**
- **Flask** - Web framework
- **SQLAlchemy** - ORM layer
- **SAFRS** - JSON:API implementation
- **React** - Admin App UI
- **Material-UI** - Component library
- **Behave** - BDD testing framework

**Community:**
- All contributors who have submitted issues, PRs, and feedback
- The Python and React ecosystems

---


## 📝 In-Depth Articles

These Medium articles provide comprehensive context on architecture, use cases, and the reasoning behind API Logic Server:

| Article | Topic | Key Insights |
|---------|-------|--------------|
| **[Welcome to GenAI-Logic](https://medium.com/@valjhuber/welcome-to-genai-logic-a610ba14bd72)** | Vision & Overview | Big picture: Does GenAI deliver business agility? Start here for context. |
| **[Declarative GenAI Architecture](https://medium.com/@valjhuber/declarative-genai-the-architecture-behind-enterprise-vibe-automation-1b8a4fe4fbd7)** | Technical Deep Dive | NL → DSL → Engines pattern, FrankenCode problem, **includes FAQ section** |
| **[Declarative Logic: Living in a Procedural World](https://medium.com/@valjhuber/declarative-logic-living-in-a-procedural-world-6c5b20552c6b)** | Architecture Philosophy | How declarative rules work in Python, the paradox resolved |
| **[Living With Logic in the Enterprise](https://medium.com/@valjhuber/living-with-logic-7e202782d0c5)** | Production Patterns | Debugging, testing, performance, customization in real deployments |
| **[Business User / IT Collaboration](https://medium.com/@valjhuber/declarative-genai-business-user-it-collaboration-c5547776ff7d)** | Team Dynamics | How logic acts as a contract between business and IT |
| **[Vibe an MCP Server](https://medium.com/@valjhuber/vibe-an-mcp-server-declarative-genai-logic-dec16719c004)** | MCP Integration | Creating MCP-enabled services with natural language |
| **[Probabilistic and Deterministic Logic](https://medium.com/@valjhuber/probabilistic-and-deterministic-logic-9a38f98d24a8)** | AI + Rules | Engineering reliability into agentic systems (AI at runtime + rules) |
| **[Enterprise Vibe Automation](https://medium.com/@valjhuber/enterprise-vibe-automation-b40c8f750a1d)** | GenAI Workflows | Full-stack automation from prompts |

**These articles represent significant research and real-world experience** - they address common questions, architectural decisions, and lessons learned from 40+ years of declarative technology evolution.

---
## 📞 Connect

- **🏠 Home:** [genai-logic.com](https://www.genai-logic.com)
- **💬 Discord:** [Join our community](https://discord.gg/fNRTTVFT) - Get help and discuss
- **🐛 Issues:** [GitHub Issues](https://github.com/ApiLogicServer/ApiLogicServer-src/issues)
- **� Discussions:** [GitHub Discussions](https://github.com/ApiLogicServer/ApiLogicServer-src/discussions)
- **� Documentation:** [apilogicserver.github.io/Docs](https://apilogicserver.github.io/Docs/)
- **📝 Blog:** [Medium Articles](https://medium.com/@valjhuber) - Conceptual background and insights

### 📖 Recommended Reading

Start with the welcome article to understand the vision and architecture:
- **[Welcome to GenAI Logic](https://medium.com/@valjhuber/welcome-to-genai-logic-a610ba14bd72)** - Introduction and core concepts

---

**[⭐ Star this repo](https://github.com/ApiLogicServer/ApiLogicServer-src)** if you find it useful!

**Made with ❤️ by the API Logic Server team**
