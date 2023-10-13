import unittest
from unittest.mock import mock_open, patch
from seqerakit import helper

mocked_yaml = """
datasets:
  - name: 'test_dataset1'
    description: 'My test dataset 1'
    header: true
    workspace: 'my_organization/my_workspace'
    file-path: './examples/yaml/datasets/samples.csv'
    overwrite: True
"""

mocked_file = mock_open(read_data=mocked_yaml)


class TestYamlParserFunctions(unittest.TestCase):
    @patch("builtins.open", mocked_file)
    def test_parse_datasets_yaml(self):
        result = helper.parse_all_yaml(["test_path.yaml"])
        expected_block_output = [
            {
                "cmd_args": [
                    "--header",
                    "./examples/yaml/datasets/samples.csv",
                    "--name",
                    "test_dataset1",
                    "--workspace",
                    "my_organization/my_workspace",
                    "--description",
                    "My test dataset 1",
                ],
                "overwrite": True,
            }
        ]

        self.assertIn("datasets", result)
        self.assertEqual(result["datasets"], expected_block_output)


# TODO: add more tests for other functions in helper.py
