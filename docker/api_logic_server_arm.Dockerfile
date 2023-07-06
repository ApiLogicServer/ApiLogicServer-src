# docker build -f docker/api_logic_server_arm.Dockerfile -t apilogicserver/api_logic_server_arm --rm .
# docker tag apilogicserver/api_logic_server_arm apilogicserver/api_logic_server_arm:9.01.03
# docker push apilogicserver/api_logic_server_arm:9.01.03

# cd ~/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/dockers
# docker run -it --name api_logic_server-arm-slim --rm --net dev-network -p 5656:5656 -p 5002:5002 -v ${PWD}:/localhost apilogicserver/arm-slim
# cd ~/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/dockers; docker run -it --name api_logic_server-arm-slim --rm --net dev-network -p 5656:5656 -p 5002:5002 -v ${PWD}:/localhost apilogicserver/arm-slim
# works, slow, 531MB w/o odbc, 895 w/ odbc

# if builds fails, check for renamed targets by breaking up Run commands

# odbc fails if enabled... 
# else:   ERROR: failed to solve: process "/bin/sh -c ACCEPT_EULA=Y apt-get install -y msodbcsql18" did not complete successfully: exit code: 100
# thanks: https://stackoverflow.com/questions/71414579/how-to-install-msodbcsql-in-debian-based-dockerfile-with-an-apple-silicon-host
# see:    api_logic_server_arm_x

FROM python:3.11.4-slim-bullseye

USER root

RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y git

# RUN apt-get update
# RUN apt-get install -y curl gnupg
# RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
# RUN curl -sSL https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
# RUN apt-get update
# RUN ACCEPT_EULA=Y apt-get install -y msodbcsql18

# RUN apt-get -y install unixodbc-dev \
#   && apt-get -y install python3-pip \
#   && pip install pyodbc==4.0.34

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