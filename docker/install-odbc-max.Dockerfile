# docker build -f docker/install-odbc-max.Dockerfile -t apilogicserver/install-odbc-max --rm .

FROM python:3.11.4-slim-bullseye

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
# RUN ~/.bashrc
# optional: for unixODBC development headers
# RUN apt-get install -y unixodbc-dev
# optional: kerberos library for debian-slim distributions
# RUN apt-get install -y libgssapi-krb5-2