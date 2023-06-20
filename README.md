# Python Implementation of Nextflow Tower Automation

This repository contains scripts that allow for 'automation' of resource creation to be able to setup and run pipelines on Nextflow Tower. This includes creation of things like organizations, teams, compute-environments, datasets, pipelines, and more.

The `build_tower_e2e.py` script specifically can be used to automate end-to-end creation of resources/entities that would be required to run pipelines.

Additionally, the script specifies which resources to create using a config file. This config file can be used to maintain provenance of how resources are created, what options are used for each resource, and allows you to re-create resources with minimal configuration.

In this script, you can:

- Set up organizations
- Add participants and members
- Add credentials and setup compute-environments
- Add datasets
- Add Tower Actions
- Add pipelines to the launchpad via source (i.e Github Repo, and through infrastructure-as-code stored in JSON files)
- Launch pipelines using your newly configured Tower instance

## Setup

Clone this repository to your local environment.

This repository provides two methods to build the minimum dependencies required to run this script in the form of:

### 1. Dependencies

twpy requires the Nextflow Tower CLI installed, but has no additional Python dependencies.

### 2. Conda environment

Using the `environment.yaml` in this repository, you can create a conda environment (assuming you have miniconda installed) using the following:

```
conda env create -f environment.yaml
conda activate tw_pywrapper
```

You will also need to have the Tower CLI installed:

```
wget -L https://github.com/seqeralabs/tower-cli/releases/download/v0.7.3/tw-0.8.0-linux-x86_64
mv tw-* tw
chmod +x ./tw
sudo mv tw /usr/local/bin/
```

### 3. Docker

You may alternatively use the provided `Dockerfile` in this repository which provides both the Tower CLI and Python dependencies required to run this script.

### 4. Install locally

For development or installation of a local copy, you can use pip. After cloning the repo, use the command:

```
pip install .
```

You can also run locally using the following command (where $REPO is the path to the local repository):

```
PYTHONPATH=$REPO python $REPO/tw_py/cli.py
```

### 4. Set your `TOWER_ACCESS_TOKEN`

You must set the `TOWER_ACCESS_TOKEN` as an environment variable to create, modify, delete resources on Tower.

```
export TOWER_ACCESS_TOKEN=<your access token>
```

## Configuration

To run this script, you must set up a yaml file that will define the resources/entities you would like to create or modify on Tower, as well as define the required options for those entities. These options are defined as key-value pairs in your yaml file.

For example, to create an organization, you can define the first block of your yaml with the resource you want to create, followed by the options required to pass to the CLI to create the resource, in your yaml:

```
organizations:
  - name: 'my_organization'
    full-name: 'company_A_organization'
    description: 'Organization created E2E with tw CLI scripting'
    location: 'Global'
    website: 'https://company.com/'
    overwrite: False
```

The key-value pairs defined in each block of your yaml file will mirror the options you would provide to the CLI. In this case, on the CLI, we would create this organization by running:

```
tw organizations add --name my_organization \
    --full-name 'company_A_organization' \
    --description 'Organization created E2E with tw CLI scripting' \
    --location 'Global' \
    --website 'https://company.com/' \
```

Optionally, you can specify `overwrite: True` for each block which will allow you to overwrite the resource if it already exists in Tower.

Additional options can be specified but the script will fail to create or update your resource unless the minimum options are specified.

To determine what minimum options are required for each resource, refer to later section named _Configuration Options_.

## Run the script

You can run the script with the following command:

```
twpy --config config.yaml
```

## Configuration Options

Below is a list of minimum and some pre-defined custom options for each resource to be used in your config file.

### Organizations

```
organizations:
  - name: # required
    full-name: # required
    description: # optional
    location: # optional
    website: # optional
    overwrite: True # optional
```

### Teams

```
teams:
  - name: # required
    organization: # required
    description: # optional
    members: # optional, specify list of users to add to your team
      - 'bob@gmail.com'
      - 'tom@gmail.com'
    overwrite: True # optional
```

### Workspaces

```
workspaces: # add method
  - name: # required
    full-name: # required
    organization: # required
    description: # optional
    visibility: # optional
    overwrite: True # optional
```

### Participants

```
participants: # add method
  - name: # required
    type: # required
    workspace: # required
    role: # required
  - name: 'tom@gmail.com' # optional, user to assign roles to
    type: 'MEMBER'
    workspace:  # required
    role: 'LAUNCH'
```

### Credentials

To avoid exposing sensitive information about your credentials, you can use environment variables in place of keys and passwords in your config file:

```
credentials:
  - type: 'google' # required
    name: # required (i.e. google_credentials)
    workspace: # required
    key: '$GOOGLE_KEY' # required
    overwrite: True # optional
  - type: 'aws'
    name: # required (i.e.'aws_credentials')
    workspace: # required
    access-key: $AWS_ACCESS_KEY_ID
    secret-key: $AWS_SECRET_ACCESS_KEY
    assume-role-arn: 'arn:aws:iam::123456789:role/TowerDevelopmentRole'
    overwrite: True # optional
```

To see the full list of credentials you can add via the CLI, try running `tw credentials add`.

### Compute Environments

To create compute environments, you can either specify all required options in the config file or supply a JSON file containing all configuration for your desired compute environment.

```
compute-envs:
  - name: # required (i.e 'aws_compute_environment')
    workspace: # required
    credentials: # required
    wait: # optional
    file-path: './compute-envs/awss3.json' # optional
    overwrite: True # optional
```

### Actions

```
actions:
  - type: # required (i.e. 'Tower' or 'Github')
    name: # required
    pipeline: # required (i.e. 'https://github.com/nf-core/rnaseq)'
    workspace: # required
    compute-env: # required
    work-dir: # required
    profile: # optional
    params: # optional
      outdir: 's3://my-bucket/nf-core-rnaseq/results'
    revision: '3.12.0' # required
    overwrite: True # optional
```

### Datasets

```
datasets:
  - name: # required
    description: # optional
    header: true # optional
    workspace: # required
    file-path: './datasets/rnaseq_samples.csv' # required
    overwrite: True # optional
```

### Pipelines

Pipelines can either be specified to be added from source (i.e. a Github repo) or using infrastructure-as-code with a file path to JSON with pipeline configuration settings.

For example, from a Github repo:

```
pipelines:
  - name: 'nf-core-rnaseq' # required
    url: 'https://github.com/nf-core/rnaseq' # required
    workspace: # required
    description: # optional
    compute-env: # required
    work-dir: # required
    profile: # optional
    revision: '3.12.0' # required
    params: # optional
      outdir: 's3://my-bucket/nf-core-rnaseq/results'
    config: './pipelines/nextflow.config' # optional
    pre-run: './pipelines/pre_run.txt' # optional
    overwrite: True # optional
```

Or, for example, from a JSON file:

```
   - name: 'nf-sentieon' # required
     workspace: # required
     compute-env: # required
     file-path: './pipelines/nf_sentieon_pipeline.json'
```

### Launch

Pipelines can be launched using an existing workspace pipeline name from the Launchpad, or from source as described above.

For example, launching a pipeline you added in the previous step:

```
launch:
  - name: 'rnaseq-test-cli'
    pipeline: 'nf-core-rnaseq'
    workspace: # required
    params: # optional
      outdir: 's3://my-bucket/nf-core-rnaseq/results'
```

## Other scripts

In the `scripts/` subdirectory of this repository are additional scripts that can be used for automation on a smaller-scale (i.e. launching multiple pipelines). You can find READMEs within the subdirectory.
