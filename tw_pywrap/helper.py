"""
This file contains helper functions for the library.
Including handling methods for each block in the YAML file, and parsing
methods for each block in the YAML file.
"""
import json
import yaml

from tw_pywrap import tower
from tw_pywrap import utils

# TODO: rename these functions to be more descriptive


def parse_yaml_block(file_path, block_name):
    # Load the YAML file.
    with open(file_path, "r") as f:
        data = yaml.safe_load(f)

    # Get the specified block.
    block = data.get(block_name)

    # Initialize an empty list to hold the lists of command line arguments.
    cmd_args_list = []

    # Iterate over each item in the block.
    for item in block:
        cmd_args_list.append(parse_block(block_name, item))

    # Return the block name and list of command line argument lists.
    return block_name, cmd_args_list


def parse_all_yaml(file_path, block_names):
    # Initialize an empty dictionary to hold all the command arguments.
    cmd_args_dict = {}

    # Iterate over each block name.
    for block_name in block_names:
        # Parse the block and add its command arguments to the dictionary.
        block_name, cmd_args_list = parse_yaml_block(file_path, block_name)
        cmd_args_dict[block_name] = cmd_args_list

    # Return the dictionary of command arguments.
    return cmd_args_dict


def parse_block(block_name, item):
    # Define the mapping from block names to functions.
    block_to_function = {
        "credentials": parse_credentials_block,
        "compute-envs": parse_compute_envs_block,
        "teams": parse_teams_block,
        "actions": parse_actions_block,
        "datasets": parse_datasets_block,
        "pipelines": parse_pipelines_block,
        "launch": parse_launch_block,
    }
    # Use the generic block function as a default.
    parse_fn = block_to_function.get(block_name, parse_generic_block)
    overwrite = item.pop("overwrite", False)

    # Call the appropriate function and return its result along with overwrite value.
    cmd_args = parse_fn(item)
    return {"cmd_args": cmd_args, "overwrite": overwrite}


# Parsers for certain blocks of yaml that require handling
# for structuring command line arguments in a certain way


def parse_generic_block(item):
    cmd_args = []
    for key, value in item.items():
        cmd_args.extend([f"--{key}", str(value)])
    return cmd_args


def parse_credentials_block(item):
    cmd_args = []
    for key, value in item.items():
        if key == "type":
            cmd_args.append(str(value))
        else:
            cmd_args.extend([f"--{key}", str(value)])
    return cmd_args


def parse_compute_envs_block(item):
    cmd_args = []
    for key, value in item.items():
        if key == "file-path":
            cmd_args.append(str(value))
        else:
            cmd_args.extend([f"--{key}", str(value)])
    return cmd_args


def parse_teams_block(item):
    # Keys for each list
    cmd_keys = ["name", "organization", "description"]
    members_keys = ["name", "organization", "members"]

    cmd_args = []
    members_cmd_args = []

    for key, value in item.items():
        if key in cmd_keys:
            cmd_args.extend([f"--{key}", str(value)])
        elif key in members_keys and key == "members":
            for member in value:
                members_cmd_args.append(
                    [
                        "--team",
                        str(item["name"]),
                        "--organization",
                        str(item["organization"]),
                        "add",
                        "--member",
                        str(member),
                    ]
                )
    return (cmd_args, members_cmd_args)


def parse_actions_block(item):
    cmd_args = []
    temp_file_name = None
    for key, value in item.items():
        if key == "type":
            cmd_args.append(str(value))
        elif key == "params":
            temp_file_name = utils.create_temp_yaml(value)
            cmd_args.extend(["--params-file", temp_file_name])
        else:
            cmd_args.extend([f"--{key}", str(value)])
    return cmd_args


def parse_datasets_block(item):
    cmd_args = []
    for key, value in item.items():
        if key == "file-path":
            cmd_args.extend(
                [
                    str(item["file-path"]),
                    "--name",
                    str(item["name"]),
                    "--workspace",
                    str(item["workspace"]),
                    "--description",
                    str(item["description"]),
                ]
            )
        if key == "header" and value is True:
            cmd_args.append("--header")
    return cmd_args


def parse_pipelines_block(item):
    cmd_args = []
    repo_args = []
    params_args = []

    for key, value in item.items():
        if key == "url":
            repo_args.extend([str(value)])
        elif key == "params":
            temp_file_name = utils.create_temp_yaml(value)
            params_args.extend(["--params-file", temp_file_name])
        elif key == "file-path":
            repo_args.extend([str(value)])
        else:
            cmd_args.extend([f"--{key}", str(value)])

    # First append the url related arguments then append the remaining ones
    cmd_args = repo_args + params_args + cmd_args
    return cmd_args


def parse_launch_block(item):
    repo_args = []
    cmd_args = []
    for key, value in item.items():
        if key == "pipeline" or key == "url":
            repo_args.extend([str(value)])
        elif key == "params":
            temp_file_name = utils.create_temp_yaml(value)
            cmd_args.extend(["--params-file", temp_file_name])
        else:
            cmd_args.extend([f"--{key}", str(value)])
    cmd_args = repo_args + cmd_args

    return cmd_args


