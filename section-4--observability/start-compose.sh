#!/bin/bash

# Note: this script works well with 
#   `aws sso login --profile cloud-course`
#   or
#   `aws configure sso --profile cloud-course`

aws configure export-credentials --profile cloud-course --format env > .env

docker compose up --build