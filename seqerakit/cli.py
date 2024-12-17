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

import logging
import sys
from typing import List, Optional
from typing_extensions import Annotated

import typer
from rich.console import Console

from seqerakit import seqeraplatform, helper, overwrite
from seqerakit.seqeraplatform import ResourceExistsError, ResourceCreationError
from seqerakit import __version__

# Initialize typer app and console
app = typer.Typer(
    help="Seqerakit: Python wrapper for the Seqera Platform CLI",
    rich_markup_mode="rich",
)
console = Console()

# Set up logging
logger = logging.getLogger(__name__)

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
            logging.debug("The '--delete' flag has been specified.\n")
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
            logging.debug(f"Overwrite is set to 'True' for {block}\n")
            self.overwrite_method.handle_overwrite(
                block, args["cmd_args"], overwrite_option
            )

        if block in self.list_for_add_method:
            helper.handle_generic_block(self.sp, block, args["cmd_args"])
        elif block in block_handler_map:
            block_handler_map[block](self.sp, args["cmd_args"])
        else:
            logger.error(f"Unrecognized resource block in YAML: {block}")

@app.command()
def main(
    yaml: Annotated[
        Optional[List[str]], 
        typer.Argument(
            help="One or more YAML files with Seqera Platform resource definitions",
            show_default=False
        )
    ] = None,
    log_level: Annotated[
        str,
        typer.Option(
            "--log-level", "-l",
            help="Set the logging level",
            case_sensitive=False
        )
    ] = "INFO",
    info: Annotated[
        bool,
        typer.Option(
            "--info", "-i",
            help="Display Seqera Platform information and exit"
        )
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option(
            "--json", "-j",
            help="Output JSON format in stdout"
        )
    ] = False,
    dryrun: Annotated[
        bool,
        typer.Option(
            "--dryrun", "-d",
            help="Print the commands that would be executed"
        )
    ] = False,
    delete: Annotated[
        bool,
        typer.Option(
            help="Recursively delete resources defined in the YAML files"
        )
    ] = False,
    cli_args: Annotated[
        Optional[str],
        typer.Option(
            "--cli",
            help="Additional Seqera Platform CLI specific options to be passed"
        )
    ] = None,
    targets: Annotated[
        Optional[str],
        typer.Option(
            help="Specify the resources to be targeted for creation"
        )
    ] = None,
):
    """
    Process YAML configuration files to manage Seqera Platform resources.
    """
    # Set up logging
    logging.basicConfig(level=getattr(logging, log_level.upper()))

    # Parse CLI arguments into a list
    cli_args_list = cli_args.split() if cli_args else []

    # Initialize SeqeraPlatform
    sp = seqeraplatform.SeqeraPlatform(
        cli_args=cli_args_list,
        dryrun=dryrun,
        json=json_output
    )

    # Handle info command
    if info:
        result = sp.info()
        if not dryrun:
            console.print(result)
        return

    # Handle YAML input
    if not yaml:
        if sys.stdin.isatty():
            raise typer.BadParameter(
                "No YAML(s) provided and no input from stdin. Please provide "
                "at least one YAML configuration file or pipe input from stdin."
            )
        yaml = [sys.stdin]

    # Initialize BlockParser
    block_manager = BlockParser(
        sp,
        [
            "organizations", # all use method.add
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
            yaml, destroy=delete, targets=targets
        )
        for block, args_list in cmd_args_dict.items():
            for args in args_list:
                block_manager.handle_block(
                    block, args, destroy=delete, dryrun=dryrun
                )
    except (ResourceExistsError, ResourceCreationError, ValueError) as e:
        logger.error(str(e))
        raise typer.Exit(code=1)

def run():
    """Entry point for the CLI"""
    app(prog_name="seqerakit")

if __name__ == "__main__":
    run()
