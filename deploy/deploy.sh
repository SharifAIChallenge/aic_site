#!/usr/bin/env bash

cd `dirname $0`

LINE='###############################################################################################################'


echo $LINE; echo '~~~~~>   EXTRACTING PACKAGE'; echo
tar -xzf deploy_package.tgz
rm deploy_package.tgz
echo '~~~~~>   DONE'

# Copy any file we want to keep from build to build



# Swap it all around, keeping the previous version aside in case something goes wrong

echo $LINE; echo '~~~~~>   COMMITTING PACKAGE BACKUP'; echo
sudo rm -rf AIC_backup
sudo mv AIC AIC_backup
echo "moving build as AIC"
mv build AIC
echo '~~~~~>   DONE'
echo $LINE; echo '~~~~~>   COMMITTING DATABASE BACKUP'; echo
docker exec aic_db_cont bash -c 'pg_dumpall > /Database_backup/aic_site_postgres_backup_2 --username=postgres'
sudo rm -f Database_backup/aic_site_postgres_backup
sudo mv Database_backup/aic_site_postgres_backup_2 Database_backup/aic_site_postgres_backup
echo '~~~~~>   DONE'

cd AIC/

#####################################
# GOOD PRACTICE :)
echo $LINE; echo '~~~~~>   STOPPING PREVIOUS CONTAINERS'; echo
docker stop aic_nginx_cont
docker stop aic_web_cont
docker stop aic_db_cont
echo '~~~~~>   DONE'
echo $LINE; echo '~~~~~>   REMOVING PREVIOUS CONTAINERS'; echo
docker rm aic_nginx_cont
docker rm aic_web_cont
docker rm aic_db_cont
echo '~~~~~>   DONE'
#####################################

echo $LINE; echo '~~~~~>   BUILDING CONTAINERS'; echo
export DJANGO_SETTINGS_MODULE="aic_site.settings.production"
docker-compose -f docker-compose.yml build
echo '~~~~~>   DONE'
echo $LINE; echo '~~~~~>   FIRING UP CONTAINERS'; echo
docker-compose -f docker-compose.yml up -d

echo $LINE; echo '~~~~~>   REMOVING DEPLOYMENT SCRIPT'; echo
rm -f ../deploy.sh
echo '~~~~~>   DONE'

echo $LINE; echo '~~~~~>   REMOVING OBSOLETE DOCKER IMAGES'; echo
docker rmi $(docker images | egrep -v "(ubuntu|nginx|postgres|aic_aic_web|aictest_aic_test_web)" | awk '{print $3}')
echo '~~~~~>   DONE'