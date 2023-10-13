# <img src="https://raw.githubusercontent.com/seqeralabs/seqera-kit/main/assets/seqerakit.svg" width=50 alt="seqerakit logo"> seqerakit

`seqerakit` is a Python wrapper for the [Seqera Platform CLI](https://github.com/seqeralabs/tower-cli). It can be leveraged to automate the creation of all of the entities in Seqera Platform via a simple configuration file in YAML format.

The key features are:

- **Simple configuration**: All of the command-line options available when using the Seqera Platform CLI can be defined in simple YAML format.
- **Infrastructure as Code**: Enable users to manage and provision their infrastructure specifications.
- **Automation**: End-to-end creation of entities within Seqera Platform, all the way from adding an Organization to launching pipeline(s) within that Organization.

## Prerequisites

You will need to have an account on Seqera Platform (see [Plans and pricing](https://cloud.tower.nf/pricing/)).

### 1. Dependencies

`seqerakit` requires the following dependencies:

1. [Seqera Platform CLI](https://github.com/seqeralabs/tower-cli#1-installation)

2. [Python (`>=3.8`)](https://www.python.org/downloads/)

3. [PyYAML](https://pypi.org/project/PyYAML/)

Alternatively, you can install the dependencies via Conda by downloading and using the [Conda environment file](https://github.com/seqeralabs/seqera-kit/blob/main/environment.yml) that has been supplied in this repository:

```console
conda env create -f environment.yml
conda activate seqerakit
```

### 2. Installation

The scripts in this repository are packaged and available on [PyPI](https://pypi.org/project/seqerakit/). They can be installed via `pip`:

```
pip install seqerakit
```

You can force overwrite the installation to use the latest changes with the command below:

```
pip install --upgrade --force-reinstall seqerakit
```

### 3. Configuration

Create a Seqera Platform access token using the [Seqera Platform](https://tower.nf/) web interface via the **Your Tokens** page in your profile.

`seqerakit` reads this token from the environment variable `TOWER_ACCESS_TOKEN`. Please export it into your terminal as shown below:

```bash
export TOWER_ACCESS_TOKEN=<your access token>
```

## Usage

Use the -h or --help parameter to list the available commands and their associated options:

```
seqerakit -h
```

### Dryrun

To print the commands that would executed with `tw` when using a YAML file, you can run `seqerakit` with the `--dryrun` flag:

```
seqerakit file.yaml --dryrun
```

### Recursively delete

Instead of adding or creating resources, you can recursively delete resources in your YAML file by specifying the `--delete` flag:

```
seqerakit file.yaml --delete
```

For example, if you have a YAML file that defines an Organization -> Workspace -> Team -> Credentials -> Compute Environment that have already been created, with the `--delete` flag, `seqerakit` will recursively delete the Compute Environment -> Credentials -> Team -> Workspace -> Organization.

### Using `tw` specific CLI options

`tw` specific CLI options can be specified with the `--cli=` flag:

```
seqerakit file.yaml --cli="--arg1 --arg2"
```

You can find the full list of options by running `tw -h`.

The Seqera Platform CLI expects to connect to a Seqera Platform instance that is secured by a TLS certificate. If your Seqera Platform instance does not present a certificate, you will need to qualify and run your `tw` commands with the `--insecure` flag.

To use `tw` specific CLI options such as `--insecure`, use the `--cli=` flag, followed by the options you would like to use enclosed in double quotes.

For example:

```
seqerakit file.yaml --cli="--insecure"
```

To use an SSL certificate that is not accepted by the default Java certificate authorities and specify a custom `cacerts` store as accepted by the `tw` CLI, you can specify the `-Djavax.net.ssl.trustStore=/absolute/path/to/cacerts` option enclosed in double quotes to `seqerakit` as you would to `tw`, preceded by `--cli=`.

For example:

```
seqerakit hello-world-config.yml --cli="-Djavax.net.ssl.trustStore=/absolute/path/to/cacerts"
```

<b>Note</b>: Use of `--verbose` option for the `tw` CLI is currently not supported by `seqerakit`. Supplying `--cli="--verbose"` will raise an error.

## Quick start

You must provide a YAML file that defines the options for each of the entities you would like to create in Seqera Platform.

You will need to have an account on Seqera Platform (see [Plans and pricing](https://cloud.tower.nf/pricing/)). You will also need access to a Workspace and a pre-defined Compute Environment where you can launch a pipeline.

### Launch via YAML

1. Create a YAML file called `hello-world-config.yml` with the contents below, and customise the `<YOUR_WORKSPACE>` and `<YOUR_COMPUTE_ENVIRONMENT>` entries as required:

   ```
   launch:
     - name: 'hello-world'                               # Workflow name
       workspace: '<YOUR_WORKSPACE>'                     # Workspace name
       compute-env: '<YOUR_COMPUTE_ENVIRONMENT>'         # Compute environment
       revision: 'master'                                # Pipeline revision
       pipeline: 'https://github.com/nextflow-io/hello'  # Pipeline URL
   ```

2. Launch the pipeline with `seqerakit`:

   ```
   seqerakit hello-world-config.yml
   ```

3. Login to your Seqera Platform instance and check the Runs page in the appropriate Workspace for the pipeline you just launched!

### Launch via a Python script

You can also launch the same pipeline via a Python script. This will essentially allow you to extend the functionality on offer within the Seqera Platform CLI by leveraging the flexibility and customisation options available in Python.

1. Download the [`launch_hello_world.py`](https://github.com/seqeralabs/seqera-kit/blob/main/examples/python/launch_hello_world.py) Python script and customise the `<YOUR_WORKSPACE>` and `<YOUR_COMPUTE_ENVIRONMENT>` entries as required.

2. Launch the pipeline with `seqerakit`:

   ```
   python launch_hello_world.py
   ```

3. Login to your Seqera Platform instance and check the Runs page in the appropriate Workspace for the pipeline you just launched!

## Real world example

Please see [`seqerakit-e2e.yml`](https://github.com/seqeralabs/seqera-kit/blob/main/examples/yaml/seqerakit-e2e.yml) for an end-to-end example that highlights how you can use `seqerakit` to create everything sequentially in Seqera Platform all the way from creating a new Organization to launching a pipeline.

You can modify this YAML to similarly create Seqera Platform resources end-to-end for your setup. This YAML encodes environment variables to protect sensitive keys, usernames, and passwords that are required to create or add certain resources (i.e. credentials, compute environments). Prior to running it with `seqerakit examples/yaml/seqerakit-e2e.yml`, you will have to set the following environment variables:

```
$TOWER_GITHUB_PASSWORD
$DOCKERHUB_PASSWORD
$AWS_ACCESS_KEY_ID
$AWS_SECRET_ACCESS_KEY
$AWS_ASSUME_ROLE_ARN
$AZURE_BATCH_KEY
$AZURE_STORAGE_KEY
$GOOGLE_KEY
$SENTIEON_LICENSE_BASE64
```

## Templates

We have provided template YAML files for each of the entities that can be created on Seqera Platform. These can be found in the [`templates/`](https://github.com/seqeralabs/blob/main/seqera-kit/templates) directory and should form a good starting point for you to add your own customization:

- [organizations.yml](https://github.com/seqeralabs/seqera-kit/blob/main/templates/organizations.yml)
- [teams.yml](https://github.com/seqeralabs/seqera-kit/blob/main/templates/teams.yml)
- [workspaces.yml](https://github.com/seqeralabs/seqera-kit/blob/main/templates/workspaces.yml)
- [participants.yml](https://github.com/seqeralabs/seqera-kit/blob/main/templates/participants.yml)
- [credentials.yml](https://github.com/seqeralabs/seqera-kit/blob/main/templates/credentials.yml)
- [secrets.yml](https://github.com/seqeralabs/seqera-kit/blob/main/templates/secrets.yml)
- [compute-envs.yml](https://github.com/seqeralabs/seqera-kit/blob/main/templates/compute-envs.yml)
- [actions.yml](https://github.com/seqeralabs/seqera-kit/blob/main/templates/actions.yml)
- [datasets.yml](https://github.com/seqeralabs/seqera-kit/blob/main/templates/datasets.yml)
- [pipelines.yml](https://github.com/seqeralabs/seqera-kit/blob/main/templates/pipelines.yml)
- [launch.yml](https://github.com/seqeralabs/seqera-kit/blob/main/templates/launch.yml)

## Contributions and Support

If you would like to contribute to `seqerakit`, please see the [contributing guidelines](https://github.com/seqeralabs/seqera-kit/blob/main/.github/CONTRIBUTING.md).

For further information or help, please don't hesitate to create an [issue](https://github.com/seqeralabs/seqera-kit/issues) in this repository.

## Credits

`seqerakit` was written by [Esha Joshi](https://github.com/ejseqera), [Adam Talbot](https://github.com/adamrtalbot) and [Harshil Patel](https://github.com/drpatelh) from the Scientific Development Team at [Seqera Labs](https://seqera.io/).
