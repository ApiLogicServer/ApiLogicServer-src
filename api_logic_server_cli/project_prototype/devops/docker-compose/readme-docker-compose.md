Use docker compose to choreograph multiple services (e.g, your application, database and web server) for a multi-tiered system.

Here is an example using MySQL - [click here](https://github.com/ApiLogicServer/docker-compose-mysql-classicmodels.git).  In this example, you create a complete project.

For an example using postgres / Northwind, [click here](https://github.com/ApiLogicServer/docker-compose-nw-postgres).  In this example, you use an existing github project.

The docker files in this directory are from that project.  To adapt them to your own project, you will need to update the database section of `docker-compose.yml`.
