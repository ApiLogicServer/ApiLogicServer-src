Feature: Check Credit

  Scenario: Good Order - Basic Chain
     Given Test customer with balance 0 and credit 1000
      When New order placed with 1 item (qty 10, product price 5.00)
      Then Customer balance is 50
      Then Constraint passes

  Scenario: Bad Order - Exceeds Credit
     Given Test customer with balance 950 and credit 1000
      When New order placed with 1 item (qty 20, product price 10.00)
      Then Rejected per Check Credit

  Scenario: Alter Item Qty - Chain Up
     Given Test customer with existing order (balance 50)
      When Item quantity changed from 10 to 20
      Then Customer balance is 100
      Then Order amount_total is 100

  Scenario: Change Product on Item
     Given Test customer with order containing product at price 5.00
      When Item product changed to product at price 10.00
      Then Item unit_price updates to 10
      Then Item amount recalculates
      Then Order amount_total updates
      Then Customer balance updates

  Scenario: Change Customer on Order
     Given Test customer A with order (balance 50)
       And Test customer B with balance 0
      When Order moved from customer A to customer B
      Then Customer A balance is 0
      Then Customer B balance is 50

  Scenario: Set Shipped - Where Clause
     Given Test customer with unshipped order (balance 50)
      When Order date_shipped set to today
      Then Customer balance is 0
      Then Kafka message sent

  Scenario: Reset Shipped - Where Clause
     Given Test customer with shipped order (balance 0)
      When Order date_shipped set to None
      Then Customer balance is 50

  Scenario: Delete Item - Aggregates Down
     Given Test customer with order containing 2 items
      When One item is deleted
      Then Order amount_total decreased
      Then Customer balance decreased
