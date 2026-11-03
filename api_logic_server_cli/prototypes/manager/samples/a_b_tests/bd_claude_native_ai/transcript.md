
basic_demo_procedural.prompt.md#1-10
Note: this is a test of native AI coding ability — please do not use ApiLogicServer, GenAI-Logic, LogicBank, or any other code-generation or business-rules/rules-engine framework. Just plain hand-written code (standard web framework + ORM of your choice).

Using basic_demo.sqlite, build a system (api + web app) that lets us enter orders.

Here's what needs to happen when someone places an order:

- For each line item on the order, look up the product's price and multiply by the quantity to get the item's amount.
- Add up the item amounts to get the order's total.
- Add the order total to the customer's balance.
- Before we let the order go through, check that the customer's balance doesn't go over their credit limit — if it would, reject the order.
Show more
I'll start by exploring the existing project structure and the SQLite database schema.

Bash List project directory contents
IN
ls -la

OUT
total 72
drwxr-xr-x@ 4 val  staff    128 Sep 17 13:50 .
drwxr-xr-x  9 val  staff    288 Sep 17 13:48 ..
-rw-r--r--@ 1 val  staff  32768 Sep 17 13:48 basic_demo.sqlite
-rw-r--r--@ 1 val  staff    763 Sep 17 13:50 basic_demo_procedural.prompt.md
Bash Show SQLite schema
IN
sqlite3 basic_demo.sqlite ".schema" 2>&1 | head -100

OUT
CREATE TABLE customer (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name VARCHAR, 
        balance DECIMAL, 
        credit_limit DECIMAL, 
        email varchar,
        email_opt_out BOOLEAN
);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE product (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name VARCHAR, 
        count_suppliers INTEGER,
        unit_price DECIMAL
);
CREATE TABLE IF NOT EXISTS "order" (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        notes VARCHAR, 
        customer_id INTEGER NOT NULL, 
        CreatedOn DATE,
        date_shipped DATE, 
        amount_total DECIMAL, 
        FOREIGN KEY(customer_id) REFERENCES customer (id)
);
CREATE TABLE item (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        order_id INTEGER, 
        product_id INTEGER NOT NULL, 
        quantity INTEGER NOT NULL, 
        amount DECIMAL, 
        unit_price DECIMAL, 
        FOREIGN KEY(order_id) REFERENCES "order" (id), 
        FOREIGN KEY(product_id) REFERENCES product (id)
);
CREATE TABLE supplier (
	id INTEGER NOT NULL, 
	name VARCHAR, 
	contact_name VARCHAR, 
	phone VARCHAR, 
	email VARCHAR, region VARCHAR, 
	PRIMARY KEY (id)
);
CREATE TABLE product_supplier (
	id INTEGER NOT NULL, 
	product_id INTEGER, 
	supplier_id INTEGER, 
	supplier_part_number VARCHAR, 
	unit_cost DECIMAL, 
	lead_time_days INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES product (id), 
	FOREIGN KEY(supplier_id) REFERENCES supplier (id)
);
Bash Sample data from key tables and check runtimes
IN
echo "--- customer ---" && sqlite3 basic_demo.sqlite "SELECT * FROM customer LIMIT 5;" && echo "--- product ---" && sqlite3 basic_demo.sqlite "SELECT * FROM product LIMIT 5;" && echo "--- order ---" && sqlite3 basic_demo.sqlite "SELECT * FROM \"order\" LIMIT 5;" && echo "--- item ---" && sqlite3 basic_demo.sqlite "SELECT * FROM item LIMIT 5;" && which python3 node

OUT
--- customer ---
1|Alice|90|5000|alice@corp.org|0
2|Bob|0|3000|bob@corp.org|0
3|Charlie|220|2000|charlie@corp.org|0
4|Diana|0|1000|diana@corp.org|0
5|Silent|220|1000|silent@corp.org|1
--- product ---
1|Gadget|0|150
2|Widget|0|90
3|Thingamajig|0|5075
4|Doodad|0|110
5|Green|0|109
--- order ---
1|First Order|2|2023-02-22|2023-03-22|300
2|Second Order|1|2023-02-22||90
3|Pending Shipment|3|2023-01-22||220
4|Urgent Order|4|2023-02-22|2023-07-15|300
5|Silent Shipment|5|2023-01-22||220
--- item ---
1|1|1|2|300|150
2|2|2|1|90|90
3|3|4|2|220|110
4|4|3|4|300|75
5|5|4|2|220|110
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3
/usr/local/bin/node
Both Python and Node are available. I'll build this with Python (FastAPI + SQLAlchemy) since it pairs well with SQLite and lets me hand-write the business logic clearly, plus a simple server-rendered web UI.

