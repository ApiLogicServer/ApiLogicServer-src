// log.debug("isHealtyCount Check Discount");
// note - cannot call logicContext here; variable does not exist on retrieval
var amt = row.AmountTotal;
if (row.healthyCount > 3) {
    // logicContext.logDebug("isHealtyCount Check Discount -- GIVEN");  // fails on retrieval
    amt = amt * 0.99;
}
return amt;
