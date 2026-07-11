---
title: Queries and Dashboards
version: 1.3 (Jul 2026) — CORRECTED Part 2 step 2: /chart_graphics/<name> must render through ui/templates/bar_chart.jinja (Chart.js), not jsonify() the raw query result — real bug found live, route returned 200 with correct data but Admin App showed raw JSON instead of a chart
usage: AI reads this when user asks for a dashboard, chart, graph, or a saved/reusable query
overhead: zero until invoked — file is read on demand only
---

# Queries and Dashboards

Two related but distinct capabilities, both built on plain SQLAlchemy + a custom API
endpoint — no special framework support, no separate CLI pipeline. This file replaces the
old `genai-logic genai-graphics` command (ChatGPT/PE pipeline) — same output shape for
dashboards, produced through the normal custom-API-endpoint workflow instead.

## ACTIVATION TRIGGERS

- "add a dashboard" / "create a dashboard"
- "graph <X> by <Y>" / "chart <X>" / "show <X> by <Y>"
- "add a query for..." / "I need a report of..."
- "how would I create a dashboard/query" / "how does this work"
- Any similar request or question about aggregated/grouped data, a chart, or a saved query

---

## STEP 0 — figure out what's actually being asked, before writing anything

**A. Is this a how-to question, or a concrete request?**
- "How would I create a dashboard?" / "how does this work?" → **explain, don't code.**
  Give the 2-option summary below (query vs. dashboard), then a CONCRETE EXAMPLE — do not
  describe the example only in the abstract ("which table/columns?"):
    1. Check `database/models.py` for a plausible aggregate (a parent with a child that has
       a numeric/FK column — e.g. Category→Product→OrderDetail, or Customer→Order) and show
       the actual query for THIS project's schema, OR
    2. If no obvious candidate or models.py is large/unclear, use the Northwind
       Category/Product/Order example below verbatim — every reader recognizes
       customers/orders/products, so it communicates the shape without needing their schema.
  Then ask which one they want (query vs. dashboard) and whether to use their own table/columns
  instead of the example. Do not generate files yet.
- "Graph sales by category" / "add a query for X by Y" → concrete enough to build. Proceed
  to STEP 1, but confirm the query-vs-dashboard choice first if it's not stated (see below).

**B. Query alone, or full dashboard?** These are genuinely different asks — check which one
before writing code:

| They want... | Build | Where it's used |
|---|---|---|
| Data for a Vibe/React app, or any custom UI | **Query only** (Part 1) | Fetched by your own frontend code — `fetch('/api/sales_by_category')` — not tied to the Admin App at all |
| A chart visible in the generated Admin App | **Query + Dashboard wiring** (Part 1 + Part 2) | Embedded as an iframe on the Admin App home page |

If they just say "graph X by Y" with no mention of the Admin App or a custom app, ask:
*"Do you want this as data for your own app (Vibe/React), or as a chart embedded in the
Admin App?"* — the code for the query itself is identical either way; only Part 2 (Admin
App wiring) differs.

---

## Quick example (both flavors, same query)

Say the ask is "graph number of orders by category."

**Query only** (add to `api/api_discovery/`, use from Vibe/React via `fetch`):
```python
@app.route('/api/orders_by_category', methods=['GET'])
def orders_by_category():
    session = safrs.DB.session
    query = (session.query(models.Category.CategoryName, func.count(models.Order.Id).label("OrderCount"))
             .join(models.Product, models.Category.Id == models.Product.CategoryId)
             .join(models.OrderDetail, models.Product.Id == models.OrderDetail.ProductId)
             .join(models.Order, models.OrderDetail.OrderId == models.Order.Id)
             .group_by(models.Category.CategoryName))
    results = [{"category": row[0], "order_count": row[1]} for row in query.all()]
    return jsonify(results)
```
Done — that's the whole deliverable. A Vibe/React app calls `GET /api/orders_by_category`
and renders it however it likes; no Admin App involvement at all.

**Full dashboard** (same query, now also visible in the Admin App): do the above, **plus**
the `/dashboard` route and the `home.js` iframe edit — see Part 2 below. Three pieces, not
one — this is the part people expect to be one step and isn't.

**See it live:** `samples/nw_sample` (or `nw_sample_nocust`) has a working dashboard already
wired end-to-end — open `api/api_discovery/dashboard_services.py` and `ui/admin/home.js`
there to see real, running code for both pieces before writing your own.

---

## Part 1 — Queries (grouped/aggregate data, no chart)

A query is just a custom read endpoint: a SQLAlchemy `session.query(...)` with joins,
`func.sum`/`func.count`, `group_by`, `order_by`, wrapped as a JSON-returning function in
`api/api_discovery/`. Nothing here is graphics-specific — this is the same pattern as any
other custom API endpoint (see the project CE's "Custom API Endpoints" service), just
oriented toward aggregation instead of CRUD.

Register it via the normal `api/api_discovery/*.py` auto-discovery mechanism — do not
hand-wire it elsewhere.

If the query result also needs to be *reusable from Python* (e.g. referenced by a rule or
another endpoint, not just exposed as JSON), define it as a classmethod on the relevant
model class in `database/database_discovery/` instead — same query body, called directly
rather than over HTTP.

**This is the entire deliverable if the answer to STEP 0.B was "query only."** Do not
proceed to Part 2 unless a dashboard/Admin-App chart was actually requested.

---

## Part 2 — Dashboards (charts embedded in the Admin App)

**This is the part that's easy to get wrong** — the query and chart-data endpoint are
straightforward, but wiring the result into the Admin App is a manual step with no
generator support, and it's the step that actually caused trouble in practice (confirmed
live, Jul 2026 — the chart/query side was fine, the Admin App integration was not).

