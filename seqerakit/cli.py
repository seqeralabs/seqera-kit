# Copyright 2023, Seqera
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This script is used to build a Seqera Platform instance from a YAML configuration file.
Requires a YAML file that defines the resources to be created in Seqera Platform and
the required options for each resource based on the Seqera Platform CLI.
"""
import argparse
import logging
import sys
import os
import yaml  # type: ignore

from pathlib import Path

from seqerakit import seqeraplatform, helper, overwrite
from seqerakit.seqeraplatform import (
    ResourceExistsError,
    ResourceNotFoundError,
    CommandError,
)
from seqerakit import __version__

logger = logging.getLogger(__name__)


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description="Seqerakit: Python wrapper for the Seqera Platform CLI"
    )
    # General options
    general = parser.add_argument_group("General Options")
    general.add_argument(
        "-l",
        "--log_level",
        default="INFO",
        choices=("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"),
        help="Set the logging level.",
    )
    general.add_argument(
        "--info",
        "-i",
        action="store_true",
        help="Display Seqera Platform information and exit.",
    )
    general.add_argument(
        "-j", "--json", action="store_true", help="Output JSON format in stdout."
    )
    general.add_argument(
        "--dryrun",
        "-d",
        action="store_true",
        help="Print the commands that would be executed.",
    )
    general.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show version number and exit.",
    )

    # YAML processing options
    yaml_processing = parser.add_argument_group("YAML Processing Options")
    yaml_processing.add_argument(
        "yaml",
        nargs="*",
        help="One or more YAML files with Seqera Platform resource definitions.",
    )
    yaml_processing.add_argument(
        "--delete",
        action="store_true",
        help="Recursively delete resources defined in the YAML files.",
    )
    yaml_processing.add_argument(
        "--cli",
        dest="cli_args",
        type=str,
        action="append",
        help="Additional Seqera Platform CLI specific options to be passed,"
        " enclosed in double quotes (e.g. '--cli=\"--insecure\"'). Can be specified"
        " multiple times.",
    )
    yaml_processing.add_argument(
        "--targets",
        dest="targets",
        type=str,
        help="Specify the resources to be targeted for creation in a YAML file through "
        "a comma-separated list (e.g. '--targets=teams,participants').",
    )
    yaml_processing.add_argument(
        "--env-file",
        dest="env_file",
        type=str,
        help="Path to a YAML file containing environment variables for configuration.",
    )
    yaml_processing.add_argument(
        "--on-exists",
        dest="on_exists",
        type=str,
        help="Globally specifies the action to take if a resource already exists.",
        choices=["fail", "ignore", "overwrite"],
    )
    yaml_processing.add_argument(
        "--overwrite",
        action="store_true",
        help="""
        Globally enable overwrite for all resources defined in YAML input(s).
        "Deprecated: Please use '--on-exists=overwrite' instead.""",
        deprecated=True,
    )
    return parser.parse_args(args)


class BlockParser:
    """
    Manages blocks of commands defined in a configuration file and calls appropriate
    functions for each block for custom handling of command-line arguments to _tw_run().
    """

    def __init__(self, sp, list_for_add_method):
        """
        Initializes a BlockParser instance.

        Args:
        sp: A Seqera Platform class instance.
        list_for_add_method: A list of blocks that need to be
        handled by the 'add' method.
        """
        self.sp = sp
        self.list_for_add_method = list_for_add_method

        # Create a separate Seqera Platform client instance without
        # JSON output to avoid mixing resource checks with creation
        # output during overwrite operations.
        sp_without_json = seqeraplatform.SeqeraPlatform(
            cli_args=sp.cli_args,
            dryrun=sp.dryrun,
            json=False,
        )
        self.overwrite_method = overwrite.Overwrite(sp_without_json)

    def handle_block(self, block, args, destroy=False, dryrun=False):
        # Check if delete is set to True, and call delete handler
        if destroy:
            logging.debug(" The '--delete' flag has been specified.\n")
            self.overwrite_method.handle_overwrite(
                block, args["cmd_args"], on_exists="fail", destroy=True
            )
            return

        # Handles a block of commands by calling the appropriate function.
        block_handler_map = {
            "teams": (helper.handle_teams),
            "participants": (helper.handle_participants),
            "compute-envs": (helper.handle_compute_envs),
            "pipelines": (helper.handle_pipelines),
            "launch": lambda sp, args: helper.handle_generic_block(
                sp, "launch", args, method_name=None
            ),
        }

        # Get the on_exists option from args for backward compatibility
        on_exists = args.get("on_exists", "fail")

        # Global settings take precedence over block-level settings
        # First check the global --on-exists parameter
        if (
            hasattr(self.sp, "global_on_exists")
            and self.sp.global_on_exists is not None
        ):
            on_exists = self.sp.global_on_exists
        # Then check for the deprecated global --overwrite flag
        elif getattr(self.sp, "overwrite", False):
            on_exists = "overwrite"

        if not dryrun:
            logging.debug(f" on_exists is set to '{on_exists}' for {block}\n")
            should_continue = self.overwrite_method.handle_overwrite(
                block, args["cmd_args"], on_exists=on_exists
            )

            # If on_exists is "ignore" and resource exists, skip creation
            if not should_continue:
                return

        if block in self.list_for_add_method:
            helper.handle_generic_block(self.sp, block, args["cmd_args"])
        elif block in block_handler_map:
            block_handler_map[block](self.sp, args["cmd_args"])
        else:
            logger.error(f"Unrecognized resource block in YAML: {block}")


