# ![tw-pywrap logo](assets/tw-py.svg) tw-pywrap

`tw-pywrap` is a Python wrapper for the [Nextflow Tower CLI](https://github.com/seqeralabs/tower-cli). It can be leveraged to automate the creation of all of the entities in Nextflow Tower via a simple configuration file in YAML format.

The key features are:

- **Simple configuration**: All of the command-line options available when using the Nextflow Tower CLI can be defined in simple YAML format.
- **Infrastructure as Code**: Enable users to manage and provision their infrastructure specifications.
- **Automation**: End-to-end creation of entities within Nextflow Tower, all the way from adding an Organization to launching pipeline(s) within that Organization.

## Prerequisites

You will need to have an account on Nextflow Tower (see [Plans and pricing](https://cloud.tower.nf/pricing/)).

### 1. Dependencies

`tw-pywrap` requires the following dependencies:

1. [Nextflow Tower CLI](https://github.com/seqeralabs/tower-cli#1-installation)

2. [Python (`>=3.8`)](https://www.python.org/downloads/)

3. [PyYAML](https://pypi.org/project/PyYAML/)

Alternatively, you can install the dependencies via Conda by downloading and using the [Conda environment file](environment.yml) that has been supplied in this repository:

```console
conda env create -f environment.yml
conda activate tw-pywrap
```

### 2. Installation

The scripts in this repository are packaged and available on [PyPI](https://pypi.org/project/tw-pywrap/). They can be installed via `pip`:

```
pip install tw-pywrap
```

You can force overwrite the installation to use the latest changes with the command below:

```
pip install --upgrade --force-reinstall tw-pywrap
```

### 3. Configuration

Create a Tower access token using the [Nextflow Tower](https://tower.nf/) web interface via the **Your Tokens** page in your profile.

`tw-pywrap` reads this token from the environment variable `TOWER_ACCESS_TOKEN`. Please export it into your terminal as shown below:

```bash
export TOWER_ACCESS_TOKEN=<your access token>
```

## Quick start

You must provide a YAML file that defines the options for each of the entities you would like to create in Nextflow Tower.

You will need to have an account on Nextflow Tower (see [Plans and pricing](https://cloud.tower.nf/pricing/)). You will also need access to a Workspace and a pre-defined Compute Environment where you can launch a pipeline.

### Launch via YAML

1. Create a YAML file called `hello-world-config.yml` with the contents below, and customise the `<YOUR_WORKSPACE>` and `<YOUR_COMPUTE_ENVIRONMENT>'` entries as required:

   ```
   launch:
     - name: 'hello-world'                               # Workflow name
       workspace: '<YOUR_WORKSPACE>'                     # Workspace name
       compute-env: '<YOUR_COMPUTE_ENVIRONMENT>'         # Compute environment
       revision: 'master'                                # Pipeline revision
       pipeline: 'https://github.com/nextflow-io/hello'  # Pipeline URL
   ```

2. Launch the pipeline with `tw-pywrap`:

   ```
   tw-pywrap hello-world-config.yml
   ```

3. Login to your Tower instance and check the Runs page in the appropriate Workspace for the pipeline you just launched!

### Launch via a Python script

You can also launch the same pipeline via a Python script. This will essentially allow you to extend the functionality on offer within the Tower CLI by leveraging the flexibility and customisation options available in Python.

1. Download the [`launch_hello_world.py`](examples/python/launch_hello_world.py) Python script and customise the `<YOUR_WORKSPACE>` and `<YOUR_COMPUTE_ENVIRONMENT>'` entries as required.

2. Launch the pipeline with `tw-pywrap`:

   ```
   python launch_hello_world.py
   ```

3. Login to your Tower instance and check the Runs page in the appropriate Workspace for the pipeline you just launched!

## Real world example

Please see [`tw-pywrap-e2e.yml`](examples/yaml/tw-pywrap-e2e.yml) for an end-to-end example that highlights how you can use `tw-pywrap` to create everything sequentially in Nextflow Tower all the way from creating a new Organization to launching a pipeline.

## Templates

We have provided template YAML files for each of the entities that can be created on Tower. These can be found in the [`templates/`](templates) directory and should form a good starting point for you to add your own customization:

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

## Contributions and Support

If you would like to contribute to `tw-pywrap`, please see the [contributing guidelines](.github/CONTRIBUTING.md).

For further information or help, please don't hesitate to create an [issue](https://github.com/seqeralabs/tw-pywrap/issues) in this repository.

## Credits

`tw-pywrap` was written by [Esha Joshi](https://github.com/ejseqera), [Adam Talbot](https://github.com/adamrtalbot) and [Harshil Patel](https://github.com/drpatelh) from the Scientific Development Team at [Seqera Labs](https://seqera.io/).
