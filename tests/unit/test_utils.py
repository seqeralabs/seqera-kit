from tw_pywrap import utils
import unittest
from unittest.mock import patch
import tempfile
import pytest
import yaml
import os


class TestFindKeyValueInDict(unittest.TestCase):
    """
    Test the find_key_value_in_dict() function.
    """

    def test_key_value_exists(self):
        data = {"key1": "value1", "key2": "value2"}
        self.assertTrue(utils.find_key_value_in_dict(data, "key1", "value1", None))

    def test_returns_correct_value(self):
        data = {"key1": "value1", "key2": "value2"}
        self.assertEqual(
            utils.find_key_value_in_dict(data, "key1", "value1", "key2"), "value2"
        )

    def test_traverse_nested_dict(self):
        data = {"key1": "value1", "nested": {"key2": "value2"}}
        self.assertTrue(utils.find_key_value_in_dict(data, "key2", "value2", None))

    def test_traverse_list_of_dict(self):
        data = [{"key1": "value1"}, {"key2": "value2"}]
        self.assertTrue(utils.find_key_value_in_dict(data, "key2", "value2", None))

    def test_returns_none_if_not_exist(self):
        data = {"key1": "value1", "key2": "value2"}
        self.assertIsNone(utils.find_key_value_in_dict(data, "key3", "value3", None))

    def test_returns_key_in_nested_dict(self):
        data = {
            "outer_key": {"inner_key1": "target_value", "return_key": "return_value"}
        }
        self.assertEqual(
            utils.find_key_value_in_dict(
                data, "inner_key1", "target_value", "return_key"
            ),
            "return_value",
        )

    @patch("tw_pywrap.utils.find_key_value_in_dict")
    def test_check_if_exists(self, mock_find_key_value_in_dict):
        # Arrange required mocks for jsondata, namekey, and namevalue
        mock_find_key_value_in_dict.return_value = False
        json_data = '{"key": "value"}'
        namekey = "key"
        namevalue = "value"

        # Act
        result = utils.check_if_exists(json_data, namekey, namevalue)

        # Assert
        self.assertFalse(result)
        mock_find_key_value_in_dict.assert_called_once_with(
            {"key": "value"}, namekey, namevalue, return_key=None
        )


# test if validation of yaml file works
def test_is_valid_yaml_with_valid_yaml():
    # Set up valid yaml file
    valid_yaml = """
    key: value
    """
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        f.write(valid_yaml)

    result = utils.is_valid_yaml(f.name)
    assert result


def test_is_valid_yaml_throws_error_with_invalid_yaml():
    # Set up invalid yaml file
    invalid_yaml = """
    {
    """
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        f.write(invalid_yaml)

    # Check if exception is thrown
    with pytest.raises(yaml.YAMLError):
        utils.is_valid_yaml(f.name)


# test getting pipeline repo
def test_get_pipeline_repo_with_nf_core():
    repo_name = "nf-core/test"
    expected_result = "https://github.com/nf-core/test"
    assert utils.get_pipeline_repo(repo_name) == expected_result


def test_get_pipeline_repo_without_nf_core():
    repo_name = "test"
    expected_result = "test"
    assert utils.get_pipeline_repo(repo_name) == expected_result


def test_get_pipeline_repo_with_nf_core_case_insensitive():
    repo_name = "NF-CORE/test"
    expected_result = "https://github.com/NF-CORE/test"
    assert utils.get_pipeline_repo(repo_name) == expected_result


# test for valid url function
def test_is_url_with_valid_url():
    url = "https://www.google.com"
    assert utils.is_url(url) is True


def test_is_url_without_prefix():
    url = "www.google.com"
    assert utils.is_url(url) is False


def test_is_url_without_netloc():
    url = "https://"
    assert utils.is_url(url) is False


def test_is_url_with_non_url_string():
    non_url_string = "not a url"
    assert utils.is_url(non_url_string) is False


# test if temp yaml file is created correctly
def test_create_temp_yaml_with_empty_dict():
    temp_file_name = utils.create_temp_yaml({})
    assert os.path.exists(temp_file_name)
    with open(temp_file_name, "r") as file:
        data = yaml.safe_load(file)
        assert data == {}
    os.remove(temp_file_name)  # cleanup of temp file


def test_create_temp_yaml_with_dict():
    test_dict = {"key1": "value1", "key2": "value2", "outdir": "path/to/directory"}
    temp_file_name = utils.create_temp_yaml(test_dict)
    assert os.path.exists(temp_file_name)
    with open(temp_file_name, "r") as file:
        data = yaml.safe_load(file)
        assert data == test_dict
    os.remove(temp_file_name)  # cleanup of temp file


if __name__ == "__main__":
    unittest.main()
