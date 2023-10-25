--   ApiLogicServer create --db_url=mysql+pymysql://root:p@localhost:3306/BudgetApp --project_name=BudgetApp

-- Create the database for the budgeting application
-- DROP DATABASE BudgetApp2;
-- CREATE DATABASE BudgetApp2;

-- Use the newly created database
-- USE BudgetApp2;

-- Create the 'users' table to store user information - Multi-Tenant
CREATE TABLE tenant_user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL
);

-- Create the 'accounts' table to store information about financial accounts
CREATE TABLE accounts (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    account_name VARCHAR(50) NOT NULL,
    balance DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES tenant_user(user_id)
);

-- Create the 'categories' table to store budget categories
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name VARCHAR(50) NOT NULL,
    is_expense INTEGER  NOT NULL DEFAULT 1  -- 1 for expense, 0 for income
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
    year_id INTEGER NOT NULL DEFAULT 2023,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
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
    qtr_id INTEGER NOT NULL,
    year_id INTEGER NOT NULL DEFAULT 2023,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    budget_total  DECIMAL(10, 2) NOT NULL,
    actual_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    created_date  DATETIME DEFAULT CURRENT_TIMESTAMP ,
    FOREIGN KEY (user_id) REFERENCES tenant_user(user_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (year_id, user_id, category_id) REFERENCES yr_total(year_id, user_id, category_id),
    PRIMARY KEY(year_id, qtr_id, user_id, category_id)
);

-- Months 1-12 JAN, FEB ... DEC
-- insert parent qtr_total if not found
DROP TABLE IF EXISTS month_total;
CREATE TABLE month_total (
    month_id INTEGER  NOT NULL,
    month_str VARCHAR(20), -- formula(month_as_string, month_id) JAN, FEB
    year_id INTEGER NOT NULL DEFAULT 2023,
    qtr_id INTEGER  NOT NULL,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    budget_total  DECIMAL(10, 2) NOT NULL,
    actual_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    created_date  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES tenant_user(user_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (year_id, qtr_id, user_id, category_id) REFERENCES qtr_total(year_id, qtr_id, user_id, category_id),
    PRIMARY KEY(year_id, qtr_id, month_id, user_id, category_id)
);


-- Create the 'budget' table to track weekly estimated vs actual data
-- insert parent week_total if not found
DROP TABLE IF EXISTS budget;
CREATE TABLE budget (
    budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
    year_id INTEGER DEfAULT 2023, -- formula(year_from_week_date)
    qtr_id INTEGER  NOT NULL, -- formula(qtr_from_month)
    month_id INTEGER  NOT NULL, -- formula(month_from_week)
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    description VARCHAR(200),
    amount DECIMAL(10, 2) NOT NULL, 
    budget_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_expense INTEGER ,  -- copy(category.is_expense)
    FOREIGN KEY (user_id) REFERENCES tenant_user(user_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (year_id, qtr_id, month_id, user_id, category_id) REFERENCES month_total(year_id, qtr_id, month_id, user_id, category_id)
);

-- Create the 'transactions' table to record financial transactions
DROP TABLE IF EXISTS transactions;
CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    year_id INTEGER DEfAULT 2023, -- formula(year_from_week_date)
    month_id INTEGER  NOT NULL, -- formula(month_from_week)
    qtr_id INTEGER  NOT NULL, -- formula(qtr_from_month)
    user_id INTEGER NOT NULL,
    category_id INT,
    account_id INTEGER NOT NULL,
    transaction_date  DATETIME DEFAULT CURRENT_TIMESTAMP,
    description VARCHAR(200),
    amount DECIMAL(10, 2) NOT NULL,
    is_expense INTEGER ,  -- copy(category.is_expense)
    FOREIGN KEY (user_id) REFERENCES tenant_user(user_id),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (year_id, qtr_id, month_id, user_id, category_id) REFERENCES month_total(year_id, qtr_id, month_id, user_id, category_id)
);
