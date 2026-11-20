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

version: 1.0
created: 2026-11-19T17:35:00
created_by: claude-opus-5-5 (valjhuber@gmail.com)
"""
from logic_bank.logic_bank import Rule
from database import models

# TODO (retention): order, order_b2b_message and order_b2b_request rows are never purged. These totals count them,
# so deleting rows would lower the totals (a delete adjusts the counts) and history would vanish from the chart.
# To purge: clear payloads but keep the rows, or freeze closed days (stop deriving a day's totals once it is past,
# keeping them as plain values) - then change this TODO to DONE.


def declare_logic():
    """Order Flow Dashboard: daily totals, one DailyFlow row per day (CreatedOnDay, set by stamping), created by the
    first arrival of the day (insert_parent).  'Rejected' = failed (error_text set); 'not yet done' = stuck."""

    Rule.count(derive=models.DailyFlow.order_count, as_count_of=models.Order, insert_parent=True)
    Rule.sum(derive=models.DailyFlow.order_amount, as_sum_of=models.Order.amount_total, insert_parent=True)

    Rule.count(derive=models.DailyFlow.message_received, as_count_of=models.OrderB2bMessage, insert_parent=True)
    Rule.count(derive=models.DailyFlow.message_processed, as_count_of=models.OrderB2bMessage, where=lambda row: row.is_processed == True, insert_parent=True)
    Rule.count(derive=models.DailyFlow.message_failed, as_count_of=models.OrderB2bMessage, where=lambda row: row.error_text is not None, insert_parent=True)
    Rule.formula(derive=models.DailyFlow.message_stuck, as_expression=lambda row: (row.message_received or 0) - (row.message_processed or 0) - (row.message_failed or 0))

    Rule.count(derive=models.DailyFlow.request_received, as_count_of=models.OrderB2bRequest, insert_parent=True)
    Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True)
    Rule.count(derive=models.DailyFlow.request_failed, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True)
    Rule.formula(derive=models.DailyFlow.request_stuck, as_expression=lambda row: (row.request_received or 0) - (row.request_processed or 0) - (row.request_failed or 0))
