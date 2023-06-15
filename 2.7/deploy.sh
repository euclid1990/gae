#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
# Treat unset variables as an error when substituting.
set -eu

project_id=${1:-project-gae-1st}

# Set working GCP project
gcloud config set project $project_id

# Check if App Engine is enabled for the project
app_engine_info=$(gcloud app describe --project="$project_id" 2>&1 || true)

if [[ $app_engine_info =~ "ERROR" ]]; then
  echo "App Engine is not enabled for project '$project_id'."
  gcloud app create --region=asia-northeast1
else
  echo "App Engine is enabled for project '$project_id'."
fi

# Deploy new source code to GAE
gcloud app deploy --promote --stop-previous-version app.yaml cron.yaml queue.yaml
