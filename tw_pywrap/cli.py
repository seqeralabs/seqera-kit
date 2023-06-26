"""
This script is used to build a Tower instance from a YAML configuration file.
Requires a YAML file that defines the resources to be created in Tower and
the required options for each resource based on the Tower CLI.
"""
import argparse
import logging
import time
import yaml

from pathlib import Path
from tw_pywrap import tower
import tw_pywrap.helper as helper  # TODO: refactor
from tw_pywrap import overwrite

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        "--log_level",
        default="INFO",
        choices=("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"),
        help="The desired log level (default: INFO).",
        type=str.upper,
    )
    parser.add_argument(
        "yaml", type=Path, help="Config file with Tower resources to create"
    )
    return parser.parse_args()


class BlockParser:
    """
    Manages blocks of commands defined in a configuration file and calls appropriate
    functions for each block for custom handling of command-line arguments to _tw_run().
    """

    def __init__(self, tw, list_for_add_method):
        """
        Initializes a BlockParser instance.

        Args:
        tw: A Tower class instance.
        list_for_add_method: A list of blocks that need to be
        handled by the 'add' method.
        """
        self.tw = tw
        self.list_for_add_method = list_for_add_method

    def handle_block(self, block, args):
        # Handles a block of commands by calling the appropriate function.
        block_handler_map = {
            "teams": helper.handle_teams,
            "participants": helper.handle_participants,
            "compute-envs": helper.handle_compute_envs,
            "pipelines": helper.handle_pipelines,
            "launch": helper.handle_launch,
        }

        # Check if overwrite is set to True, and call overwrite handler
        overwrite_option = args.get("overwrite", False)
        if overwrite_option:
            logging.debug(f" Overwrite is set to 'True' for {block}\n")
            overwrite.Overwrite(self.tw).handle_overwrite(block, args["cmd_args"])

        if block in self.list_for_add_method:
            helper.handle_add_block(self.tw, block, args["cmd_args"])
        elif block in block_handler_map:
            block_handler_map[block](self.tw, args["cmd_args"])
        else:
            logger.error(f"Unrecognized resource block in YAML: {block}")


def main():
    options = parse_args()
    logging.basicConfig(level=options.log_level)

    tw = tower.Tower()
    block_manager = BlockParser(
        tw,
        [
            "organizations",  # all use method.add
            "workspaces",
            "credentials",
            "secrets",
            "actions",
            "datasets",
        ],
    )
    with open(options.yaml, "r") as f:
        data = yaml.safe_load(f)

    # Returns a dict that maps block names to lists of command line arguments.
    cmd_args_dict = helper.parse_all_yaml(options.yaml, list(data.keys()))

    for block, args_list in cmd_args_dict.items():
        for args in args_list:
            # Run the methods for each block
            block_manager.handle_block(block, args)
            time.sleep(3)


if __name__ == "__main__":
    main()
