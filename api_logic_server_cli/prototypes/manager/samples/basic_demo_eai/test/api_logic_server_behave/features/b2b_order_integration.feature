Feature: B2B Order Integration

  # Custom API OrderB2B: Account -> Customer by name, Items.Name -> Product by name, Items.QuantityOrdered -> Item.quantity

  Scenario: Partner Order Accepted
    Given Customer "Erin" with credit limit 5000
    When Partner order posted via OrderB2B for account "Erin" with 2 Widget and 1 Gadget
    Then OrderB2B reports an Order with 2 items for the customer
    And Items are mapped to Products Widget and Gadget with quantities 2 and 1

  Scenario: Unknown Account Rejected
    When Partner order posted via OrderB2B for unknown account "No Such Customer" with 1 Widget
    Then OrderB2B answers HTTP 400 and no Order is created
