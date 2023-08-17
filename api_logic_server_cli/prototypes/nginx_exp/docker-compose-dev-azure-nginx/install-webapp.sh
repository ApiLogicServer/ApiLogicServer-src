#!/bin/bash

# typically run from project root
# sh ./devops/docker-compose/install-webapp.sh

# obtain the web directories

if [ -d "etc" ] 
then
    echo "\n... starting\n"
else
    echo "\n.. cd ./devops/docker-compose-dev-azure-nginx \n" 
    cd ./devops/docker-compose-dev-azure-nginx
fi

read -p "Ready to obtain web app files, press ENTER to proceed> "

curl https://github.com/thomaxxl/safrs-react-admin/releases/download/0.1.2/safrs-react-admin-0.1.2.zip -LO
echo "unzipping sra to build.."
set +x
unzip safrs-react-admin-0.1.2.zip
set -x

echo "\nrenaming to wwwadmin-app"
mkdir www
mv build www/admin-app
