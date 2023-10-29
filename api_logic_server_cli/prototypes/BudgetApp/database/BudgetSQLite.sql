--   ApiLogicServer create --db_url=mysql+pymysql://root:p@localhost:3306/BudgetApp --project_name=BudgetApp

-- Create the database for the budgeting application
DROP DATABASE BudgetApp;
CREATE DATABASE BudgetApp;

-- Use the newly created database
USE BudgetApp;

-- Create the 'users' table to store user information - Multi-Tenant
DROP TABLE IF EXISTS tenant_user;
CREATE TABLE tenant_user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL
);

-- Create the 'accounts' table to store information about financial accounts
DROP TABLE IF EXISTS accounts;
CREATE TABLE accounts (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER  NOT NULL,
    account_name VARCHAR(50) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES tenant_user(user_id)
);

-- Create the 'categories' table to store budget categories
DROP TABLE IF EXISTS categories;
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name VARCHAR(50) NOT NULL,
    is_expense INTEGER NOT NULL DEFAULT 1  -- 1 for expense, 0 for income
);

-- Insert sample data into the 'tenant_user' table

INSERT INTO tenant_user (username, password, email)
VALUES
    ('user1', 'password1', 'user1@example.com'),
    ('user2', 'password2', 'user2@example.com');

-- Insert sample data into the 'accounts' table

INSERT INTO accounts (user_id, account_name)
VALUES
    (1, 'Checking Account'),
    (1, 'Savings Account');

-- Insert sample data into the 'categories' table

INSERT INTO categories (category_name,is_expense)
VALUES
    ('Groceries',1),
    ('Mortgage',1),
    ('Utilities',1),
    ('Auto Loan',1),
    ('Cell Phone',1),
    ('Salary',0),
    ('Entertainment',1);

    
-- YEAR 2023 -    
DROP TABLE IF EXISTS yr_total;
CREATE TABLE yr_total (
    year_id INTEGER  NOT NULL DEFAULT 2023,
    user_id INTEGER  NOT NULL,
    budget_total  DECIMAL(10, 2) DEFAULT 0,
    actual_amount DECIMAL(10, 2) DEFAULT 0,
    variance_amount DECIMAL(10, 2) DEFAULT 0,  
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES tenant_user(user_id),
    PRIMARY KEY(year_id, user_id)
);


-- Months 1-12 JAN, FEB ... DEC
-- insert parent qtr_total if not found
DROP TABLE IF EXISTS month_total;
CREATE TABLE month_total (
    month_id INTEGER   NOT NULL,
    month_str VARCHAR(20), 
    year_id INTEGER ,
    user_id INTEGER  NOT NULL,
    budget_total  DECIMAL(10, 2) DEFAULT 0,
    actual_amount DECIMAL(10, 2) DEFAULT 0,
    variance_amount DECIMAL(10, 2) DEFAULT 0,
    created_date  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES tenant_user(user_id),
    PRIMARY KEY(year_id, month_id, user_id)
);


-- Months 1-12 JAN, FEB ... DEC
-- insert parent qtr_total if not found
DROP TABLE IF EXISTS category_total;
CREATE TABLE category_total (
    year_id INTEGER ,
    user_id INTEGER  NOT NULL,
    category_id INTEGER  NOT NULL,
    budget_total  DECIMAL(10, 2) DEFAULT 0,
    actual_amount DECIMAL(10, 2)  DEFAULT 0,
    variance_amount DECIMAL(10, 2) DEFAULT 0,
    is_expense INTEGER  ,  
    created_date  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES tenant_user(user_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (year_id, user_id) REFERENCES yr_total(year_id, user_id)  ON DELETE CASCADE,
    PRIMARY KEY(year_id, category_id,  user_id)
);

-- Create the 'budget' table to track weekly estimated vs actual data
-- insert parent week_total if not found
DROP TABLE IF EXISTS budget;
CREATE TABLE budget (
    budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
    year_id INTEGER  DEfAULT 2023, 
    month_id INTEGER  NOT NULL,
    user_id INTEGER  NOT NULL,
    category_id INTEGER  NOT NULL,
    description VARCHAR(200),
    amount DECIMAL(10, 2) NOT NULL, 
    actual_amount DECIMAL(10, 2) DEFAULT 0,
    variance_amount DECIMAL(10, 2) DEFAULT 0,
    count_transactions INTEGER  DEFAULT 0, 
    budget_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_expense INTEGER DEFAULT 1 ,  
    FOREIGN KEY (user_id) REFERENCES tenant_user(user_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (year_id, category_id, user_id) REFERENCES category_total(year_id, category_id, user_id) ON DELETE CASCADE,
    FOREIGN KEY (year_id, month_id,user_id) REFERENCES month_total(year_id, month_id, user_id)  ON DELETE CASCADE
);

-- Create the 'transactions' table to record financial transactions OneToMany -> Budget
DROP TABLE IF EXISTS transactions;
CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    budget_id INTEGER  NOT NULL,
    year_id INTEGER , 
    month_id INTEGER , 
    user_id INTEGER ,
    category_id INT, 
    account_id INTEGER NOT NULL,
    transaction_date  DATETIME DEFAULT CURRENT_TIMESTAMP,
    description VARCHAR(200),
    amount DECIMAL(10, 2) NOT NULL,
    is_expense INTEGER DEFAULT 1, 
    FOREIGN KEY (user_id) REFERENCES tenant_user(user_id),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (budget_id) REFERENCES budget(budget_id) ON DELETE CASCADE
);
