## Using the standard container

There are many, many ways of using docker.

1. You can use the existing apilogicserver/api_logic_server container as shown in `devops/docker-standard-image`.

2. Or, you can create your own container, as described in the next section.

&nbsp;

## Creating per-project containers

Use these directories to deploy your system to the cloud.  This means you can provide a preview of [working software](https://apilogicserver.github.io/Docs/Working-Software-Now/) for your team:

* **Developers** can use the API to begin custom User Interface development

* **Business Users** can use the Admin App to see *working screens*, enabling **collaboration** with the development team.

> For example procedures, [click here](https://apilogicserver.github.io/Docs/DevOps-Containers-Deploy-Multi/).

These directories simplify the sometimes-tricky deployment to the cloud. 

1. Use `auth-db` to prepare a docker image that includes test database data, including security

2. Start with `docker-image` to create an image for deployment

3. Use `docker-compose-dev-local` to verify multi-container (application, database) execution

4. Use `docker-compose-dev-azure` to deploy this multi-container system to azure

5. Optionally, use `docker-compose-dev-local-nginx` to explore an additional web server container - nginx