def find_yaml_files(path_list=None):
    """
    Find YAML files in the given path list.

    Args:
        path_list (list, optional): A list of paths to search for YAML files.

    Returns:
        list: A list of YAML files found in the given path list or stdin.
    """

    yaml_files = []
    yaml_exts = ["**/*.[yY][aA][mM][lL]", "**/*.[yY][mM][lL]"]

    if not path_list:
        if sys.stdin.isatty():
            raise ValueError(
                "No YAML(s) provided and no input from stdin. Please provide at least "
                "one YAML configuration file or pipe input from stdin."
            )
        return [sys.stdin]

    for path in path_list:
        if path == "-":
            yaml_files.append(path)
            continue

        path = Path(path)
        if not path.exists():
            raise FileExistsError(f"File {path} does not exist")

        if path.is_file():
            yaml_files.append(str(path))
        elif path.is_dir():
            for ext in yaml_exts:
                yaml_files.extend(str(p) for p in path.rglob(ext))
        else:
            yaml_files.append(str(path))

    return yaml_files


def main(args=None):
    options = parse_args(args if args is not None else sys.argv[1:])
    logging.basicConfig(level=getattr(logging, options.log_level.upper()))

    # Parse CLI arguments into a list
    cli_args_list = []
    if options.cli_args:
        for cli_arg in options.cli_args:
            cli_args_list.extend(cli_arg.split())

    # Merge environment variables from env_file with existing ones
    # Will prioritize env_file values
    if options.env_file:
        with open(options.env_file, "r") as f:
            env_vars = yaml.safe_load(f)
            # Only update environment variables that are explicitly defined in env_file
            for key, value in env_vars.items():
                if value is not None:
                    full_value = os.path.expandvars(str(value))
                    os.environ[key] = full_value

    sp = seqeraplatform.SeqeraPlatform(
        cli_args=cli_args_list, dryrun=options.dryrun, json=options.json
    )
    sp.overwrite = options.overwrite  # If global overwrite is set

    # Store the global on_exists parameter if provided
    sp.global_on_exists = options.on_exists if options.on_exists else None

    # If the info flag is set, run 'tw info'
    try:
        if options.info:
            result = sp.info()
            if not options.dryrun:
                print(result)
            return
    except CommandError as e:
        logging.error(e)
        sys.exit(1)

    yaml_files = find_yaml_files(options.yaml)

    block_manager = BlockParser(
        sp,
        [
            "organizations",  # all use method.add
            "workspaces",
            "labels",
            "members",
            "credentials",
            "secrets",
            "actions",
            "datasets",
            "studios",
            "data-links",
        ],
    )

    # Parse the YAML file(s) by blocks
    # and get a dictionary of command line arguments
    try:
        cmd_args_dict = helper.parse_all_yaml(
            yaml_files, destroy=options.delete, targets=options.targets
        )
        for block, args_list in cmd_args_dict.items():
            for args in args_list:
                block_manager.handle_block(
                    block, args, destroy=options.delete, dryrun=options.dryrun
                )
    except (ResourceExistsError, ResourceNotFoundError, CommandError, ValueError) as e:
        logging.error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
