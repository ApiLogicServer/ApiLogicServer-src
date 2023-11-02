Note project name is in project (devops etc)

Home page video is ai_, but without the ai

New article
  * basic_demo
  * readme has logic/security
  * iteration too?

Check it out at:
https://apilogicserver.github.io/Docs/Tutorial-AI/

Breaking changes
  Updated http_type APILOGICPROJECT_HTTP_SCHEME=http

9.1 changes
  Self-reln parent name is class, not 'parent'

Fix image failures
  x postgres
  SqlServer - FAILS - incompatible type

Cloud deploy
  az script
  https

x remove the _x stuff

release?
  Tyler's expose db uri - yes
  
  x Bug: remove all Config. references (eg, security)
    explore security_enabled, and provider, in config

  TP
  x proxy port for swagger - will add client_url arg to safrs

  Tyler verb auth?

  TC: if I set APILOGICPROJECT_PORT as an env var and also have it set in env.list which one takes precedence?
  x Remove docker - apilogicserver/api_logic_server_arm (unified target)
  x Codespaces ready -> devcontainer loaded
  x Multi-Arch dockers
  x log: 0 authentication tables loaded

Multi-container Azure deployement
  Note: docker-compose -> docker compose
  https://learn.microsoft.com/en-us/azure/app-service/quickstart-multi-container
  https://code.visualstudio.com/docs/containers/docker-compose
  https://docs.docker.com/cloud/aci-integration/
    Umm... Docker Compose’s integration for ECS and ACI is retiring in November 2023

New tests

  add-auth test?  for classicmodels?

  docker-compose test?
    build mysql
    containerize
    docker-compose (per IP?)
    start (then run admin manually)
  
  multi-field key
      Location country, city
      Order Country, City



http://localhost:5656/filters_cats
  security  - 4 rows (2:5)
  main      - 

nw_readme.md -> README.md
    * remove internal IDE links
    just a note


https://github.com/community/community/discussions/30205



Creating the ApiLogicServer dev environment
===========================================


    Directory Presumption
    ---------------------

    See https://apilogicserver.github.io/Docs/Architecture-Internals/#how-to-install-it


    Creating ApiLogicServer
    -----------------------

    see link above


    Creating safrs-react-admin (only required if you are changing it)
    --------------------------
    cd dev
    git clone https://github.com/thomaxxl/safrs-react-admin
    cd safrs-react-admin
    git clone https://github.com/thomaxxl/rav3-jsonapi-client # modified data provider used, installed in the project root
    npm install

    npm run build  # for building ApiLogicServer, below

    npm start  # testing changes


