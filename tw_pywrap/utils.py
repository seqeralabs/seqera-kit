import os
import json
from pathlib import Path
from datetime import date
import tempfile
import yaml
from urllib.parse import urlparse


def tw_env_var(tw_variable):
    """
    Check if a tw environment variable exists
    """
    if tw_variable not in os.environ:
        raise EnvironmentError(
            f"Tower environment variable '{tw_variable}' is not set."
        )
    return os.environ[tw_variable]


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


def find_key_value_in_dict(data, target_key, target_value, return_key):
    """
    Generic method to find a key-value pair in a nested dictionary and within
    lists of dictionaries.
    Can use the input of json.loads() converting JSON string to dict.
    #TODO: huge candidate for refactoring
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key and value == target_value:
                # If we find our target key-value pair,
                # return the value of the specified return key if it is not None
                if return_key is not None:
                    return data.get(return_key)
                else:
                    # or any other value to indicate the existence of the key-value pair
                    return True
            if isinstance(value, dict):
                result = find_key_value_in_dict(
                    value, target_key, target_value, return_key
                )
                if result:
                    return result
            if isinstance(value, list):
                for item in value:
                    result = find_key_value_in_dict(
                        item, target_key, target_value, return_key
                    )
                    if result:
                        return result
    elif isinstance(data, list):
        for item in data:
            result = find_key_value_in_dict(item, target_key, target_value, return_key)
            if result:
                return result
    return None


def validate_id(json_data, name):
    """
    Wrapper around find_key_value_in_dict() to validate that a resource was
    created successfully in Tower by looking for the name.
    """
    data = json.loads(json_data)
    if not find_key_value_in_dict(data, "name", name):
        raise ValueError(f"Could not find '{name}' in Tower. Something went wrong.")


def check_if_exists(json_data, namekey, namevalue):
    """
    Wrapper around find_key_value_in_dict() to validate that a resource was
    created successfully in Tower by looking for the name and value.
    """
    data = json.loads(json_data)
    if find_key_value_in_dict(data, namekey, namevalue, return_key=None):
        return True


def is_valid_json(file_path):
    """
    Check if a file is valid JSON
    """
    try:
        with open(file_path, "r") as file:
            json.load(file)
        return True
    except json.JSONDecodeError:
        return False


def is_valid_yaml(file_path):
    """
    Check if a file is valid YAML
    """
    try:
        with open(file_path, "r") as file:
            yaml.safe_load(file)
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
    """
    Parse a yaml file and return a dict of info required for launching of pipelines
    """
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


def is_url(s):
    """
    Check if a string is a valid URL
    """
    try:
        result = urlparse(s)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def create_temp_yaml(params_dict):
    """
    Create a generic temporary yaml file given a dictionary
    """
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".yaml"
    ) as temp_file:
        yaml.dump(params_dict, temp_file)
        return temp_file.name
