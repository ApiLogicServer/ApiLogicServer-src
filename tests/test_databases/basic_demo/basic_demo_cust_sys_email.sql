-- serious trouble with adding this table in CoPilot

CREATE TABLE sys_email (
	id INTEGER NOT NULL, 
	message TEXT, 
	subject VARCHAR(200), 
	customer_id INTEGER NOT NULL, 
	"CreatedOn" DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(customer_id) REFERENCES customer (id)
)