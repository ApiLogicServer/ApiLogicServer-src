var dbPrefix = "testMERGE_INSERT - ";
var requestJson =
{
    CompanyName: "New Supplier",
    ContactName: "New Contact"
};


// Tests MERGE_INSERT, creates / alters New Supplier, or throws error.

function post(aRequestJSON) {
    var supplierSelfServiceURL = req.localFullBaseURL + "SupplierSelfService";
    var postSettings = { headers: { Authorization: "CALiveAPICreator partnerAuth:1" }};  // created on Auth Tokens screen
    var postParams = null;
    log.debug(dbPrefix + "posting to: " + supplierSelfServiceURL);

    var postResponseString = SysUtility.restPut(supplierSelfServiceURL, postParams, postSettings, aRequestJSON);
    var postResponse = JSON.parse(postResponseString);
    log.debug(dbPrefix + "request completed with statusCode: " + postResponse.statusCode);
    var orderNumber = 0;
    if (postResponse.statusCode > 201) {
        log.debug("ERROR: Post txSummary did not find expected 200 or 201...");
        log.debug(dbPrefix + postResponse); //an object which will include a transaction summary and a summary of the rules fired during this request
        throw new Error("ERROR: Post txSummary did not find expected 200 or 201...");
    }
    return postResponse;
}


var postResponse = post(requestJson);
log.debug(dbPrefix + "created");

requestJson.ContactName = "New Contact **";
postResponse = post(requestJson);  // due to MERGE_INSERT (see Request Event), this should update existing row
var txSummary = postResponse.txsummary;
log.debug(dbPrefix + "updated");

var verifyURL = req.localFullBaseURL + "SupplierSelfService";
var getSettings = { headers: { Authorization: "CALiveAPICreator partnerAuth:1" }};  // created on Auth Tokens screen
var getParams = {sysfilter: "equal(CompanyName:'New Supplier')"};
log.debug(dbPrefix + "get SupplierSelfService - verify only 1...");

var getResponseString = SysUtility.restGet(verifyURL, getParams, getSettings);
log.debug(dbPrefix + "getResponseString = " + getResponseString);
var getResponse = JSON.parse(getResponseString);
var rowCount = 0;
for (var eachRowNum = 0; eachRowNum < getResponse.length; eachRowNum++) {
    var eachRow = getResponse[eachRowNum];
    rowCount ++;
    // eachUpdateRow.@metadata is bad JavaScript syntax, so use bracket syntax
    var metaData = eachRow['@metadata'];
    var rowType = metaData.resource;
    if (rowType == 'SupplierInfo') {
        log.debug(eachRow);
    }
}
if (rowCount !== 1) {
    throw new Error("should have retrieved 1 row, got: " + rowCount);
}
log.debug(" ");
return getResponse;
