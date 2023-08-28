var webHooks = req.getUserProperties().get("order.supplierHooks");   // userProperties to maintain state in transaction
if (webHooks !== null) {
    logicContext.logDebug("*** POST SupplierAlert - WebHook URLs accrued in Order Details ***  from webHooks: " + B2B.db(webHooks));
    for each (var url in webHooks.values()) {

        // B2B.transformToWebHook(LogicContext, "SupplierAlert", url);

        // MUCH CODE follows, more than you'd like to see in a rule
        //    .. and, it's a common pattern -- retrieve a resource, and post to a URL
        // So, we can make it re-usable:
        //    1. Remove all the code from here to ## STOP DELETING
        //    2. Uncomment the B2B.transformToWebHook line, above
        //    3. Locate the code in API Properties > Libraries > Your Libraries > B2BLib > transformToWebHook
        // And (for training), the line above has a bug (LogicContext should be logicContext)
        //    1. Avoid it, by using Code Completion (Control-Space)
        //    2. Diagnose it using the Log and the Debugger
        //

	    var resourceURL = url; // "http://localhost:8080/rest/default/b2bderbypavlov/v1/SalesReports";

        // custom resource provides name mapping
        // logicContext.logDebug("getting aLogicContext.getTableDefinition()");
        var options = {sysfilter: "equal(OrderID:" + logicContext.getCurrentState().OrderID + ")"
                ,"sysfilter..SupplierAlert.OrderDetails_List.Product.Supplier": "equal(CompanyName: '" + "Pavlova, Ltd." + "')" };
        var resourceGetResponse = SysUtility.getResource("SupplierAlert", options);  // FIXME

        // system console output
        logicContext.logDebug(resourceGetResponse.toString());
        //  ??  logicContext.logDebug("Post SupplierAlert posting getResponse: " + JSON.stringify(resourceGetResponse).substring(1, 20) + "...");
        logicContext.logDebug("Post SupplierAlert to URL: " + resourceURL);

        if (resourceURL === null || resourceURL === "") {
            out = java.lang.System.out;
            out.println("WebHook URL is null/empty - this not posted:\n" + (JSON.stringify(resourceGetResponse)).substring(1, 4) + "...");
        } else {
            var settings = { headers: { Authorization: "CALiveAPICreator supplier:1" }};  // FIXME
            var postResponse = SysUtility.restPost(resourceURL, null, settings, resourceGetResponse);

            // API Creator log output
            // log.debug('ok, using re-usable solution');
            if (JSON.parse(postResponse).statusCode !== 201) throw "Post SupplierAlert unexpected post response: " + postResponse;
        }
        // ## STOP DELETING
    }
}