Bash Check if required Python packages are installed
IN
python3 -m pip show fastapi uvicorn sqlalchemy jinja2 2>&1 | grep -E "Name|WARNING|not found" 

OUT
WARNING: Package(s) not found: fastapi, uvicorn
Name: SQLAlchemy
Name: Jinja2
SQLAlchemy and Jinja2 are present but FastAPI/uvicorn aren't. I'll set up a virtual environment to keep things clean and installable.

Bash Create venv and install dependencies
IN
python3 -m venv venv && source venv/bin/activate && pip install --quiet fastapi uvicorn sqlalchemy jinja2 python-multipart 2>&1 | tail -20

OUT
[notice] A new release of pip is available: 25.1.1 -> 26.2.1
[notice] To update, run: pip install --upgrade pip
Installed cleanly. Now let's set up the project structure.

Bash Create app directories
IN
mkdir -p app/templates app/static && sqlite3 basic_demo.sqlite "SELECT COUNT(*) FROM customer; SELECT COUNT(*) FROM product;"

OUT
5
6
Now let's build the SQLAlchemy models.

Write models.py
67 lines
Now the core order-placement logic, kept as plain hand-written code (no rules engine):

Write orders.py
73 lines
Now the FastAPI app with both JSON API endpoints and a server-rendered web UI.

Write main.py
148 lines
Now let's create the templates. First a base layout, then the three pages.

Write base.html
27 lines
Write orders_list.html
25 lines
Write order_detail.html
28 lines
Now the order form, with dynamic add/remove line item rows (plain JS, no framework):

Write order_form.html
57 lines
Now let's fix the DB path issue — the relative path ../basic_demo.sqlite depends on cwd. Let me make it robust using an absolute path based on the file location.

Edit models.py
Added 3 lines
Now let's create a run script and requirements file, then test the app.

Bash Generate requirements.txt
IN
source venv/bin/activate && pip freeze | grep -iE "fastapi|uvicorn|sqlalchemy|jinja2|python-multipart|starlette|pydantic" > requirements.txt && cat requirements.txt

OUT
fastapi==0.141.1
Jinja2==3.1.6
pydantic==2.13.5
pydantic_core==2.46.5
python-multipart==0.0.32
SQLAlchemy==2.0.54
starlette==1.6.0
uvicorn==0.53.0
Let's back up the database before testing, since order placement will mutate it.

Bash Backup the sqlite database
IN
cp basic_demo.sqlite basic_demo.sqlite.bak && ls -la

OUT
total 144
drwxr-xr-x@ 8 val  staff    256 Sep 17 13:55 .
drwxr-xr-x  9 val  staff    288 Sep 17 13:48 ..
drwxr-xr-x@ 7 val  staff    224 Sep 17 13:55 app
-rw-r--r--@ 1 val  staff  32768 Sep 17 13:48 basic_demo.sqlite
-rw-r--r--@ 1 val  staff  32768 Sep 17 13:55 basic_demo.sqlite.bak
-rw-r--r--@ 1 val  staff    763 Sep 17 13:50 basic_demo_procedural.prompt.md
-rw-r--r--@ 1 val  staff    147 Sep 17 13:55 requirements.txt
drwxr-xr-x@ 7 val  staff    224 Sep 17 13:54 venv
Now let's start the server in the background and test it.

Bash Start FastAPI server in background
IN
source venv/bin/activate && uvicorn app.main:app --port 8000 > /tmp/uvicorn.log 2>&1 &
sleep 2 && cat /tmp/uvicorn.log

OUT
INFO:     Started server process [14218]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
Server started fine. Let's test the API endpoints.

Bash Test list customers and products API
IN
curl -s http://127.0.0.1:8000/api/customers && echo && curl -s http://127.0.0.1:8000/api/products && echo

