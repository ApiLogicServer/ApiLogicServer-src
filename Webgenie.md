# Build container

```bash
docker build -f docker/webgenie.Dockerfile -t apilogicserver/webgenie --rm .
```

# Run

Without persistence (projects are deleted when container is deleted):

```bash
docker run -it --rm --name webgenie -p 8080:80 --env-file webgenie.env apilogicserver/webgenie
```

The web interface is accessible at http://localhost:8080

To keep the projects on the host, mount a writable folder in the container (`/opt/projects`):
```bash
mkdir projects
chmod 777 projects
docker run -it --rm --name webgenie -p 8080:80 --env-file webgenie.env $PWD/projects: apilogicserver/webgenie
```

Configuration parameters are set in the environment. (`--env-file` container argument)
```
# Nginx port
APILOGICPROJECT_EXTERNAL_PORT=8080

# Gunicorn port (nginx will reverse proxy to this port)
APILOGICPROJECT_PORT=5657

# OpenAI API key
APILOGICSERVER_CHATGPT_APIKEY=sk-proj-

# Webgenie security configuration
# login password for the admin user
# ADMIN_PASSWORD=password
```


