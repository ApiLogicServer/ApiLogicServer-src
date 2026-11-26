**New to the container setup?  Start with the [DevOps Quick Start](https://apilogicserver.github.io/Docs/DevOps-Quick-Start/):** install, run your project in the standard container, and validate it in about 15 minutes.

&nbsp;

## Container options

This project runs in the **standard image**, `apilogicserver/api_logic_server` (Python, the libraries, API Logic Server): no per-project build is required.  It is a plain Flask app; the container needs nothing but your project folder and environment variables.

1. **Run in the standard image** - `devops/docker-standard-image` (start here, no build)

    ```bash
    cd <project>
    docker run -it --rm --name api_logic_project -p 5656:5656 -v ${PWD}:/app apilogicserver/api_logic_server python3 /app/api_logic_server_run.py
    ```

    Or use `docker compose -f devops/docker-standard-image/docker-compose-standard-image.yml up`.  Open `http://localhost:5656`.

2. **Build your own image** - `devops/docker-image` (the project is baked into an image you can push to a registry).  Extend the standard image, so only your project is added:

    ```
    FROM apilogicserver/api_logic_server
    ```

    ```bash
    sh devops/docker-image/build_image.sh .     # build locally
    sh devops/docker-image/run_image.sh         # run it
    ```

    Need an additional Python package?  Add `RUN pip install <package>` to `build_image.dockerfile`.

Podman: type `podman` for `docker`, and `export CONTAINER_CLI=podman` so the scripts above use it.

Configuration (database URI, security, ports) is by environment variable - see `env.list` in either directory.

&nbsp;

## Dev, pre-prod and prod

One image runs in every environment; only its environment variables differ.  Dev uses `config/default.env` (see `config/readme-config.md`).  Pre-prod and prod get their settings from the deployment and their secrets from a secrets store, never from a committed file.

`docker-compose-prod` runs a prod-shaped environment on your machine: the project's image, `APILOGICPROJECT_ENV=prod`, and secrets from a gitignored `secrets.env` (copy it from `secrets.env.example`, which explains each value).  With SQL security, the server refuses to start in prod until you set a real `SECRET_KEY`.

Pre-prod (test, staging) uses the same folder: on the pre-prod machine, its own `secrets.env` holds the pre-prod database and key, and `APILOGICPROJECT_ENV=preprod docker compose -f docker-compose-prod.yml up` starts it.  There is deliberately no `docker-compose-test`: one deployment definition, different values per environment.

> Walkthrough, including creating the prod database and migrating its schema with Alembic: [DevOps Quick Start: Dev to Prod](https://apilogicserver.github.io/Docs/DevOps-Quick-Start-Dev-to-Prod/).

&nbsp;

## Deploying to the cloud

Use these directories to deploy your system to the cloud.  This means you can provide a preview of [working software](https://apilogicserver.github.io/Docs/Working-Software-Now/) for your team:

* **Developers** can use the API to begin custom User Interface development

* **Business Users** can use the Admin App to see *working screens*, enabling **collaboration** with the development team.

> For example procedures, [click here](https://apilogicserver.github.io/Docs/DevOps-Containers-Deploy-Multi/).

1. Use `auth-db` to prepare a docker image that includes test database data, including security

2. Start with `docker-image` to create an image for deployment

3. Use `docker-compose-dev-local` to verify multi-container (application, database) execution

4. Use `docker-compose-dev-azure` to deploy this multi-container system to azure

5. Optionally, use `docker-compose-dev-local-nginx` to explore an additional web server container - nginx
