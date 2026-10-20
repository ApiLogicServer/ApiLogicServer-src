Feature: B2B Order Integration
  # Traceability: api/api_discovery/order_b2b_api.py  (Req §2)
  #   POST /api/OrderB2B maps Account -> Customer by name, Items.Name -> Product by name,
  #   Items.QuantityOrdered -> Item.quantity; Check Credit rules then apply to the new rows.

  Scenario: Partner Order Is Accepted And Rules Derive The Totals
    Given Customer "Acme" with balance 0 and credit limit 1000
    When B2B order is posted for "Acme" with 2 Widget and 1 Gadget
    Then B2B order is accepted
    Then Order has 2 items
    Then Order amount_total is 330
    Then Customer balance is 330

  Scenario: Partner Order For An Unknown Customer Is Rejected
    Given Customer "Beta" with balance 0 and credit limit 1000
    When B2B order is posted for unknown customer with 1 Widget
    Then B2B order is rejected with status 404
    Then Customer balance is 0

  Scenario: Partner Order Exceeding Credit Limit Is Rejected
    Given Customer "Gamma" with balance 0 and credit limit 100
    When B2B order is posted for "Gamma" with 2 Widget
    Then B2B order is not accepted
    Then Customer balance is 0
