Alter table "Product" rename to TempData;

CREATE TABLE "Product" (
  "Id" INTEGER PRIMARY KEY AUTOINCREMENT, 
  "ProductName" VARCHAR(8000) NULL, 
  "SupplierId" INTEGER NOT NULL, 
  "CategoryId" INTEGER NOT NULL, 
  "QuantityPerUnit" VARCHAR(8000) NULL, 
  "UnitPrice" DECIMAL NOT NULL, 
  "UnitsInStock" INTEGER NOT NULL, 
  "UnitsOnOrder" INTEGER NOT NULL, 
  "ReorderLevel" INTEGER NOT NULL, 
  "Discontinued" INTEGER NOT NULL,
  "UnitsShipped" INTEGER,
  FOREIGN KEY("CategoryId") REFERENCES "CategoryTableNameTest"("Id")
);

INSERT INTO Product  
SELECT *
FROM TempData;


Drop table TempData;


Alter table "OrderDetail" rename to TempData1;

CREATE TABLE OrderDetail (
	"Id"	INTEGER,
	"OrderId"	INTEGER NOT NULL,
	"ProductId"	INTEGER NOT NULL,
	"UnitPrice"	DECIMAL,
	"Quantity"	INTEGER NOT NULL DEFAULT 1,
	"Discount"	DOUBLE DEFAULT 0,
	"Amount"	Decimal,
	"ShippedDate"	VARCHAR(8000),
	PRIMARY KEY("Id" AUTOINCREMENT),
	FOREIGN KEY("OrderId") REFERENCES "Order" on delete cascade
    FOREIGN KEY("ProductId") REFERENCES "Product" on delete set null
);

INSERT INTO OrderDetail  
SELECT *
FROM TempData1;


drop table TempData1;


CREATE VIEW ProductDetails_View as
select 
p.*, 
c.CategoryName_ColumnName, c.Description as [CategoryDescription],
s.CompanyName as [SupplierName], s.Region as [SupplierRegion]
from "Product" p
join "CategoryTableNameTest" c on p.CategoryId = c.id
join [Supplier] s on s.id = p.SupplierId


INSERT INTO Region (RegionDescription)
SELECT DISTINCT ShipRegion
FROM "Order";