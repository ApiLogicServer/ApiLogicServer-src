--   ApiLogicServer create --db_url=mysql+pymysql://root:p@localhost:3306/BudgetApp --project_name=BudgetApp

-- Create the MySQL database for the budgeting application
-- DROP DATABASE BudgetApp;
CREATE DATABASE BudgetApp2

-- Use the newly created database
USE BudgetApp;

-- Create the 'users' table to store user information - Multi-Tenant
DROP TABLE IF EXISTS tenant_user;
CREATE TABLE tenant_user (
    user_id INT  PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL
);

-- Create the 'accounts' table to store information about financial accounts
DROP TABLE IF EXISTS accounts;
CREATE TABLE accounts (
    account_id INT  PRIMARY KEY AUTOINCREMENT,
    user_id INT  NOT NULL,
    account_name VARCHAR(50) NOT NULL,
    balance DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES tenant_user(user_id)
);

-- Create the 'categories' table to store budget categories
DROP TABLE IF EXISTS categories;
CREATE TABLE categories (
    category_id INT  PRIMARY KEY AUTOINCREMENT,
    category_name VARCHAR(50) NOT NULL,
    is_expense INT   NOT NULL DEFAULT 1  -- 1 for expense, 0 for income
);

-- Insert sample data into the 'tenant_user' table

INSERT INTO tenant_user (username, password, email)
VALUES
    ('user1', 'password1', 'user1@example.com'),
    ('user2', 'password2', 'user2@example.com');

-- Insert sample data into the 'accounts' table

INSERT INTO accounts (user_id, account_name, balance)
VALUES
    (1, 'Checking Account', 5000.00),
    (1, 'Savings Account', 10000.00);

-- Insert sample data into the 'categories' table

INSERT INTO categories (category_name)
VALUES
    ('Groceries'),
    ('Mortgage'),
    ('Utilities'),
    ('Cell Phone'),
    ('Salary'),
    ('Entertainment');

    
-- YEAR 2023 -    
DROP TABLE IF EXISTS yr_total;
CREATE TABLE yr_total (
    year_id INT  NOT NULL DEFAULT 2023,
    user_id INT  NOT NULL,
    category_id INT  NOT NULL,
    budget_total  DECIMAL(10, 2) NOT NULL,
    actual_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES tenant_user(user_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    PRIMARY KEY(year_id, user_id, category_id)
);

-- Create 1,2,3,4 
-- insert parent yr_total if not found
DROP TABLE IF EXISTS qtr_total;
CREATE TABLE qtr_total (
    qtr_id INT  NOT NULL,
    year_id INT  NOT NULL DEFAULT 2023,
    user_id INT  NOT NULL,
    category_id INT  NOT NULL,
    budget_total  DECIMAL(10, 2) NOT NULL,
    actual_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    created_date  DATETIME DEFAULT CURRENT_TIMESTAMP ,
    FOREIGN KEY (user_id) REFERENCES tenant_user(user_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (year_id, user_id, category_id) REFERENCES yr_total(year_id, user_id, category_id) ON DELETE CASCADE,
    PRIMARY KEY(year_id, qtr_id, user_id, category_id)
);

-- Months 1-12 JAN, FEB ... DEC
-- insert parent qtr_total if not found
DROP TABLE IF EXISTS month_total;
CREATE TABLE month_total (
    month_id INT   NOT NULL,
    month_str VARCHAR(20), 
    year_id INT ,
    qtr_id INT   NOT NULL,
    user_id INT  NOT NULL,
    category_id INT  NOT NULL,
    budget_total  DECIMAL(10, 2) NOT NULL,
    actual_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    created_date  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES tenant_user(user_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (year_id, qtr_id, user_id, category_id) REFERENCES qtr_total(year_id, qtr_id, user_id, category_id)  ON DELETE CASCADE,
    PRIMARY KEY(year_id, qtr_id, month_id, user_id, category_id)
);


-- Create the 'budget' table to track weekly estimated vs actual data
-- insert parent week_total if not found
DROP TABLE IF EXISTS budget;
CREATE TABLE budget (
    budget_id INT  PRIMARY KEY AUTOINCREMENT,
    year_id INT  DEfAULT 2023, 
    qtr_id INT   NOT NULL, 
    month_id INT   NOT NULL,
    user_id INT  NOT NULL,
    category_id INT  NOT NULL,
    description VARCHAR(200),
    amount DECIMAL(10, 2) NOT NULL, 
    actual_amount DECIMAL(10, 2) DEFAULT 0,
    count_transactions INT  DEFAULT 0, 
    budget_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_expense INT  ,  
    FOREIGN KEY (user_id) REFERENCES tenant_user(user_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (year_id, qtr_id, month_id, user_id, category_id) REFERENCES month_total(year_id, qtr_id, month_id, user_id, category_id)  ON DELETE CASCADE
);

-- Create the 'transactions' table to record financial transactions
DROP TABLE IF EXISTS transactions;
CREATE TABLE transactions (
    transaction_id INT  PRIMARY KEY AUTOINCREMENT,
    budget_id INT  NOT NULL,
    year_id INT , 
    month_id INT , 
    qtr_id INT , 
    user_id INT ,
    category_id INT, 
    account_id INT  NOT NULL,
    transaction_date  DATETIME DEFAULT CURRENT_TIMESTAMP,
    description VARCHAR(200),
    amount DECIMAL(10, 2) NOT NULL,
    is_expense INT  , 
    FOREIGN KEY (user_id) REFERENCES tenant_user(user_id),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (budget_id) REFERENCES budget(budget_id) ON DELETE CASCADE
);
