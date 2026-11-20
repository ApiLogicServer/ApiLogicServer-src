"""
Feature: Order Flow Dashboard

  Scenario: Show that orders are flowing
    Given orders arrive through the B2B API and the Kafka topic order_b2b
    When an operator opens the Admin App home page
    Then maintain daily totals of orders (count and total amount), and of order_b2b messages and B2B requests
         (received, processed, rejected, and not yet done)
    And chart the daily totals for the last 30 days, showing a day with no activity as zero
    And date each Order, message and request when it arrives
    And show current data each time the page is opened
"""
import datetime
import logging
from flask import request, jsonify
from jinja2 import Environment, FileSystemLoader
import safrs
from database import models

app_logger = logging.getLogger("api_logic_server_app")

DAYS_SHOWN = 30   # the last 30 calendar days, ending today - a day with no activity shows as zero
FIGURES = ["order_count", "order_amount",
           "message_received", "message_processed", "message_failed", "message_stuck",
           "request_received", "request_processed", "request_failed", "request_stuck"]


def daily_flow() -> dict:
    """API service order flow: the rule-maintained DailyFlow totals for the last DAYS_SHOWN calendar days; a day with
    no DailyFlow row (nothing arrived, so no rule ran) is filled with zeros."""
    today = datetime.date.today()
    days = [(today - datetime.timedelta(days=n)).isoformat() for n in range(DAYS_SHOWN - 1, -1, -1)]
    rows = {r.day: r for r in safrs.DB.session.query(models.DailyFlow).filter(models.DailyFlow.day >= days[0]).all()}
    result = {"days": days}
    for figure in FIGURES:
        result[figure] = [float(getattr(rows[d], figure) or 0) if d in rows else 0 for d in days]
    return result


def _flow_chart(title: str, data: dict, prefix: str) -> dict:
    return {"title": title, "labels": data["days"],
            "series": [{"label": "received", "data": data[f"{prefix}_received"], "color": "rgba(54, 162, 235, 0.6)"},
                       {"label": "processed", "data": data[f"{prefix}_processed"], "color": "rgba(75, 192, 192, 0.6)"},
                       {"label": "rejected", "data": data[f"{prefix}_failed"], "color": "rgba(255, 99, 132, 0.7)"},
                       {"label": "not yet done", "data": data[f"{prefix}_stuck"], "color": "rgba(255, 205, 86, 0.8)"}]}


def _chart_orders() -> dict:
    data = daily_flow()
    return {"title": "Orders per day", "labels": data["days"], "y1_title": "total amount",
            "series": [{"label": "orders", "data": data["order_count"], "color": "rgba(75, 192, 192, 0.6)"},
                       {"label": "total amount", "data": data["order_amount"], "type": "line", "axis": "y1",
                        "color": "rgba(255, 159, 64, 1)"}]}


CHARTS = {"orders_per_day": _chart_orders,
          "messages_per_day": lambda: _flow_chart("order_b2b messages per day", daily_flow(), "message"),
          "requests_per_day": lambda: _flow_chart("B2B requests per day", daily_flow(), "request")}


def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators = []):
    """API service order flow: the daily totals (JSON) and the Admin App home-page dashboard."""

    @app.route('/order_flow/daily', methods=['GET'])
    def order_flow_daily():
        """API service order flow: the daily totals for the last 30 days, as JSON (dashboard, tests, custom UIs)."""
        return jsonify(daily_flow())

    @app.route('/dashboard', methods=['GET'])
    def dashboard():
        """API service order flow: the dashboard iframes, embedded at the top of ui/admin/home.js."""
        server = request.host_url
        frame = ('<div class="dashboard-iframe" style="flex: 1;"><iframe src="{url}" '
                 'style="border: none; width: 100%; height: 230px;"></iframe></div>')
        frames = " ".join(frame.format(url=f"{server}chart_graphics/{name}") for name in CHARTS)
        return f'<div style="display: flex; flex-direction: row; gap: 10px; border: none;">{frames}</div>'

    @app.route('/chart_graphics/<path:path>', methods=['GET'])
    def chart_graphics(path):
        """API service order flow: one chart, rendered on every request (never cached) so it shows current data."""
        if path not in CHARTS:
            return jsonify({"result": "not found"}), 404
        try:
            result = CHARTS[path]()
        except Exception as e:   # one bad chart shows in its own frame, not the whole dashboard
            app_logger.error(f"chart {path} failed: {e}")
            return f"<p>chart {path} unavailable: {e}</p>", 500
        template = Environment(loader=FileSystemLoader('ui/templates')).get_template('multi_series_chart.jinja')
        return template.render(result=result)
