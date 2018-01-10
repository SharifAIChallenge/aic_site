#!/usr/bin/env bash

DEPLOY_PASS=smallbrain
DEPLOY_USER=ssc
DEPLOY_PATH=/home/ssc/aic_site
DEPLOY_HOST=81.31.168.207

LINE='###############################################################################################################'


echo $LINE; echo '~~~~~>   GATHERING DEPLOYMENT FILES'; echo
mkdir build
rsync -r --exclude='.*' --exclude='build' ./ build
cd build/config/nginx/sites-available
cp aichallenge.sharif.edu ../sites-enabled
cd ../../../..
echo '~~~~~>   DONE'
echo $LINE; echo '~~~~~>   OPTIMIZING IMAGES FOR DEPLOYMENT'; echo
cd build/apps/
find . -iname '*.png' -print0 | xargs -0 optipng -o7 -preserve
find . -iname '*.jpg' -print0 | xargs -0 jpegoptim --max=90 --strip-all --preserve --totals
cd ../..
echo '~~~~~>   DONE'
echo $LINE; echo '~~~~~>   COMPRESSING DEPLOYMENT PACKAGE'; echo
tar -czf deploy_package.tgz build
echo '~~~~~>   DONE'
echo $LINE; echo '~~~~~>   UPLOADING DEPLOYMENT PACKAGE'; echo
export SSHPASS=$DEPLOY_PASS
sshpass -e rsync --progress -avzhe 'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null' \
 deploy_package.tgz $DEPLOY_USER@$DEPLOY_HOST:$DEPLOY_PATH
rm -r build deploy_package.tgz
echo '~~~~~>   DONE'
echo $LINE; echo '~~~~~>   UPLOADING DEPLOYMENT SCRIPT'; echo
sshpass -e rsync --progress -avzhe 'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null' \
 deploy.sh $DEPLOY_USER@$DEPLOY_HOST:$DEPLOY_PATH
echo '~~~~~>   DONE'
echo $LINE; echo '~~~~~>   DEPLOYING...'; echo
sshpass -e ssh $DEPLOY_USER@$DEPLOY_HOST chmod +x $DEPLOY_PATH/deploy.sh
sshpass -e ssh $DEPLOY_USER@$DEPLOY_HOST $DEPLOY_PATH/deploy.sh
echo '~~~~~>   DEPLOYMENT DONE SUCCESSFULLY!'