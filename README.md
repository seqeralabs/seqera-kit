# <img src="https://raw.githubusercontent.com/seqeralabs/seqera-kit/main/assets/seqerakit.svg" width=50 alt="seqerakit logo"> seqerakit

`seqerakit` is a Python wrapper for the [Seqera Platform CLI](https://github.com/seqeralabs/tower-cli). It can be leveraged to automate the creation of all of the entities in Seqera Platform via a simple configuration file in YAML format.

The key features are:

- **Simple configuration**: All of the command-line options available when using the Seqera Platform CLI can be defined in simple YAML format.
- **Infrastructure as Code**: Enable users to manage and provision their infrastructure specifications.
- **Automation**: End-to-end creation of entities within Seqera Platform, all the way from adding an Organization to launching pipeline(s) within that Organization.

## Prerequisites

You will need to have an account on Seqera Platform (see [Plans and pricing](https://cloud.tower.nf/pricing/)).

## Installation

`seqerakit` requires the following dependencies:

1. [Seqera Platform CLI](https://github.com/seqeralabs/tower-cli#1-installation)

2. [Python (`>=3.8`)](https://www.python.org/downloads/)

3. [PyYAML](https://pypi.org/project/PyYAML/)

### Conda

You can install `seqerakit` and its dependencies via Conda. Ensure that you have the correct channels configured:

```console
conda config --add channels defaults
conda config --add channels bioconda
conda config --add channels conda-forge
conda config --set channel_priority strict
```

You can then create a conda environment with `seqerakit` installed using the following:

```
conda env create -n seqerakit seqerakit
conda activate seqerakit
```

### Pip

If you already have [Seqera Platform CLI](https://github.com/seqeralabs/tower-cli#1-installation) and Python installed on your system, you can install `seqerakit` directly from [PyPI](https://pypi.org/project/seqerakit/):

```console
pip install seqerakit
```

You can force overwrite the installation to use the latest changes with the command below:

```console
pip install --upgrade --force-reinstall seqerakit
```

## Configuration

Create a Seqera Platform access token using the [Seqera Platform](https://tower.nf/) web interface via the **Your Tokens** page in your profile.

`seqerakit` reads this token from the environment variable `TOWER_ACCESS_TOKEN`. Please export it into your terminal as shown below:

```bash
export TOWER_ACCESS_TOKEN=<your access token>
```

## Usage

To confirm the installation of `seqerakit`, configuration of the Seqera Platform CLI and connection is working as expected:

```bash
seqerakit --info
```

Use the `-h` or `--help `parameter to list the available commands and their associated options:

```bash
seqerakit --help
```

### Dryrun

To print the commands that would executed with `tw` when using a YAML file, you can run `seqerakit` with the `--dryrun` flag:

```bash
seqerakit file.yaml --dryrun
```

### Recursively delete

Instead of adding or creating resources, you can recursively delete resources in your YAML file by specifying the `--delete` flag:

```bash
seqerakit file.yaml --delete
```

For example, if you have a YAML file that defines an Organization -> Workspace -> Team -> Credentials -> Compute Environment that have already been created, with the `--delete` flag, `seqerakit` will recursively delete the Compute Environment -> Credentials -> Team -> Workspace -> Organization.

### Using `tw` specific CLI options

`tw` specific CLI options can be specified with the `--cli=` flag:

```bash
seqerakit file.yaml --cli="--arg1 --arg2"
```

You can find the full list of options by running `tw -h`.

The Seqera Platform CLI expects to connect to a Seqera Platform instance that is secured by a TLS certificate. If your Seqera Platform Enterprise instance does not present a certificate, you will need to qualify and run your `tw` commands with the `--insecure` flag.

To use `tw` specific CLI options such as `--insecure`, use the `--cli=` flag, followed by the options you would like to use enclosed in double quotes.

For example:

```bash
seqerakit file.yaml --cli="--insecure"
```

For Seqera Platform Enterprise, to use an SSL certificate that is not accepted by the default Java certificate authorities and specify a custom `cacerts` store as accepted by the `tw` CLI, you can specify the `-Djavax.net.ssl.trustStore=/absolute/path/to/cacerts` option enclosed in double quotes to `seqerakit` as you would to `tw`, preceded by `--cli=`.

For example:

```bash
seqerakit hello-world-config.yml --cli="-Djavax.net.ssl.trustStore=/absolute/path/to/cacerts"
```

<b>Note</b>: Use of `--verbose` option for the `tw` CLI is currently not supported by `seqerakit`. Supplying `--cli="--verbose"` will raise an error.

## YAML Configuration Options

There are several options that can be provided in your YAML configuration file, that are handled specially by seqerakit and/or are not exposed as `tw` CLI options.

### 1. Pipeline parameters using `params` and `params-file`

To specify pipeline parameters, you may either use `params:` to specify a list of parameters, or use `params-file:` to point to a parameters file.

For example, to specify pipeline parameters within your YAML:

```yaml
params:
  outdir: 's3://path/to/outdir'
  fasta: 's3://path/to/reference.fasta'
```

Alternatively, to specify a file containing pipeline parameters:

```yaml
params-file: '/path/to/my/parameters.yaml'
```

Optionally, you may provide both:

```yaml
params-file: '/path/to/my/parameters.yaml'
params:
  outdir: 's3://path/to/outdir'
  fasta: 's3://path/to/reference.fasta'
```

**Note**: If duplicate parameters are provided, the parameters provided as key-value pairs inside the `params` nested dictionary of the YAML file will take precedence **over** values in the provided `params-file`.

### 2. `overwrite` Functionality
For every entity defined in your YAML file, you can specify `overwrite: True` to overwrite any existing entities in Seqera Platform of the same name. 

`seqerakit` will first check to see if the name of the entity exists, if so, it will invoke a `tw <subcommand> delete` command before attempting to create it based on the options defined in the YAML file.

```console
DEBUG:root: Overwrite is set to 'True' for organizations

DEBUG:root: Running command: tw -o json organizations list
DEBUG:root: The attempted organizations resource already exists. Overwriting.

DEBUG:root: Running command: tw organizations delete --name $SEQERA_ORGANIZATION_NAME
DEBUG:root: Running command: tw organizations add --name $SEQERA_ORGANIZATION_NAME --full-name $SEQERA_ORGANIZATION_NAME --description 'Example of an organization'
```
### 3. Specifying JSON configuration files with `file-path`
The Seqera Platform CLI allows export and import of entities through JSON configuration files for pipelines and compute environments. To use these files to add a pipeline or compute environment to a workspace, use the `file-path` key to specify a path to a JSON configuration file.

An example of the `file-path` option is provided in the [compute-envs.yml](templates/compute-envs.yml) template:

```yaml
compute-envs:
  - name: 'my_aws_compute_environment'                              # required
    workspace: 'my_organization/my_workspace'                       # required
    credentials: 'my_aws_credentials'                               # required
    wait: 'AVAILABLE'                                               # optional
    file-path: './compute-envs/my_aws_compute_environment.json'     # required
    overwrite: True
```


## Quick start

You must provide a YAML file that defines the options for each of the entities you would like to create in Seqera Platform.

You will need to have an account on Seqera Platform (see [Plans and pricing](https://cloud.tower.nf/pricing/)). You will also need access to a Workspace and a pre-defined Compute Environment where you can launch a pipeline.

### Launch via YAML

1. Create a YAML file called `hello-world-config.yml` with the contents below, and customise the `<YOUR_WORKSPACE>` and `<YOUR_COMPUTE_ENVIRONMENT>` entries as required:

   ```yaml # noqa
   launch:
     - name: 'hello-world'                              # Workflow name
       workspace: '<YOUR_WORKSPACE>'                    # Workspace name
       compute-env: '<YOUR_COMPUTE_ENVIRONMENT>'        # Compute environment
       revision: 'master'                               # Pipeline revision
       pipeline: 'https://github.com/nextflow-io/hello' # Pipeline URL
   ```

2. Launch the pipeline with `seqerakit`:

   ```bash
   seqerakit hello-world-config.yml
   ```

3. Login to your Seqera Platform instance and check the Runs page in the appropriate Workspace for the pipeline you just launched!

### Launch via a Python script

You can also launch the same pipeline via a Python script. This will essentially allow you to extend the functionality on offer within the Seqera Platform CLI by leveraging the flexibility and customisation options available in Python.

1. Download the [`launch_hello_world.py`](https://github.com/seqeralabs/seqera-kit/blob/main/examples/python/launch_hello_world.py) Python script and customise the `<YOUR_WORKSPACE>` and `<YOUR_COMPUTE_ENVIRONMENT>` entries as required.

2. Launch the pipeline with `seqerakit`:

```bash
   python launch_hello_world.py
```

3. Login to your Seqera Platform instance and check the Runs page in the appropriate Workspace for the pipeline you just launched!

## Real world example

Please see [`seqerakit-e2e.yml`](https://github.com/seqeralabs/seqera-kit/blob/main/examples/yaml/seqerakit-e2e.yml) for an end-to-end example that highlights how you can use `seqerakit` to create everything sequentially in Seqera Platform all the way from creating a new Organization to launching a pipeline.

You can modify this YAML to similarly create Seqera Platform resources end-to-end for your setup. This YAML encodes environment variables to protect sensitive keys, usernames, and passwords that are required to create or add certain resources (i.e. credentials, compute environments). Prior to running it with `seqerakit examples/yaml/seqerakit-e2e.yml`, you will have to set the following environment variables:

```console
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
