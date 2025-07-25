-- see https://www.sqlitetutorial.net/sqlite-dump/
-- rm tests/test_databases/basic_demo/basic_demo_cust.sqlite; sqlite3 tests/test_databases/basic_demo/basic_demo_cust.sqlite < tests/test_databases/basic_demo/basic_demo_cust.sql
--

BEGIN TRANSACTION;
CREATE TABLE customer (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name VARCHAR, 
        balance DECIMAL, 
        credit_limit DECIMAL, 
        email varchar,
        email_opt_out BOOLEAN,
        PRIMARY KEY (id)
);
INSERT INTO customer VALUES(1,'Alice',90,5000, "alice@corp.org", 0);
INSERT INTO customer VALUES(2,'Bob',0,3000, "bob@corp.org", 0);
INSERT INTO customer VALUES(3,'Charlie',220,2000, "charlie@corp.org", 0);
INSERT INTO customer VALUES(4,'Diana',0,1000, "diana@corp.org", 0);
INSERT INTO customer VALUES(5,'Silent',220,1000, "silent@corp.org", 1);

CREATE TABLE product (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name VARCHAR, 
        unit_price DECIMAL,
        PRIMARY KEY (id)
);
INSERT INTO product VALUES(1,'Gadget',150);
INSERT INTO product VALUES(2,'Widget',90);
INSERT INTO product VALUES(3,'Thingamajig',75);
INSERT INTO product VALUES(4,'Doodad',110);
INSERT INTO product VALUES(5,'Green',109);

CREATE TABLE IF NOT EXISTS "order" (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        notes VARCHAR, 
        customer_id INTEGER NOT NULL, 
        CreatedOn DATE,
        date_shipped DATE, 
        amount_total DECIMAL, 
        PRIMARY KEY (id), 
        FOREIGN KEY(customer_id) REFERENCES customer (id)
);
INSERT INTO "order" VALUES(1,'First Order',2, '2023-02-22', '2023-03-22',300);
INSERT INTO "order" VALUES(2,'Second Order',1, '2023-02-22',NULL,90);
INSERT INTO "order" VALUES(3,'Pending Shipment',3, '2023-01-22',NULL,220);
INSERT INTO "order" VALUES(4,'Urgent Order',4, '2023-02-22', '2023-07-15',220);
INSERT INTO "order" VALUES(5,'Silent Shipment',5, '2023-01-22',NULL,220);

CREATE TABLE item (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        order_id INTEGER, 
        product_id INTEGER NOT NULL, 
        quantity INTEGER NOT NULL, 
        amount DECIMAL, 
        unit_price DECIMAL, 
        PRIMARY KEY (id), 
        FOREIGN KEY(order_id) REFERENCES "order" (id), 
        FOREIGN KEY(product_id) REFERENCES product (id)
);
INSERT INTO item VALUES(1,1,1,2,300,150);
INSERT INTO item VALUES(2,2,2,1,90,90);
INSERT INTO item VALUES(3,3,4,2,220,110);
INSERT INTO item VALUES(4,4,3,4,300,75);
INSERT INTO item VALUES(5,5,4,2,220,110);

CREATE TABLE IF NOT EXISTS sys_email (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        message VARCHAR, 
        subject VARCHAR,
        customer_id INTEGER NOT NULL, 
        CreatedOn DATE,
        PRIMARY KEY (id), 
        FOREIGN KEY(customer_id) REFERENCES customer (id)
);


COMMIT;


