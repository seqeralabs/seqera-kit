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

import logging
import json
import tempfile
import os
import yaml
from urllib.parse import urlparse
import re


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


def check_if_exists(json_data, namekey, namevalue):
    """
    Wrapper around find_key_value_in_dict() to validate that a resource was
    created successfully in Seqera Platform by looking for the name and value.
    """
    if not json_data:
        return False
    logging.info(f" Checking if {namekey} {namevalue} exists in Seqera Platform...")
    # Regex pattern to match environment variables in the string
    env_var_pattern = re.compile(r"\$\{?[\w]+\}?")

    # Substitute environment variables in namevalue
    resolved_value = env_var_pattern.sub(replace_env_var, namevalue)

    data = json.loads(json_data)
    if find_key_value_in_dict(data, namekey, resolved_value, return_key=None):
        return True


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


class quoted_str(str):
    pass


def quoted_str_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')


yaml.add_representer(quoted_str, quoted_str_representer)


def create_temp_yaml(params_dict, params_file=None):
    """
    Create a temporary YAML file given a dictionary.
    Optionally combine with contents from a JSON or YAML file if provided.
    """

    def read_file(file_path):
        with open(file_path, "r") as file:
            return (
                json.load(file) if file_path.endswith(".json") else yaml.safe_load(file)
            )

    combined_params = {}

    if params_file:
        file_params = read_file(params_file)
        combined_params.update(file_params)

    combined_params.update(params_dict)

    for key, value in combined_params.items():
        if isinstance(value, str):
            expanded_value = re.sub(r"\$\{?\w+\}?", replace_env_var, value)
            combined_params[key] = quoted_str(expanded_value)

    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".yaml"
    ) as temp_file:
        yaml.dump(combined_params, temp_file, default_flow_style=False)
        return temp_file.name


def replace_env_var(match):
    var_name = match.group().lstrip("$").strip("{}")
    var_value = os.getenv(var_name)
    if var_value is None:
        raise EnvironmentError(f"Environment variable {var_name} not found")
    return var_value
