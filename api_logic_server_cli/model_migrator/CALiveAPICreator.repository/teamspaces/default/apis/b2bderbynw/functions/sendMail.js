var mail = B2B.sendEmail();     // this is a loadable library
log.debug("sendMail function, with args: " + parameters.title);
var config = {
    to:     row.FirstName + "." + row.LastName + '@acme.com',   // better, find this from DB
    from:   'system@acme.com',
    title:  parameters.title,
    text:   'This email is sent to: ' + row.fullName
};
mail.configure(config);
var msg = mail.send();
log.debug('Sending Mail - msg: ' + msg);
return {result: msg};
