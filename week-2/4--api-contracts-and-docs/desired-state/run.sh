#!/bin/bash

set -e

#####################
# --- Constants --- #
#####################

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
MINIMUM_TEST_COVERAGE_PERCENT=0


##########################
# --- Task Functions --- #
##########################

# install core and development Python dependencies into the currently activated venv
function install {
    python -m pip install --upgrade pip
    python -m pip install --editable "$THIS_DIR/[dev]"
}

function generate-python-api-client-docker {
    OUTDIR="./files-api-client-2"
    rm -rf "$OUTDIR"
    docker run \
        --rm \
        -v "$PWD:/local" \
    openapitools/openapi-generator-cli generate \
        --input-spec http://host.docker.internal:8000/openapi.json \
        --generator-name python-pydantic-v1 \
        --output local/$OUTDIR \
        --package-name files_api_client \
        --model-package models \
        --api-package api \
        --artifact-version $(cat "$THIS_DIR/version.txt")
}

function generate-python-api-server-docker {
    OUTDIR="./files-api-server"
    rm -rf "$OUTDIR"
    docker run \
        --rm \
        -v "$PWD:/local" \
        --network host \
    openapitools/openapi-generator-cli generate \
        --input-spec http://host.docker.internal:8000/openapi.json \
        --generator-name python-fastapi \
        --output local/$OUTDIR \
        --package-name files_api_client \
        --model-package models \
        --api-package api \
        --artifact-version $(cat "$THIS_DIR/version.txt") \
        --package-version "9.9.9"
}

# FastAPI docs for generating api clients: https://fastapi.tiangolo.com/advanced/generate-clients/
# OpenAPI python client: https://github.com/openapi-generators/openapi-python-client
function generate-python-api-client {
    # write a temp config file to disk
    cat > "$THIS_DIR/openapi-python-client-config.yaml" <<EOF
project_name_override: files-api-client
package_name_override: files_api_client
package_version_override: "$(cat $THIS_DIR/version.txt)"
EOF

    which pipx || python -m pip install pipx
    pipx run openapi-python-client generate \
        --url "$API_BASE_URL/openapi.json" \
        --meta setup \
        --config "$THIS_DIR/openapi-python-client-config.yaml" \
        --overwrite || true
}

function run {
    AWS_PROFILE=cloud-course \
    S3_BUCKET_NAME="some-bucket" \
        uvicorn 'files_api.main:create_app' --reload --factory
}

# start the FastAPI app, pointed at a mocked aws endpoint
function run-mock {
    set +e

    # kill the moto server if it is already running
    lsof -i :5000 | grep LISTEN | awk '{print $2}' | xargs kill -9

    # Start moto.server in the background on localhost:5000
    python -m moto.server -p 5000 &
    MOTO_PID=$!

    # point the AWS CLI and boto3 to the mocked AWS server using mocked credentials
    export AWS_ENDPOINT_URL="http://localhost:5000"
    export AWS_SECRET_ACCESS_KEY="mock"
    export AWS_ACCESS_KEY_ID="mock"
    export S3_BUCKET_NAME="some-bucket"

    # create a bucket called "some-bucket" using the mocked aws server
    aws s3 mb "s3://$S3_BUCKET_NAME"

    # Trap EXIT signal to kill the moto.server process when uvicorn stops
    trap 'kill $MOTO_PID' EXIT

    # Set AWS endpoint URL and start FastAPI app with uvicorn in the foreground
    uvicorn files_api.main:create_app --reload --factory

    # Wait for the moto.server process to finish (this is optional if you want to keep it running)
    wait $MOTO_PID
}

# run linting, formatting, and other static code quality tools
function lint {
    pre-commit run --all-files
}

# same as `lint` but with any special considerations for CI
function lint:ci {
    # We skip no-commit-to-branch since that blocks commits to `main`.
    # All merged PRs are commits to `main` so this must be disabled.
    SKIP=no-commit-to-branch pre-commit run --all-files
}

# execute tests that are not marked as `slow`
function test:quick {
    run-tests -m "not slow" ${@:-"$THIS_DIR/tests/"}
}

# execute tests against the installed package; assumes the wheel is already installed
function test:ci {
    INSTALLED_PKG_DIR="$(python -c 'import files_api; print(files_api.__path__[0])')"
    # in CI, we must calculate the coverage for the installed package, not the src/ folder
    COVERAGE_DIR="$INSTALLED_PKG_DIR" run-tests
}

# (example) ./run.sh test tests/test_states_info.py::test__slow_add
function run-tests {
    PYTEST_EXIT_STATUS=0
    rm -rf "$THIS_DIR/test-reports" || true
    python -m pytest ${@:-"$THIS_DIR/tests/"} \
        --cov "${COVERAGE_DIR:-$THIS_DIR/src}" \
        --cov-report html \
        --cov-report term \
        --cov-report xml \
        --junit-xml "$THIS_DIR/test-reports/report.xml" \
        --cov-fail-under "$MINIMUM_TEST_COVERAGE_PERCENT" || ((PYTEST_EXIT_STATUS+=$?))
    mv coverage.xml "$THIS_DIR/test-reports/" || true
    mv htmlcov "$THIS_DIR/test-reports/" || true
    mv .coverage "$THIS_DIR/test-reports/" || true
    return $PYTEST_EXIT_STATUS
}

function test:wheel-locally {
    deactivate || true
    rm -rf test-env || true
    python -m venv test-env
    source test-env/bin/activate
    clean || true
    pip install build
    build
    pip install ./dist/*.whl pytest pytest-cov
    test:ci
    deactivate || true
}

# serve the html test coverage report on localhost:8000
function serve-coverage-report {
    python -m http.server --directory "$THIS_DIR/test-reports/htmlcov/" 8000
}

# build a wheel and sdist from the Python source code
function build {
    python -m build --sdist --wheel "$THIS_DIR/"
}

function release:test {
    lint
    clean
    build
    publish:test
}

function release:prod {
    release:test
    publish:prod
}

function publish:test {
    try-load-dotenv || true
    twine upload dist/* \
        --repository testpypi \
        --username=__token__ \
        --password="$TEST_PYPI_TOKEN"
}

function publish:prod {
    try-load-dotenv || true
    twine upload dist/* \
        --repository pypi \
        --username=__token__ \
        --password="$PROD_PYPI_TOKEN"
}

# remove all files generated by tests, builds, or operating this codebase
function clean {
    rm -rf dist build coverage.xml test-reports
    find . \
      -type d \
      \( \
        -name "*cache*" \
        -o -name "*.dist-info" \
        -o -name "*.egg-info" \
        -o -name "*htmlcov" \
      \) \
      -not -path "*env/*" \
      -exec rm -r {} + || true

    find . \
      -type f \
      -name "*.pyc" \
      -not -path "*env/*" \
      -exec rm {} +
}

# export the contents of .env as environment variables
function try-load-dotenv {
    if [ ! -f "$THIS_DIR/.env" ]; then
        echo "no .env file found"
        return 1
    fi

    while read -r line; do
        export "$line"
    done < <(grep -v '^#' "$THIS_DIR/.env" | grep -v '^$')
}

# print all functions in this file
function help {
    echo "$0 <task> <args>"
    echo "Tasks:"
    compgen -A function | cat -n
}

TIMEFORMAT="Task completed in %3lR"
time ${@:-help}
