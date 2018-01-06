#!/usr/bin/env bash

cd `dirname $0`

# Extract the package

tar -xzf deploy_package.tgz
#rm deploy_package.tgz

# Copy any file we want to keep from build to build



# Swap it all around, keeping the previous version aside in case something goes wrong

rm -rf AIC_backup
mv AIC AIC_backup
mv build AIC

cp -r Database Database_backup_2
rm -rf Database_backup
mv Database_backup_2 Database_backup

cd AIC

#####################################
# BAD PRACTICE
docker stop $(docker ps -q)
docker rm $(docker ps -aq)
#####################################

docker-compose build
docker-compose up -d