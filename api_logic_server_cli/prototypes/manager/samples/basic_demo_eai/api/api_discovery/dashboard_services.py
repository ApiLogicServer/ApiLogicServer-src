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

import safrs
from flask import request, jsonify
from jinja2 import Environment, FileSystemLoader

from database import models

app_logger = logging.getLogger("api_logic_server_app")

WINDOW_DAYS = 30   # the 30 days before today, plus today


def _window_days() -> list:
    """Dashboard: the calendar window, oldest first, as 'YYYY-MM-DD' strings (today and the 30 days before it)."""
    today = datetime.date.today()
    return [(today - datetime.timedelta(days=n)).isoformat() for n in range(WINDOW_DAYS, -1, -1)]


def _daily_totals() -> tuple:
    """Dashboard: reads DailyFlow (maintained by the rules) for the window; a day with no bucket is all zeros."""
    days = _window_days()
    rows = safrs.DB.session.query(models.DailyFlow).filter(models.DailyFlow.day >= days[0], models.DailyFlow.day <= days[-1]).all()
    by_day = {each.day: each for each in rows}
    columns = ["order_count", "order_amount", "message_processed", "message_rejected", "message_pending",
               "request_processed", "request_rejected", "request_pending"]
    totals = {col: [float(getattr(by_day[d], col) or 0) if d in by_day else 0 for d in days] for col in columns}
    labels = [d[5:] for d in days]   # MM-DD
    return labels, totals


def order_volume_query() -> dict:
    """Dashboard chart: orders per day (count, bars) and their total amount (line), zero-filled."""
    try:
        labels, t = _daily_totals()
        return {"title": f"Orders per day - last {WINDOW_DAYS} days", "labels": labels, "stacked": False,
                "y_title": "orders", "y2_title": "amount",
                "datasets": [
                    {"label": "Orders", "data": t["order_count"], "color": "rgba(54, 162, 235, 0.7)"},
                    {"label": "Order amount", "data": t["order_amount"], "type": "line", "yAxisID": "y2",
                     "color": "rgba(255, 159, 64, 1)"}]}
    except Exception as e:
        app_logger.error(f"order_volume chart failed: {e}", exc_info=True)
        return {"error": "chart unavailable - see logs/als.log"}


def message_flow_query() -> dict:
    """Dashboard chart: order_b2b messages and B2B requests per day, stacked as processed / rejected / not yet done."""
    try:
        labels, t = _daily_totals()
        green, red, grey = "rgba(75, 192, 120, 0.8)", "rgba(230, 80, 80, 0.8)", "rgba(160, 160, 160, 0.8)"
        return {"title": "Kafka messages (left) and B2B requests (right) per day", "labels": labels, "stacked": True,
                "y_title": "received",
                "datasets": [
                    {"label": "Messages processed", "data": t["message_processed"], "stack": "messages", "color": green},
                    {"label": "Messages rejected", "data": t["message_rejected"], "stack": "messages", "color": red},
                    {"label": "Messages not yet done", "data": t["message_pending"], "stack": "messages", "color": grey},
                    {"label": "Requests processed", "data": t["request_processed"], "stack": "requests", "color": "rgba(40, 140, 90, 0.8)"},
                    {"label": "Requests rejected", "data": t["request_rejected"], "stack": "requests", "color": "rgba(170, 40, 40, 0.8)"},
                    {"label": "Requests not yet done", "data": t["request_pending"], "stack": "requests", "color": "rgba(110, 110, 110, 0.8)"}]}
    except Exception as e:
        app_logger.error(f"message_flow chart failed: {e}", exc_info=True)
        return {"error": "chart unavailable - see logs/als.log"}


CHARTS = {'order_volume': order_volume_query, 'message_flow': message_flow_query}


def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators=[]):
    """API service dashboard: /dashboard (the iframes on the Admin App home page) and /chart_graphics/<name>."""

    @app.route('/dashboard', methods=['GET'])
    def dashboard():
        """API service dashboard: two order-flow charts side by side, each in its own iframe."""
        server = request.host_url
        iframes = ''.join(
            f'<div class="dashboard-iframe" style="flex: 1;"><iframe src="{server}chart_graphics/{name}" '
            f'style="border: none; width: 100%; height: 300px;"></iframe></div>' for name in CHARTS)
        return f'<div style="display: flex; flex-direction: row; gap: 10px; border: none;">{iframes}</div>'

    @app.route('/chart_graphics/<path:path>', methods=['GET'])
    def chart_graphics(path):
        """API service dashboard: renders one chart as HTML - on EVERY request (never cached), so data is current."""
        if path not in CHARTS:
            return jsonify({"result": "not found"}), 404
        template = Environment(loader=FileSystemLoader('ui/templates')).get_template('multi_series_chart.jinja')
        return template.render(result=CHARTS[path]())