To release ALS
==============
    1 Rebuild safrs-react-admin
        a cd ApiLogicServer/react-admin
        b sh rebuild-react-admin go
    2 Build pip
        a cd ApiLogicServer
        b python3 setup.py sdist bdist_wheel
        c python3 -m twine upload  --username vhuber --password xMP0x --skip-existing dist/*
            * to install locally: pip install /Users/val/dev/ApiLogicServer
            * python3 -m twine upload  --repository-url https://test.pypi.org/legacy/ --skip-existing dist/*
    3 Build Docker
        a see Dockerfile to build docker image


Ports and Hosts
===============
    Verified you can run SAFRS and Basic Web App concurrently
    Recent changes enabled pythonanywhere (PA), which works per wiki
    curl
        curl -X GET "http://localhost:5656/Order/?include=Customer%2CEmployee%2COrderDetailList&fields%5BOrder%5D=Id%2CCustomerId%2CEmployeeId%2COrderDate%2CRequiredDate%2CShippedDate%2CShipVia%2CFreight%2CShipName%2CShipAddress%2CShipCity%2CShipRegion%2CShipPostalCode%2CShipCountry%2CAmountTotal&page%5Boffset%5D=0&page%5Blimit%5D=10&sort=Id%2CCustomerId%2CEmployeeId%2COrderDate%2CRequiredDate%2CShippedDate%2CShipVia%2CFreight%2CShipName%2CShipAddress%2CShipCity%2CShipRegion%2CShipPostalCode%2CShipCountry%2CAmountTotal%2Cid" -H  "accept: application/vnd.api+json" -H  "Content-Type: application/vnd.api+json"


TVF
===

Use SampleDB;

Alter FUNCTION udfEmployeeInLocation (
    @location nvarchar(50)
)
RETURNS TABLE
AS
RETURN
    SELECT
      Id, Name, Location
    FROM
      Employees
    WHERE
      Location LIKE @location;


SELECT * FROM udfEmployeeInLocation('Sweden');

this gives the cols:
SELECT TABLE_CATALOG AS [Database], TABLE_SCHEMA AS [Schema], TABLE_NAME AS [Function],
       COLUMN_NAME AS [Column], DATA_TYPE AS [Data Type], CHARACTER_MAXIMUM_LENGTH AS [Char Max Length]
FROM INFORMATION_SCHEMA.ROUTINE_COLUMNS
WHERE TABLE_NAME IN (SELECT ROUTINE_NAME FROM INFORMATION_SCHEMA.ROUTINES WHERE ROUTINE_TYPE = 'FUNCTION' AND DATA_TYPE = 'TABLE') ORDER BY TABLE_NAME, COLUMN_NAME;

to get the args - https://www.mssqltips.com/sqlservertip/1669/generate-a-parameter-list-for-all-sql-server-stored-procedures-and-functions/
SELECT
   SCHEMA_NAME(SCHEMA_ID) AS [Schema]
  ,SO.name AS [ObjectName]
  ,SO.Type_Desc AS [ObjectType (UDF/SP)]
  ,P.parameter_id AS [ParameterID]
  ,P.name AS [ParameterName]
  ,TYPE_NAME(P.user_type_id) AS [ParameterDataType]
  ,P.max_length AS [ParameterMaxBytes]
  ,P.is_output AS [IsOutPutParameter]
FROM sys.objects AS SO
INNER JOIN sys.parameters AS P ON SO.OBJECT_ID = P.OBJECT_ID
ORDER BY [Schema], SO.name, P.parameter_id


Fix OrderDetail
===============

update OrderDetail
      set  ShippedDate =
          (select ShippedDate
          from "Order"
          where Id = OrderId)
2156 rows
Id 10643; OrderDetails are blank on load.  ugh

select CompanyName, Balance from Customer where Id="ALFKI";

update Customer set Balance = (select AmountTotal from "Order" where Customer.Id = CustomerId and ShippedDate is null);

{
  "data": {
    "attributes": {
      "Id": 0,
      "CustomerId": "ALFKI",
      "EmployeeId": 5,
      "OrderDate": "",
      "RequiredDate": "0001-01-01",
      "ShippedDate": "",
      "ShipVia": 0,
      "Freight": 0,
      "ShipName": "",
      "ShipAddress": "",
      "ShipCity": "",
      "ShipRegion": "",
      "ShipPostalCode": "",
      "ShipCountry": "",
      "AmountTotal": 0,
      "Country": "France",
      "City": "Paris",
      "Ready": false,
      "OrderDetailCount": 0
    },
    "type": "Order"
  }
}

python -m venv venv; source venv/bin/activate; pip install -r requirements.txt


Removal of pyodbc (else brew + unixodbc)
========================================

Req'd for sqlserver...
Verify other DBs don't require pyodbc

  pip
  ===
    sqlserver   fails: ModuleNotFoundError: No module named 'pyodbc'
    postgres    runs:  tho, many not-impl on startup
    mysql       runs:  tho updates fail for customer vs Customer 

  docker
  ======
    sqlserver   runs: with updates
    postgres    runs (as above)
    mysql       runs


Exploring
=========

7/29/2022 - SqlServer fails on Swagger, but not Admin app (!)

admin app api:

GET /api/Categories?include=&page%5Blimit%5D=25&page%5Bnumber%5D=1&page%5Boffset%5D=0&page%5Bsize%5D=25&sort=CategoryName HTTP/1.1" 200

swagger api:

curl -X 'GET' \
  'http://localhost:5656/api/Categories/?include=ProductList&fields%5BCategory%5D=CategoryID%2CCategoryName%2CDescription%2CPicture&page%5Boffset%5D=0&page%5Blimit%5D=10&sort=CategoryID%2CCategoryName%2CDescription%2CPicture%2Cid' \
  -H 'accept: application/vnd.api+json' \
  -H 'Content-Type: application/vnd.api+json'

  since trying to sort on Picture


Install too complicated
=======================

TL:DR for local
---------------

cd ApiLogicServer     # presume already installed
source venv/bin/activate;

ApiLogicServer create
code ApiLogicProject  # decline docker (maybe don't build??)
# project venv setup yuck https://stackoverflow.com/questions/54106071/how-can-i-set-up-a-virtual-environment-for-python-in-visual-studio-code


TL:DR for docker
----------------

cd ApiLogicServer
docker run
$ create
$ exit
code ApiLogicProject


ApiLogicServer create-and-run --project_name=/localhost/CheckIP --db_url=  --swagger_host=10.0.0.77