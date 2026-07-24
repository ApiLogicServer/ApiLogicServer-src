Feature: Charge Distribution Rules

  Scenario: Charge Posted - cascades to dept and GL allocations
    Given a funding setup with Roads 60% / Construction 40%
    And Roads splits to Labor 60% / Equipment 40%
    And Construction splits to Labor 70% / Materials 30%
    When a Charge of 100000 is posted to the Project
    Then Charge total_distributed_amount is 100000
    And ChargeDeptAllocation amounts are 60000 and 40000
    And ChargeGlAllocation amounts for Roads are 36000 and 24000
    And ChargeGlAllocation amounts for Construction are 28000 and 12000

  Scenario: Charge total_distributed_amount rollup - sums dept allocations
    Given a funding setup with Roads 60% / Construction 40%
    And Roads splits to Labor 60% / Equipment 40%
    And Construction splits to Labor 70% / Materials 30%
    When a Charge of 50000 is posted to the Project
    Then Charge total_distributed_amount is 50000

  Scenario: Project total_charges rollup - sums charges for the project
    Given a funding setup with Roads 60% / Construction 40%
    And Roads splits to Labor 60% / Equipment 40%
    And Construction splits to Labor 70% / Materials 30%
    When a Charge of 30000 is posted to the Project
    And a second Charge of 20000 is posted to the same Project
    Then Project total_charges is 50000

  Scenario: GlAccount total_allocated rollup - sums GL allocations
    Given a funding setup with Roads 60% / Construction 40%
    And Roads splits to Labor 60% / Equipment 40%
    And Construction splits to Labor 70% / Materials 30%
    When a Charge of 100000 is posted to the Project
    Then Roads Labor GlAccount total_allocated is 36000
    And Roads Equipment GlAccount total_allocated is 24000

  Scenario: Charge Rejected - project funding definition not active
    Given a funding setup with Roads 60% / Construction 40% missing a line
    When a Charge of 10000 is posted to the Project
    Then Charge is rejected with inactive funding error

  Scenario: Allocation percent frozen at charge time - not retroactively changed
    Given a funding setup with Roads 60% / Construction 40%
    And Roads splits to Labor 60% / Equipment 40%
    And Construction splits to Labor 70% / Materials 30%
    When a Charge of 100000 is posted to the Project
    And the Roads funding line percent is later changed to 90
    Then the existing ChargeDeptAllocation percent for Roads is still 60
