from unittest.mock import patch, mock_open
from seqerakit import helper
import yaml
import pytest
from io import StringIO


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
    print(f"debug - file_path: {file_path}")
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


def test_create_mock_computeevs_source_yaml(mock_yaml_file):
    test_data = {
        "compute-envs": [
            {
                "name": "test_computeenv",
                "workspace": "my_organization/my_workspace",
                "credentials": "my_credentials",
                "file-path": "./computeenvs/computeenv.json",
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
                "./computeenvs/computeenv.json",
                "--credentials",
                "my_credentials",
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


def test_create_mock_computeevs_cli_yaml(mock_yaml_file):
    test_data = {
        "compute-envs": [
            {
                "name": "test_computeenv",
                "workspace": "my_organization/my_workspace",
                "credentials": "my_credentials",
                "type": "aws-batch",
                "config-mode": "forge",
                "wait": "AVAILABLE",
            }
        ],
    }

    expected_block_output = [
        {
            "cmd_args": [
                "aws-batch",
                "forge",
                "--credentials",
                "my_credentials",
                "--name",
                "test_computeenv",
                "--wait",
                "AVAILABLE",
                "--workspace",
                "my_organization/my_workspace",
            ],
            "overwrite": False,
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


def test_create_mock_teams_yaml(mock_yaml_file):
    test_data = {
        "teams": [
            {
                "name": "test_team1",
                "organization": "my_organization",
                "description": "My test team 1",
                "members": ["user1@org.io"],
                "overwrite": True,
            },
        ]
    }
    expected_block_output = [
        {
            "cmd_args": (
                [
                    "--description",
                    "My test team 1",
                    "--name",
                    "test_team1",
                    "--organization",
                    "my_organization",
                ],
                [
                    [
                        "--team",
                        "test_team1",
                        "--organization",
                        "my_organization",
                        "add",
                        "--member",
                        "user1@org.io",
                    ]
                ],
            ),
            "overwrite": True,
        }
    ]

    file_path = mock_yaml_file(test_data)
    result = helper.parse_all_yaml([file_path])

    assert "teams" in result
    assert result["teams"] == expected_block_output


def test_create_mock_members_yaml(mock_yaml_file):
    test_data = {"members": [{"user": "bob@myorg.io", "organization": "myorg"}]}
    expected_block_output = [
        {
            "cmd_args": [
                "--organization",
                "myorg",
                "--user",
                "bob@myorg.io",
            ],
            "overwrite": False,
        }
    ]
    file_path = mock_yaml_file(test_data)
    result = helper.parse_all_yaml([file_path])

    assert "members" in result
    assert result["members"] == expected_block_output


def test_empty_yaml_file(mock_yaml_file):
    test_data = {}
    file_path = mock_yaml_file(test_data)

    with pytest.raises(ValueError) as e:
        helper.parse_all_yaml([file_path])
    assert f"The file '{file_path}' is empty or does not contain valid data." in str(
        e.value
    )


def test_empty_stdin_file():
    # Prepare the mock to simulate empty stdin
    with patch("sys.stdin", StringIO("")):
        # Use '-' to indicate that stdin should be read
        with pytest.raises(ValueError) as e:
            helper.parse_all_yaml(["-"])
        assert (
            "The input from stdin is empty or does not contain valid YAML data."
            in str(e.value)
        )


def test_stdin_yaml_file():
    # Prepare the mock to simulate stdin
    yaml_data = """
compute-envs:
  - name: test_computeenv
    config-mode: forge
    workspace: my_organization/my_workspace
    credentials: my_credentials
    type: aws-batch
    wait: AVAILABLE
        """
    with patch("sys.stdin", StringIO(yaml_data)):
        result = helper.parse_all_yaml(["-"])

    expected_block_output = [
        {
            "cmd_args": [
                "aws-batch",
                "forge",
                "--name",
                "test_computeenv",
                "--workspace",
                "my_organization/my_workspace",
                "--credentials",
                "my_credentials",
                "--wait",
                "AVAILABLE",
            ],
            "overwrite": False,
        }
    ]
    assert "compute-envs" in result
    assert result["compute-envs"] == expected_block_output


def test_error_type_yaml_file(mock_yaml_file):
    test_data = {
        "compute-envs": [
            {
                "name": "test_computeenv",
                "workspace": "my_organization/my_workspace",
                "credentials": "my_credentials",
                "wait": "AVAILABLE",
            }
        ],
    }
    file_path = mock_yaml_file(test_data)

    with pytest.raises(ValueError) as e:
        helper.parse_all_yaml([file_path])
    assert (
        "Please specify at least 'type' or 'file-path' for creating the resource."
        in str(e.value)
    )


def test_error_duplicate_name_yaml_file(mock_yaml_file):
    test_data = {
        "compute-envs": [
            {
                "name": "test_computeenv",
                "workspace": "my_organization/my_workspace",
                "credentials": "my_credentials",
                "type": "aws-batch",
                "config-mode": "forge",
                "wait": "AVAILABLE",
            },
            {
                "name": "test_computeenv",
                "workspace": "my_organization/my_workspace",
                "credentials": "my_credentials",
                "type": "aws-batch",
                "config-mode": "forge",
                "wait": "AVAILABLE",
            },
        ],
    }
    file_path = mock_yaml_file(test_data)

    with pytest.raises(ValueError) as e:
        helper.parse_all_yaml([file_path])
    assert (
        "Duplicate name key specified in config file for "
        "compute-envs: test_computeenv. Please specify "
        "a unique value." in str(e.value)
    )


def test_targets_specified():
    #  mock YAML data
    yaml_data = """
organizations:
  - name: org1
    description: Organization 1
workspaces:
  - name: workspace1
    organization: org1
    description: Workspace 1
pipelines:
  - name: pipeline1
    workspace: workspace1
    description: Pipeline 1
"""
    with patch("builtins.open", lambda f, _: StringIO(yaml_data)):
        result = helper.parse_all_yaml(
            ["dummy_path.yaml"], targets="organizations,workspaces"
        )

    expected_organizations_output = [
        {
            "cmd_args": ["--name", "org1", "--description", "Organization 1"],
            "overwrite": False,
        }
    ]
    expected_workspaces_output = [
        {
            "cmd_args": [
                "--name",
                "workspace1",
                "--organization",
                "org1",
                "--description",
                "Workspace 1",
            ],
            "overwrite": False,
        }
    ]
    # Check that only 'organizations' and 'workspaces' are in the result
    assert "organizations" in result
    assert result["organizations"] == expected_organizations_output
    assert "workspaces" in result
    assert result["workspaces"] == expected_workspaces_output
    assert "pipelines" not in result


def test_no_targets_specified():
    yaml_data = """
organizations:
  - name: org1
    description: Organization 1
workspaces:
  - name: workspace1
    organization: org1
    description: Workspace 1
pipelines:
  - name: pipeline1
    workspace: workspace1
    description: Pipeline 1
"""
    with patch("builtins.open", lambda f, _: StringIO(yaml_data)):
        result = helper.parse_all_yaml(["dummy_path.yaml"])

    # Check that all blocks are in the result
    assert "organizations" in result
    assert "workspaces" in result
    assert "pipelines" in result
