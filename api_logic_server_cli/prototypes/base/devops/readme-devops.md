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
