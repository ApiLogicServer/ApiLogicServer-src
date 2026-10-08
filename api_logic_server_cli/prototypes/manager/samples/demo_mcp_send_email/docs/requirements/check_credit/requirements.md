# Check Credit

Verbatim excerpt from `docs/requirements/project_creation_prompt.md` that drove
`logic/logic_discovery/check_credit.py`:

```
Check Credit
    1. The Customer's balance is less than the credit limit
    2. The Customer's balance is the sum of the unshipped Order amount_total
    3. The Order's amount_total is the sum of the Item amount
    4. The Item amount is the quantity * unit_price
    5. The Item unit_price is copied from the Product unit_price
```
