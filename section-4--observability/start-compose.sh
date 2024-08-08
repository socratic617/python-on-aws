#!/bin/bash

aws configure export-credentials --profile cloud-course --format env > .env

docker compose up --build