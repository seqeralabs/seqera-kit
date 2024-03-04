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

from pathlib import Path
from seqerakit import seqeraplatform, helper, overwrite, dump
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
        type=Path,
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
        help="Additional arguments to pass to Seqera Platform"
        " CLI enclosed in double quotes (e.g. '--cli=\"--insecure\"')",
    )

    # YAML dumping options
    yaml_dumping = parser.add_argument_group("YAML Dumping Options")
    yaml_dumping.add_argument(
        "--dump", help="Dump Seqera Platform entity definitions to YAML."
    )
    yaml_dumping.add_argument(
        "--workspace",
        "-w",
        dest="workspace",
        type=str,
        help="Name/ID of the workspace to dump YAML definitions for",
    )
    yaml_dumping.add_argument(
        "--prefix",
        "-p",
        dest="prefix",
        type=str,
        help="Prefix for output YAML files (defaults to workspace name).",
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
        # Create an instance of Overwrite class
        self.overwrite_method = overwrite.Overwrite(self.sp)

    def handle_block(self, block, args, destroy=False):
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
        if overwrite_option:
            logging.debug(f" Overwrite is set to 'True' for {block}\n")
            self.overwrite_method.handle_overwrite(
                block, args["cmd_args"], overwrite_option
            )
        else:
            self.overwrite_method.handle_overwrite(block, args["cmd_args"])

        if block in self.list_for_add_method:
            helper.handle_generic_block(self.sp, block, args["cmd_args"])
        elif block in block_handler_map:
            block_handler_map[block](self.sp, args["cmd_args"])
        else:
            logger.error(f"Unrecognized resource block in YAML: {block}")


def main(args=None):
    options = parse_args(args if args is not None else sys.argv[1:])
    logging.basicConfig(level=options.log_level)

    # If the info flag is set, run 'tw info'
    if options.info:
        sp = seqeraplatform.SeqeraPlatform()
        print(sp.info())
        return

    if not options.yaml and not options.dump:
        logging.error(
            " No YAML(s) provided. Please provide atleast one YAML configuration file."
        )
        sys.exit(1)
    if options.dump:
        if not options.workspace:
            logging.error(
                " Please provide a workspace name or ID to dump YAML definitions for."
            )
            sys.exit(1)
        else:
            sp = seqeraplatform.SeqeraPlatform()
            dp = dump.DumpYaml(sp, options.workspace)
            if options.prefix:
                dp.generate_yaml_dump(options.prefix)
            else:
                dp.generate_yaml_dump(options.workspace)

    # Parse CLI arguments into a list
    cli_args_list = options.cli_args.split() if options.cli_args else []

    sp = seqeraplatform.SeqeraPlatform(cli_args=cli_args_list, dryrun=options.dryrun)

    block_manager = BlockParser(
        sp,
        [
            "organizations",  # all use method.add
            "workspaces",
            "credentials",
            "secrets",
            "actions",
            "datasets",
        ],
    )

    # Parse the YAML file(s) by blocks
    # and get a dictionary of command line arguments
    try:
        cmd_args_dict = helper.parse_all_yaml(options.yaml, destroy=options.delete)
        for block, args_list in cmd_args_dict.items():
            for args in args_list:
                try:
                    # Run the 'tw' methods for each block
                    block_manager.handle_block(block, args, destroy=options.delete)
                except (ResourceExistsError, ResourceCreationError) as e:
                    logging.error(e)
                    sys.exit(1)
    except ValueError as e:
        logging.error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
