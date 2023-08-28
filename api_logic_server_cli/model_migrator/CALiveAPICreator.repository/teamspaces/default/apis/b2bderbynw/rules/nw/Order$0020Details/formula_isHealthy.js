// logicContext.logDebug("computing isHealthy");
if (! row.Products)
    return false;
if (row.Products.CategoryID > 6 ) { // fruit or fish
    return true;
} else {
    return false;
}
