CREATE TABLE IF NOT EXISTS Customers (
    CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
    FirstName TEXT,
    LastName TEXT,
    Email TEXT,
    CreditLimit DECIMAL(10, 2),
    Balance DECIMAL(10, 2) DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS Products (
    ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
    ProductName TEXT,
    UnitPrice DECIMAL(10, 2)
);

CREATE TABLE IF NOT EXISTS Orders (
    OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
    CustomerID INTEGER,
    OrderDate DATE,
    ShipDate DATE,
    AmountTotal DECIMAL(10, 2),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);

CREATE TABLE IF NOT EXISTS Items (
    ItemID INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderID INTEGER,
    ProductID INTEGER,
    Quantity INTEGER,
    UnitPrice DECIMAL(10, 2),
    Amount DECIMAL(10, 2),
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