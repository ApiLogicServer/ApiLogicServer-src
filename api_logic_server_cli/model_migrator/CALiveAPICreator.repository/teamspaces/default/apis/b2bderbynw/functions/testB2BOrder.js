// Tests logic for placing order.  Returns order post response, or throws error.

var newPartnerOrderJson = B2B.sampleOrder();
var partnerOrderURL = req.localFullBaseURL + "PartnerOrder";
var postSettings = { headers: { Authorization: "CALiveAPICreator partnerAuth:1" }};  // created on Auth Tokens screen
var postParams = null;
log.debug("B2BTest - posting...");

var postResponseString = SysUtility.restPost(partnerOrderURL, postParams, postSettings, newPartnerOrderJson);
var postResponse = JSON.parse(postResponseString);
log.debug(".. request completed with statusCode: " + postResponse.statusCode);
var orderNumber = 0;
if (postResponse.statusCode !== 201) {
    log.debug("ERROR: Post txSummary did not find expected 201...");
    log.debug(postResponse); //an object which will include a transaction summary and a summary of the rules fired during this request
    throw new Error("ERROR: Post txSummary did not find expected 201...");
}
var txSummary = postResponse.txsummary;
// log.debug(theUpdates);
for (var eachRowNum = 0; eachRowNum < txSummary.length; eachRowNum++) {
    var eachUpdatedRow = txSummary[eachRowNum];
    // eachUpdateRow.@metadata is bad JavaScript syntax
    var metaData = eachUpdatedRow['@metadata'];
    var rowType = metaData.resource;
    if (rowType == 'PartnerOrder') {
        orderNumber = eachUpdatedRow.OrderNumber;
        log.debug('....OrderNumber: ' + orderNumber);
        // log.debug(eachUpdatedRow);
    }
}
if (orderNumber === 0) {
    throw new Error("response did not include an order");
}
log.debug(" ");
return postResponse;