# Handlers to call the actual tower method,
# based on the block name and uses that as subcommand.
# Recall: we dynamically add methods to the `Tower` class to run `tw` subcommand


def handle_add_block(tw, block, args):
    method = getattr(tw, block)
    method("add", *args)


def handle_teams(tw, args):
    cmd_args, members_cmd_args = args
    tw.teams("add", *cmd_args)
    for sublist in members_cmd_args:
        tw.teams("members", *sublist)


def handle_participants(tw, args):
    new_args = []
    skip_next = False
    for arg in args:
        if skip_next or arg == "--role":
            skip_next = not skip_next
            continue
        new_args.append(arg)
    tw.participants("add", *new_args)
    tw.participants("update", *args)


def handle_compute_envs(tw, args):
    tw.compute_envs("import", *args)


def handle_pipelines(tw, args):
    method = getattr(tw, "pipelines")
    for arg in args:
        # Check if arg is a url or a json file.
        # If it is, use the appropriate method and break.
        if utils.is_url(arg):
            method("add", *args)
            break
        elif ".json" in arg:
            method("import", *args)


def handle_launch(tw, args):
    method = getattr(tw, "launch")
    method(*args)


# Handle overwrite functionality


def get_delete_identifier(block, yaml_key, key_value, target_key, tw_args):
    """
    Special handler for resources that need to be deleted by another identifier.
    TODO: Remove when `--overwrite` is supported by the CLI
    """
    # Get details about entity to delete in JSON
    tw = tower.Tower()
    base_method = getattr(tw, "-o json")

    # Get json data for block using list method
    block_data = base_method(block, "list", "-o", tw_args)

    # Get the identifier key for the block
    real_identifier = utils.find_key_value_in_dict(
        json.loads(block_data), yaml_key, key_value, target_key
    )

    # Return the correct identifier to use delete method on
    return real_identifier


def handle_overwrite(tw, block, args):
    """
    Handler for overwrite functionality which will delete the resource
    before adding it again.
    # TODO: Remove when `--overwrite` is supported by the CLI
    # TODO: Refactor this desperately
    """
    # Define blocks for simple overwrite with --name and --workspace
    generic_deletion = [
        "credentials",
        "secrets",
        "compute-envs",
        "datasets",
        "actions",
        "pipelines",
    ]
    # Special handlers for certain resources that need to be deleted with specific args
    block_operations = {
        "organizations": {
            "keys": ["name"],
            "method_args": lambda tw_args: ("delete", "--name", tw_args["name"]),
            "name_key": "orgName",
        },
        # Requires teamId to delete, not name
        "teams": {
            "keys": ["name", "organization"],
            "method_args": lambda tw_args: (
                "delete",
                "--id",
                str(
                    get_delete_identifier(
                        "teams",
                        "name",
                        tw_args["name"],
                        "teamId",
                        tw_args["organization"],
                    )
                ),
                "--organization",
                tw_args["organization"],
            ),
            "name_key": "name",
        },
        "participants": {
            "keys": ["name", "type", "workspace"],
            "method_args": lambda tw_args: (
                "delete",
                "--name",
                tw_args["name"],
                "--type",
                tw_args["type"],
                "--workspace",
                tw_args["workspace"],
            ),
            "name_key": "email",
        },
        # Requires workspace formatted a certain way for valid workspace name
        "workspaces": {
            "keys": ["name", "organization"],
            "method_args": lambda tw_args: (
                "delete",
                "--name",
                "{}/{}".format(tw_args["organization"], tw_args["name"]),
            ),
            "name_key": "workspaceName",
        },
    }

    if block in generic_deletion:
        block_operations[block] = {
            "keys": ["name", "workspace"],
            "method_args": lambda tw_args: (
                "delete",
                "--name",
                tw_args["name"],
                "--workspace",
                tw_args["workspace"],
            ),
            "name_key": "name",
        }

    if block in block_operations:
        operation = block_operations[block]
        keys_to_get = operation["keys"]

        # Return JSON data to check if resource exists
        json_method = getattr(tw, "-o json")

        if block == "teams":
            tw_args = get_values_from_cmd_args(args[0], keys_to_get)
            json_data = json_method(block, "list", "-o", tw_args["organization"])
        elif block == "participants":
            tw_args = get_values_from_cmd_args(args, keys_to_get)
            json_data = json_method(block, "list", "-w", tw_args["workspace"])
            if tw_args["type"] == "TEAM":
                operation["name_key"] = "teamName"
        else:
            tw_args = get_values_from_cmd_args(args, keys_to_get)
            json_data = json_method(block, "list")

        # Check if the resource exists, if true, delete it, else return
        if utils.check_if_exists(json_data, operation["name_key"], tw_args["name"]):
            method_args = operation["method_args"](tw_args)
            method = getattr(tw, block)
            method(*method_args)
        else:
            return


# Other utility functions
def get_values_from_cmd_args(cmd_args, keys):
    values = {key: None for key in keys}
    key = None

    for arg in cmd_args:
        if arg.startswith("--"):
            key = arg[2:]
        else:
            if key and key in keys:
                values[key] = arg
            key = None
    return values
