import pytest
from tw_py import Tower


def test_tower_init_with_env_var(monkeypatch):
    # Use monkeypatch to set the environment variable for the duration of the test
    monkeypatch.setenv("TW_WORKSPACE_NAME", "test_value")

    # Call the Tower constructor with no arguments
    tower_instance = Tower()

    # Assert that the workspace name is set correctly
    assert tower_instance.workspace == "test_value"


def test_tower_init_with_arg():
    # Call the Tower constructor with an argument for workspace name
    tower_instance = Tower("arg_value")

    # Assert that the workspace name is set correctly
    assert tower_instance.workspace == "arg_value"


def test_tower_init_no_env_var_no_arg():
    # Call the Tower constructor with no environment variable set and no argument
    with pytest.raises(ValueError) as e_info:
        tower_instance = Tower()

    # Check that the exception message is as expected
    assert (
        str(e_info.value)
        == "Neither an environment variable for workspace name nor an argument was provided."
    )
