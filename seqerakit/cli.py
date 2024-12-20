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
import yaml

from seqerakit import seqeraplatform, helper, overwrite
from seqerakit.seqeraplatform import ResourceExistsError, ResourceCreationError
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
        help="Additional Seqera Platform CLI specific options to be passed,"
        " enclosed in double quotes (e.g. '--cli=\"--insecure\"').",
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
                block, args["cmd_args"], overwrite=False, destroy=True
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

        # Check if overwrite is set to True, and call overwrite handler
        overwrite_option = args.get("overwrite", False)
        if overwrite_option and not dryrun:
            logging.debug(f" Overwrite is set to 'True' for {block}\n")
            self.overwrite_method.handle_overwrite(
                block, args["cmd_args"], overwrite_option
            )

        if block in self.list_for_add_method:
            helper.handle_generic_block(self.sp, block, args["cmd_args"])
        elif block in block_handler_map:
            block_handler_map[block](self.sp, args["cmd_args"])
        else:
            logger.error(f"Unrecognized resource block in YAML: {block}")


def main(args=None):
    options = parse_args(args if args is not None else sys.argv[1:])
    logging.basicConfig(level=getattr(logging, options.log_level.upper()))

    # Parse CLI arguments into a list
    cli_args_list = options.cli_args.split() if options.cli_args else []

    # add and overwrite existing environment variables with those in the env_file
    if options.env_file:
        with open(options.env_file, "r") as f:
            env_vars = yaml.safe_load(f)
            os.environ.update(env_vars)

    sp = seqeraplatform.SeqeraPlatform(
        cli_args=cli_args_list,
        dryrun=options.dryrun,
        json=options.json,
        env_file=options.env_file,
    )

    # If the info flag is set, run 'tw info'
    if options.info:
        result = sp.info()
        if not options.dryrun:
            print(result)
        return

    if not options.yaml:
        if sys.stdin.isatty():
            logging.error(
                " No YAML(s) provided and no input from stdin. Please provide "
                "at least one YAML configuration file or pipe input from stdin."
            )
            sys.exit(1)
        else:
            options.yaml = [sys.stdin]

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
        ],
    )

    # Parse the YAML file(s) by blocks
    # and get a dictionary of command line arguments
    try:
        cmd_args_dict = helper.parse_all_yaml(
            options.yaml, destroy=options.delete, targets=options.targets
        )
        for block, args_list in cmd_args_dict.items():
            for args in args_list:
                block_manager.handle_block(
                    block, args, destroy=options.delete, dryrun=options.dryrun
                )
    except (ResourceExistsError, ResourceCreationError, ValueError) as e:
        logging.error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
