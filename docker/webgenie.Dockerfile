
# GA release -- DELETE BUILD DIRS FIRST

# docker build -f docker/webgenie.Dockerfile -t apilogicserver/webgenie --no-cache  --rm .

# docker buildx build --push -f docker/webgenie.Dockerfile --tag apilogicserver/webgenie:11.00.20 -o type=image --platform=linux/arm64,linux/amd64 .
# docker buildx build --push -f docker/webgenie.Dockerfile --tag apilogicserver/webgenie:latest -o type=image --platform=linux/arm64,linux/amd64 .

# Beta - test codespaces with tutorial, API_Fiddle (change .devcontainer.json -> apilogicserver/webgenie_x)
# docker buildx build --push -f docker/webgenie.Dockerfile --tag apilogicserver/webgenie_x:9.05.00 -o type=image --platform=linux/arm64,linux/amd64 .

# Internal - verify what is done with build_and_test
# docker build -f docker/webgenie.Dockerfile -t apilogicserver/webgenie_local --rm .
# docker tag apilogicserver/webgenie_local apilogicserver/webgenie_local:latest
#    -- now run locally:
# docker run -it apilogicserver/webgenie_local  # minimal (no ports, no mounts, no network, files protected)
# cd ~/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/dockers
# docker run -it --name api_logic_server --rm --net dev-network -p 5656:5656 -p 5002:5002 -v ${PWD}:/localhost apilogicserver/webgenie_local
#    -- but not this (fails complaining about $PATH, tho echo $PATH has /home/api_logic_server/bin
# docker run -it apilogicserver/webgenie_local ApiLogicServer create-and-run --project_name=api_logic_project --db_url=
# Thos scenario (cd first)...
# docker run -it --name api_logic_server --rm -v ${PWD}:/localhost apilogicserver/webgenie_local ApiLogicServer create --project_name=/localhost/nw --db_url=
# docker run -it --name api_logic_server --rm -p 5656:5656 -p 5002:5002 -v ${PWD}:/localhost apilogicserver/webgenie_local ApiLogicServer run --project_name=/localhost/nw


# docker run -it --name api_logic_server_local --rm --net dev-network -p 5656:5656 -p 5002:5002 -v .:/localhost apilogicserver/webgenie_local
# docker run -it --name api_logic_server_local --rm --net dev-network -p 5656:5656 -p 5002:5002 -v {str(dest)}:/localhost apilogicserver/webgenie_local sh -c "export PATH=$PATH:/home/api_logic_server/bin && /bin/sh /localhost/docker-commands.sh"

# dev containers: https://apilogicserver.github.io/Docs/DevOps-Docker/
# run containers: https://apilogicserver.github.io/Docs/DevOps-Containers-Build/

# cd ~/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/dockers
# docker run -it --name api_logic_server --rm --net dev-network -p 5656:5656 -p 5002:5002 -v ${PWD}:/localhost apilogicserver/webgenie

