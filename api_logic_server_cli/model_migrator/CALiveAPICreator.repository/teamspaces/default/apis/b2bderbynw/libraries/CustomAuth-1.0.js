// Custom authentication provider, uploaded in B2B install script.
// Authenticates using RESTful service, configured to be employees table in Northwind-B2B.

// At its core, an Authorization Provider is a JavaScript function that returns an object (see end) containing these 4 functions:
//   getConfigInfo: function() {...},  configure: function(values) {...}, getLoginInfo: function() {...}, authenticate:


out = java.lang.System.out;

function create() {

    var result = {};
    var configSetup = {
        logonApiKey : '',
        loginBaseURL : '',
        loginGroupURL : '',
        keyLifetimeMinutes : 60
    };


    // This function is called by API Creator when the user enters a value
    // for the parameters specified by getConfigInfo and clicks Save.
    // Returns configuration values which API Creator will save into Admin DB;
    // these are exported in the json config file
    result.configure = function configure(myConfig) {
        configSetup.logonApiKey = myConfig.logonApiKey || 'demo_full';  // supply, or default
        configSetup.loginBaseURL = myConfig.loginBaseURL || 'http://localhost:8080/rest/default/v1/...';
        configSetup.loginGroupURL = myConfig.loginGroupURL || 'http://localhost:8080/rest/default/v1/...';
        configSetup.keyLifetimeMinutes = myConfig.keyLifetimeMinutes || 60;
    };


    // Main crux of Auth Provider - called by API Server on post to @authenticate, to return list of Roles
    // NOTE: the function configure must be called first - this will validate the user/pw

    // The argument passed in will contain whatever values were provided to the @authentication service.
    // If the caller is well-behaved, this should correspond to the parameters described by getLoginInfo,
    // but you should not depend on that.

    // This function must return an object containing just an error message if the authentication failed.
    // If the authentication succeeded, then it must return an object with the following properties:
    result.authenticate = function authenticate(payload) {

        out.println("Authentication called...");

        var roles = [];
        var errorMsg = null;
        var resetPasswordURL = null;
        var forgotPasswordURL = null;
        var myUserData = [];
        var params = null;
        var settings = {
            headers : {
                'Authorization' : 'CALiveAPICreator ' + configSetup.logonApiKey + ':1'
            }
        };

        try {
            if (payload.username == 'admin' || payload.username == 'demo') {
                out.println("Authentication - default admin/demo/ user - good to go..");
                // out.println("Lab test OK...");  // uncomment this for Readiness Lab
                roles = ['Full access']; // || HARD CODED FOR DEMO (we even ignore the pwd)
                errorMsg = null; // authorized successfully
            }
            else if (payload.username == 'pavlov' ||  payload.username == 'Pavlov') {
                out.println("Authentication - Pavlov - role is Supplier, with Global ID===7");
                roles = ['Supplier']; // Permission's Row Filter uses the following Global
                myUserData = {ID: '7', AnotherParm: 'like this'};  //  reference like this: "SupplierID" = @{ID}
                errorMsg = null; // authorized successfully
            }
            else {
                // GET this JSON request to determine if username and password is valid
                // if so, return an array of role names (here just 'Full Access')
                // and, to simplify typing in demos, will allow the default Password1
                var pwd = payload.password;
                if (payload.username == "Janet" && payload.password == "Password1") {
                    pwd = "Leverling";
                }
                var loginAttemptURL = configSetup.loginBaseURL
                    + "?sysfilter=equal(FirstName:'"+ payload.username
                    + "')&sysfilter=equal(LastName:'" + pwd
                    + "')";
                out.println("Authentication - finding [" + payload.username + "." + pwd + "]");
                out.println("... via Rest URL: " + loginAttemptURL);
                out.println("... using settings: " + JSON.stringify(settings));
                var loginAttempt = SysUtility.restGet(loginAttemptURL, params, settings);
                var groups = JSON.parse(loginAttempt);
                // out.println(JSON.stringify(groups, null, 2));

                if (groups.hasOwnProperty('errorMessage')) {
                    out.println("...errorMessage found in loginAttempt: " + loginAttempt);
                    errorMsg = groups.errorMessage;
                }
                else {
                    // change the field name below .name to the name of your
                    // roleName column
                    errorMsg = 'Username ' + payload.username + ' not found with last name as password';
                    for ( var row in groups) {
                        roles = ['Full access']; // || HARD CODED FOR DEMO
                        // roles.push(groups[row].Region);
                        // myUserData.push(groups[row].Region)
                        errorMsg = null; // if one role is found then we are good to return
                    }
                }
                if (errorMsg != null) {
                    out.println("...get failed to find this user, loginAttempt: " + loginAttempt);
                }
            }
        }
        catch (e) {
            errorMsg = e.message;
        }

        var autResponse = {
            errorMessage : errorMsg,
            roleNames : roles,
            userIdentifier : payload.username,
            keyExpiration : new Date(+new Date()
                    + (+configSetup.keyLifetimeMinutes) * 60 * 1000),
            userData : myUserData,
            lastLogin : {
                datetime : null,
                ipAddress : null
            }
        };
        return autResponse;
    };


    // FUNCTION getAllGroups is used to map all available groups for existing application -
    // unused in this example, provided for illustration purposes only...
    result.getAllGroups = function getAllGroups() {
        var roles = [];
        var errorMsg = null;
        var params = null;
        var settings = {
            headers : {
                'Authorization' : 'CALiveAPICreator ' + configSetup.logonApiKey + ':1'
            }
        };

        try {
            var loginAttemptURL = configSetup.loginGroupURL; // no filter needed- get all roles?
            var groupsResponse = SysUtility.restGet(loginAttemptURL, params,
                    settings);
            var groups = JSON.parse(groupsResponse);
            if (groups.hasOwnProperty('errorMessage')) {
                errorMsg = groups.errorMessage;
            }
            else {
                // change the .name to refrelect the name of your roles returned
                // in the JSON object
                for ( var row in groups) {
                    roles.push(groups[row].name);
                }
            }
        }
        catch (e) {
            errorMsg = e.message;
        }

        var autResponse = {
            errorMessage : errorMsg,
            roleNames : roles
        };

        return autResponse;
    };


    // FUNCTION getLoginInfo is used to create the login dialog - DO NOT CHANGE
    // This function is called by API Server when a client needs to know what kind of information is required for authentication.
    // Basically, this describes what the login dialog should look like (assuming the client is an interactive application).
    result.getLoginInfo = function getLoginInfo() {
        return {
            fields : [
                    {
                        name : "username",
                        display : "Username",
                        description : "Enter your First Name",
                        type : "text",
                        length : 40,
                        helpURL : "http://liveapicreator.ca.com"
                    },
                    {
                        name : "password",
                        display : "Password",
                        description : "Enter your Last Name as Password",
                        type : "password",
                        length : 40,
                        helpURL : "http://liveapicreator.ca.com/"
                    } ],
            links : [

            ]
        };
    };

    result.getConfigInfo = function getConfigInfo() {
        return {
            current : {
                "keyLifetimeMinutes" : configSetup.keyLifetimeMinutes,
                "logonApiKey" :        configSetup.logonApiKey,
                "loginBaseURL" :       configSetup.loginBaseURL,
                "loginGroupURL" :      configSetup.loginGroupURL
            },
            fields : [ {
                name : "logonApiKey",
                display : "logonApiKey",
                type : "text",
                length : 60,
                helpURL : ""
            }, {
                name : "loginBaseURL",
                display : "loginBaseURL",
                type : "text",
                length : 120,
                helpURL : ""
            }, {
                name : "loginGroupURL",
                display : "loginGroupURL",
                type : "text",
                length : 120,
                helpURL : ""
            }, {
                name : "keyLifetimeMinutes",
                display : "API Key Lifetime (Minutes)",
                type : "number",
                length : 8,
                helpURL : "http://www.liveapicreator.ca.com"
            } ],
            links : []
        };
    };

    // returns object containing the 4 functions that define a Custom Authentication Provider:
    //   getConfigInfo: function() {...},  configure: function(values) {...}, getLoginInfo: function() {...}, authenticate:

    return result;  // returns the 4 func
}
