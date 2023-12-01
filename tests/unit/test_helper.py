from unittest.mock import mock_open
from seqerakit import helper
import yaml
import pytest


# Fixture to mock a YAML file
@pytest.fixture
def mock_yaml_file(mocker):
    def _mock_yaml_file(test_data, file_name="mock_file.yaml"):
        # Convert test data to YAML format
        yaml_content = yaml.dump(test_data, default_flow_style=False)
        mock_file = mock_open(read_data=yaml_content)
        mocker.patch("builtins.open", mock_file)

        return file_name

    return _mock_yaml_file


def test_create_mock_organization_yaml(mock_yaml_file):
    test_data = {
        "organizations": [
            {
                "name": "test_organization1",
                "full-name": "My test organization 1",
                "description": "My test organization 1",
                "location": "Global",
                "url": "https://example.com",
                "overwrite": True,
            }
        ]
    }
    expected_block_output = [
        {
            "cmd_args": [
                "--description",
                "My test organization 1",
                "--full-name",
                "My test organization 1",
                "--location",
                "Global",
                "--name",
                "test_organization1",
                "--url",
                "https://example.com",
            ],
            "overwrite": True,
        }
    ]

    file_path = mock_yaml_file(test_data)
    result = helper.parse_all_yaml([file_path])

    assert "organizations" in result
    assert result["organizations"] == expected_block_output


def test_create_mock_workspace_yaml(mock_yaml_file):
    test_data = {
        "workspaces": [
            {
                "name": "test_workspace1",
                "full-name": "My test workspace 1",
                "organization": "my_organization",
                "description": "My test workspace 1",
                "visibility": "PRIVATE",
                "overwrite": True,
            }
        ]
    }
    expected_block_output = [
        {
            "cmd_args": [
                "--description",
                "My test workspace 1",
                "--full-name",
                "My test workspace 1",
                "--name",
                "test_workspace1",
                "--organization",
                "my_organization",
                "--visibility",
                "PRIVATE",
            ],
            "overwrite": True,
        }
    ]

    file_path = mock_yaml_file(test_data)
    result = helper.parse_all_yaml([file_path])

    assert "workspaces" in result
    assert result["workspaces"] == expected_block_output


def test_create_mock_dataset_yaml(mock_yaml_file):
    test_data = {
        "datasets": [
            {
                "name": "test_dataset1",
                "description": "My test dataset 1",
                "workspace": "my_organization/my_workspace",
                "header": True,
                "file-path": "./examples/yaml/datasets/samples.csv",
                "overwrite": True,
            }
        ]
    }
    expected_block_output = [
        {
            "cmd_args": [
                "./examples/yaml/datasets/samples.csv",
                "--name",
                "test_dataset1",
                "--workspace",
                "my_organization/my_workspace",
                "--description",
                "My test dataset 1",
                "--header",
            ],
            "overwrite": True,
        }
    ]

    file_path = mock_yaml_file(test_data)
    result = helper.parse_all_yaml([file_path])

    assert "datasets" in result
    assert result["datasets"] == expected_block_output


def test_create_mock_computeevs_yaml(mock_yaml_file):
    test_data = {
        "compute-envs": [
            {
                "name": "test_computeenv",
                "workspace": "my_organization/my_workspace",
                "credentials": "my_credentials",
                "file-path": "./examples/yaml/computeenvs/computeenvs.yaml",
                "wait": "AVAILABLE",
                "fusion-v2": True,
                "fargate": False,
                "overwrite": True,
            }
        ],
    }

    expected_block_output = [
        {
            "cmd_args": [
                "--credentials",
                "my_credentials",
                "./examples/yaml/computeenvs/computeenvs.yaml",
                "--fusion-v2",
                "--name",
                "test_computeenv",
                "--wait",
                "AVAILABLE",
                "--workspace",
                "my_organization/my_workspace",
            ],
            "overwrite": True,
        }
    ]

    file_path = mock_yaml_file(test_data)
    result = helper.parse_all_yaml([file_path])

    assert "compute-envs" in result
    assert result["compute-envs"] == expected_block_output


def test_create_mock_pipeline_add_yaml(mock_yaml_file):
    test_data = {
        "pipelines": [
            {
                "name": "test_pipeline1",
                "url": "https://github.com/nf-core/test_pipeline1",
                "workspace": "my_organization/my_workspace",
                "description": "My test pipeline 1",
                "compute-env": "my_computeenv",
                "work-dir": "s3://work",
                "profile": "test",
                "params-file": "./examples/yaml/pipelines/test_pipeline1/params.yaml",
                "config": "./examples/yaml/pipelines/test_pipeline1/config.txt",
                "pre-run": "./examples/yaml/pipelines/test_pipeline1/pre_run.sh",
                "revision": "master",
                "overwrite": True,
                "stub-run": True,
            }
        ]
    }

    # params file cmds parsed separately
    expected_block_output = [
        {
            "cmd_args": [
                "--compute-env",
                "my_computeenv",
                "--config",
                "./examples/yaml/pipelines/test_pipeline1/config.txt",
                "--description",
                "My test pipeline 1",
                "--name",
                "test_pipeline1",
                "--pre-run",
                "./examples/yaml/pipelines/test_pipeline1/pre_run.sh",
                "--profile",
                "test",
                "--revision",
                "master",
                "--stub-run",
                "--work-dir",
                "s3://work",
                "--workspace",
                "my_organization/my_workspace",
                "https://github.com/nf-core/test_pipeline1",
                "--params-file",
                "./examples/yaml/pipelines/test_pipeline1/params.yaml",
            ],
            "overwrite": True,
        }
    ]

    file_path = mock_yaml_file(test_data)
    result = helper.parse_all_yaml([file_path])

    assert "pipelines" in result
    assert result["pipelines"] == expected_block_output
