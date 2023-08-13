Use these directories to rapidly deploy your system to the cloud.  This means you can provide a preview for your team:

* Developers can use the API to begin custom User Interface development

* **Business Users** can use the Admin App to see working software, enabling collaboration the the development team.

These directories simplify the sometimes-tricky deployment to the cloud. 

1. Use `auth-db` to prepare a docker image that includes test database data 

2. Start with `docker-image` - create an image for deployment

3. Use `docker-compose-dev-local` to verify multi-container (application, database) execution

4. Use `docker-compose-dev-localazure` to deploy this multi-container system to azure

5. Optionally, use `docker-compose-dev-local-nginx` to explore an additional web server container - nginx

> For more information, [click here](https://apilogicserver.github.io/Docs/DevOps-Containers-Deploy-Multi/).