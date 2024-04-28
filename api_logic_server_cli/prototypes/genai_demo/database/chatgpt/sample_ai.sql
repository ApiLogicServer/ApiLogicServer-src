-- Create Customers table
CREATE TABLE Customers (
    CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
    CustomerName TEXT NOT NULL,
    Address TEXT,
    Phone TEXT,
    Balance DECIMAL(10, 2),
    CreditLimit DECIMAL(10, 2) NOT NULL
);

-- Create Products table
CREATE TABLE Products (
    ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
    ProductName TEXT NOT NULL,
    UnitPrice DECIMAL(10, 2) NOT NULL
);

-- Create Orders table
CREATE TABLE Orders (
    OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
    CustomerID INTEGER,
    OrderDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    Notes TEXT,
    ShipDate DATETIME,
    AmountTotal DECIMAL(10, 2),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);

-- Create Items table
CREATE TABLE Items (
    ItemID INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderID INTEGER,
    ProductID INTEGER,
    Quantity INTEGER NOT NULL,
    UnitPrice DECIMAL(10, 2),
    Amount DECIMAL(10, 2),
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);

-- Insert sample data into Customers table
INSERT INTO Customers (CustomerName, Address, Phone, Balance, CreditLimit) VALUES
    ('John Doe', '123 Main St', '555-1234', 1000.00, 5000.00),
    ('Jane Smith', '456 Oak Ave', '555-5678', 500.00, 2000.00);

-- Insert sample data into Products table
INSERT INTO Products (ProductName, UnitPrice) VALUES
    ('Widget A', 19.99),
    ('Gadget B', 29.99);

-- Insert sample data into Orders table
INSERT INTO Orders (CustomerID, Notes, ShipDate, AmountTotal) VALUES
    (1, 'Order 1', NULL, 0.00),
    (2, 'Order 2', NULL, 0.00);

-- Update Items.UnitPrice as a copy from Product.UnitPrice
UPDATE Items
SET UnitPrice = (SELECT UnitPrice FROM Products WHERE Products.ProductID = Items.ProductID);

-- Update Order.AmountTotal as Sum(Items.Amount)
UPDATE Orders
SET AmountTotal = (SELECT SUM(Quantity * UnitPrice) FROM Items WHERE Items.OrderID = Orders.OrderID);

-- Update Customer.Balance as Sum(Order.AmountTotal) where ShipDate is null
UPDATE Customers
SET Balance = (SELECT SUM(AmountTotal) FROM Orders WHERE Orders.CustomerID = Customers.CustomerID AND Orders.ShipDate IS NULL);
