var title = "Request Event [Insert_Lookup_Merge] - ";  // see resources PartnerOrder, SupplierSelfService
var extProps = null;
try {
    extProps = SysUtility.getExtendedPropertiesFor(req.resourceName);
} catch(e) {
    // occurs for non-resources, etc
}
    if (extProps && 'object' === typeof extProps && ! Array.isArray(extProps) && extProps.hasOwnProperty('InsertActions') ) {
    if (req.verb.toString() == 'POST' || req.verb.toString() == 'PUT' ) {
        var insertActionsArray = [];
        if ( Array.isArray(extProps.InsertActions))  // support one node, or array of nodes
            insertActionsArray = extProps.InsertActions;
        else
            insertActionsArray.put(extProps.InsertActions);
        json = insertActions.insertActionsForResource(json, insertActionsArray);
        print(title + req.resourceName + " is tag-inserted; from insertActions: " + JSON.stringify(insertActionsArray) +
                "\n  > inserted payload: " + json);
    }
} else {
    // print(title + req.resourceName + " **not** tag-inserted from props, res.extProps: " + res.extProps);
}