OUT
[{"id":1,"name":"Alice","balance":90.0,"credit_limit":5000.0},{"id":2,"name":"Bob","balance":0.0,"credit_limit":3000.0},{"id":3,"name":"Charlie","balance":220.0,"credit_limit":2000.0},{"id":4,"name":"Diana","balance":0.0,"credit_limit":1000.0},{"id":5,"name":"Silent","balance":220.0,"credit_limit":1000.0}]
[{"id":1,"name":"Gadget","unit_price":150.0},{"id":2,"name":"Widget","unit_price":90.0},{"id":3,"name":"Thingamajig","unit_price":5075.0},{"id":4,"name":"Doodad","unit_price":110.0},{"id":5,"name":"Green","unit_price":109.0},{"id":6,"name":"Egyptian Cotton Sheets","unit_price":200.0}]
Now test placing a valid order (Bob, balance 0, limit 3000 — order 2 Widgets = 180, should succeed):

Bash Test creating a valid order via API
IN
curl -s -X POST http://127.0.0.1:8000/api/orders -H "Content-Type: application/json" -d '{"customer_id": 2, "notes": "Test order", "items": [{"product_id": 2, "quantity": 2}]}' && echo

OUT
{"id":6,"customer_id":2,"amount_total":180.0,"items":[{"product_id":2,"quantity":2,"unit_price":90.0,"amount":180.0}]}
Now test the credit limit rejection (Diana, balance 0, limit 1000 — order Thingamajig at 5075 should be rejected):

Bash Test credit limit rejection and verify balance update
IN
curl -s -X POST http://127.0.0.1:8000/api/orders -H "Content-Type: application/json" -d '{"customer_id": 4, "notes": "Over limit test", "items": [{"product_id": 3, "quantity": 1}]}' && echo
echo "--- verify Bob's balance updated ---"
curl -s http://127.0.0.1:8000/api/customers && echo

OUT
{"detail":"Order rejected: order total 5075.0000000000 would bring Diana's balance to 5075.0000000000, exceeding their credit limit of 1000.0000000000"}
--- verify Bob's balance updated ---
[{"id":1,"name":"Alice","balance":90.0,"credit_limit":5000.0},{"id":2,"name":"Bob","balance":180.0,"credit_limit":3000.0},{"id":3,"name":"Charlie","balance":220.0,"credit_limit":2000.0},{"id":4,"name":"Diana","balance":0.0,"credit_limit":1000.0},{"id":5,"name":"Silent","balance":220.0,"credit_limit":1000.0}]
The rejection correctly rolled back with no partial balance change, and Bob's balance updated properly for the accepted order. Now let's test the web UI in a browser.

Bash Check home page renders
IN
curl -s http://127.0.0.1:8000/ | head -30

OUT
Internal Server Error
Bash Check server error log
IN
tail -30 /tmp/uvicorn.log

