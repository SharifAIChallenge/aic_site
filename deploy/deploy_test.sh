#!/usr/bin/env bash

cd `dirname $0`

LINE='###############################################################################################################'


echo $LINE; echo '~~~~~>   EXTRACTING PACKAGE'; echo
tar -xzf deploy_test_package.tgz
rm deploy_test_package.tgz
echo '~~~~~>   DONE'

# Copy any file we want to keep from build to build



# Swap it all around, keeping the previous version aside in case something goes wrong

echo $LINE; echo '~~~~~>   COMMITTING PACKAGE BACKUP'; echo
sudo rm -rf AIC_test_backup
sudo mv AIC_test AIC_test_backup
echo "moving build_test as AIC_test"
mv build_test AIC_test
echo '~~~~~>   DONE'
echo $LINE; echo '~~~~~>   COMMITTING DATABASE BACKUP'; echo
docker exec aic_test_db_cont bash -c 'pg_dumpall > /Database_backup/aic_test_site_postgres_backup_2 --username=postgres'
sudo rm -f Database_backup/aic_test_site_postgres_backup
sudo mv Database_backup/aic_test_site_postgres_backup_2 Database_backup/aic_test_site_postgres_backup
echo '~~~~~>   DONE'

cd AIC_test/

#####################################
# GOOD PRACTICE :)
echo $LINE; echo '~~~~~>   STOPPING PREVIOUS CONTAINERS'; echo
docker stop aic_test_nginx_cont
docker stop aic_test_web_cont
docker stop aic_test_db_cont
echo '~~~~~>   DONE'
echo $LINE; echo '~~~~~>   REMOVING PREVIOUS CONTAINERS'; echo
docker rm aic_test_nginx_cont
docker rm aic_test_web_cont
docker rm aic_test_db_cont
echo '~~~~~>   DONE'
#####################################

echo $LINE; echo '~~~~~>   BUILDING CONTAINERS'; echo
export DJANGO_SETTINGS_MODULE="aic_site.settings.production_test"
docker-compose -f docker-compose.yml build
echo '~~~~~>   DONE'
echo $LINE; echo '~~~~~>   FIRING UP CONTAINERS'; echo
docker-compose -f docker-compose.yml up -d

echo $LINE; echo '~~~~~>   REMOVING DEPLOYMENT SCRIPT'; echo
rm -f ../deploy_test.sh
echo '~~~~~>   DONE'