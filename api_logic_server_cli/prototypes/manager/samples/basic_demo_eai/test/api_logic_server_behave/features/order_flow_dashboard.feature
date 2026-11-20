Feature: Order Flow Dashboard

  # Daily totals (DailyFlow) maintained by rules; checked as changes to today's /order_flow/daily figures.

  Scenario: Order Placed Is Dated Today
    Given Customer "Dana" with credit limit 5000
    When B2B order placed for "Dana" with 1 Widget
    Then the Order is dated today

  Scenario: Order With Its Own Date Keeps It
    Given Customer "Eli" with credit limit 5000
    When an Order dated 2026-01-15 is created for "Eli" through the API
    Then the Order keeps its date 2026-01-15

  Scenario: New Order Counts In Daily Totals
    Given Customer "Fran" with credit limit 5000
    And the daily totals are read
    When B2B order placed for "Fran" with 2 Widget
    Then today's order_count rises by 1 and order_amount by 180

  Scenario: Changed Item Adjusts Daily Amount
    Given Customer "Gale" with credit limit 5000
    And Order is created for "Gale" with 2 Widget
    And the daily totals are read
    When Item quantity changed to 3
    Then today's order_count rises by 0 and order_amount by 90

  Scenario: Deleted Order Leaves Daily Totals
    Given Customer "Hank" with credit limit 5000
    And Order is created for "Hank" with 2 Widget
    And the daily totals are read
    When Order is deleted
    Then today's order_count rises by -1 and order_amount by -180

  Scenario: Order Moved To Another Day
    Given Customer "Ivo" with credit limit 5000
    And Order is created for "Ivo" with 1 Widget
    And the daily totals are read
    When the Order is moved to yesterday
    Then today's order_count rises by -1 and order_amount by -90
    And yesterday's order_count rises by 1

  Scenario: Delivered Message Counts In Daily Totals
    Given Customer "Gil" with credit limit 5000
    And the daily totals are read
    When an inbound order message for "Gil" with 1 Widget and 2 Gadget is delivered to topic order_b2b
    Then today's message_received and message_processed rise by 1
    And today's message_stuck is unchanged

  Scenario: Rejected Message Counts In Daily Totals (live Kafka only)
    Given the daily totals are read
    When an inbound order message for an unknown account is delivered live to topic order_b2b
    Then today's message_received and message_failed rise by 1

  Scenario: Dashboard Shows Current Data
    Given Customer "Hugo" with credit limit 5000
    When B2B order placed for "Hugo" with 1 Widget
    Then the dashboard shows the three charts with today
