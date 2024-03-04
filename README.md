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

### Local development installation
You can install the development branch of `seqerakit` on your local machine to test feature updates of the tool. Before proceeding, ensure that you have [Python](https://www.python.org/downloads/) and [Git](https://git-scm.com/downloads) installed on your system.

1. To install directly from pip:
```bash
pip install git+https://github.com/seqeralabs/seqera-kit.git@dev
```

2. Alternatively, you may clone the repository locally and install manually:
```bash
git clone https://github.com/seqeralabs/seqera-kit.git
cd seqera-kit
git checkout dev
pip install .
```

You can verify your installation with:
```bash
pip show seqerakit
```

## Configuration

Create a Seqera Platform access token using the [Seqera Platform](https://tower.nf/) web interface via the **Your Tokens** page in your profile.

`seqerakit` reads this token from the environment variable `TOWER_ACCESS_TOKEN`. Please export it into your terminal as shown below:

```bash
export TOWER_ACCESS_TOKEN=<your access token>
```

## Usage

To confirm the installation of `seqerakit`, configuration of the Seqera Platform CLI and connection is working as expected. This will run the `tw info` command under the hood:

```bash
seqerakit --info
```

Use the `--help` or `-h` parameter to list the available commands and their associated options:
```bash
seqerakit --help
```

Use `--version` or `-v` to retrieve the current version of your seqerakit installation:
```bash
seqerakit --version
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
## YAML Dump Feature
**Note: This is an experimental feature and is under active development. It may not be fully stable is subject to further change and improvements in future releases. If you encounter issues using this feature or want to provide feedback, please feel free to contribute via [GitHub Issues](https://github.com/seqeralabs/seqera-kit/issues) or [Pull Requests](https://github.com/seqeralabs/seqera-kit/pulls).**

To generate definitions for objects and entities that exist within a Workspace on Seqera Platform in YAML format, you can use the `seqerakit dump` command.

To use this feature, specify the Workspace name or ID for which you want to generate YAML files for, and optionally, a prefix for your YAML filenames (this defaults to the Workspace):
```bash
seqerakit dump --workspace <workspace_name/ID> --prefix <optional_prefix>
```
This command will generate YAML definitions for entities (i.e. Pipelines, Compute Environments) in the specified Workspace. These definitions can be used to compare to YAML files initially used to create entities and analyze changes, or to maintain provenance and IaC of the current state of objects in the Platform.

*Note*: This feature currently only supports emitting YAML definitions for Compute Environments and Pipelines.

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

## Defining your YAML file using CLI options

All available options to provide as definitions in your YAML file can be determined by running the Seqera Platform CLI help command for your desired entity.

1. Retrieve CLI Options

To obtain a list of available CLI options for defining your YAML file, use the help command of the Seqera Platform CLI. For instance, if you want to configure a pipeline to be added to the Launchpad, you can view the options as follows:

```console
$ tw pipelines add -h

Usage: tw pipelines add [OPTIONS] PIPELINE_URL

Add a workspace pipeline.

Parameters:
*     PIPELINE_URL                         Nextflow pipeline URL.

Options:
* -n, --name=<name>                        Pipeline name.
  -w, --workspace=<workspace>              Workspace numeric identifier (TOWER_WORKSPACE_ID as default) or workspace reference as OrganizationName/WorkspaceName
  -d, --description=<description>          Pipeline description.
      --labels=<labels>[,<labels>...]      List of labels seperated by coma.
  -c, --compute-env=<computeEnv>           Compute environment name.
      --work-dir=<workDir>                 Path where the pipeline scratch data is stored.
  -p, --profile=<profile>[,<profile>...]   Comma-separated list of one or more configuration profile names you want to use for this pipeline execution.
      --params-file=<paramsFile>           Pipeline parameters in either JSON or YML format.
      --revision=<revision>                A valid repository commit Id, tag or branch name.
  ...
```
2. Define Key-Value Pairs in YAML

Translate each CLI option into a key-value pair in the YAML file. The structure of your YAML file should reflect the hierarchy and format of the CLI options. For instance:

```yaml
pipelines:
  - name: 'my_first_pipeline'
    url: 'https://github.com/username/my_pipeline'
    workspace: 'my_organization/my_workspace'
    description: 'My test pipeline'
    labels: 'yeast,test_data'
    compute-env: 'my_compute_environment'
    work-dir: 's3://my_bucket'
    profile: 'test'
    params-file: '/path/to/params.yaml'
    revision: '1.0'
```

In this example:

- `name`, `url`, `workspace`, etc., are the keys derived from the CLI options.
- The corresponding values are user-defined

### Best Practices:
- Ensure that the indentation and structure of the YAML file are correct - YAML is sensitive to formatting.
- Use quotes around strings that contain special characters or spaces.
- When listing multiple values (`labels`, `instance-types`, `allow-buckets`, etc), separate them with commas as shown above.
- For complex configurations, refer to the [Templates](/templates/) provided in this repository.


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

## Real world example

Please see [`seqerakit-e2e.yml`](./examples/yaml/seqerakit-e2e.yml) for an end-to-end example that highlights how you can use `seqerakit` to create everything sequentially in Seqera Platform all the way from creating a new Organization to launching a pipeline.

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

## Contributions and Support

If you would like to contribute to `seqerakit`, please see the [contributing guidelines](https://github.com/seqeralabs/seqera-kit/blob/main/.github/CONTRIBUTING.md).

For further information or help, please don't hesitate to create an [issue](https://github.com/seqeralabs/seqera-kit/issues) in this repository.

## Credits

`seqerakit` was written by [Esha Joshi](https://github.com/ejseqera), [Adam Talbot](https://github.com/adamrtalbot) and [Harshil Patel](https://github.com/drpatelh) from the Scientific Development Team at [Seqera Labs](https://seqera.io/).
