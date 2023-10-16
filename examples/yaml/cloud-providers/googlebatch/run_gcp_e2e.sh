#!/bin/bash

# Seqera platform specific env variables
export SEQERA_ORGANIZATION_NAME=''          # Name of the Organization you want to creat
export SEQERA_WORKSPACE_NAME=''             # Name of the Workspace you want to create
export SEQERA_TEAM_NAME=''                  # Name of the Team you want to create
export TEAM_MEMBER_EMAIL1=''                # An email address for a Team Member you want to add
export TEAM_MEMBER_EMAIL2=''                # (Optional) Second email address for a Team Member you want to add
export GITHUB_USERNAME=''                   # Your GitHub username to add GitHub credentials to the Platform
export SEQERA_GITHUB_PASSWORD=''            # Your GitHub PAT (preferred) or password to create Github credentials
export DOCKERHUB_USERNAME=''                # Your Docker username to add Docker credentials
export DOCKERHUB_PASSWORD=''                # Your Docker password

# Google Batch specific variables
export GOOGLE_KEY=''                        # Your Google Service Account key to create Google credentials
export GCP_COMPUTE_ENV_NAME=''              # Name of the Google Batch Compute Environment you want to create
export SEQERA_WORK_DIR=''                   # Path to the desired Nextflow work directory when creating a compute env

# Pipeline/launch specific variables
export PIPELINE_NAME_PREFIX=''              # Prefix to add to the pipeline name added to Seqera Platform
export TIME=`date +"%Y%m%d-%H%M%S"`         # Time stamp to add to the pipeline launch name

# Run the yaml
seqerakit seqerakit-gcp-e2e.yml
