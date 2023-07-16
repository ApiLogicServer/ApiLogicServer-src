# docker build -f docker/install-odbc.Dockerfile -t apilogicserver/install-odbc --rm .

# https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16&tabs=debian18-install%2Calpine17-install%2Cdebian8-install%2Credhat7-13-install%2Crhel7-offline

FROM python:3.11.4-slim-bullseye

RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y git

RUN apt-get update
RUN apt-get install -y curl gnupg

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

#Debian 11
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN ACCEPT_EULA=Y apt-get install -y msodbcsql18

# optional: for bcp and sqlcmd
RUN ACCEPT_EULA=Y apt-get install -y mssql-tools18
RUN echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
RUN ~/.bashrc
# optional: for unixODBC development headers
RUN apt-get install -y unixodbc-dev
# optional: kerberos library for debian-slim distributions
# RUN apt-get install -y libgssapi-krb5-2