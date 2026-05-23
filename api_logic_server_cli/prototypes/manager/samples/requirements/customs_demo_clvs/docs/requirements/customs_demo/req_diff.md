# Requirements Diff: requirements_w.md vs requirements.md

**Generated:** 2026-05-22  
**Source A:** `demo_customs_clvs_2_W/docs/requirements/customs_demo/requirements_w.md`  
**Source B:** `samples/requirements/customs_demo_clvs/docs/requirements/customs_demo/requirements.md`

## Result: Files are identical

No differences found. Both files contain the same 4-step prompt sequence:

| Step | Description |
|---|---|
| Step 1 | Subscribe to Kafka topic `isdc`, parse CIMCorp XML, persist shipments with replace-on-duplicate policy |
| Step 2 | Importer matching — look up Customer by `trprt_bill_to_acct_nbr`, create ShipmentParty row |
| Step 3 | CLVS Eligibility — BDD scenario for shipment eligibility evaluation |
| Step 4 | Live Kafka end-to-end test with consumer group configuration |

## Note

`requirements_w.md` (the `_w` variant) is the starting-point requirements file for the `demo_customs_clvs_2_W` workspace project. It matches `requirements.md` in the samples folder exactly — both represent the same canonical requirements for this demonstration.

The `_W` suffix on the workspace project indicates it is a "workshop" or "work-in-progress" variant, not a requirements difference.
