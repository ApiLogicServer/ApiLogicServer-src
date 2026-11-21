---
title: Queries and Dashboards
version: 1.7 (Nov 2026) — home.js and /dashboard iframes use relative URLs (src="/dashboard", src="/chart_graphics/<name>") (was http://localhost:5656/dashboard, which broke on Codespaces, containers and deployed servers). 1.6 (Nov 2026) — per-period totals maintained by rules (insert_parent + stamped day key); quiet days shown as zero; charts no longer cached (the template froze them at server start). 1.5 (Jul 2026) — Added link to published user-facing demo (Admin-Customization#ai-assistant), which documents this exact capability with the same sales-by-region/sales-by-category example this file was tested against
usage: AI reads this when user asks for a dashboard, chart, graph, or a saved/reusable query
overhead: zero until invoked — file is read on demand only
---

# Queries and Dashboards

Two related but distinct capabilities, both built on plain SQLAlchemy + a custom API
endpoint — no special framework support, no separate CLI pipeline. This file replaces the
old `genai-logic genai-graphics` command (ChatGPT/PE pipeline) — same output shape for
dashboards, produced through the normal custom-API-endpoint workflow instead.

**Published user-facing demo:** [Admin-Customization — AI Assistant](https://apilogicserver.github.io/Docs/Admin-Customization/#ai-assistant)
shows this exact capability working end-to-end (prompt: *"create a dashboard with sales by
region, and sales by category"*) — the same use case this file was built and tested against.
Point users here if they want to see it publicly documented, not just described in chat.

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

## Per-period totals: maintain them with rules, then read them

When the ask is a count or sum **per day / month** of something that happens (orders placed, messages received,
requests rejected) — an operations or flow dashboard — do not group-by the transaction tables on every read. Keep a
**totals table** and maintain it with rules, so the figures are governed like any other derived value (they appear
in the logic diagram, the traceability report and the tests) and are adjusted incrementally, never recomputed:

1. **The period key comes from stamping.** Turn on stamping in `logic/logic_discovery/system/all_classes_stamping.py`
   (`enable_stamping := True`); add `CreatedOn` plus `CreatedOnDay` (`'YYYY-MM-DD'`, TEXT) or `CreatedOnYearMonth`
   to the child table. `CreatedOn` is stamped only when empty, so imported / seeded rows keep their own dates. Do not
   write a per-table event to date rows — that duplicates the system handler.
2. **The totals table** (e.g. `daily_flow`, PK `day` TEXT) gets one column per figure; each child carries an FK to it
   on its day key (`CreatedOnDay` → `daily_flow.day`).
3. **The rules**, with `insert_parent=True` so the first row of a day creates its bucket
   (see `logic_bank_api.md`, "insert_parent"):
   ```python
   Rule.count(derive=models.DailyFlow.order_count, as_count_of=models.Order, insert_parent=True)
   Rule.sum(derive=models.DailyFlow.order_amount, as_sum_of=models.Order.amount_total, insert_parent=True)
   Rule.count(derive=models.DailyFlow.failed_count, as_count_of=models.XyzMessage,
              where=lambda row: row.error_text is not None, insert_parent=True)
   Rule.formula(derive=models.DailyFlow.stuck_count,      # arrived, neither done nor failed
                as_expression=lambda row: row.received_count - row.processed_count - row.failed_count)
   ```
   A count over a column that something writes OUTSIDE the governed session is never maintained: check that every
   write the counts depend on goes through `safrs.DB.session` (e.g. `EaiSubscribeMapper.record_error_text` does).
4. **Retention:** never purge the child rows the totals count — a delete adjusts the counts, so history vanishes.
   Put a TODO saying so in the totals logic file (to purge, clear payloads but keep rows, or freeze closed days).
5. **Reading:** the dashboard reads the totals table and **fills a fixed calendar window (e.g. the last 30 days) with
   zeros** for days that have no bucket. No rule can create a row for a day when nothing happened ("Absence of an
   Event", `logic_bank_api.md`): a quiet day must still show as zero, or the chart cannot show the flow stopping.

Use plain group-by queries (Part 1) for ad-hoc analysis — "sales by category" — not for running per-period totals.

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
`chart_type`/`title`/`columns`/`results` shape from step 1) — render through it. It draws ONE series; for several
series in one chart (received / processed / failed), add a multi-series template beside it rather than editing it. Returning
`jsonify(query_result)` from this route is the single most common mistake: the route
"works" (200 OK, correct data) but the Admin App iframe shows a raw JSON dump instead of a
chart, because nothing ever turned the data into HTML/Chart.js.

```python
from jinja2 import Environment, FileSystemLoader

def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators=[]):

    @app.route('/dashboard', methods=['GET'])
    def dashboard():
        # relative src: the chart loads from whatever host the page came from (local, Codespace, deployed, https)
        iframe = (f'<div class="dashboard-iframe"><iframe '
                  f'src="/chart_graphics/sales_by_category" '
                  f'style="flex: 1; border: none; width: 90%; height: 200px;"></iframe></div>')
        return f'<div style="display: flex; flex-direction: row; gap: 10px; border: none;">{iframe}</div>'

    CHARTS = {'sales_by_category': sales_by_category_query}   # your query function(s) from step 1

    @app.route('/chart_graphics/<path:path>', methods=['GET'])
    def chart_graphics(path):
        # Rendered on EVERY request - never cache at module level: a cache freezes the charts at server start, and
        # the dashboard then shows stale data until a restart.
        if path not in CHARTS:
            return jsonify({"result": "not found"}), 404
        template = Environment(loader=FileSystemLoader('ui/templates')).get_template('bar_chart.jinja')
        color = 'rgba(75, 192, 192, 0.2)'
        return template.render(result=CHARTS[path](), color=color)   # rendered HTML - NOT jsonify()
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
dashboard hook by default — you must add it.

**Placement: put the iframe at the TOP, before the welcome content — not appended after.**
This matches `samples/nw_sample/ui/admin/home.js` (the working reference implementation):
the chart is the first thing a user sees, not something they scroll past a page of text to
reach. Edit the `sla_doc` string itself (not `getContent()`) — insert the iframe right after
the opening wrapper `<div>`, before the "Welcome to..." `<h2>`:

```javascript
const sla_doc =
    '<div class="MuiTypography-root jss4" style="color: rgba(0, 0, 0, 0.66)">' +
    '<div style="text-align:center">' +
    '<div class="dashboard-iframe">' +
    '<iframe id="iframeTargetDashboard" src="/dashboard" style="flex: 1; border: none; width: 100%; height: 200px;"></iframe>' +
    '</div>' +
    '<h2>Welcome to Your GenAI-Logic Project</h2>' +
    '</div><br>' +
    // ...rest of existing welcome content unchanged...
    '</div>'

function getContent(){
    let result = "";
    result += sla_doc;
    return result;
}
```

If `home.js` uses a different structure (e.g. `getContent()` builds the string directly
rather than via a `const sla_doc`), insert the iframe as the first element appended, before
any other content — the principle is "chart first," not the specific variable name.

Use a **relative** `src="/dashboard"`, never `http://localhost:5656/dashboard`. The Admin App is served by
the project's own server, so a relative URL reaches whatever host and port the page was opened on. A hard-coded
`localhost:5656` works only on the developer's machine: on a Codespace, in a container or on a deployed server the
browser asks its own localhost, and the chart frame is blank. The same holds for the chart iframes `/dashboard` returns: `src="/chart_graphics/<name>"`, not
`request.host_url`, which behind a proxy (Codespaces) can come out as `http://` on an `https://` page, and the browser
blocks it as mixed content.

**Verify:** restart the server, open the Admin App home page — the iframe should load
`/dashboard`, which loads `/chart_graphics/<name>` for each chart, and show an actual
rendered bar chart (not text). Common failures:
- **Iframe shows raw JSON/text, not a chart** → step 2's `/chart_graphics/<name>` is
  returning `jsonify(...)` instead of `template.render(...)` through `bar_chart.jinja`.
  Confirmed live (Jul 2026): query and route both returned `200 OK` with correct data, but
  the page showed a JSON dump because the Jinja render step was skipped entirely.
- **Iframe is blank / 404** → step 3 was skipped (no iframe present in `home.js` at all),
  or the `src` is an absolute URL (`http://localhost:5656/...`) that does not match the host the page was opened on: use the relative `/dashboard`. Check browser console for the
  inner request's status.

---

## Why this file exists (context, not required reading for the AI)

Formerly `genai-logic genai-graphics` generated steps 1–2 from a natural-language prompt
file via ChatGPT, but never touched `home.js` — step 3 was always a manual, user-performed
edit, documented only in a single end-user doc page (WebGenAI-CLI.md). An AI assistant
without that doc open reliably gets steps 1–2 right and stalls on step 3. This file exists
so that gap doesn't repeat now that dashboard requests are handled by direct AI
implementation instead of the old CLI pipeline.
