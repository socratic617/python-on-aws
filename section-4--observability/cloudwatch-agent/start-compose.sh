#!/bin/bash

THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

function create_aws_credentials_to_mount_into_cloudwatch_agent_container {
    # export cloud-course profile to .env file
    eval $(aws configure export-credentials --profile cloud-course --format env-no-export)
    aws configure export-credentials --profile cloud-course --format env > .env
    export AWS_REGION=${AWS_REGION:-us-west-2}

    mkdir -p $THIS_DIR/.aws

    echo "\
[AmazonCloudWatchAgent]
aws_access_key_id = $AWS_ACCESS_KEY_ID
aws_secret_access_key = $AWS_SECRET_ACCESS_KEY
" > $THIS_DIR/.aws/credentials

# default to us-west-2 if AWS_REGION is not set
    echo "\
[profile AmazonCloudWatchAgent]
region = ${AWS_REGION:-us-west-2}
" > $THIS_DIR/.aws/config
}

create_aws_credentials_to_mount_into_cloudwatch_agent_container

# start the cw-agent
docker compose --file docker-compose.local.yaml up --build