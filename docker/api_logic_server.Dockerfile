# GA release
# docker buildx build --push -f docker/api_logic_server.Dockerfile --tag apilogicserver/api_logic_server:9.02.03 -o type=image --platform=linux/arm64,linux/amd64 .

# Beta - test codespaces with tutorial, API_Fiddle (change .devcontainer.json -> apilogicserver/api_logic_server_x)
# docker buildx build --push -f docker/api_logic_server.Dockerfile --tag apilogicserver/api_logic_server_x:9.02.03 -o type=image --platform=linux/arm64,linux/amd64 .

# Internal - verify what is done with build_and_test
# docker build -f docker/api_logic_server.Dockerfile -t apilogicserver/api_logic_server_local --rm .
# docker tag apilogicserver/api_logic_server_local apilogicserver/api_logic_server_local:latest
# repeat with latest

# cd ~/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/dockers
# docker run -it --name api_logic_server --rm --net dev-network -p 5656:5656 -p 5002:5002 -v ${PWD}:/localhost apilogicserver/api_logic_server

# https://medium.com/geekculture/docker-build-with-mac-m1-d668c802ab96#id_token=eyJhbGciOiJSUzI1NiIsImtpZCI6IjY3NmRhOWQzMTJjMzlhNDI5OTMyZjU0M2U2YzFiNmU2NTEyZTQ5ODMiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJuYmYiOjE2ODk1Mzk1NjgsImF1ZCI6IjIxNjI5NjAzNTgzNC1rMWs2cWUwNjBzMnRwMmEyamFtNGxqZGNtczAwc3R0Zy5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbSIsInN1YiI6IjEwOTU2MTk5NTc1MzE3MTM0NTcyOSIsImVtYWlsIjoidmFsamh1YmVyQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJhenAiOiIyMTYyOTYwMzU4MzQtazFrNnFlMDYwczJ0cDJhMmphbTRsamRjbXMwMHN0dGcuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJuYW1lIjoiVmFsIEh1YmVyIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FBY0hUdGZFeFUxNTllcVNUSGpXYm9qS2pfaG5WY3VZRjRxeXUtMkN6SGRzc1dTZmNvVT1zOTYtYyIsImdpdmVuX25hbWUiOiJWYWwiLCJmYW1pbHlfbmFtZSI6Ikh1YmVyIiwiaWF0IjoxNjg5NTM5ODY4LCJleHAiOjE2ODk1NDM0NjgsImp0aSI6Ijc0YWM4NGQ3YzhjNWEwZTE3YjMzMDdjYjRlOTJhMzFjNDMzZjdiMWQifQ.VvCoA5Dd2KYhOvlkh8ejR_gp-vt83rpSbKYfL5xImYxj_99fdZOaEJJVNfP3mzzzyRhiQousI2aPVEdv51TKwG4FxVAnTOikjYp88y1WE3cOk_46ci-kavsHH0vN3zK3CI3-FK889yxIPbna8Wo_A8USwbLZcwTRucG7dKceRL9J0UcVgLk4JRv5ZQ1TJ_y5yLcddvSo_79x4O7fIX6WmrDHOfK16EqPYtsqyE1PuSnJtdddyP_ZLsRcDJflb5iHAIuNkQz1soL4fdOlh5T57pl734igWdbJNSufSKpLm9RzVN_E-Dvkk7ND6tEuOMs09DUdXhArcS_PTprQmYqE2g
# 823MB

# https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16&tabs=alpine18-install%2Calpine17-install%2Cdebian8-install%2Credhat7-13-install%2Crhel7-offline

# if builds fails, check for renamed targets by breaking up Run commands

FROM python:3.11.4-slim-bullseye
ARG TARGETOS
ARG TARGETARCH
LABEL ApiLogicServer-9.00.14 ${TARGETARCH}

USER root

RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y git

RUN apt-get update
RUN apt-get install -y curl gnupg

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
  && pip install pyodbc==4.0.34

RUN useradd --create-home --shell /bin/bash api_logic_server
WORKDIR /home/api_logic_server
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
USER api_logic_server
COPY . .

USER root
RUN chmod +x bin/ApiLogicServer \
    && chmod a+rwx -R api_logic_server_cli/api_logic_server_info.yaml \
    && chmod +x bin/py
USER api_logic_server

ENV APILOGICSERVER_RUNNING=DOCKER
ENV APILOGICSERVER_FROM=python:3.11.4-slim-bullseye

CMD ["bash"]