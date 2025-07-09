-- sqlite3 date_test.sqlite < date_test.sql
-- genai-logic create  --project_name=date_test --db_url=sqlite:///date_test.sqlite
--    Rule.formula(derive=models.Employee.age,  as_exp=lambda row: int((datetime.datetime.now() - row.birth_date).days / 365.25) if row.birth_date else None)

-- Observe: Invalid Rules:  [AttributeError("'function' object has no attribute 'strip'")]


CREATE TABLE Employee (
        id INTEGER NOT NULL, 
        name VARCHAR, 
        email varchar,
        email_opt_out BOOLEAN,
        birth_date date,
        age int,
        PRIMARY KEY (id)
);