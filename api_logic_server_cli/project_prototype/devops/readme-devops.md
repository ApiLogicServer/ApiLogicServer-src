These resources are designed to provide useful starting point for sometimes-tricky devops operations.

You can run some aspects of this with the demo, but we encourage the use the docker sample classic models.  To see how to start it, [click here](https://apilogicserver.github.io/Docs/Database-Docker/#classicmodels-mysql-docker).

&nbsp;

## auth-db

After creating projects, you add role-based security:

```bash
cd <your project>
ApiLogicServer add-auth --project_name=. --db_url=mysql+pymysql://root:p@localhost:3306/authdb
```

The system introspects your `--db_url` database, creates models for it, and configures your project to enable security.

The command above uses the pre-supplied [docker database](https://apilogicserver.github.io/Docs/Database-Connectivity/#docker-databases), here MySQL.

Security databases must include certain tables and columns.  Your authdb can optionally provide a superset of these.  Such extensions are useful in declaring role-based authorization.

To help you get started, the `auth-db` folder provides starter kits for creating these databases.  Alter these files for your project, prepare database containers for your team, and use them in the `add-auth` command above.

&nbsp;

## docker-image

These scripts simplify creating and running docker containers for your project.  Their use is illustrated in the links above.

Important Notes:

1. The docker compose steps use the created image, so you must perform this step first

2. The image must contain the security models created in the step above

&nbsp;

## docker-compose

Use docker compose to choreograph multiple services (e.g, your application, database and web server) for a multi-tiered system.

Here is an example using MySQL / `classicmodels` - [click here](https://github.com/ApiLogicServer/docker-compose-mysql-classicmodels.git).  In this example, you create a complete project.  

> We strongly recommend executing this example before configuring your own projects.  Should only take 15-20 minutes.

For an example using postgres / `Northwind`, [click here](https://github.com/ApiLogicServer/docker-compose-nw-postgres).  In this example, you use an existing github project.

The docker files in this directory are from the MySQL project.  To adapt them to your own project, you will need to update the database section of the docker-compose files.

&nbsp;

## More information

For more information, see [DevOps Documentation](https://apilogicserver.github.io/Docs/DevOps-Containers/).
