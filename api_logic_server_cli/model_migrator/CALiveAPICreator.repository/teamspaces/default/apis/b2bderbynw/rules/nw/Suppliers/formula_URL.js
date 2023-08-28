var localBase = req.localBaseUrl;  // e.g., http://localhost:8080/rest/default/b2bAuth/
var serverUrl = localBase.substring(0, localBase.indexOf("/rest/default"));
print ("Derive URL for WebHook posting - URL:" + serverUrl + "/rest/default/b2bderbypavlov/v1/SalesReports");
return serverUrl + "/rest/default/b2bderbypavlov/v1/SalesReports";
