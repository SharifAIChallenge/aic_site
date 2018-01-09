#!/usr/bin/env bash

DEPLOY_PASS=smallbrain
DEPLOY_USER=ssc
DEPLOY_PATH=/home/ssc/aic_site
DEPLOY_HOST=81.31.168.207

LINE='###############################################################################################################'


echo $LINE; echo '~~~~~>   CREATING DEPLOYMENT PACKAGE'; echo
mkdir build
rsync -r --exclude='.*' --exclude='build' ./ build
cd build/config/nginx/sites-available
cp aichallenge.sharif.edu ../sites-enabled
cd ../../../..
tar -czf deploy_package.tgz build
echo '~~~~~>   DONE'
echo $LINE; echo '~~~~~>   UPLOADING DEPLOYMENT PACKAGE'; echo
export SSHPASS=$DEPLOY_PASS
sshpass -e scp -o stricthostkeychecking=no deploy_package.tgz $DEPLOY_USER@$DEPLOY_HOST:$DEPLOY_PATH
rm -r build deploy_package.tgz
echo '~~~~~>   DONE'
echo $LINE; echo '~~~~~>   UPLOADING DEPLOYMENT SCRIPT'; echo
sshpass -e scp -o stricthostkeychecking=no deploy.sh $DEPLOY_USER@$DEPLOY_HOST:$DEPLOY_PATH
echo '~~~~~>   DONE'
echo $LINE; echo '~~~~~>   DEPLOYING...'; echo
sshpass -e ssh $DEPLOY_USER@$DEPLOY_HOST chmod +x $DEPLOY_PATH/deploy.sh
sshpass -e ssh $DEPLOY_USER@$DEPLOY_HOST $DEPLOY_PATH/deploy.sh
echo '~~~~~>   DEPLOYMENT DONE SUCCESSFULLY!'