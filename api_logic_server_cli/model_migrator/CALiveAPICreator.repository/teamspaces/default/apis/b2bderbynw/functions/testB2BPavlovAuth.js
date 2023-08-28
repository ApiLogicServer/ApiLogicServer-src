// Tests row security filter, per AuthToken.  Returns get response; checks for 1 row else throws error.

var supplierInfoURL = req.localFullBaseURL + "SupplierInfo";
var getSettings = { headers: { Authorization: "CALiveAPICreator pavlovAuth:1" }};  // created on Auth Tokens screen
var getParams = {sysfilter: "greater(SupplierID:0)"};
log.debug("B2BTest - get SupplierInfo...");

var getResponseString = SysUtility.restGet(supplierInfoURL, getParams, getSettings);
var getResponse = JSON.parse(getResponseString);
var rowCount = 0;
// log.debug(theUpdates);
for (var eachRowNum = 0; eachRowNum < getResponse.length; eachRowNum++) {
    var eachRow = getResponse[eachRowNum];
    rowCount ++;
    // eachUpdateRow.@metadata is bad JavaScript syntax
    var metaData = eachRow['@metadata'];
    var rowType = metaData.resource;
    if (rowType == 'SupplierInfo') {
        log.debug(eachRow);
    }
}
if (rowCount !== 1) {
    log.debug("throwing: should have retrieved 1 row, got: " + rowCount + ", getResponse: " + getResponse);
    throw new Error("should have retrieved 1 row, got: " + rowCount + ", getResponse: " + getResponse);
}
log.debug(" ");
return getResponse;
