# Automate benchmark tests on Tower via CLI

This sub-directory contains scripts that allow for 'automation' of running nf-core pipelines on Tower for benchmarking.

## Setup
TODO

## Usage

### Config for running pipelines in `benchmark_tests.yaml`
In this config, specify what
 - Workspace
 - Compute-env
 - Pipelines and their revisions you want to run for your
 - Specify a base cloud storage URI with `outdir_base` that will be used to output results of the pipelines to. Results will be stored as: `{outdir_base}/{pipeline_name}/profile_{profile}/{date}`
 - Specify configuration options in `config_file`

There are default examples provided in this repo that can be edited or just used out of the box.

You can save versions of these configs for provenance (i.e. `run_benchmarks_profile_test.yaml`, `benchmarks_profile_test_full.yaml`)

### Run the script
You can execute launching of the pipelines by running the script as follows:
```
python run_benchmarks.py --config benchmark_tests.yaml
```

All pipelines you specified will be launched into the provided workspace on Tower.
