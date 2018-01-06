#!/usr/bin/env bash

cd `dirname $0`

LINE='###############################################################################################################'


echo $LINE; echo '~~~~~>   EXTRACTING PACKAGE'; echo
tar -xzf deploy_package.tgz
echo '~~~~~>   DONE'

# Copy any file we want to keep from build to build



# Swap it all around, keeping the previous version aside in case something goes wrong

echo $LINE; echo '~~~~~>   COMMITTING PACKAGE BACKUP'; echo
rm -rf AIC_backup
mv AIC AIC_backup
mv build AIC
echo '~~~~~>   DONE'
echo $LINE; echo '~~~~~>   COMMITTING DATABASE BACKUP'; echo
docker exec aic_db_cont bash -c 'pg_dumpall > /Database_backup/aic_site_postgres_backup_2 --username=postgres'
rm -f Database_backup/aic_site_postgres_backup
mv Database_backup/aic_site_postgres_backup_2 Database_backup/aic_site_postgres_backup
echo '~~~~~>   DONE'

cd AIC

#####################################
# BAD PRACTICE
echo $LINE; echo '~~~~~>   STOPPING PREVIOUS CONTAINERS'; echo
docker stop $(docker ps -q)
echo '~~~~~>   DONE'
echo $LINE; echo '~~~~~>   REMOVING PREVIOUS CONTAINERS'; echo
docker rm $(docker ps -aq)
echo '~~~~~>   DONE'
#####################################

echo $LINE; echo '~~~~~>   BUILDING CONTAINERS'; echo
export DJANGO_SETTINGS_MODULE="aic_site.settings.production"
docker-compose build
echo '~~~~~>   DONE'
echo $LINE; echo '~~~~~>   FIRING UP CONTAINERS'; echo
docker-compose up -d
echo '~~~~~>   DONE'