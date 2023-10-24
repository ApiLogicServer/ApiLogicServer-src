
-- Create the 'users' table to store user information - Multi-Tenant
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL
);

-- Create the 'accounts' table to store information about financial accounts
DROP TABLE IF EXISTS accounts;
CREATE TABLE accounts (
    account_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    account_name VARCHAR(50) NOT NULL,
    balance DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Create the 'categories' table to store budget categories
DROP TABLE IF EXISTS categories;
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL,
    is_expense TINYINT(1) NOT NULL DEFAULT 1  -- 1 for expense, 0 for income
);

-- Insert sample data into the 'users' table
INSERT INTO users (username, password, email)
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
	year_id INT NOT NULL DEFAULT 2023,
	user_id INT NOT NULL,
    account_id INT NOT NULL,
    category_id INT NOT NULL,
    budget_total  DECIMAL(10, 2) NOT NULL,
    actual_amount DECIMAL(10, 2) NOT NULL,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    PRIMARY KEY(user_id, category_id, account_id, year_id)
);

-- Create 1,2,3,4 
-- insert parent yr_total if not found
DROP TABLE IF EXISTS qtr_total;
CREATE TABLE qtr_total (
    qtr_id TINYINT(1) NOT NULL,
	year_id INT NOT NULL DEFAULT 2023,
	user_id INT NOT NULL,
    account_id INT NOT NULL,
    category_id INT NOT NULL,
    budget_total  DECIMAL(10, 2) NOT NULL,
    actual_amount DECIMAL(10, 2) NOT NULL,
    created_date  DATETIME DEFAULT CURRENT_TIMESTAMP ,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (user_id, category_id, account_id, year_id) REFERENCES yr_total(user_id, category_id, account_id, year_id),
    PRIMARY KEY(user_id, category_id, account_id, year_id, qtr_id)
);

-- Months 1-12 JAN, FEB ... DEC
-- insert parent qtr_total if not found
DROP TABLE IF EXISTS month_total;
CREATE TABLE month_total (
    month_id TINYINT(1) NOT NULL,
    month_str VARCHAR(20), -- formula(month_as_string, month_id) JAN, FEB
    qtr_id TINYINT(1) NOT NULL,
	year_id INT NOT NULL DEFAULT 2023,
	user_id INT NOT NULL,
    account_id INT NOT NULL,
    category_id INT NOT NULL,
    budget_total  DECIMAL(10, 2) NOT NULL,
    actual_amount DECIMAL(10, 2) NOT NULL,
    created_date  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (user_id, category_id, account_id, year_id, qtr_id) REFERENCES qtr_total(user_id, category_id, account_id, year_id, qtr_id),
    PRIMARY KEY(user_id, category_id, account_id, month_id, qtr_id, year_id)
);

-- Weeks 1-52
-- insert parent qtr_total if not found
DROP TABLE IF EXISTS week_total;
CREATE TABLE week_total (
    week_id TINYINT(1) NOT NULL,	
	month_id TINYINT(1) NOT NULL, -- formula(month_from_week)
    qtr_id TINYINT(1) NOT NULL, -- formula(qtr_from_month)
	year_id INT NOT NULL DEFAULT 2023, -- formula(year_from?)
	user_id INT NOT NULL,
    account_id INT NOT NULL,
    category_id INT NOT NULL,
    budget_total  DECIMAL(10, 2) NOT NULL, -- SUM(budet.amount)
    actual_amount DECIMAL(10, 2) NOT NULL, -- sum(transactions.amount)
    difference DECIMAL(10, 2) NOT NULL, -- formula(budget - actual)
    created_date  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (user_id, category_id, account_id, month_id, qtr_id, year_id) REFERENCES month_total(user_id, category_id, account_id, month_id, qtr_id, year_id),
    PRIMARY KEY(user_id, category_id, account_id, week_id,  month_id, qtr_id, year_id)
);

-- Create the 'budget' table to track weekly estimated vs actual data
-- insert parent week_total if not found
DROP TABLE IF EXISTS budget;
CREATE TABLE budget (
    budget_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    account_id INT NOT NULL,
    category_id INT NOT NULL,
    week_date  DATETIME DEFAULT CURRENT_TIMESTAMP,
    month_id TINYINT(1) NOT NULL, -- formula(month_from_week)
    qtr_id TINYINT(1) NOT NULL, -- formula(qtr_from_month)
    week_id TINYINT(1) DEFAULT 1, -- formula(lookup week by week_date)
    year_id INT DEfAULT 2023, -- formula(year_from_week_date)
    description VARCHAR(200),
    amount DECIMAL(10, 2) NOT NULL, 
    is_expense TINYINT(1) NOT NULL,  -- copy(category.is_expense)
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (user_id, category_id, account_id, week_id,  month_id, qtr_id, year_id) REFERENCES week_total(user_id, category_id, account_id, week_id,  month_id, qtr_id, year_id)
);

-- Create the 'transactions' table to record financial transactions
DROP TABLE IF EXISTS transactions;
CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    account_id INT NOT NULL,
    category_id INT,
    transaction_date  DATETIME DEFAULT CURRENT_TIMESTAMP,
    year_id INT DEfAULT 2023, -- formula(year_from_week_date)
    month_id TINYINT(1) NOT NULL, -- formula(month_from_week)
    qtr_id TINYINT(1) NOT NULL, -- formula(qtr_from_month)
    week_id TINYINT(1) DEFAULT 1, -- formula(lookup week by week_date)
    description VARCHAR(200),
    amount DECIMAL(10, 2) NOT NULL,
    is_expense TINYINT(1) NOT NULL,  -- copy(category.is_expense)
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (user_id, category_id, account_id, week_id,  month_id, qtr_id, year_id) REFERENCES week_total(user_id, category_id, account_id, week_id,  month_id, qtr_id, year_id)
);
