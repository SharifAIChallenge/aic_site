#!/usr/bin/env bash

cd `dirname $0`

# Extract the package

tar -xzf deploy_package.tgz
rm deploy_package.tgz

# Copy any file we want to keep from build to build



# Swap it all around, keeping the previous version aside in case something goes wrong

rm -rf www_old
mv www www_old
mv build www

cd www
docker-compose up