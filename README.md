# tw-pywrap

`tw-pywrap` is a Python wrapper for the [Nextflow Tower CLI](https://github.com/seqeralabs/tower-cli). It can be leveraged to automate the creation of the following entities in Nextflow Tower via a simple configuration file in YAML format:

  - Organizations
  - Teams
  - Workspaces
  - Participants
  - Credentials
  - Secrets
  - Compute Environments
  - Actions
  - Datasets
  - Pipelines
  - Launch

The key features are:

- **Simple configuration**: All of the command-line options available when using the Nextflow Tower CLI can be defined in simple YAML format.
- **Infrastructure as Code**: Enable users to manage and provision their infrastructure specifications.
- **Automation**: End-to-end creation of entities within Nextflow Tower, all the way from adding an Organization to launching pipeline(s) within that Organization.

## Prerequisites

This guide covers the installation and configuration of `tw-pywrap`.

### 1. Dependencies

1. [Nextflow Tower CLI](https://github.com/seqeralabs/tower-cli#1-installation)

2. [Python (`>=3.8`)](https://www.python.org/downloads/) and [PyYAML](https://pypi.org/project/PyYAML/)

A [Dockerfile](Dockerfile) with these requirements has been provided if you wish to build you own container.

### 2. Installation

The scripts in this repository will eventually be packaged via `pip`, but for now you can install them within your existing Python / Conda environment with the command below:

```
pip install git+https://github.com/seqeralabs/tw-pywrap.git@main
```

You can force overwrite the installation to use the latest changes with the command below:

```
pip install --upgrade --force-reinstall git+https://github.com/seqeralabs/tw-pywrap.git@main
```

### 3. Configuration

Create a Tower access token using the [Tower](https://tower.nf/) web interface via the **Your Tokens** page in your profile.

Providing `tw-pywrap` access to Tower with your access token can be achieved by:

1. Exporting it directly into your terminal:

    ```bash
    export TOWER_ACCESS_TOKEN=<your access token>
    ```

2. Adding the above `export` command to a file such as `.bashrc` to be automatically added into your environment.

## Quick start

<!-- To run this script, you must set up a yaml file that will define the resources/entities you would like to create or modify on Tower, as well as define the required options for those entities. These options are defined as key-value pairs in your yaml file.

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

## Other scripts

In the `scripts/` subdirectory of this repository are additional scripts that can be used for automation on a smaller-scale (i.e. launching multiple pipelines). You can find READMEs within the subdirectory. -->


Example to launch hello world as part of the Quick start
- Create a YAML to launch hello world from URL

## Templates

Template YAML files can be found in the [`templates/`](templates) directory:

  - [organizations.yml](templates/organizations.yml)
  - [teams.yml](templates/teams.yml)
  - [workspaces.yml](templates/workspaces.yml)
  - [participants.yml](templates/participants.yml)
  - [credentials.yml](templates/credentials.yml)
  - [secrets.yml](templates/secrets.yml)
  - [compute-envs.yml](templates/compute-envs.yml)
  - [actions.yml](templates/actions.yml)
  - [datasets.yml](templates/datasets.yml)
  - [pipelines.yml](templates/pipelines.yml)
  - [launch.yml](templates/launch.yml)

## Credits

`tw-wrapy` was written by [Esha Joshi](https://github.com/ejseqera), [Adam Talbot](https://github.com/adamrtalbot) and [Harshil Patel](https://github.com/drpatelh) from the Scientific Development Team at [Seqera Labs](https://seqera.io/).