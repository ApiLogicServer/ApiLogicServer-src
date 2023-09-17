-- sqlite3 customer_orders.sqlite < customer_orders.sql

CREATE TABLE Customers (
    CustomerID INT PRIMARY KEY,
    FirstName VARCHAR(255),
    LastName VARCHAR(255),
    Email VARCHAR(255),
    CreditLimit DECIMAL(10, 2),
    Balance DECIMAL(10, 2)
);

CREATE TABLE Products (
    ProductID INT PRIMARY KEY,
    ProductName VARCHAR(255),
    UnitPrice DECIMAL(10, 2)
);

CREATE TABLE Orders (
    OrderID INT PRIMARY KEY,
    CustomerID INT,
    OrderDate DATE,
    ShipDate DATE,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);

CREATE TABLE OrderItems (
    OrderItemID INT PRIMARY KEY,
    OrderID INT,
    ProductID INT,
    Quantity INT,
    ItemPrice DECIMAL(10, 2), -- Derived from Product UnitPrice
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);

-- Inserting customer data
INSERT INTO Customers (CustomerID, FirstName, LastName, Email, CreditLimit, Balance)
VALUES
    (1, 'John', 'Doe', 'john@example.com', 1000.00, 0.00),
    (2, 'Jane', 'Smith', 'jane@example.com', 1500.00, 0.00);

-- Inserting product data
INSERT INTO Products (ProductID, ProductName, UnitPrice)
VALUES
    (101, 'Product A', 10.00),
    (102, 'Product B', 15.00),
    (103, 'Product C', 8.50);

