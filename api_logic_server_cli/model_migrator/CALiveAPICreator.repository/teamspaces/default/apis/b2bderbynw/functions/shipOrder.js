row.ShippedDate = new Date();  // triggers logic (e.g., balance adjustment)
return [ {"status": "Success"}, {"AmountTotal": row.AmountTotal} ];

/*
This works with the Orders Table (and can also work with Orders Custom Resources):
    http://localhost:8080/rest/default/b2bderbynw/v1/nw:Orders/10643/shipOrder

*/
