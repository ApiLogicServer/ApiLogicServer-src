# docker build -f docker/api_logic_server_x.Dockerfile -t apilogicserver/api_logic_server_x --rm .
# docker tag apilogicserver/api_logic_server_x apilogicserver/api_logic_server_x:09.01.11
# docker push apilogicserver/api_logic_server_x:09.01.11

# docker run -it --name api_logic_server --rm -p 5656:5656 -p 5002:5002 -v ~/dev/servers:/localhost apilogicserver/api_logic_server_x
#   docker run -it --name api_logic_server --rm --net dev-network -p 5656:5656 -p 5002:5002 -v ${PWD}:/localhost apilogicserver/api_logic_server_x
#   docker image inspect apilogicserver/api_logic_server
#   docker run -it --name api_logic_server --rm -p 5656:5656 -p 5002:5002 -v ${PWD}:/localhost apilogicserver/api_logic_server-x
#   docker run -it --name api_logic_server --rm --net dev-network -p 5656:5656 -p 5002:5002 -v ${PWD}:/localhost apilogicserver/api_logic_server_x sh /localhost/Start.sh hullo

# The software auto-prompts you for the next steps (assuming {"HOST_IP": "10.0.0.234"}):
# ApiLogicServer run --project_name=/localhost/api_logic_server --db_url=
#   ApiLogicServer create  --project_name=/localhost/sqlsvr-nw-docker --db_url=sqlsvr-nw-docker
#   ApiLogicServer create --project_name=/localhost/sqlserver --db_url='mssql+pyodbc://sa:Posey3861@10.0.0.234:1433/NORTHWND?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=no&Encrypt=no'
#   ApiLogicServer create --project_name=/localhost/classicmodels --db_url=mysql+pymysql://root:p@mysql-container:3306/classicmodels
#   ApiLogicServer create --project_name=/localhost/postgres --db_url=postgresql://postgres:p@postgresql-container/postgres
#   python /localhost/api_logic_server/api_logic_server_run.py

# shout outs...
#   Thmomas Pollet          https://github.com/thomaxxl/safrs-react-admin -- safrs, safrs-react-admin
#   Max Tardiveau           https://www.galliumdata.com/
#   Shantanu                https://forum.astronomer.io/t/how-to-pip-install-pyodbc-in-the-dockerfile/983
#   Piotr Maślewski         https://medium.com/swlh/dockerize-your-python-command-line-program-6a273f5c5544
#   MS:                     https://github.com/microsoft/vscode-dev-containers/tree/main/containers/python-3
#   itamar@pythonspeed.com  https://pythonspeed.com/articles/base-image-python-docker-images/

# Runs with SqlServer, 895M

# if builds fails, check for renamed targets by breaking up Run commands

FROM python:3.11.4-slim-bullseye
#    python:3.11-slim-bullseye - runs  sqlsvr-nw-docker, 838M
#    python:3.11-slim-bookworm - fails sqlsvr-nw-docker
#    python:3.11.4             - fails sqlsvr-nw-docker, 1.4G
#    mcr.microsoft.com/devcontainers/python:3.11-bullseye - runs  sqlsvr-nw-docker, 1.77G

USER root

RUN apt-get update \
  && apt-get install -y curl \
  && apt-get install -y git

RUN apt-get update
RUN apt-get install -y curl gnupg
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl -sSL https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql18

# TODO RUN wget https://packages.microsoft.com/debian/10/prod/pool/main/m/mssql-tools/mssql-tools_17.8.1.1-1_amd64.deb;

RUN apt-get -y install unixodbc-dev \
  && apt-get -y install python3-pip \
  && pip install pyodbc==4.0.34

RUN useradd --create-home --shell /bin/bash api_logic_server
WORKDIR /home/api_logic_server
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
USER api_logic_server
COPY . .
# EXPOSE 5000:5000
# EXPOSE 8080
USER root
RUN chmod +x bin/ApiLogicServer \
    && chmod a+rwx -R api_logic_server_cli/api_logic_server_info.yaml \
    && chmod +x bin/py
# CMD ["ApiLogicServer"]
USER api_logic_server

ENV APILOGICSERVER_RUNNING=DOCKER
ENV APILOGICSERVER_FROM=python:3.11.4-slim-bullseye

# RUN chmod a+rwx -R api_logic_server_cli/api_logic_server_info.yaml
CMD ["bash"]