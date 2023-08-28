var product = row.Products;    // role accessor
var supplier = product.Suppliers;
print ("DB - Accrue WebHooks for registered Suppliers, product: " + logicContext.rowToJSON(product));
print ("DB - Accrue WebHooks for registered Suppliers, supplier: " + logicContext.rowToJSON(supplier));
if (supplier.URL !== null )
    B2B.putPropertyMap(logicContext, "order.supplierHooks", supplier.CompanyName, supplier.URL);