### The three pieces, in order

**1. The query** — same as Part 1: a `session.query(...)` returning grouped/aggregated
rows. Shape the result as:
```python
{
    "results": [{"Category Name": "Beverages", "Total Sales": 12345.67}, ...],
    "columns": ["Category Name", "Total Sales"],
    "title": "Sales by Category",
    "chart_type": "bar",        # or "line", "pie", etc — whatever the charting lib supports
    "xAxis": "Category Name",
    "yAxis": "Total Sales",
}
```

**2. The `/dashboard` and `/chart_graphics/<name>` routes** — add to
`api/api_discovery/dashboard_services.py` (create if it doesn't exist):

🚨 **`/chart_graphics/<name>` must return RENDERED HTML, not the raw JSON from step 1.**
Every project already has `ui/templates/bar_chart.jinja` (Chart.js, reads exactly the
`chart_type`/`title`/`columns`/`results` shape from step 1) — render through it. Returning
`jsonify(query_result)` from this route is the single most common mistake: the route
"works" (200 OK, correct data) but the Admin App iframe shows a raw JSON dump instead of a
chart, because nothing ever turned the data into HTML/Chart.js.

```python
from jinja2 import Environment, FileSystemLoader

dashboard_result = {}  # cache — module level, outside add_service()

def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators=[]):

    @app.route('/dashboard', methods=['GET'])
    def dashboard():
        server = request.host_url
        iframe = (f'<div class="dashboard-iframe"><iframe '
                  f'src="{server}chart_graphics/sales_by_category" '
                  f'style="flex: 1; border: none; width: 90%; height: 200px;"></iframe></div>')
        return f'<div style="display: flex; flex-direction: row; gap: 10px; border: none;">{iframe}</div>'

    def get_dashboards():
        if len(dashboard_result) > 0:
            return dashboard_result
        env = Environment(loader=FileSystemLoader('ui/templates'))
        template = env.get_template('bar_chart.jinja')
        result = sales_by_category_query()  # your query function(s) from step 1
        color = 'rgba(75, 192, 192, 0.2)'
        dashboard_result['sales_by_category'] = template.render(result=result, color=color)
        return dashboard_result

    @app.route('/chart_graphics/<path:path>', methods=['GET'])
    def chart_graphics(path):
        dashboards = get_dashboards()
        if path in dashboards:
            return dashboards[path]   # already-rendered HTML string — NOT jsonify()
        return jsonify({"result": "not found"}), 404
```

Wrap each chart's query in try/except — one bad query should degrade to an error message
in its own iframe, not break the whole dashboard:
```python
def sales_by_category_query():
    try:
        ...  # the query from Part 1
        return json_results
    except Exception as e:
        app_logger.error(f"sales_by_category query failed: {e}")
        return {"error": "chart unavailable"}
```

**3. 🚨 Manual step — embed the iframe into `ui/admin/home.js`:**

Nothing generates this automatically, and a freshly-created project's `home.js` has no
dashboard hook by default — you must add it. Find the `getContent()` function (or the
`sla_doc`/welcome-content string it returns) and append the iframe:

```javascript
function getContent(){
    let result = sla_doc;  // existing welcome content
    result += '<iframe id="iframeTargetDashboard" src="http://localhost:5656/dashboard" ' +
              'style="flex: 1; border: none; width: 100%; height: 200px;"></iframe>';
    return result;
}
```

Use the project's actual running port (usually `5656`) — hardcoded, not templated;
`home.js` is plain JS served statically, no build step to inject it at request time.

**Verify:** restart the server, open the Admin App home page — the iframe should load
`/dashboard`, which loads `/chart_graphics/<name>` for each chart, and show an actual
rendered bar chart (not text). Common failures:
- **Iframe shows raw JSON/text, not a chart** → step 2's `/chart_graphics/<name>` is
  returning `jsonify(...)` instead of `template.render(...)` through `bar_chart.jinja`.
  Confirmed live (Jul 2026): query and route both returned `200 OK` with correct data, but
  the page showed a JSON dump because the Jinja render step was skipped entirely.
- **Iframe is blank / 404** → step 3 was skipped (no iframe present in `home.js` at all),
  or the `src` port/host doesn't match the running server. Check browser console for the
  inner request's status.

---

## Why this file exists (context, not required reading for the AI)

Formerly `genai-logic genai-graphics` generated steps 1–2 from a natural-language prompt
file via ChatGPT, but never touched `home.js` — step 3 was always a manual, user-performed
edit, documented only in a single end-user doc page (WebGenAI-CLI.md). An AI assistant
without that doc open reliably gets steps 1–2 right and stalls on step 3. This file exists
so that gap doesn't repeat now that dashboard requests are handled by direct AI
implementation instead of the old CLI pipeline.
