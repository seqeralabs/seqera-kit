import subprocess
import os
import json
from pathlib import Path
import yaml
import shlex
from datetime import date
import tempfile


def tw_run(cmd, *args, **kwargs):
    """
    Run a tw command with supplied commands
    """
    command = ["tw"]
    if kwargs.get("to_json"):
        command.extend(["-o", "json"])
    command.extend(cmd)
    command.extend(args)

    if kwargs.get("config") is not None:
        config_path = kwargs["config"]
        command.append(f"--config={config_path}")

    if "params_file" in kwargs:
        params_path = kwargs["params_file"]
        command.append(f"--params-file={params_path}")

    full_cmd = " ".join(shlex.quote(arg) for arg in command)

    # Run the command and return the stdout
    process = subprocess.Popen(full_cmd, stdout=subprocess.PIPE, shell=True)
    stdout, _ = process.communicate()
    stdout = stdout.decode("utf-8").strip()

    return stdout


def tw_env_var(tw_variable):
    """
    Check if a tw environment variable exists
    """
    if not tw_variable in os.environ:
        raise EnvironmentError(
            f"Tower environment variable '{tw_variable}' is not set."
        )
    else:
        return os.environ[tw_variable]


def validate_credentials(credentials, workspace):
    """
    Validate credentials for a workspace using the name of the credentials
    """
    credentials_avail = tw_run(
        ["credentials", "list", "--workspace", workspace], to_json=True
    )
    credentials_avail = json.loads(credentials_avail)

    # Check if provided credentials exist in the workspace
    if credentials not in [item["name"] for item in credentials_avail["credentials"]]:
        raise ValueError(
            f"Credentials '{credentials}' not found in workspace '{workspace}'"
        )


def get_json_files(json_files):
    """
    Convert a list of PosixPath objects for the provided JSON files
    into a comma-separated list of strings and parse the name of JSONs out
    to use as the name for the CE being created.

    If a single path is provided, return the string representation of the path..
    Returns both lists in a tuple.
    """
    if not isinstance(json_files, list):
        json_files = [json_files]

    json_str = [str(json_in) for json_in in json_files]
    basenames = [Path(x).stem for x in json_files]

    return json_str, basenames


def find_key_value_in_dict(data, target_key, target_value):
    """
    Generic method to find a key-value pair in a nested dictionary and within
    lists of dictionaries.
    Can use the input of json.loads() converting JSON string to dict.
    #TODO: huge candidate for refactoring
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key and value == target_value:
                return True
            if isinstance(value, dict) and find_key_value_in_dict(
                value, target_key, target_value
            ):
                return True
            if isinstance(value, list):
                for item in value:
                    if find_key_value_in_dict(item, target_key, target_value):
                        return True
    elif isinstance(data, list):
        for item in data:
            if find_key_value_in_dict(item, target_key, target_value):
                return True
    return False


def validate_id(json_data, name):
    """
    Wrapper around find_key_value_in_dict() to validate that a resource was
    created successfully in Tower by looking for the name.
    """
    data = json.loads(json_data)
    if not find_key_value_in_dict(data, "name", name):
        raise ValueError(f"Could not find '{name}' in Tower. Something went wrong.")


def check_if_exists(json_data, name):
    """
    Wrapper around find_key_value_in_dict() to validate that a resource was
    created successfully in Tower by looking for the name.
    """
    data = json.loads(json_data)
    if find_key_value_in_dict(data, "name", name):
        raise ValueError(f"Resource '{name}' already exists in Tower.")


def is_valid_json(file_path):
    """
    Check if a file is valid JSON
    """
    try:
        with open(file_path, "r") as f:
            json.load(f)
        return True
    except json.JSONDecodeError:
        return False


def is_valid_yaml(file_path):
    """
    Check if a file is valid YAML
    """
    try:
        with open(file_path, "r") as f:
            yaml.safe_load(f)
        return True
    except yaml.YAMLError:
        return False


def get_date():
    """
    Get the current date in YYYY_MM_DD format
    """
    current_date = date.today()
    formatted_date = current_date.strftime("%Y_%m_%d")
    return formatted_date


def get_pipeline_params(pipeline_data, pipeline_name):
    """
    Create a temporary params.yaml file containing `parameters`
    defined in the yaml file used to launch pipelines.
    """

    # Define a new class to register a new YAML representer to put single
    # quotes around the string values
    class quoted_str(str):
        pass

    def quoted_str_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="'")

    yaml.add_representer(quoted_str, quoted_str_representer)

    for pipeline in pipeline_data:
        if pipeline["name"] == pipeline_name:
            pipeline_parameters = {
                k: quoted_str(v) if k == "outdir" and isinstance(v, str) else v
                for k, v in pipeline["parameters"].items()
            }

    # Create a temporary file to write the modified data
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        params_yaml = temp_file.name

        # Write the modified data to the temporary file
        with open(params_yaml, "w") as file:
            yaml.dump(pipeline_parameters, file)
    return params_yaml


def parse_yaml_file(file_path):
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)

    pipeline_data = []
    for pipeline in data["pipelines"]:
        pipeline_dict = {
            "name": pipeline.get("name", None),
            "url": pipeline["url"],
            "revision": pipeline["revision"],
            "profiles": pipeline["profiles"],
            "parameters": pipeline["parameters"],
            "config": pipeline.get(
                "config", None
            ),  # Not all pipelines might have a config
        }
        pipeline_data.append(pipeline_dict)

    return pipeline_data


def get_pipeline_repo(pipeline_repo):
    """
    Provide full nf-core github URL if
    only the repo name is provided
    """
    if "nf-core" in pipeline_repo.lower():
        return "https://github.com/" + pipeline_repo
    else:
        return pipeline_repo
