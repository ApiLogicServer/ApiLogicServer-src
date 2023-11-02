DROP TABLE if exists Customers;
CREATE TABLE Customers (
    CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Balance DECIMAL(10, 2) NULL,
    CreditLimit DECIMAL(10, 2) NULL,
    Region VARCHAR(32),
    ContactName VARCHAR(32)
);

-- Create the Products table
DROP TABLE if exists Products;
CREATE TABLE Products (
    ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    UnitPrice DECIMAL(10, 2) NULL
);

-- Create the Orders table
DROP TABLE if exists Orders;
CREATE TABLE Orders (
    OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
    CustomerID INTEGER NULL,
    AmountTotal DECIMAL(10, 2) NULL,
    ShipDate DATE NULL,
    Notes TEXT NULL,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);

-- Create the Items table
DROP TABLE if exists Items;
CREATE TABLE Items (
    ItemID INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderID INTEGER NULL,
    ProductID INTEGER NULL,
    Quantity INTEGER NULL,
    Amount DECIMAL(10, 2) NULL,
    UnitPrice DECIMAL(10, 2) NULL,
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);
-- Insert sample customers
INSERT INTO Customers (Name, Balance, CreditLimit, Region, ContactName) VALUES
    ('Customer 1', 0, 2000.00, "US", "Tyler"),
    ('Customer 2', 50.00, 3000.00, "France", "Thomas"),
    ('Inactive British', 0, 0, 'British Isles', 'Mike'),
    ('Active British', 0, 1000, 'British Isles', 'John');

-- Insert sample products
INSERT INTO Products (Name, UnitPrice) VALUES
    ('Product A', 10.00),
    ('Product B', 20.00);

-- Sample Order

INSERT INTO ORDERS (OrderID, CustomerID, AmountTotal) VALUES
    (1, 2, 50.00);

INSERT INTO ITEMS (OrderID, ProductID, Quantity, Amount, UnitPrice) VALUES
    (1, 1, 1, 10.00, 10.00),
    (1, 2, 2, 40.00, 20.00)
