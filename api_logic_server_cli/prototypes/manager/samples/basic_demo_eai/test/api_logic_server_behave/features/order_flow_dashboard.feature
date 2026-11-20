Feature: Order Flow Dashboard

  Scenario: A new order is dated today and counted in today's totals
    Given a new customer "Flow Cust" with credit limit 5000
    And today's totals are noted
    When a B2B order is placed for "Flow Cust" with 2 Widget and 1 Gadget
    Then the order is dated today
    And today's order count rose by 1 and order amount by 330

  Scenario: Changing an order's value adjusts today's order amount
    Given a new customer "Flow Change" with credit limit 5000
    And a B2B order is placed for "Flow Change" with 2 Widget and 1 Gadget
    And today's totals are noted
    When the quantity of the first item is changed to 3
    Then today's order count rose by 0 and order amount by 90

  Scenario: Deleting an order removes it from today's totals
    Given a new customer "Flow Delete" with credit limit 5000
    And a B2B order is placed for "Flow Delete" with 1 Gadget
    And today's totals are noted
    When the order is deleted
    Then today's order count rose by -1 and order amount by -150

  Scenario: Moving an order to another day adjusts both days
    Given a new customer "Flow Move" with credit limit 5000
    And a B2B order is placed for "Flow Move" with 1 Gadget
    And today's totals are noted
    And the totals of day "2000-01-01" are noted
    When the order is moved to day "2000-01-01"
    Then today's order count rose by -1 and order amount by -150
    And day "2000-01-01" order count rose by 1 and order amount by 150

  Scenario: Accepted and rejected B2B requests are counted
    Given a new customer "Flow Req" with credit limit 5000
    And today's totals are noted
    When a B2B order is placed for "Flow Req" with 1 Widget
    And a B2B order is placed for "Flow Req" with 1 Sprocket
    Then today's requests rose by 2 received, 1 processed, 1 rejected and 0 not yet done
    And the B2B request is dated today

  Scenario: A request set back to not processed counts as not yet done
    Given a new customer "Flow Req Undo" with credit limit 5000
    And a B2B order is placed for "Flow Req Undo" with 1 Widget
    And today's totals are noted
    When the B2B request is set back to not processed
    Then today's requests rose by 0 received, -1 processed, 0 rejected and 1 not yet done

  Scenario: An accepted message is counted
    Given a new customer "Flow Msg" with credit limit 5000
    And today's totals are noted
    When an order message for "Flow Msg" with 1 Widget and 2 Gadget is delivered to topic order_b2b
    Then the message is processed
    And today's messages rose by 1 received, 1 processed, 0 rejected and 0 not yet done
    And the message is dated today

  Scenario: A message set back to not processed counts as not yet done
    Given a new customer "Flow Msg Undo" with credit limit 5000
    And an order message for "Flow Msg Undo" with 1 Widget and 2 Gadget is delivered to topic order_b2b
    And today's totals are noted
    When the message is set back to not processed
    Then today's messages rose by 0 received, -1 processed, 0 rejected and 1 not yet done

  Scenario: A rejected message is counted (live Kafka only)
    Given a new customer "Flow Msg Bad" with credit limit 5000
    And today's totals are noted
    When an order message for "Flow Msg Bad" with 1 Sprocket is delivered live to topic order_b2b
    Then today's messages rose by 1 received, 0 processed, 1 rejected and 0 not yet done

  Scenario: The chart shows the last 30 days with quiet days as zero
    When the order volume chart is opened
    Then the chart shows 31 days ending today
    And every day with no totals shows zero

  Scenario: The chart shows current data each time it is opened
    Given a new customer "Flow Chart" with credit limit 5000
    And the order volume chart is opened
    When a B2B order is placed for "Flow Chart" with 1 Gadget
    And the order volume chart is opened again
    Then the chart's value for today rose by 1 and matches today's order count
