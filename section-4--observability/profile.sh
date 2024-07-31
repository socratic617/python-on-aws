#!/bin/bash

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null
then
    echo "AWS CLI not installed. Please install it first."
    exit 1
fi

# Get the profile name from the user input argument
if [ -z "$1" ]; then
    echo "Usage: $0 <profile_name>"
    exit 1
fi

PROFILE_NAME=$1

# Determine the credentials file path
CREDENTIALS_FILE="$HOME/.aws/credentials"
SSO_CACHE_DIR="$HOME/.aws/sso/cache"

# Function to extract credentials from the credentials file
extract_from_credentials() {
    AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id --profile $PROFILE_NAME)
    AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key --profile $PROFILE_NAME)
    AWS_SESSION_TOKEN=$(aws configure get aws_session_token --profile $PROFILE_NAME)
}

# Function to extract credentials from the SSO cache
extract_from_sso_cache() {
    SSO_CACHE_FILE=$(find $SSO_CACHE_DIR -type f -name "*.json" | xargs grep -l "\"startUrl\": \"https://$PROFILE_NAME\"" | head -n 1)
    AWS_ACCESS_KEY_ID=$(jq -r '.accessToken' $SSO_CACHE_FILE)
    AWS_SECRET_ACCESS_KEY=$(jq -r '.secretAccessKey' $SSO_CACHE_FILE)
    AWS_SESSION_TOKEN=$(jq -r '.sessionToken' $SSO_CACHE_FILE)
}

# Check if the profile exists in the credentials file
if grep -q "\[$PROFILE_NAME\]" $CREDENTIALS_FILE; then
    extract_from_credentials
elif [ -d "$SSO_CACHE_DIR" ] && [ "$(find $SSO_CACHE_DIR -type f -name "*.json" | wc -l)" -gt 0 ]; then
    extract_from_sso_cache
else
    echo "Profile not found in ~/.aws/credentials or ~/.aws/sso/cache."
    exit 1
fi

# Create the .env file
cat <<EOF > .env
AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN
AWS_REGION=us-west-2
EOF

echo ".env file created successfully."
