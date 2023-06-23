import json
import tempfile
import yaml
from urllib.parse import urlparse


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
    created successfully in Tower by looking for the name and value.
    """
    data = json.loads(json_data)
    if find_key_value_in_dict(data, namekey, namevalue, return_key=None):
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


def create_temp_yaml(params_dict):
    """
    Create a generic temporary yaml file given a dictionary
    """

    class quoted_str(str):
        pass

    def quoted_str_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="'")

    yaml.add_representer(quoted_str, quoted_str_representer)
    for k, v in params_dict.items():
        if k == "outdir" and isinstance(v, str):
            params_dict[k] = quoted_str(v)

    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".yaml"
    ) as temp_file:
        yaml.dump(params_dict, temp_file)
        return temp_file.name
