var salesRep = row.EmployeeID;      // object model (row) provides accessors to related objects
if (salesRep !== null) {
    var mail = B2B.sendEmail();     // this is a loadable library
    var config = {
        to:     'Andrew.Fuller@acme.com',   // better, find this from DB
        from:   'sales@acme.com',
        title:  'Congratulations on your new Order',
        text:   'An order was placed for you, totaling ' + row.AmountTotal
    };
    mail.configure(config);
    var msg = mail.send();
    logicContext.logDebug('Sending Mail - msg: ' + msg);
}
