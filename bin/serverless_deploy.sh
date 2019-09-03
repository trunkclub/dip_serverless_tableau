#!/usr/bin/env bash

# Exit script if you try to use an uninitialized variable.
set -o nounset

# Exit script if a statement returns a non-true return value.
set -o errexit

# Use the error status of the first failure, rather than that of the last item in a pipeline.
set -o pipefail

CREDS=""

circle_branch=$1

if [ "$circle_branch" == "production" ]; then
echo "Branch is $circle_branch; Assuming Prod Serverless Role"

CREDS=$(aws sts assume-role --role-arn arn:aws:iam::592554832856:role/serverless_role --role-session-name serverless-tableau-deploy)
# This is the role that the serverless lambdas will use. 
# Its referenced in serverless.yaml .
export TABLEAU_ROLE=arn:aws:iam::592554832856:role/tableau_lambda_serverless_role
STAGE=prod

else 
echo "Branch is $circle_branch; Assuming Dev Serverless Role"
CREDS=$(aws sts assume-role --role-arn arn:aws:iam::985139809500:role/serverless_role --role-session-name serverless-tableau-deploy)
export TABLEAU_ROLE=arn:aws:iam::985139809500:role/tableau_lambda_serverless_role
STAGE=dev

fi

export AWS_ACCESS_KEY_ID=$(echo $CREDS | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo $CREDS | jq -r '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(echo $CREDS | jq -r '.Credentials.SessionToken')

echo 'Deploying...'

# `sudo npm install` often causes '/usr/local/bin/sls: Permission denied' error,
# Not using `sudo npm install`, and instead adding these parameters while installing
# magically fixes it. I think this is because the docker image we are using did not install
# node correctly. Tried a few different images and circle doesn't have 
# one with a better install easily available. You also neede these parameters
# when running sls deploy. 

export NPM_CONFIG_PREFIX=/home/circleci/.npm-global
export PATH=$PATH:/home/circleci/.npm-global/bin 

sls deploy --stage $STAGE

echo "Finished."
