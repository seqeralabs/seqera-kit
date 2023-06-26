"""
This file contains helper functions for the library.
Including handling methods for each block in the YAML file, and parsing
methods for each block in the YAML file.
"""
import yaml

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
