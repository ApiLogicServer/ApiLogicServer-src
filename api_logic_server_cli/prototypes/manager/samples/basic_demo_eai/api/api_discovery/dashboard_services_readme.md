# How the Order Flow Dashboard works

The dashboard on the Admin App home page is requirement §6. The numbers are the easy part: the rules in
`logic/logic_discovery/order_flow_dashboard.py` keep one `DailyFlow` row per day. This file explains how those
numbers get onto the screen. That path has five hops across three files, and none of them says why it is built
this way.

## The five hops

```
Admin App home page
  │  ui/admin/home.js: a fixed HTML snippet with one <iframe src=".../dashboard">
  ▼
GET /dashboard                         api/api_discovery/dashboard_services.py: dashboard()
  │  returns HTML: one <iframe> per chart, side by side
  ▼
GET /chart_graphics/<name>             dashboard_services.py: chart_graphics()
  │  looks up <name> in CHARTS, calls that function
  ▼
order_volume_query() / message_flow_query()
  │  read DailyFlow (via _daily_totals), return a dict shaped for the template
  ▼
ui/templates/multi_series_chart.jinja
     renders a page that loads Chart.js from a CDN and draws the dict
```

## Why each hop exists

| Hop | Why it is there |
|---|---|
| `home.js` → `/dashboard` | The Admin App's home page is one fixed HTML string (`sla_doc` in `home.js`). It cannot run your Python or fetch JSON, but it can hold an `<iframe>`. So the dashboard arrives as a web page served by this project. |
| `/dashboard` → one iframe per chart | `home.js` frames a single URL. Putting the chart list on the server side means adding a chart is a Python change: an entry in `CHARTS`. `home.js` is never touched again. |
| `/chart_graphics/<name>` | One route serves every chart. `<name>` is a key in `CHARTS`; an unknown name returns 404. |
| `*_query()` functions | The data. Each one reads the rule-maintained `DailyFlow` rows and returns a plain dict. They do not compute totals, they only read them. |
| The Jinja template | Chart.js runs in the browser, so the data has to be written into an HTML page. The template does that (`{{ result \| tojson }}`) and maps the dict onto Chart.js options. |

## The dict a chart function returns

The template (`multi_series_chart.jinja`) expects this shape:

```python
{
    "title":    "Orders per day - last 30 days",
    "labels":   ["10-21", "10-22", ...],             # x axis: one per day, oldest first
    "stacked":  False,                                # True: datasets with the same "stack" sit on top of each other
    "y_title":  "orders",                             # optional: left axis title
    "y2_title": "amount",                             # optional: adds a right axis for datasets with yAxisID "y2"
    "datasets": [
        {"label": "Orders", "data": [5, 7, ...], "color": "rgba(54, 162, 235, 0.7)"},
        {"label": "Order amount", "data": [...], "type": "line", "yAxisID": "y2", "color": "..."},
    ],
}
```

`type` defaults to a bar. `stack` groups bars into one column: the messages chart has two stacks per day,
`messages` and `requests`, each split into processed, rejected and not yet done.
A function that fails returns `{"error": "..."}`; the template shows that text in the chart's frame, and the other
chart still renders.

## Details that matter

* **Current data:** `chart_graphics()` renders on every request. Nothing is cached, so opening the home page shows
  the totals as of now (requirement §6: "show current data each time the page is opened").
* **Quiet days show as zero:** `_daily_totals()` builds the full 31-day window and fills a day with no `DailyFlow`
  row with zeros. A day with no row is a day when nothing arrived. Without the fill, the chart would skip the day,
  and the flow stopping would not be visible.
* **No login:** `/dashboard` and `/chart_graphics/*` are plain Flask routes, outside the JSON:API security. Anyone
  who can reach the server can see the charts. Fine for a demo; for production, add an auth check or put them
  behind the same login as the API.
* **Any host:** the iframe in `home.js` is relative (`src="/dashboard"`), so it reaches the server the page came
  from: your machine, a Codespace, a container or a deployed server. The chart iframes that
  `/dashboard` returns are relative too (`/chart_graphics/<name>`). Never hard-code `http://localhost:5656` there: on any other host the browser would
  ask its own localhost, and the frame would be blank.

## Adding a chart

1. Write a function that returns the dict above, for example `def returns_query() -> dict:`, reading rule-maintained
   totals or a query.
2. Add it to `CHARTS`: `CHARTS = {..., 'returns': returns_query}`.
3. Restart the server. `/dashboard` frames it beside the others; `home.js` does not change.

Or ask your AI assistant ("add a chart of ... to the dashboard"). It follows `docs/training/queries_dashboards.md`,
which covers both the totals (rules) and this wiring.