# https://medium.com/geekculture/docker-build-with-mac-m1-d668c802ab96#id_token=eyJhbGciOiJSUzI1NiIsImtpZCI6IjY3NmRhOWQzMTJjMzlhNDI5OTMyZjU0M2U2YzFiNmU2NTEyZTQ5ODMiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJuYmYiOjE2ODk1Mzk1NjgsImF1ZCI6IjIxNjI5NjAzNTgzNC1rMWs2cWUwNjBzMnRwMmEyamFtNGxqZGNtczAwc3R0Zy5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbSIsInN1YiI6IjEwOTU2MTk5NTc1MzE3MTM0NTcyOSIsImVtYWlsIjoidmFsamh1YmVyQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJhenAiOiIyMTYyOTYwMzU4MzQtazFrNnFlMDYwczJ0cDJhMmphbTRsamRjbXMwMHN0dGcuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJuYW1lIjoiVmFsIEh1YmVyIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FBY0hUdGZFeFUxNTllcVNUSGpXYm9qS2pfaG5WY3VZRjRxeXUtMkN6SGRzc1dTZmNvVT1zOTYtYyIsImdpdmVuX25hbWUiOiJWYWwiLCJmYW1pbHlfbmFtZSI6Ikh1YmVyIiwiaWF0IjoxNjg5NTM5ODY4LCJleHAiOjE2ODk1NDM0NjgsImp0aSI6Ijc0YWM4NGQ3YzhjNWEwZTE3YjMzMDdjYjRlOTJhMzFjNDMzZjdiMWQifQ.VvCoA5Dd2KYhOvlkh8ejR_gp-vt83rpSbKYfL5xImYxj_99fdZOaEJJVNfP3mzzzyRhiQousI2aPVEdv51TKwG4FxVAnTOikjYp88y1WE3cOk_46ci-kavsHH0vN3zK3CI3-FK889yxIPbna8Wo_A8USwbLZcwTRucG7dKceRL9J0UcVgLk4JRv5ZQ1TJ_y5yLcddvSo_79x4O7fIX6WmrDHOfK16EqPYtsqyE1PuSnJtdddyP_ZLsRcDJflb5iHAIuNkQz1soL4fdOlh5T57pl734igWdbJNSufSKpLm9RzVN_E-Dvkk7ND6tEuOMs09DUdXhArcS_PTprQmYqE2g
# 823MB

# https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16&tabs=alpine18-install%2Calpine17-install%2Cdebian8-install%2Credhat7-13-install%2Crhel7-offline

# if builds fails, check for renamed targets by breaking up Run commands

FROM python:3.12.3-slim-bullseye
# FROM python:3.12.3-alpine3.19  - fails /bin/sh -c apt-get update
ARG TARGETOS
ARG TARGETARCH
# LABEL ApiLogicServer-10.03.45 ${TARGETARCH}
LABEL product="ApiLogicServer-11.00.07" targetarch=${TARGETARCH}
USER root

RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y git

RUN apt-get update
RUN apt-get install -y curl gnupg
RUN apt-get install -y nginx

# ODBC: https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16&tabs=debian18-install%2Calpine17-install%2Cdebian8-install%2Credhat7-13-install%2Crhel7-offline
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

#Debian 11
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update

RUN ACCEPT_EULA=Y apt-get install -y msodbcsql18

# optional: for bcp and sqlcmd
RUN apt-get install apt-utils


RUN apt-get -y install unixodbc-dev \
  && apt-get -y install python3-pip \
  && pip install pyodbc==5.1.0

RUN useradd --create-home --shell /bin/bash api_logic_server
WORKDIR /home/api_logic_server
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
USER api_logic_server
COPY . .

USER root
RUN chmod +x bin/ApiLogicServer \
    && chmod +x bin/py
    #&& chmod a+rwx -R api_logic_server_cli/api_logic_server_info.yaml \
RUN mkdir -p /home/api_logic_project \
    && chown -R api_logic_server /home/api_logic_project
USER api_logic_server

ENV APILOGICSERVER_RUNNING=DOCKER
ENV APILOGICSERVER_FROM=python:3.11.4-slim-bullseye
ENV PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/api_logic_server/bin


# Webgenie
USER root
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/wg.conf /etc/nginx/wg.conf
RUN mkdir /etc/nginx/apis
#RUN mkdir /var/log/nginx
RUN chown -R api_logic_server /var/log/nginx /etc/nginx/apis
RUN chown api_logic_server /var/lib/nginx
RUN chmod 777 /run # TODO!! security issue?
#RUN  usermod -aG adm api_logic_server


RUN mkdir -p /opt/projects
COPY webgenai /opt/webgenai
RUN chown -R api_logic_server /opt /home/api_logic_server
USER api_logic_server

#COPY sra-build /home/api_logic_server/api_logic_server_cli/create_from_model/safrs-react-admin-npm-build
#COPY sra-build /var/www/html/admin-app

EXPOSE 5656-7000
# EXPOSE 5002

#CMD ["bash"]
CMD ["bash", "-c", "/opt/webgenai/arun.sh"]

