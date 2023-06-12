import pytest
import json
from tw_py import Pipelines

# Runs actual integration tests with subprocess and real workspaces
# to test the Pipelines() class and validate that the methods work on CLI


def test_get_list_json():
    """
    Integration test for the get_list method with json = true for Pipelines() class.
    This test runs the method on an actual workspace and checks for a real
    JSON response.
    """
    # Instantiate Pipelines class with a test workspace name
    # TODO: We might want to set this to scidev/showcase
    pipelines_instance = Pipelines("scidev/testing")

    # Run get_list() method with json = true
    result = pipelines_instance.get_list(to_json=True)

    # Check if result is a valid JSON
    try:
        json.loads(result)
    except json.JSONDecodeError:
        pytest.fail("get_list() did not return a valid JSON")
