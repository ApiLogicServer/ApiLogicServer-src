var amount = row.Quantity * row.UnitPrice * (100 - row.Discount) / 100;
if (row.Quantity >  200)
    amount = 0.8 * amount;
logicContext.logDebug("amount: " + amount);
return amount;
