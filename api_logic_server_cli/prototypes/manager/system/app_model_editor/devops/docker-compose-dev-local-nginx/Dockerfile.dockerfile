# Invoked by build command of service: api_logic_server

# ensure platform for common amd deployment, even if running on M1/2 mac --platform=linux/amd64
FROM --platform=linux/amd64 apilogicserver/api_logic_server

EXPOSE 5000

USER root

# user api_logic_server comes from apilogicserver/api_logic_server
WORKDIR /app/ApiLogicProject
USER api_logic_server
COPY ../../../ .