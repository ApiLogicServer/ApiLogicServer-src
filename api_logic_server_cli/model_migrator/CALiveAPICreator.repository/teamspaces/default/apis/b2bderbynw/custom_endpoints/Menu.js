var html = "<!DOCTYPE html>\n";
html += "<html>";
html += "<body>";
html += "<title>B2B Menu</title>";
html += "<p>Illustrates you can build simple html pages - no deploy";
html += "<p>.. See Custom Endpoints (disable Short Menus)";
html += "<h1>B2B Documentation</h1>";
html += "<a href='https://docops.ca.com/ca-live-api-creator/5-0/en/tutorials-and-samples/b2b-api-sample' target='_blank'>Docs</a>";
html += "<h1>B2B Execution</h1>";
html += "<a href='http://localhost:8080/DataExplorer/index.html#/?serverName=http:%2F%2Flocalhost:8080%2Frest%2Fdefault%2Fb2bderbynw%2Fv1%2F&forceLogin=true'  target='_blank'>Run Data Explorer</a>";
html += "</body>";
html += "</html>";

responseHeaders.put('Content-Type', 'text/html');
return html;
