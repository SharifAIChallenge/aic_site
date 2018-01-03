#!/usr/bin/env bash

DEPLOY_PASS=smallbrain
DEPLOY_USER=ssc
DEPLOY_PATH=/home/ssc/aic_2017_deploy_test
DEPLOY_HOST=81.31.168.207


mkdir build
rsync -r --exclude='.*' --exclude='build' ./ build
tar -czf deploy_package.tgz build
export SSHPASS=$DEPLOY_PASS
sshpass -e scp -o stricthostkeychecking=no deploy_package.tgz $DEPLOY_USER@$DEPLOY_HOST:$DEPLOY_PATH
sshpass -e scp -o stricthostkeychecking=no deploy.sh $DEPLOY_USER@$DEPLOY_HOST:$DEPLOY_PATH
sshpass -e ssh $DEPLOY_USER@$DEPLOY_HOST chmod +x $DEPLOY_PATH/deploy.sh
sshpass -e ssh $DEPLOY_USER@$DEPLOY_HOST $DEPLOY_PATH/deploy.sh

rm -r build deploy_package.tgz