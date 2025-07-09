-- sqlite3 date_test.sqlite < date_test.sql
-- genai-logic create  --project_name=date_test --db_url=sqlite:///date_test.sqlite
-- 

CREATE TABLE Employee (
        id INTEGER NOT NULL, 
        name VARCHAR, 
        email varchar,
        email_opt_out BOOLEAN,
        birth_date datetime,
        PRIMARY KEY (id)
);