# Create 1 or more .feature files here, and corresponding /steps/<feature>.py files
# Run Launch Configuration:
#   - Behave Run - runs your test suite
#   - Behave Logic Report - produces wiki for Behave Run, including Logic

Feature: Maintain Sales Totals

  # Requirement (logic/logic_discovery/place_order/maintain_sales_totals.py):
  #   1. Orders can be assigned to people who are salesreps
  #   2. Maintain monthly sales totals and order counts for each sales rep
  #
  # SalesRepTotal(sales_rep_id, year_month) is a composite-natural-key "bucket" row,
  # auto-created on first reference via Rule.sum/Rule.count(insert_parent=True) - not
  # pre-seeded. year_month is stamped generically (CreatedOnYearMonth, from CreatedOn)
  # by logic/logic_discovery/system/all_classes_stamping.py - not a custom event.
  #
  # See internal_dev/composite_key_issue/composite_key_issue.md (ApiLogicServer-src) for
  # the LogicBank bug these scenarios guard against: insert_parent silently failing to
  # create the parent, and silently nulling the child's own composite-FK columns, when a
  # component of the key is set AFTER row construction (as CreatedOnYearMonth is here).

  Scenario: First Order for a New Sales Rep Creates the Sales Total Bucket
     Given A new Sales Rep with no prior orders
      When An Order is placed for that Sales Rep
      Then A SalesRepTotal bucket is auto-created with order_count 1

  Scenario: Second Order for the Same Sales Rep Adjusts the Bucket
     Given A new Sales Rep with no prior orders
      And An Order is placed for that Sales Rep
      When A second Order is placed for the same Sales Rep
      Then The same SalesRepTotal bucket is adjusted, not recreated, with order_count 2

  Scenario: Order Retains its Sales Rep Assignment
     Given A new Sales Rep with no prior orders
      When An Order is placed for that Sales Rep
      Then The Order's sales_rep_id and CreatedOnYearMonth are not null
