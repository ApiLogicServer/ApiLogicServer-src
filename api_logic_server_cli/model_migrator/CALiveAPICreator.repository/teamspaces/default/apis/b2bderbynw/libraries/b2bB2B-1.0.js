var B2B = {};  // a common JavaScript technique to name-scope shared functions
//TODO: employ arrow functions when fully supported by Nashorn

B2B.transformToWebHook = function transformToWebHook(aLogicContext, aResourceName, aTargetUrl) {
    aLogicContext.logDebug("*** B2B.transformToWebHook *** using: " + aResourceName + ", to: " + aTargetUrl);
    var resourceURL = aTargetUrl; // "http://localhost:8080/rest/default/b2bderbypavlov/v1/SalesReports";

    // custom resource provides name mapping
    // readiness lab: uncomment this  =====>
    // aLogicContext.logDebug("getting aLogicContext.getTableDefinition()");
    var metaTable = aLogicContext.getTableDefinition();
    aLogicContext.logDebug("*** transformToWebHook ***  metaTable: " + metaTable);
    var options = {sysfilter: "equal(OrderID:" + aLogicContext.getCurrentState().OrderID + ")"
            ,"sysfilter..SupplierAlert.Order_DetailsList.Product.Supplier": "equal(CompanyName: '" + "Pavlova, Ltd." + "')" };
    var resourceGetResponse = SysUtility.getResource(aResourceName, options);  // FIXME

    // system console output
    aLogicContext.logDebug("B2B.transformToWebHook posting getResponse: " + JSON.stringify(resourceGetResponse).substring(1, 20) + "...");
    aLogicContext.logDebug("B2B.transformToWebHook to URL: " + resourceURL);

    if (resourceURL === null || resourceURL === "") {
        out = java.lang.System.out;
        out.println("WebHook URL is null/empty - this not posted:\n" + (JSON.stringify(resourceGetResponse)).substring(1, 4) + "...");
    }
    else {
        var settings = { headers: { Authorization: "CALiveAPICreator supplier:1" }};  // FIXME
        var postResponse = SysUtility.restPost(resourceURL, null, settings, resourceGetResponse);

        // API Creator log output
        // log.debug('ok, using re-usable solution');
        if (JSON.parse(postResponse).statusCode !== 201) {
            throw "B2B.transformToWebHook unexpected post response: " + postResponse;
        }
    }

    return null;
};


B2B.sendToWebHook = function sendToWebHook(aPostRequest, aTargetUrl) {
    resourceURL = aTargetUrl;
    var tryIt = true;
    if (tryIt === true) {
        if (resourceURL === null || resourceURL === "") {
            out = java.lang.System.out;
            out.println("WebHook URL is null/empty - this not posted:\n" + (JSON.stringify(aPostRequest)).substring(1, 20) + "...");
        }
        else {
            var settings = { headers: { Authorization: "CALiveAPICreator supplier:1" }};  // FIXME
            var postResponse = SysUtility.restPost(resourceURL, null, settings, aPostRequest);

            // API Creator log output
            // log.debug('ok, using re-usable solution');
            if (JSON.parse(postResponse).statusCode !== 201) {
                throw "B2B.sendToWebHook unexpected post response: " + postResponse;
            }
        }
    }
    return null;
};


// you can save state in logicContext.userProperties, including complex objects such as Maps

B2B.putPropertyMap = function putPropertyMap(logicContext, propertyName, key, value) {
    var RestRequest = Java.type('com.kahuna.server.rest.RestRequest');
    var req = RestRequest.getCurrentRestRequest();
    logicContext.logDebug("*** B2B.putPropertyMap - propertyName: " + propertyName + ", key: " + key + ", value: " + value + ", on req: " + req);
    var property = req.getUserProperties().get(propertyName);   // userProperties to maintain state in transaction
    if (property === null) {
        property = new java.util.HashMap();
    }
    property.put(key, value);
    req.setUserProperty(propertyName, property);
};


//approach for global (static) properties (dynamic properties can be saved in req.getUserProperties().get)
//(alternative: store them in a 1 row table, edit with Data Explorer, accessors here)

B2B.supplierURL = function supplierURL(req) {
    var resultURL = req.localFullBaseURL.replace("nw","pavlov");
    out.println("B2B.supplierURL returns: " + resultURL);
    return resultURL;
};


//returns a sample order, for testing

B2B.sampleOrder = function sampleOrder() {
    var newPartnerOrderJson =
    {
        "CustomerNumber": "VINET",
        "Items": [
            {
            "Product": {
                "ProductName": "Pavlova"
            },
            "Quantity": 1
            }, {
                "Product": {
                    "ProductName": "Uncle Bob's Organic Dried Pears"
                },
                "Quantity": 2
            }, {
                "Product": {
                    "ProductName": "Tofu"
                },
                "Quantity": 3
            }, {
                "Product": {
                    "ProductName": "Ikura"
                },
                "Quantity": 4
            }, {
                "Product": {
                    "ProductName": "Konbu"
                },
                "Quantity": 5
            }, {
                "Product": {
                    "ProductName": "Alice Mutton"
                },
                "Quantity": 1
            }
        ],
        "Shipper": {
            "CompanyName": "Federal Shipping"
        }
    };

    return newPartnerOrderJson;
};


// send email

B2B.sendEmail = function sendEmail() {
    var result = {};
    var msg = "error";
    var configSetup = {
        to: "to",
        from: "from",
        title: "title",
        text: "text"
    };

    result.configure = function configure(myconfig) {
        configSetup.to = myconfig.to || "to";
        configSetup.from = myconfig.from || "from";
        configSetup.title = myconfig.title || "title";
        configSetup.text = myconfig.text || "text";
    };

    result.send = function send() {
        try {
            // call my mail interface here
            msg = "Send email (stub) title: " + configSetup.title + " to: " + configSetup.to + ", from: " + configSetup.from + " body text: " + configSetup.text;
        }
        catch (e) {
            return e;
        }
        out.println("B2B.sendMail returns: " + msg);
        return msg;
    };

    return result;
}


// minor debug helper, to prevent NPE in logging anObject.toString
// where anObject is null

B2B.db = function db(anObject) {
    var result = "null";
    if (anObject !== null) {
        result = anObject.toString();
    }
    return result;
};


// copies like-named attributes from logicContext's row -> targetRow,
// ignoring attributes part of pKey

B2B.copyAttributes = function copyAttributes(logicContext, targetRow) {

    sourceRow = logicContext.getCurrentState();

    var sourceMetaEntity = sourceRow.getMetaEntity();
    var targetMetaEntity = targetRow.getMetaEntity();

    logicContext.touch(targetRow);
    var debugMoved = [];

    for each (var eachProp in sourceMetaEntity.getProperties()) {
      if ( eachProp.isAttribute() ) {
        var targetMetaProp = targetMetaEntity.getPropertyByName(eachProp.name);
        // NB: cannot use hasOwnProperty (Java obj, not JS)
        if (null !== targetMetaProp) {
            if (targetMetaProp.isInPrimaryKey() === true) {
                // logicContext.logDebug("copyAttributes -  skipping eachProp since in pKey: " + eachProp.name);
            }
            else {
                var propValue = sourceRow[eachProp.name];
                targetRow[eachProp.name] = propValue;
                debugMoved.push(eachProp.name);
            }
        }
        else {
            // logicContext.logDebug("copyAttributes - skipping eachProp since not in target: " + eachProp.name);
        }
      }
    }
    logicContext.logDebug("copyAttributes - moved: [" + debugMoved + "]");
    logicContext.update(targetRow);
};
