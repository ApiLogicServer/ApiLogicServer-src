

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