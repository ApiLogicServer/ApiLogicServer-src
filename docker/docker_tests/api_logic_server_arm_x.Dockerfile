# docker build -f docker/api_logic_server_arm_x.Dockerfile -t apilogicserver/api_logic_server_arm_x --rm .
# docker tag apilogicserver/api_logic_server_arm_x apilogicserver/api_logic_server_arm_x:9.00.14
# docker push apilogicserver/api_logic_server_arm_x:9.00.14

# cd ~/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/dockers
# docker run -it --name api_logic_server-arm-slim --rm --net dev-network -p 5656:5656 -p 5002:5002 -v ${PWD}:/localhost apilogicserver/arm-slim
# cd ~/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/dockers; docker run -it --name api_logic_server-arm-slim --rm --net dev-network -p 5656:5656 -p 5002:5002 -v ${PWD}:/localhost apilogicserver/arm-slim
# works, slow, 531MB w/o odbc, 895 w/ odbc

# if builds fails, check for renamed targets by breaking up Run commands

# thanks: https://stackoverflow.com/questions/71414579/how-to-install-msodbcsql-in-debian-based-dockerfile-with-an-apple-silicon-host
# else:   ERROR: failed to solve: process "/bin/sh -c ACCEPT_EULA=Y apt-get install -y msodbcsql18" did not complete successfully: exit code: 100

FROM python:3.11.4-slim-bullseye
# ARG TARGETPLATFORM=linux/arm/v7 VSC fails to load Python; this doesn't help

USER root

RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y git

RUN apt-get update
RUN apt-get install -y curl gnupg

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

#Debian 11
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update

RUN ACCEPT_EULA=Y apt-get install -y msodbcsql18

# optional: for bcp and sqlcmd
RUN apt-get install apt-utils

RUN ACCEPT_EULA=Y apt-get install -y mssql-tools18
RUN echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
RUN ~/.bashrc
# optional: for unixODBC development headers
# RUN apt-get install -y unixodbc-dev
# optional: kerberos library for debian-slim distributions
# RUN apt-get install -y libgssapi-krb5-2
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