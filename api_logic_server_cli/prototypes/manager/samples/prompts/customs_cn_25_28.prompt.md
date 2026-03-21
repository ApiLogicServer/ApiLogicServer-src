As a customs calculation engine
I want to determine when the CN 25‑28 25% surtax applies to imported goods that contain steel melted & poured in China or aluminum smelted & cast in China, and compute the surtax on the value for duty
So that import declarations include accurate CN 25‑28 charges in addition to regular duties/taxes, with correct documentation rules and exemptions enforced.
Feature: CN 25-28 Surtax Calculation (25% on value for duty)
  Background:
    Given the system can read "value for duty" as determined under sections 47–55 of the Customs Act
      # used as the base for CN 25-28 surtax
    And the shipment includes HS classification and documentary data for COM (country of melt & pour) and CSC (country of smelt & cast)
    And the system date reflects the importation date used by CBSA (incl. FPOA logic if required)
 
 # Core applicability
  Scenario: Apply 25% surtax to steel melted and poured in China
    Given the goods are steel covered by Part 1 of the SOR/2025-154 Schedule
    And any portion of the raw steel was first produced in liquid state and poured into its first solid state in China
    When I calculate CN 25-28
    Then I add a surtax of 25% of the value for duty
    And I record reason code "Steel – Chinese melt & pour (CN 25-28)"
    And I retain links to supporting documents
    # Source: CN 25-28; SOR/2025-154 s.2(1), s.3(1) (25% on value for duty)
    # [1](https://www.delmarcargo.com/resource-center/blog/cbsa-issues-steel-goods-and-aluminum-goods-surtax-order)[2](https://sourcealliance.net/cbsa-issues-new-surtax-order-on-steel-and-aluminum-goods-effective-july-31-2025/)
 
  Scenario: Apply 25% surtax to aluminum smelted and cast in China
    Given the goods are aluminum covered by Part 2 of the SOR/2025-154 Schedule
    And either the largest or second-largest volume of primary aluminum was produced in China
      Or the aluminum was most recently liquified and cast into solid state in China
    When I calculate CN 25-28
    Then I add a surtax of 25% of the value for duty
    And I record reason code "Aluminum – Chinese smelt & cast (CN 25-28)"
    # Source: CN 25-28; SOR/2025-154 s.2(2), s.4(1)
    # [1](https://www.delmarcargo.com/resource-center/blog/cbsa-issues-steel-goods-and-aluminum-goods-surtax-order)[2](https://sourcealliance.net/cbsa-issues-new-surtax-order-on-steel-and-aluminum-goods-effective-july-31-2025/)
 
  # Deeming rule if documentation not provided
  Scenario: Deem steel subject to surtax when importer fails to provide proof
    Given the goods are subject steel
    And the importer fails to provide, when requested, acceptable proof that the steel is NOT melted and poured in China
    When I calculate CN 25-28
    Then I deem the steel to contain Chinese melt & pour
    And I apply the 25% surtax on the value for duty
    # Source: Deeming provision for steel (certificate/report/invoice)
    # [1](https://www.delmarcargo.com/resource-center/blog/cbsa-issues-steel-goods-and-aluminum-goods-surtax-order)[2](https://sourcealliance.net/cbsa-issues-new-surtax-order-on-steel-and-aluminum-goods-effective-july-31-2025/)
 
  Scenario: Deem aluminum subject to surtax when importer fails to provide proof
    Given the goods are subject aluminum
    And the importer fails to provide, when requested, acceptable proof that the aluminum is NOT smelted and cast in China
    When I calculate CN 25-28
    Then I deem aluminum to be smelted & cast in China
    And I apply the 25% surtax on the value for duty
    # Source: Deeming provision for aluminum
    # [2](https://sourcealliance.net/cbsa-issues-new-surtax-order-on-steel-and-aluminum-goods-effective-july-31-2025/)
 
  # Documentation timing rule (commercial invoice no longer sufficient after Sept 22, 2025)
  Scenario: Enforce stricter COM/CSC documentation on/after 2025-09-22
    Given the importation date is on or after 2025-09-22
    And the importer submits only a commercial invoice or "report" as proof of COM/CSC
    When I validate proof
    Then I reject it as insufficient for avoiding CN 25-28
    And I require mill test certificates or equivalent technical certificates
    # Source: CN 25-28 update and industry guidance clarifying the 2025-09-22 cutoff
    # [3](https://www.advancedinstaller.com/per-user-per-machine-msi-installation.html)[4](https://taxnews.ey.com/news/2025-1728)
 
  # Exemptions and non-applicability
  Scenario: Exempt U.S.-origin goods
    Given goods originate in the United States per CUSMA marking regulations
    When I evaluate CN 25-28
    Then I do not apply the 25% surtax
    # [1](https://www.delmarcargo.com/resource-center/blog/cbsa-issues-steel-goods-and-aluminum-goods-surtax-order)[4](https://taxnews.ey.com/news/2025-1728)
 
  Scenario: Exempt goods in transit before 2025-07-31 (with proof)
    Given the goods were in transit to Canada before 2025-07-31 and evidence is provided (e.g., bill of lading)
    When I evaluate CN 25-28
    Then I do not apply the 25% surtax
    # [1](https://www.delmarcargo.com/resource-center/blog/cbsa-issues-steel-goods-and-aluminum-goods-surtax-order)[4](https://taxnews.ey.com/news/2025-1728)
 
  Scenario: Exempt CN 25-28 when Chapter 98 applies
    Given the goods are correctly classified under Chapter 98 of the Customs Tariff
    When I evaluate CN 25-28
    Then I do not apply the 25% surtax even if the goods otherwise match Schedule items
    # [4](https://taxnews.ey.com/news/2025-1728)
 
  Scenario: Exempt low-value shipments under CAD 5,000 (per CAD)
    Given the cumulative value for duty of all CN 25-28 goods on a single Commercial Accounting Declaration is ≤ CAD 5,000
    When I evaluate CN 25-28
    Then I do not apply the 25% surtax
    # [5](https://www.thewindowsclub.com/you-do-not-have-sufficient-privileges-to-install-the-program)[6](https://cscb.ca/en/article/updated-customs-notice-25-28-steel-goods-and-aluminum-goods-surtax-order)
 
  # Interactions with other charges
  Scenario: Surtax is in addition to other duties and taxes
    Given the goods are subject to MFN/customs duty, SIMA AD/CVD, and GST/HST
    When I calculate totals
    Then I add CN 25-28 surtax on top of these other amounts (computed on value for duty)
    # [1](https://www.delmarcargo.com/resource-center/blog/cbsa-issues-steel-goods-and-aluminum-goods-surtax-order)[7](https://learn.microsoft.com/en-us/answers/questions/5578070/i-just-set-up-a-new-computer-i-cant-install-softwa)
 
  # HS coverage check
  Scenario: Apply only if HS classification is listed in the SOR/2025-154 Schedule (or Chapter 99 fallback)
    Given the HS code is present in Part 1 (steel) or Part 2 (aluminum) of the Schedule
      Or the goods fall under Chapter 99 but would otherwise fall under those parts
    When I evaluate applicability
    Then I proceed with CN 25-28 calculation as relevant
    Else I do not apply CN 25-28
    # [2](https://sourcealliance.net/cbsa-issues-new-surtax-order-on-steel-and-aluminum-goods-effective-july-31-2025/)[8](https://dl.laplink.com/documentation/pdf/pcmover/pcment/11/pcmover_11_ent_client_ug_eng.pdf)