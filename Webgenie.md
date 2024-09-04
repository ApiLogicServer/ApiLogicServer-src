# Build container

```bash
docker build -f docker/webgenie.Dockerfile -t apilogicserver/webgenie --rm .
```

# Run
Without persistence (projects are deleted when container shuts down):

```bash
docker run -it --rm --name webgenie -p 8080:80 --env-file /opt/webgenai_env apilogicserver/webgenie
```

The web interface is accessible at http://localhost:8080

To keep the projects on the host, mount a writable folder in the container (`/opt/projects`):
```bash
mkdir projects
chmod 777 projects
docker run -it --rm --name webgenie -p 8080:80 --env-file /opt/webgenai_env $PWD/projects: apilogicserver/webgenie
```

