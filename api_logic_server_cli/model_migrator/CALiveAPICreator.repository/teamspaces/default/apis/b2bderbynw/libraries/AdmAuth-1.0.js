// Custom authentication provider, for admin user authentication (access to API Creator).
// Authenticates hard coded users; in real-life, you might authenticate against LDAP, AD, etc.

// At its core, an Authorization Provider is a JavaScript (create) function
// that returns an object (see end) containing these 4 functions:
//   configure: function(values) {...},
// authenticate(payload) {...},
// getConfigInfo: function() {...},
// getLoginInfo: function() {...}


out = java.lang.System.out;

// register this create function to LAC.
// as above, it returns an object containing the 4 functions noted above.
function create() {

    var result = {};  // returned to LAC, containing the 4 functions noted above
    var configSetup = {
        keyLifetimeMinutes : 60
    };
    var allRoles = ['System administrator', 'Account admin', 'Data admin', 'Data designer'];


    // This function is called by API Creator when the user enters a value
    // for the parameters specified by getConfigInfo and clicks Save.
    // Returns configuration values which API Creator will save into Admin DB;
    // these are exported in the json config file
    result.configure = function configure(myConfig) {
        configSetup.keyLifetimeMinutes = myConfig.keyLifetimeMinutes || 60;
    };


    // Main crux of Auth Provider - called by API Server on post to @authenticate, to return list of Roles
    // NOTE: the function configure must be called first - this will validate the user/pw

    // Eg, you might with to query LDAP, Active Directory etc, to empower corporate users
    // to use Live API Creator to create database.
    // You will also need to compute the proper admin roles explained in the product documentation
    // under Admin Authentication Providers

    // The argument passed in will contain whatever values were provided to the @authentication service.
    // If the caller is well-behaved, this should correspond to the parameters described by getLoginInfo,
    // but you should not depend on that.

    // This function must return an object containing just an error message if the authentication failed.
    // If the authentication succeeded, then it must return an object with the following properties:
    result.authenticate = function authenticate(payload) {

        out.println("Admin Authentication called...");

        var roles = [];
        var errorMsg = "Sorry, you are not authorized";
        var resetPasswordURL = null;
        var forgotPasswordURL = null;
        var myUserData = [];
        var autResponse = errorMsg;

        // these hard-coded users are in lieu of actually doing a query against LDAP, AD etc.
        if (payload.username == 'admin' || payload.username == 'demo' || payload.username == 'sa' || payload.username == 'boris') {
            out.println("Admin Authentication - default admin/demo/sa user - good to go..");
            roles = allRoles; // || HARD CODED FOR DEMO (we even ignore the pwd)
            myUserData = {accountIdent:'1000'};
            if (payload.username == 'demo') {
                myUserData = {accountIdent:'1'};
                out.println("... with SA account visibility..");
            }
            autResponse = {
                errorMessage : null,
                roleNames : roles,
                userIdentifier : payload.username,
                keyExpiration : new Date(+new Date()
                        + (+configSetup.keyLifetimeMinutes) * 60 * 1000),
                userData : myUserData,
                userInfo : myUserData,
                lastLogin : {
                    datetime : null,
                    ipAddress : null
                }
            };
            out.println("Admin Authentication successful - returning.." + JSON.stringify(autResponse));
            return autResponse;
        } else {
            out.println("Admin Authentication FAILED!");
            return {
                errorMessage : errorMsg,
                roleNames : roles,
                userIdentifier : payload.username,
                keyExpiration : new Date(+new Date()
                        + (+configSetup.keyLifetimeMinutes) * 60 * 1000),
                userData : myUserData,
                userInfo : myUserData,
                lastLogin : {
                    datetime : null,
                    ipAddress : null
                }
            };
        }
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
                "keyLifetimeMinutes" : configSetup.keyLifetimeMinutes
            },
            fields : [
                {
                name : "keyLifetimeMinutes",
                display : "API Key Lifetime (Minutes)",
                type : "number",
                length : 8,
                helpURL : "http://www.liveapicreator.ca.com"
            } ],
            links : []
        };
    }

    // returns object containing the 4 functions that define a Custom Authentication Provider:
    //   getConfigInfo: function() {...},  configure: function(values) {...}, getLoginInfo: function() {...}, authenticate:

    // returns the 4 functions
    return result;
}
