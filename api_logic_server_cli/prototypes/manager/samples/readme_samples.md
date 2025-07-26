## Pre-built samples

See https://apilogicserver.github.io/Docs/Data-Model-Examples/

The created `samples/nw_sample` illustrates important customization sample code - a key part of training.  Search for #als.

## Sqlite Sample Databases

The `samples/db` files are pre-installed sqlite databases.  These allow you to explore creating projects from existing databases.

For example, create Northwind and basic_demo like this:

```bash
genai-logic create  --project_name=nw --db_url=sqlite:///samples/dbs/nw.sqlite

genai-logic create --project_name=basic_demo --db_url=sqlite:///samples/dbs/basic_demo.sqlite
```

## Database Connectivity

Sample project creation commands:

```bash
# local sqlite
genai-logic create --db_url=sqlite:///c:\genai-logic\nw.sqlite --project_name=nw
genai-logic create --db_url=sqlite:///samples/dbs/todos.sqlite --project_name=todo
genai-logic create --db_url=sqlite:////Users/val/dev/ApiLogicServer/ApiLogicServer-dev/clean/ApiLogicServer/samples/dbs/todos.sqlite --project_name=todo

# from localhost to mysql container
genai-logic create --db_url=mysql+pymysql://root:p@localhost:3306/classicmodels --project_name=docker_classicmodels
genai-logic create --db_url=mysql+pymysql://root:p@localhost:3306/Chinook --project_name=docker_chinook

# from container to mysql container  replace localhost with....
genai-logic create --db_url=mysql+pymysql://root:p@mysql-container:3306/Chinook --project_name=/localhost/docker_chinook

# microsoft sql server (setup: https://apilogicserver.github.io/Docs/Install-pyodbc/)
genai-logic create --db_url='mssql+pyodbc://sa:Posey3861@localhost:1433/NORTHWND?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=no&Encrypt=no' --project-name=NORTHWND

# oracle
genai-logic create --project_name=oracle_hr --db_url='oracle+oracledb://hr:tiger@localhost:1521/?service_name=ORCL'

# postgres
genai-logic create --db_url=postgresql://postgres:p@localhost/northwind --project-name=nw-postgres
genai-logic create --db_url=postgresql://postgres:p@10.0.0.234/postgres
genai-logic create --project_name=my_schema --db_url=postgresql://postgres:p@localhost/my_schema
genai-logic create --db_url=postgresql://postgres:password@localhost:5432/postgres?options=-csearch_path%3Dmy_db_schema

# pythonanywhere
genai-logic create --project_name=Chinook \
  --host=ApiLogicServer.pythonanywhere.com --port= \
  --db_url=mysql+pymysql://ApiLogicServer:@ApiLogicServer.mysql.pythonanywhere-services.com/ApiLogicServer\$Chinook
```

## Docker Databases

You probably don't need _all_ these, but here's how you start the docker databases (schema details below):

```
docker network create dev-network  # only required once

docker run --name mysql-container --net dev-network -p 3306:3306 -d -e MYSQL_ROOT_PASSWORD=p apilogicserver/mysql8.0:latest

docker run -d --name postgresql-container --net dev-network -p 5432:5432 -e PGDATA=/pgdata -e POSTGRES_PASSWORD=p apilogicserver/postgres:latest

docker run --name sqlsvr-container --net dev-network -p 1433:1433 -d apilogicserver/sqlsvr:latest

docker run --name sqlsvr-container --net dev-network -p 1433:1433 -d apilogicserver/sqlsvr-m1:latest  # Mac M1
```


