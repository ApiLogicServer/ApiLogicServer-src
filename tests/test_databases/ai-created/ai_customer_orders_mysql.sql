-- sqlite3 ai_customer_orders.sqlite < ai_customer_orders.sql
-- sqlite3 ai_customer_orders.sqlite
-- commands such as .schema
-- ApiLogicServer create --project_name=ai_customer_orders --db_url=sqlite:////Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/tests/test_databases/ai-created/ai_customer_orders.sqlite
-- SELECT COUNT(*) FROM sqlite_sequence;

DROP DATABASE IF EXISTS ai_customer_orders;

CREATE DATABASE ai_customer_orders;

USE ai_customer_orders;

CREATE TABLE IF NOT EXISTS Customers (
    CustomerID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName TEXT,
    LastName TEXT,
    Email TEXT,
    CreditLimit DECIMAL,
    Balance DECIMAL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS Products (
    ProductID INT AUTO_INCREMENT PRIMARY KEY,
    ProductName TEXT,
    UnitPrice REAL
);

CREATE TABLE IF NOT EXISTS Orders (
    OrderID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID INTEGER,
    AmountTotal DECIMAL,
    OrderDate DATE,
    ShipDate DATE,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);

CREATE TABLE IF NOT EXISTS OrderItems (
    OrderItemID INT AUTO_INCREMENT PRIMARY KEY,
    OrderID INTEGER,
    ProductID INTEGER,
    Quantity INTEGER,
    ItemPrice DECIMAL,
    Amount DECIMAL,
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);


-- Insert customer data
INSERT INTO Customers (FirstName, LastName, Email, CreditLimit) VALUES
    ('John', 'Doe', 'john@example.com', 1000.00),
    ('Jane', 'Smith', 'jane@example.com', 1500.00);

-- Insert product data
INSERT INTO Products (ProductName, UnitPrice) VALUES
    ('Product A', 10.00),
    ('Product B', 15.00),
    ('Product C', 8.50);
