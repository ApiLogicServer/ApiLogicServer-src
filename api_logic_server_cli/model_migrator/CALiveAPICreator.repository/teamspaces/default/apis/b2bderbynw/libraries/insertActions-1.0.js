var insertActions = {};  // a common JavaScript technique to name-scope shared functions


// internal routine to fix path expression from jsonPath (another library)

var fixPathObject = function fixPathObject(path,jsonObj) {
    var index = path;//'[\'Items\'][0][\'Product\']';
    var res = index.split("]");
    res.splice(res.length-1,1);
    var target = jsonObj;
    for (var i = 0; i < res.length; i++) {
        var replacement = res[i].replace("[","").replace("'","").replace("'","");
        target = target[replacement];
    }
    return target;
};


// internal routine to create metadata tag

var getMetadataTag = function getMetadataTag(anAction) {
    var result = null;
    if (anAction === "LOOKUP") {
        result = { "action": "LOOKUP" };
    }
    else if (anAction === "MERGE_INSERT") {
        result = { "action": "MERGE_INSERT" };
    }
    else {
        throw "insertAction tag must be LOOKUP or MERGE_INSERT";
    }
    return result;
};


// internal routine to insert the tag (iff it does not already exist)

var insertActionTag = function insertActionTag(aTarget, aTag) {
    if (typeof aTarget["@metadata"] !== "undefined") {
        // log.debug(dbTitle + " *** metadata tag already exists, no action taken");
    }
    else {
        aTarget["@metadata"] = getMetadataTag(aTag);
    }
};

function db(aString) {
    log.debug(aString);
    print (aString);
}


/* insert metadata actions tags for resource into json string, (e.g., LOOKUP) iff they don't already exist
   returns json string of altered request
   
   example from B2B:  PartnerOrder has res.extendedProperties: {
  "InsertActions": [
    {
      "path": "$..Product",
      "insertActions": "LOOKUP"
    },
    {
      "path": "Shipper",
      "insertActions": "LOOKUP"
    }
  ]
}
    json = insertActions.insertActions(req, json, actions);  // API Server processes this...
*/

insertActions.insertActionsForResource = function insertActionsForResource(json, actions) {
    var dbTitle = "insertActions.InsertActionsForResource: ";
    // db(dbTitle + "running with actions: " + JSON.stringify(actions) + ", json -->\n" + json);
    if (json === null) {
        return json;
    }
    var jsonObj = null; // hold off on parse, until we are sure this resource is relevant

    // for (let eachAction of actions) { -- syntax not supported
    for each (var eachAction in actions) {
        if (jsonObj === null) {
            jsonObj = JSON.parse(json);
        }
        if (eachAction.path === "") {
            insertActionTag(jsonObj, eachAction.insertActions);  // root
        }
        else {
            var paths = jsonPath(jsonObj, eachAction.path, {resultType:"PATH"});
            for each (var eachPath in paths) {       // perform insertion for eachPath
                var target = fixPathObject(eachPath.substring(1), jsonObj);
                insertActionTag(target, eachAction.insertActions);
            }
        }
    }

    if (jsonObj === null) {
        return json;
    }
    else {
        return JSON.stringify(jsonObj);
    }
};


// insert metadata action tags into json string, (e.g., LOOKUP) iff they don't already exist
// actions array is {resource-name, path-for-insert, "INSERT" || "MERGE_INSERT"}
// returns json string of altered request
// example from B2B:
//    var actions = [
//      {resource: "PartnerOrder", path: "$..Product", insertActions: "LOOKUP"},
//      {resource: "PartnerOrder", path: "Shipper",    insertActions: "LOOKUP"}
//    ];
//    json = insertActions.insertActions(req, json, actions);  // API Server processes this...

insertActions.insertActions = function insertActions(req, json, actions) {
    var dbTitle = "InsertActions: ";
    if (json === null) {
        db(dbTitle + "null request object - no action");
        return json;
    }
    var jsonObj = null; // hold off on parse, until we are sure this resource is relevant

    // for (let eachAction of actions) { -- syntax not supported
    for each (var eachAction in actions) {
        if (req.resourceName === eachAction.resource) {
            if (jsonObj === null) {
                jsonObj = JSON.parse(json);
            }
            if (eachAction.path === "") {
                insertActionTag(jsonObj, eachAction.insertActions);  // root
            }
            else {
                var paths = jsonPath(jsonObj, eachAction.path, {resultType:"PATH"});
                log.debug(dbTitle + "paths: " + paths);  // ==>  [ $['Items'][0]['Product'] ...]
                for each (var eachPath in paths) {       // perform insertion for eachPath
                    var target = fixPathObject(eachPath.substring(1), jsonObj);
                    insertActionTag(target, eachAction.insertActions);
                }
            }
        }
    }

    if (jsonObj === null) {
        db(dbTitle + "no change");
        return json;
    }
    else {
        db(dbTitle + "transformed to: " + JSON.stringify(jsonObj));
        return JSON.stringify(jsonObj);
    }
};
