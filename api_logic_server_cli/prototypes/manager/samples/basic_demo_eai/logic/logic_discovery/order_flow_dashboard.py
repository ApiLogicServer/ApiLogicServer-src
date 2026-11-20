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
created: 2026-11-19T19:02:00
created_by: claude-opus-5-5 (valjhuber@gmail.com)
"""

from logic_bank.logic_bank import Rule
from database import models


def declare_logic():
    """Daily totals for the Order Flow Dashboard, keyed by CreatedOnDay (set by the stamping handler,
    logic/logic_discovery/system/all_classes_stamping.py). The first row of a day creates its DailyFlow bucket.

    TODO retention: never purge the Order, OrderB2bMessage or OrderB2bRequest rows these totals count -
         a delete adjusts the counts, so history would vanish. To limit size, clear old payloads but keep the rows."""

    # Orders (count and total amount) - rejected orders roll back, so they are never counted here
    Rule.count(derive=models.DailyFlow.order_count, as_count_of=models.Order, insert_parent=True)
    Rule.sum(derive=models.DailyFlow.order_amount, as_sum_of=models.Order.amount_total, insert_parent=True)

    # order_b2b messages (Kafka): received, processed, rejected, not yet done
    Rule.count(derive=models.DailyFlow.message_received, as_count_of=models.OrderB2bMessage, insert_parent=True)
    Rule.count(derive=models.DailyFlow.message_processed, as_count_of=models.OrderB2bMessage, where=lambda row: row.is_processed == True, insert_parent=True)
    Rule.count(derive=models.DailyFlow.message_rejected, as_count_of=models.OrderB2bMessage, where=lambda row: row.error_text is not None, insert_parent=True)
    Rule.formula(derive=models.DailyFlow.message_pending, as_expression=lambda row: (row.message_received or 0) - (row.message_processed or 0) - (row.message_rejected or 0))

    # B2B requests (OrderB2B API): received, processed, rejected, not yet done
    Rule.count(derive=models.DailyFlow.request_received, as_count_of=models.OrderB2bRequest, insert_parent=True)
    Rule.count(derive=models.DailyFlow.request_processed, as_count_of=models.OrderB2bRequest, where=lambda row: row.is_processed == True, insert_parent=True)
    Rule.count(derive=models.DailyFlow.request_rejected, as_count_of=models.OrderB2bRequest, where=lambda row: row.error_text is not None, insert_parent=True)
    Rule.formula(derive=models.DailyFlow.request_pending, as_expression=lambda row: (row.request_received or 0) - (row.request_processed or 0) - (row.request_rejected or 0))
