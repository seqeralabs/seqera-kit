# <img src="https://raw.githubusercontent.com/seqeralabs/twkit/main/assets/twkit.svg" width=50 alt="twkit logo"> twkit

`twkit` is a Python wrapper for the [Nextflow Tower CLI](https://github.com/seqeralabs/tower-cli). It can be leveraged to automate the creation of all of the entities in Nextflow Tower via a simple configuration file in YAML format.

The key features are:

- **Simple configuration**: All of the command-line options available when using the Nextflow Tower CLI can be defined in simple YAML format.
- **Infrastructure as Code**: Enable users to manage and provision their infrastructure specifications.
- **Automation**: End-to-end creation of entities within Nextflow Tower, all the way from adding an Organization to launching pipeline(s) within that Organization.

## Prerequisites

You will need to have an account on Nextflow Tower (see [Plans and pricing](https://cloud.tower.nf/pricing/)).

### 1. Dependencies

`twkit` requires the following dependencies:

1. [Nextflow Tower CLI](https://github.com/seqeralabs/tower-cli#1-installation)

2. [Python (`>=3.8`)](https://www.python.org/downloads/)

3. [PyYAML](https://pypi.org/project/PyYAML/)

Alternatively, you can install the dependencies via Conda by downloading and using the [Conda environment file](https://github.com/seqeralabs/twkit/blob/main/environment.yml) that has been supplied in this repository:

```console
conda env create -f environment.yml
conda activate twkit
```

### 2. Installation

The scripts in this repository are packaged and available on [PyPI](https://pypi.org/project/twkit/). They can be installed via `pip`:

```
pip install twkit
```

You can force overwrite the installation to use the latest changes with the command below:

```
pip install --upgrade --force-reinstall twkit
```

### 3. Configuration

Create a Tower access token using the [Nextflow Tower](https://tower.nf/) web interface via the **Your Tokens** page in your profile.

`twkit` reads this token from the environment variable `TOWER_ACCESS_TOKEN`. Please export it into your terminal as shown below:

```bash
export TOWER_ACCESS_TOKEN=<your access token>
```

## Quick start

You must provide a YAML file that defines the options for each of the entities you would like to create in Nextflow Tower.

You will need to have an account on Nextflow Tower (see [Plans and pricing](https://cloud.tower.nf/pricing/)). You will also need access to a Workspace and a pre-defined Compute Environment where you can launch a pipeline.

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

2. Launch the pipeline with `twkit`:

   ```
   twkit hello-world-config.yml
   ```

   <b>Note</b>: The Tower CLI expects to connect to a Tower instance that is secured by a TLS certificate. If your Tower instance does not present a certificate, you will need to qualify and run your `tw` commands with `--cli` followed by the `--insecure` flag. For example:

   ```
   twkit hello-world-config.yml --cli --insecure
   ```

   To use an SSL certificate that it is not accepted by the default Java certificate authorities and specify a custom `cacerts` store as accepted by the `tw` CLI, you can specify the `-Djavax.net.ssl.trustStore=/absolute/path/to/cacerts` option to `twkit` as you would to `tw`, preceded by `--cli` flag to indicate use of `tw` specific CLI options. For example:

   ```
   twkit hello-world-config.yml --cli -Djavax.net.ssl.trustStore=/absolute/path/to/cacerts

   ```

3. Login to your Tower instance and check the Runs page in the appropriate Workspace for the pipeline you just launched!

### Launch via a Python script

You can also launch the same pipeline via a Python script. This will essentially allow you to extend the functionality on offer within the Tower CLI by leveraging the flexibility and customisation options available in Python.

1. Download the [`launch_hello_world.py`](https://github.com/seqeralabs/twkit/blob/main/examples/python/launch_hello_world.py) Python script and customise the `<YOUR_WORKSPACE>` and `<YOUR_COMPUTE_ENVIRONMENT>` entries as required.

2. Launch the pipeline with `twkit`:

   ```
   python launch_hello_world.py
   ```

3. Login to your Tower instance and check the Runs page in the appropriate Workspace for the pipeline you just launched!

## Real world example

Please see [`twkit-e2e.yml`](https://github.com/seqeralabs/twkit/blob/main/examples/yaml/twkit-e2e.yml) for an end-to-end example that highlights how you can use `twkit` to create everything sequentially in Nextflow Tower all the way from creating a new Organization to launching a pipeline.

You can modify this YAML to similarly create Nextflow Tower resources end-to-end for your setup. This YAML encodes environment variables to protect sensitive keys, usernames, and passwords that are required to create or add certain resources (i.e. credentials, compute environments). Prior to running it with `twkit examples/yaml/twkit-e2e.yml`, you will have to set the following environment variables:

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

We have provided template YAML files for each of the entities that can be created on Tower. These can be found in the [`templates/`](https://github.com/seqeralabs/blob/main/twkit/templates) directory and should form a good starting point for you to add your own customization:

- [organizations.yml](https://github.com/seqeralabs/twkit/blob/main/templates/organizations.yml)
- [teams.yml](https://github.com/seqeralabs/twkit/blob/main/templates/teams.yml)
- [workspaces.yml](https://github.com/seqeralabs/twkit/blob/main/templates/workspaces.yml)
- [participants.yml](https://github.com/seqeralabs/twkit/blob/main/templates/participants.yml)
- [credentials.yml](https://github.com/seqeralabs/twkit/blob/main/templates/credentials.yml)
- [secrets.yml](https://github.com/seqeralabs/twkit/blob/main/templates/secrets.yml)
- [compute-envs.yml](https://github.com/seqeralabs/twkit/blob/main/templates/compute-envs.yml)
- [actions.yml](https://github.com/seqeralabs/twkit/blob/main/templates/actions.yml)
- [datasets.yml](https://github.com/seqeralabs/twkit/blob/main/templates/datasets.yml)
- [pipelines.yml](https://github.com/seqeralabs/twkit/blob/main/templates/pipelines.yml)
- [launch.yml](https://github.com/seqeralabs/twkit/blob/main/templates/launch.yml)

## Contributions and Support

If you would like to contribute to `twkit`, please see the [contributing guidelines](https://github.com/seqeralabs/twkit/blob/main/.github/CONTRIBUTING.md).

For further information or help, please don't hesitate to create an [issue](https://github.com/seqeralabs/twkit/issues) in this repository.

## Credits

`twkit` was written by [Esha Joshi](https://github.com/ejseqera), [Adam Talbot](https://github.com/adamrtalbot) and [Harshil Patel](https://github.com/drpatelh) from the Scientific Development Team at [Seqera Labs](https://seqera.io/).
