to rebuild basic basic_demo
1. update the .sql files
2. sh tests/test_databases/basic_demo/basic_demo.sh

xxxxx  WG fails!  somehow the (unique) name got included in the pkey - sqlacodegen bug?
CREATE TABLE customer (
	id INTEGER NOT NULL, 
	name VARCHAR, 
	balance DECIMAL, 
	credit_limit DECIMAL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
)

yyyy this works
CREATE TABLE customer (
        id INTEGER NOT NULL, 
        name VARCHAR, 
        balance DECIMAL, 
        credit_limit DECIMAL, 
        PRIMARY KEY (id)
);


CREATE TABLE product (
        id INTEGER NOT NULL, 
        name VARCHAR, 
        unit_price DECIMAL, 
        carbon_neutral BOOLEAN,
        PRIMARY KEY (id)
);
INSERT INTO product VALUES(1,'Gadget',150, 1);
INSERT INTO product VALUES(2,'Widget',90, NULL);
INSERT INTO product VALUES(3,'Thingamajig',75, NULL);
INSERT INTO product VALUES(4,'Doodad',110, NULL);
INSERT INTO product VALUES(5,'Green',109, 1);