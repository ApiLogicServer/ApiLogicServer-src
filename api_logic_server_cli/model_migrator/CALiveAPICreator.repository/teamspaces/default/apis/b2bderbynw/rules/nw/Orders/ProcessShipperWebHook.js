var shipper = row.Shippers;   // object model (row) provides accessors to related objects
if (shipper !== null) {                 // resource defines transform: cols, aliases, related objects
   var transform = logicContext.transformCurrentRow("ShipperAPIDef");   // find with code completion
   B2B.sendToWebHook(transform, shipper.webHookURL);                    // loadable library (API Properties > Libraries)
}
