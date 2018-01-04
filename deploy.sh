#!/usr/bin/env bash

cd `dirname $0`

# Extract the package

tar -xzf deploy_package.tgz
#rm deploy_package.tgz

# Copy any file we want to keep from build to build



# Swap it all around, keeping the previous version aside in case something goes wrong

rm -rf AIC_test_old
mv AIC_test AIC_test_old
mv build AIC_test

cd AIC_test
docker-compose build
docker-compose up