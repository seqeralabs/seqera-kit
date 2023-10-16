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

# Azure specific variables
export AZURE_BATCH_ACCOUNT_KEY=''           # Your Azure Batch account key to create Azure credentials
export AZURE_BATCH_ACCOUNT_NAME=''          # Name of your Azure Batch account
export AZURE_STORAGE_ACCOUNT_KEY=''         # Your Azure Storage account key
export AZURE_STORAGE_ACCOUNT_NAME=''        # Name of your Azure Storage account
export AZURE_COMPUTE_ENV_NAME=''            # Name of the Azure Compute Environment you want to create
export AZURE_LOCATION=''                    # Azure region to create the compute environment in
export SEQERA_WORK_DIR=''                   # Path to the desired Nextflow work directory when creating a compute env

# Pipeline/launch specific variables
export PIPELINE_NAME_PREFIX=''              # Prefix to add to the pipeline name added to Seqera Platform
export TIME=`date +"%Y%m%d-%H%M%S"`         # Time stamp to add to the pipeline launch name

# Run the yaml
seqerakit seqerakit-azure-e2e.yml
