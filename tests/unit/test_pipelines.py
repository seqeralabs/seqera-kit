import pytest
from unittest.mock import patch, MagicMock, call
from tw_py import Pipelines


def test_get_list_unit():
    """
    Unit test for the get_list method of Tower base class.
    This test checks that the get_list method constructs the
    proper commands to be passed to the _tw_run method of the base class.
    """
    # Unit test to check that the get_list method constructs proper commands
    # to be passed to `_tw_run` method of the base class
    with patch.object(Pipelines, "_tw_run", return_value=None) as mock_tw_run:
        p = Pipelines("workspace_name")
        p.get_list()

    # Check that _tw_run was called with the correct arguments
    mock_tw_run.assert_called_once_with(
        ["pipelines", "list", "--workspace", "workspace_name"]
    )


# Integration test to check that get_list() works with subprocess
# Create mock object for subprocess.Popen
@patch("subprocess.Popen")
def test_get_list_subprocess(mock_popen):
    """
    Integration test for the get_list method for Pipelines() class.
    This test checks that the get_list method correctly interacts
    with the subprocess.Popen method to run tw subcommands.
    """
    # Mock subprocess.Popen with monkeypatch
    # Return value is a tuple of (stdout, stderr), we don't need stderr
    mock_popen.return_value.communicate.return_value = (b"My_pipeline_name\n", b"")

    # Instantiate Pipelines class with a test workspace name
    pipelines_instance = Pipelines("workspace_name")

    # Call the get_list method
    result = pipelines_instance.get_list()

    # Assert that the result is as expected
    assert result == "My_pipeline_name"

    # Check that subprocess.Popen was called with the expected arguments
    mock_popen.assert_called_once_with(
        "tw pipelines list --workspace workspace_name", stdout=-1, shell=True
    )


@patch("subprocess.Popen")
def test_get_list_subprocess_json(mock_popen):
    """
    Integration test for the get_list method with json = true for Pipelines() class.
    This test checks that the get_list method correctly interacts
    with the subprocess.Popen method to run tw subcommands.
    """
    # Mock subprocess.Popen with monkeypatch
    # Return value is a tuple of (stdout, stderr), we don't need stderr
    mock_popen.return_value.communicate.return_value = (b"My_pipeline_name\n", b"")

    # Instantiate Pipelines class with a test workspace name
    pipelines_instance = Pipelines("workspace_name")

    # Call the get_list method
    result = pipelines_instance.get_list(to_json=True)

    # Assert that the result is as expected
    assert result == "My_pipeline_name"

    # Check that subprocess.Popen was called with the expected arguments
    mock_popen.assert_called_once_with(
        "tw -o json pipelines list --workspace workspace_name", stdout=-1, shell=True
    )


def test_view_method_unit():
    """
    Unit test for the view method of Tower base class.
    This test checks that the view method constructs the
    proper commands to be passed to the _tw_run method of the base class.
    """
    with patch.object(Pipelines, "_tw_run", return_value=None) as mock_tw_run:
        p = Pipelines("workspace_name")
        p.view("pipeline_name")

    mock_tw_run.assert_called_once_with(
        ["pipelines", "view", "--name", "pipeline_name"]
    )


@patch("subprocess.Popen")
def test_view_method_subprocess(mock_popen):
    """
    Integration test for the view method for Pipelines() class.
    This test checks that the view method correctly interacts
    with the subprocess.Popen method to run tw subcommands.
    """
    mock_popen.return_value.communicate.return_value = (b"hello_world\n", b"")

    # Instantiate Pipelines class with a test workspace name
    pipelines_instance = Pipelines("workspace_name")

    # Call the view method on a pipeline name
    result = pipelines_instance.view("hello_world")

    assert result == "hello_world"

    mock_popen.assert_called_once_with(
        "tw pipelines view --name hello_world", stdout=-1, shell=True
    )


def test_add_method_unit():
    """
    Unit test for the add method of Pipelines class, overriding the base class.
    This test checks that the add method constructs the
    proper commands to be passed to the _tw_run method of the base class.
    """
    with patch.object(Pipelines, "_tw_run", return_value=None) as mock_tw_run:
        p = Pipelines("workspace_name")
        p.add("my_git_repo", "pipeline_name")

    mock_tw_run.assert_called_once_with(
        [
            "pipelines",
            "add",
            "my_git_repo",
            "--name",
            "pipeline_name",
            "--workspace",
            "workspace_name",
        ]
    )


def test_add_method_unit_with_config():
    """
    Unit test for the add method of Pipelines class, overriding the base class.
    This test checks that the add method constructs the proper commands and keyword args to be passed to the
    _tw_run method of the base class.
    """
    with patch.object(Pipelines, "_tw_run", return_value=None) as mock_tw_run:
        p = Pipelines("workspace_name")
        p.add("my_git_repo", "pipeline_name", config="config_path")

    mock_tw_run.assert_called_once_with(
        [
            "pipelines",
            "add",
            "my_git_repo",
            "--name",
            "pipeline_name",
            "--workspace",
            "workspace_name",
            "--params-file",
            "config_path",
        ]
    )


def test_delete_unit():
    """
    Unit test for the delete method of Tower base class.
    This test checks that the delete method constructs the
    proper commands to be passed to the _tw_run method of the base class.
    """
    with patch.object(Pipelines, "_tw_run", return_value=None) as mock_tw_run:
        p = Pipelines("workspace_name")
        p.delete("pipeline_name")

    mock_tw_run.assert_called_once_with(
        ["pipelines", "delete", "--name", "pipeline_name"]
    )


def test_import_pipeline_unit():
    """
    Unit test for the import_ce method of the Pipelines class.
    This test checks that the delete method constructs the
    proper commands to be passed to the _tw_run method of the base class.
    """
    with patch.object(Pipelines, "_tw_run", return_value=None) as mock_tw_run:
        p = Pipelines("workspace_name")
        p.import_pipeline("hello_world", config="config_path")

    mock_tw_run.assert_called_once_with(
        [
            "pipelines",
            "import",
            "--name",
            "hello_world",
            "config_path",
            "--workspace",
            "workspace_name",
        ]
    )


@patch("subprocess.Popen")
def test_import_pipeline_subprocess(mock_popen):
    """
    Integration test for the import_pipeline method for Pipelines() class.
    """
    mock_popen.return_value.communicate.return_value = (
        b"Pipeline successfully imported\n",
        b"",
    )

    # Instantiate Pipelines class with a test workspace name
    pipelines_instance = Pipelines("workspace_name")

    # Call the import_pipeline method on a pipeline name and provided config
    result = pipelines_instance.import_pipeline("hello_world", "hello_world.json")

    assert result == None

    mock_popen.assert_called_once_with(
        "tw pipelines import --name hello_world hello_world.json --workspace workspace_name",
        stdout=-1,
        shell=True,
    )


# TODO: fix this test
# def test_export_pipeline_unit():
#     """
#     Unit test for the export_pipeline method of the Pipelines class.
#     """
#     with patch.object(Pipelines, "_tw_run", return_value=None) as mock_tw_run:
#         p = Pipelines("workspace_name")
#         p.export_pipeline("hello_world")

#     mock_path = MagicMock()
#     mock_path.name = "workspace_name/hello_world.json"

#     mock_tw_run.assert_called_once_with(
#         ["pipelines", "export", "--workspace", "workspace_name", "--name", "hello_world", mock_path]
#     )


# TODO: def test_export_pipeline_subprocess():
# TODO: def test_launch_pipeline_unit():
# TODO: def test_launch_pipeline_subprocess():