OUT
    ^
  File "/Users/val/dev/marketing/SampleApps/bd_claude_native_ai/venv/lib/python3.13/site-packages/anyio/_backends/_asyncio.py", line 2706, in run_sync_in_worker_thread
    return await future
           ^^^^^^^^^^^^
  File "/Users/val/dev/marketing/SampleApps/bd_claude_native_ai/venv/lib/python3.13/site-packages/anyio/_backends/_asyncio.py", line 1100, in run
    result = context.run(func, *args)
  File "/Users/val/dev/marketing/SampleApps/bd_claude_native_ai/app/main.py", line 102, in home
    return templates.TemplateResponse(
           ~~~~~~~~~~~~~~~~~~~~~~~~~~^
        "orders_list.html", {"request": request, "orders": orders}
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/Users/val/dev/marketing/SampleApps/bd_claude_native_ai/venv/lib/python3.13/site-packages/starlette/templating.py", line 148, in TemplateResponse
    template = self.get_template(name)
  File "/Users/val/dev/marketing/SampleApps/bd_claude_native_ai/venv/lib/python3.13/site-packages/starlette/templating.py", line 115, in get_template
    return self.env.get_template(name)
           ~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "/Users/val/dev/marketing/SampleApps/bd_claude_native_ai/venv/lib/python3.13/site-packages/jinja2/environment.py", line 1016, in get_template
    return self._load_template(name, globals)
           ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
  File "/Users/val/dev/marketing/SampleApps/bd_claude_native_ai/venv/lib/python3.13/site-packages/jinja2/environment.py", line 964, in _load_template
    template = self.cache.get(cache_key)
  File "/Users/val/dev/marketing/SampleApps/bd_claude_native_ai/venv/lib/python3.13/site-packages/jinja2/utils.py", line 477, in get
    return self[key]
           ~~~~^^^^^
  File "/Users/val/dev/marketing/SampleApps/bd_claude_native_ai/venv/lib/python3.13/site-packages/jinja2/utils.py", line 515, in __getitem__
    rv = self._mapping[key]
         ~~~~~~~~~~~~~^^^^^
TypeError: unhashable type: 'dict'
This is a known Starlette 1.6.0/Jinja2 version-mismatch quirk with the older TemplateResponse(name, context) positional signature. Let me use the newer keyword form.

Bash Check starlette and fastapi versions
IN
source venv/bin/activate && python3 -c "import starlette; print(starlette.__version__)" && python3 -c "import fastapi; print(fastapi.__version__)"

OUT
1.6.0
0.141.1
This starlette version expects TemplateResponse(request, name, context). Let me update all three usages in main.py.

Read main.py (lines 99-113)
Edit main.py
Modified
Read main.py (lines 108-157)
Edit main.py
Added 1 line
Edit main.py
Modified
Uvicorn is running with --reload off, so I need to restart it to pick up changes.

Bash Restart server with template fix
IN
pkill -f "uvicorn app.main:app" ; sleep 1
cd /Users/val/dev/marketing/SampleApps/bd_claude_native_ai && source venv/bin/activate && uvicorn app.main:app --port 8000 > /tmp/uvicorn.log 2>&1 &
sleep 2 && cat /tmp/uvicorn.log

OUT
INFO:     Started server process [14907]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
Bash Verify all three web UI pages render correctly
IN
curl -s http://127.0.0.1:8000/ -o /tmp/home.html -w "%{http_code}\n" && grep -o "<h1>.*</h1>" /tmp/home.html
curl -s http://127.0.0.1:8000/orders/new -o /tmp/new.html -w "%{http_code}\n" && grep -o "<h1>.*</h1>" /tmp/new.html
curl -s http://127.0.0.1:8000/orders/6 -o /tmp/detail.html -w "%{http_code}\n" && grep -o "<h1>.*</h1>" /tmp/detail.html

OUT
200
<h1>Orders</h1>
200
<h1>New Order</h1>
200
<h1>Order #6</h1>
All three pages render successfully. Let's do an end-to-end test of the form submission (rejecting an over-limit order) and confirm the error message displays properly.

Bash Test form submission for over-limit order rejection
IN
curl -s -i -X POST http://127.0.0.1:8000/orders/new -d "customer_id=4&notes=form+test&product_id=3&quantity=1" -H "Content-Type: application/x-www-form-urlencoded" | head -10

OUT
HTTP/1.1 303 See Other
date: Thu, 17 Sep 2026 20:56:56 GMT
server: uvicorn
content-length: 0
location: /orders/new?error=Order%20rejected%3A%20order%20total%205075.0000000000%20would%20bring%20Diana%27s%20balance%20to%205075.0000000000%2C%20exceeding%20their%20credit%20limit%20of%201000.0000000000
Redirects correctly with the error message. Let's confirm the error renders on the redirected page.

Bash Confirm error displays in form page
IN
curl -s "http://127.0.0.1:8000/orders/new?error=Order%20rejected%3A%20test" | grep -A2 "class=\"error\""

OUT
<div class="error">Order rejected: test</div>
Now let's test a valid form submission end-to-end.

Bash Test valid multi-line-item form submission
IN
curl -s -i -X POST http://127.0.0.1:8000/orders/new -d "customer_id=1&notes=Alice+web+order&product_id=1&quantity=1&product_id=4&quantity=2" -H "Content-Type: application/x-www-form-urlencoded" | head -6

OUT
HTTP/1.1 303 See Other
date: Thu, 17 Sep 2026 20:57:05 GMT
server: uvicorn
content-length: 0
location: /orders/7
Bash Verify multi-item order detail page
IN
curl -s http://127.0.0.1:8000/orders/7

OUT
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Order #7</title>
    <style>
        body { font-family: -apple-system, Helvetica, Arial, sans-serif; max-width: 800px; margin: 2rem auto; color: #222; }
        h1 { font-size: 1.5rem; }
        table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
        th, td { border: 1px solid #ddd; padding: 0.5rem; text-align: left; }
        th { background: #f5f5f5; }
        a { color: #0b5fff; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .error { background: #fdecea; color: #b3261e; border: 1px solid #f5c2c0; padding: 0.75rem; border-radius: 4px; margin-bottom: 1rem; }
        .btn { display: inline-block; background: #0b5fff; color: white; padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer; font-size: 1rem; }
        .btn:hover { background: #0a4fd6; text-decoration: none; }
        .line-item-row select, .line-item-row input { padding: 0.3rem; }
        .top-nav { margin-bottom: 1.5rem; }
        .muted { color: #777; font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="top-nav"><a href="/">&larr; All Orders</a></div>
    
<h1>Order #7</h1>
<p><strong>Customer:</strong> Alice (balance: 460.00, credit limit: 5000.00)</p>
<p><strong>Notes:</strong> Alice web order</p>
<p><strong>Created:</strong> 2026-09-17</p>

<table>
    <thead>
        <tr><th>Product</th><th>Quantity</th><th>Unit Price</th><th>Amount</th></tr>
    </thead>
    <tbody>
        
        <tr>
            <td>Gadget</td>
            <td>1</td>
            <td>150.00</td>
            <td>150.00</td>
        </tr>
        
        <tr>
            <td>Doodad</td>
            <td>2</td>
            <td>110.00</td>
            <td>220.00</td>
        </tr>
        
    </tbody>
    <tfoot>
        <tr><th colspan="3">Order Total</th><th>370.00</th></tr>
    </tfoot>
</table>

</body>
</html>
Everything is working correctly — 150 + 220 = 370 total, Alice's balance went from 90 to 460. All business rules confirmed working: item amount calculation, order total summation, balance update, and credit limit rejection. Now let's restore the database to its original state and clean up test artifacts.

Bash Stop server and restore original database
IN
pkill -f "uvicorn app.main:app"
cd /Users/val/dev/marketing/SampleApps/bd_claude_native_ai && mv basic_demo.sqlite.bak basic_demo.sqlite
sqlite3 basic_demo.sqlite "SELECT * FROM customer;"

OUT
1|Alice|90|5000|alice@corp.org|0
2|Bob|0|3000|bob@corp.org|0
3|Charlie|220|2000|charlie@corp.org|0
4|Diana|0|1000|diana@corp.org|0
5|Silent|220|1000|silent@corp.org|1
Database restored to its original state. Now let's add a .gitignore and a README with run instructions, and a run.sh convenience script.

Write .gitignore
5 lines
Write run.sh
6 lines
Bash Make run script executable
IN
chmod +x /Users/val/dev/marketing/SampleApps/bd_claude_native_ai/run.sh

OUT
(Bash completed with no output)
Write README.md
29 lines
Let's do a final restart and sanity check that everything still works with the fresh database, then leave the server stopped.

Bash Final smoke test then stop server
IN
source venv/bin/activate && uvicorn app.main:app --port 8000 > /tmp/uvicorn_final.log 2>&1 &
sleep 2
curl -s http://127.0.0.1:8000/ -o /dev/null -w "home: %{http_code}\n"
curl -s http://127.0.0.1:8000/orders/new -o /dev/null -w "new order form: %{http_code}\n"
curl -s http://127.0.0.1:8000/api/customers -o /dev/null -w "api customers: %{http_code}\n"
pkill -f "uvicorn app.main:app"
cat /tmp/uvicorn_final.log

OUT
home: 200
new order form: 200
api customers: 200
INFO:     Started server process [15597]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:56350 - "GET / HTTP/1.1" 200 OK
INFO:     127.0.0.1:56351 - "GET /orders/new HTTP/1.1" 200 OK
INFO:     127.0.0.1:56352 - "GET /api/customers HTTP/1.1" 200 OK
Everything works cleanly. Here's a summary:

Built: a plain hand-written FastAPI + SQLAlchemy + Jinja2 app in app/ over basic_demo.sqlite — no code-gen or rules-engine framework.

app/models.py — SQLAlchemy models for customer, product, order, item
app/orders.py — place_order(): the four business rules (price×qty → item amount, sum → order total, add to customer balance, reject if balance would exceed credit limit), all in one transaction with rollback on rejection
app/main.py — JSON API (/api/customers, /api/products, /api/orders) plus a server-rendered web UI (order list, new-order form with dynamic line items, order detail)
app/templates/ — the three HTML pages
Tested end-to-end via curl: valid orders update balances correctly (verified item amounts and totals arithmetically), and an over-limit order is rejected with no partial state change. Restored basic_demo.sqlite to its original contents afterward.

Run with ./run.sh, then open http://127.0.0.1:8000.

