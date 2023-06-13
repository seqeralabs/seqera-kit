#!/usr/bin/env python3

"""
Wrapper script to automate pipeline running for a set of nf-core/pipelines
provided in a config.yaml
"""
import argparse
from pathlib import Path
import sys
import logging
import time
import yaml
from tw_py import Tower
from tw_py import utils

logger = logging.getLogger(__name__)


def log_and_continue(e):
    logger.error(e)
    return


def parse_args():
    # TODO: description and usage
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, help="Config file with pipelines to run")
    parser.add_argument(
        "-l",
        "--log_level",
        default="INFO",
        choices=("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"),
        help="The desired log level (default: WARNING).",
    )
    return parser.parse_args()


def handle_launch(
    tw_wrapper: Tower,
    pipeline_url: str,
    profile: str,
    name: str = None,
    revision: str = None,
    compute_env: str = None,
    workspace: str = None,
    params_file: str = None,
    config_file: str = None,
):
    try:
        # Prepare the list of additional command line options
        cmd_options = [
            f"--name={name}",
            f"--revision={revision}",
            f"--profile={profile}",
            f"--compute-env={compute_env}",
            f"--workspace={workspace}",
        ]

        tw_wrapper.launch(
            utils.get_pipeline_repo(pipeline_url),
            *cmd_options,  # Expand the list as positional arguments
            params_file=params_file,
            config=config_file,
        )
        logging.info(
            f"Launched pipeline {pipeline_url} with revision {revision} and profile {profile}"
        )
    except Exception as e:
        logger.error(e)


def main():
    args = parse_args()
    logging.basicConfig(level=args.log_level)

    # Check environment variables first
    try:
        utils.tw_env_var("TOWER_ACCESS_TOKEN")
    except EnvironmentError as e:
        logger.error(e)

    # Make sure config is provided
    if not args.config:
        logger.error(
            "Please provide a path to the YAML configuration file using --config."
        )
        return

    # Validate YAML file
    if not utils.is_valid_yaml(args.config):
        logging.error("Invalid YAML configuration file")
        return

    # Load YAML configuration
    try:
        with open(args.config, "r") as f:
            config = yaml.safe_load(f)
    except (FileNotFoundError, yaml.YAMLError) as e:
        logging.error(f"Error loading the YAML configuration file: {e}")
        return

    # Parse config file fields for workspace and ce
    workspace = config.get("workspace") or utils.tw_env_var("TOWER_WORKSPACE_ID")
    compute_env = config.get("compute-env")

    # Create an instance of the Tower wrapper class
    tw = Tower(workspace)

    # Parse the YAML file
    pipeline_data = utils.parse_yaml_file(args.config)

    # Launch the pipeline
    for pipeline in pipeline_data:
        logging.info(f"Launching pipeline {pipeline['name']}")

        # Get pipeline specific params to pass to launch command
        pipeline_params = utils.get_pipeline_params(pipeline_data, pipeline["name"])

        handle_launch(
            tw,
            pipeline["url"],
            pipeline["profiles"],
            pipeline["name"],
            pipeline.get("revision"),
            compute_env,
            workspace,
            params_file=pipeline_params,
            config_file=pipeline["config"] if pipeline.get("config") else None,
        )
    time.sleep(5)


if __name__ == "__main__":
    sys.exit(main())
