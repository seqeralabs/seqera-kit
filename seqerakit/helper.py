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
This file contains helper functions for the library.
Including handling methods for each block in the YAML file, and parsing
methods for each block in the YAML file.
"""
import yaml
from seqerakit import utils
import sys
import json


def parse_yaml_block(yaml_data, block_name):
    # Get the name of the specified block/resource.
    block = yaml_data.get(block_name)

    # If block is not found in the YAML, return an empty list.
    if not block:
        return block_name, []

    # Initialize an empty list to hold the lists of command line arguments.
    cmd_args_list = []

    # Initialize a set to track the --name values within the block.
    name_values = set()

    # Iterate over each item in the block.
    # TODO: fix for resources that can be duplicate named in an org
    for item in block:
        cmd_args = parse_block(block_name, item)
        name = find_name(cmd_args)
        if name in name_values:
            raise ValueError(
                f" Duplicate name key specified in config file"
                f" for {block_name}: {name}. Please specify a unique value."
            )
        name_values.add(name)

        cmd_args_list.append(cmd_args)

    # Return the block name and list of command line argument lists.
    return block_name, cmd_args_list


def parse_all_yaml(file_paths, destroy=False, targets=None):
    # If multiple yamls, merge them into one dictionary
    merged_data = {}

    # Special handling for stdin represented by "-"
    if not file_paths or "-" in file_paths:
        # Read YAML directly from stdin
        data = yaml.safe_load(sys.stdin)
        if not data:
            raise ValueError(
                " The input from stdin is empty or does not contain valid YAML data."
            )
        merged_data.update(data)

    for file_path in file_paths:
        if file_path == "-":
            continue
        try:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)
                if not data:
                    raise ValueError(
                        f" The file '{file_path}' is empty or "
                        "does not contain valid data."
                    )
            # Process each key-value pair in YAML data
            for key, new_value in data.items():
                # Check if key exist in merged_data and
                # new value is a list of dictionaries
                if (
                    key in merged_data
                    and isinstance(new_value, list)
                    and all(isinstance(i, dict) for i in new_value)
                ):
                    # Serialize dictionaries to JSON strings for comparison
                    existing_items = {
                        json.dumps(d, sort_keys=True) for d in merged_data[key]
                    }
                    for item in new_value:
                        # Check if item is not already present in merged data
                        item_json = json.dumps(item, sort_keys=True)
                        if item_json not in existing_items:
                            # Append item to merged data
                            merged_data[key].append(item)
                else:
                    merged_data[key] = new_value

        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
            sys.exit(1)

    block_names = list(merged_data.keys())

    # Filter blocks based on targets if provided
    if targets:
        target_blocks = set(targets.split(","))
        block_names = [block for block in block_names if block in target_blocks]

    # Define the order in which the resources should be created.
    resource_order = [
        "organizations",
        "teams",
        "workspaces",
        "labels",
        "members",
        "participants",
        "credentials",
        "compute-envs",
        "secrets",
        "actions",
        "datasets",
        "pipelines",
        "launch",
    ]

    # Reverse the order of resources to delete if destroy is True
    if destroy:
        resource_order = resource_order[:-1][::-1]

    # Initialize an empty dictionary to hold all the command arguments.
    cmd_args_dict = {}

    # Iterate over each block name in the desired order.
    for block_name in resource_order:
        if block_name in block_names:
            # Parse the block and add its command line arguments to the dictionary.
            block_name, cmd_args_list = parse_yaml_block(merged_data, block_name)
            cmd_args_dict[block_name] = cmd_args_list

    # Return the dictionary of command arguments.
    return cmd_args_dict


def parse_block(block_name, item):
    # Define the mapping from block names to functions.
    block_to_function = {
        "credentials": parse_type_block,
        "compute-envs": parse_type_block,
        "actions": parse_type_block,
        "teams": parse_teams_block,
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


def parse_type_block(item, priority_keys=["type", "config-mode", "file-path"]):
    cmd_args = []

    # Ensure at least one of 'type' or 'file-path' is present
    if not any(key in item for key in ["type", "file-path"]):
        raise ValueError(
            "Please specify at least 'type' or 'file-path' for creating the resource."
        )

    # Process priority keys first
    for key in priority_keys:
        if key in item:
            cmd_args.append(str(item[key]))
            del item[key]  # Remove the key to avoid repeating in args

    for key, value in item.items():
        if isinstance(value, bool):
            if value:
                cmd_args.append(f"--{key}")
        elif key == "params":
            temp_file_name = utils.create_temp_yaml(value)
            cmd_args.extend(["--params-file", temp_file_name])
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
    params_file_path = None

    for key, value in item.items():
        if key == "url":
            repo_args.extend([str(value)])
        elif key == "params":
            params_dict = value
        elif key == "params-file":
            params_file_path = str(value)
        elif key == "file-path":
            repo_args.extend([str(value)])
        elif isinstance(value, bool):
            if value:
                cmd_args.append(f"--{key}")
        else:
            cmd_args.extend([f"--{key}", str(value)])

    # Create the temporary YAML file after processing all items
    if "params" in item:
        temp_file_name = utils.create_temp_yaml(
            params_dict, params_file=params_file_path
        )
        params_args.extend(["--params-file", temp_file_name])

    if params_file_path and "params" not in item:
        params_args.extend(["--params-file", params_file_path])

    combined_args = cmd_args + repo_args + params_args
    return combined_args


def parse_launch_block(item):
    repo_args = []
    cmd_args = []
    params_args = []
    params_file_path = None

    for key, value in item.items():
        if key == "pipeline" or key == "url":
            repo_args.extend([str(value)])
        elif key == "params":
            params_dict = value
        elif key == "params-file":
            params_file_path = str(value)
        elif isinstance(value, bool):
            if value:
                cmd_args.append(f"--{key}")
        else:
            cmd_args.extend([f"--{key}", str(value)])

    if "params" in item:
        temp_file_name = utils.create_temp_yaml(
            params_dict, params_file=params_file_path
        )
        params_args.extend(["--params-file", temp_file_name])

    if params_file_path and "params" not in item:
        params_args.extend(["--params-file", params_file_path])

    cmd_args = cmd_args + repo_args + params_args
    return cmd_args


# Handlers to call the actual sp method,based on the block name.
# Certain blocks required special handling and combination of methods.


def handle_generic_block(sp, block, args, method_name="add"):
    # Generic handler for most blocks, with optional method name
    method = getattr(sp, block)
    if method_name is None:
        method(*args)
    else:
        method(method_name, *args)


def handle_teams(sp, args):
    cmd_args, members_cmd_args = args
    sp.teams("add", *cmd_args)
    for sublist in members_cmd_args:
        sp.teams("members", *sublist)


def handle_participants(sp, args):
    # Generic handler for blocks with a key to skip
    method = getattr(sp, "participants")
    skip_key = "--role"
    new_args = [
        arg
        for i, arg in enumerate(args)
        if not (args[i - 1] == skip_key or arg == skip_key)
    ]
    method("add", *new_args)
    method("update", *args)


def handle_compute_envs(sp, args):
    json_file = any(".json" in arg for arg in args)

    method = getattr(sp, "compute_envs")

    if json_file:
        method("import", *args)
    else:
        method("add", *args)


def handle_pipelines(sp, args):
    method = getattr(sp, "pipelines")
    for arg in args:
        # Check if arg is a url or a json file.
        # If it is, use the appropriate method and break.
        if utils.is_url(arg):
            method("add", *args)
            break
        elif ".json" in arg:
            method("import", *args)


def find_name(cmd_args):
    """
    Find and return the value associated with --name in cmd_args, where cmd_args
    can be a list, a tuple of lists, or nested lists/tuples.

    The function searches for the following keys: --name, --user, --email.

    Parameters:
    - cmd_args: The command arguments (list, tuple, or nested structures).

    Returns:
    - The value associated with the first key found, or None if none are found.
    """
    # Predefined list of keys to search for
    keys = {"--name", "--user", "--email"}

    def search(args):
        it = iter(args)
        for arg in it:
            if isinstance(arg, str) and arg in keys:
                return next(it, None)
            elif isinstance(arg, (list, tuple)):
                result = search(arg)
                if result is not None:
                    return result
        return None

    return search(cmd_args.get("cmd_args", []))
