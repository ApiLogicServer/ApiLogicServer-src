-- sqlite3 basic_demo_unique_name.sqlite < basic_demo_unique_name.sql;
-- ApiLogicServer create --db_url=sqlite:///basic_demo_unique_name.sqlite --project_name=basic_demo_unique_name

PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE customer (
        id INTEGER NOT NULL, 
        name VARCHAR, 
        balance DECIMAL, 
        credit_limit DECIMAL, 
        UNIQUE (name),
        PRIMARY KEY (id)
);
INSERT INTO customer VALUES(1,'Alice',90,5000);
INSERT INTO customer VALUES(2,'Bob',0,3000);
INSERT INTO customer VALUES(3,'Charlie',220,2000);
INSERT INTO customer VALUES(4,'Diana',0,1000);
CREATE TABLE product (
        id INTEGER NOT NULL, 
        name VARCHAR, 
        unit_price DECIMAL, 
        PRIMARY KEY (id)
);
INSERT INTO product VALUES(1,'Gadget',150);
INSERT INTO product VALUES(2,'Widget',90);
INSERT INTO product VALUES(3,'Thingamajig',75);
INSERT INTO product VALUES(4,'Doodad',110);
CREATE TABLE IF NOT EXISTS "order" (
        id INTEGER NOT NULL, 
        notes VARCHAR, 
        customer_id INTEGER NOT NULL, 
        date_shipped DATE, 
        amount_total DECIMAL, 
        PRIMARY KEY (id), 
        FOREIGN KEY(customer_id) REFERENCES customer (id)
);
INSERT INTO "order" VALUES(1,'First Order',2,'2023-03-22',300);
INSERT INTO "order" VALUES(2,'Second Order',1,NULL,90);
INSERT INTO "order" VALUES(3,'Pending Shipment',3,NULL,220);
INSERT INTO "order" VALUES(4,'Urgent Order',4,'2023-07-15',220);
CREATE TABLE item (
        id INTEGER NOT NULL, 
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
COMMIT;