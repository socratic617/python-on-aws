#!/bin/bash

set -e

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# start the FastAPI app, enabling hot reload on save (assuming files_api packages is installed)
function run {
    uvicorn src.files_api.main:app --reload
}

# start the FastAPI app, enabling hot reload on save (assuming files_api packages is not installed)
function run-py {
    PYTHONPATH="${THIS_DIR}/src" uvicorn files_api.main:app --reload
}

TIMEFORMAT="Task completed in %3lR"
time ${@:-help}
