#!/usr/bin/env bash

# Exit script if you try to use an uninitialized variable.
set -o nounset

# Exit script if a statement returns a non-true return value.
set -o errexit

# Use the error status of the first failure, rather than that of the last item in a pipeline.
set -o pipefail

# `sudo npm install` often causes '/usr/local/bin/sls: Permission denied' error
# This magically fixes it. I think this is because the docker image we are using did not install
# node correctly.
export NPM_CONFIG_PREFIX=/home/circleci/.npm-global
export PATH=$PATH:/home/circleci/.npm-global/bin 

npm install -g serverless
npm install --save serverless-python-requirements
npm install # any other dependencies 
