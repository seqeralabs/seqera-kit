import unittest
from unittest.mock import patch
from twkit import tower
import json
import subprocess


class TestTower(unittest.TestCase):
    def setUp(self):
        self.tw = tower.Tower()

    @patch("subprocess.Popen")
    def test_run_with_jsonout_command(self, mock_subprocess):
        mock_pipelines_json = {
            "id": "5lWcpupLHnHkq9fM5JYaOn",
            "computeEnvId": "403VpC7AetAmj42MnMOAwJ",
            "pipeline": "https://github.com/nextflow-io/hello",
            "workDir": "s3://myworkdir/test",
            "revision": "",
            "configText": "",
            "paramsText": "",
            "resume": "false",
            "pullLatest": "false",
            "stubRun": "false",
            "dateCreated": "2023-02-15T13:14:30Z",
        }
        # Mock the stdout of the Popen process
        mock_subprocess.return_value.communicate.return_value = (
            json.dumps(mock_pipelines_json).encode(),
            b"",
        )

        # Dynamically get the pipelines command
        command = getattr(self.tw, "pipelines")

        # Run the command with arguments
        result = command("view", "--name", "pipeline_name", to_json=True)

        # Check that Popen was called with the right arguments
        mock_subprocess.assert_called_once_with(
            "tw -o json pipelines view --name pipeline_name",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
        )

        # Check that the output was decoded correctly
        self.assertEqual(result, mock_pipelines_json)

    def test_resource_exists_error(self):
        with patch("subprocess.Popen") as mock_subprocess:
            # Simulate a 'resource already exists' error
            mock_subprocess.return_value.communicate.return_value = (
                b"ERROR: Resource already exists",
                b"",
            )

            command = getattr(self.tw, "pipelines")

            # Check that the error is raised
            with self.assertRaises(tower.ResourceExistsError):
                command("arg1", "arg2")

    def test_resource_exists_error_alt_error(self):
        with patch("subprocess.Popen") as mock_subprocess:
            # Simulate a 'resource already exists' error
            mock_subprocess.return_value.communicate.return_value = (
                b"ERROR: Already a participant",
                b"",
            )

            command = getattr(self.tw, "pipelines")

            # Check that the error is raised
            with self.assertRaises(tower.ResourceExistsError):
                command("arg1", "arg2")

    def test_resource_creation_error(self):
        with patch("subprocess.Popen") as mock_subprocess:
            # Simulate a 'resource creation failed' error
            mock_subprocess.return_value.communicate.return_value = (
                b"ERROR: Resource creation failed",
                b"",
            )

            command = getattr(self.tw, "pipelines")

            # Check that the error is raised
            with self.assertRaises(tower.ResourceCreationError):
                command("import", "my_pipeline.json", "--name", "pipeline_name")

    def test_json_parsing(self):
        with patch("subprocess.Popen") as mock_subprocess:
            # Mock the stdout of the Popen process to return JSON
            mock_subprocess.return_value.communicate.return_value = (
                b'{"key": "value"}',
                b"",
            )

            command = getattr(self.tw, "pipelines")

            # Check that the JSON is parsed correctly
            self.assertEqual(command("arg1", "arg2", to_json=True), {"key": "value"})


class TestTowerCLIArgs(unittest.TestCase):
    def setUp(self):
        self.cli_args = ["--url", "http://tower-api.com", "--insecure"]
        self.tw = tower.Tower(cli_args=self.cli_args)

    @patch("subprocess.Popen")
    def test_cli_args_inclusion(self, mock_subprocess):
        # Mock the stdout of the Popen process
        mock_subprocess.return_value.communicate.return_value = (
            json.dumps({"key": "value"}).encode(),
            b"",
        )

        # Call a method
        self.tw.pipelines("view", "--name", "pipeline_name", to_json=True)

        # Extract the command used to call Popen
        called_command = mock_subprocess.call_args[0][0]

        # Check if the cli_args are present in the called command
        for arg in self.cli_args:
            self.assertIn(arg, called_command)

    @patch("subprocess.Popen")
    def test_cli_args_inclusion_ssl_certs(self, mock_subprocess):
        # Add path to custom certs store to cli_args
        self.cli_args.append("-Djavax.net.ssl.trustStore=/absolute/path/to/cacerts")

        # Initialize Tower with cli_args
        tower.Tower(cli_args=self.cli_args)

        # Mock the stdout of the Popen process
        mock_subprocess.return_value.communicate.return_value = (
            json.dumps({"key": "value"}).encode(),
            b"",
        )

        # Call a method
        self.tw.pipelines("view", "--name", "pipeline_name", to_json=True)

        # Extract the command used to call Popen
        called_command = mock_subprocess.call_args[0][0]

        # Check if the cli_args are present in the called command
        self.assertIn(
            "-Djavax.net.ssl.trustStore=/absolute/path/to/cacerts", called_command
        )

    def test_cli_args_exclusion_of_verbose(self):  # TODO: remove this test once fixed
        # Add --verbose to cli_args
        verbose_args = ["--verbose"]

        # Check if ValueError is raised when initializing Tower with --verbose
        with self.assertRaises(ValueError) as context:
            tower.Tower(cli_args=verbose_args)

        # Check the error message
        self.assertEqual(
            str(context.exception),
            "--verbose is not supported as a CLI argument to twkit.",
        )


class TestKitOptions(unittest.TestCase):
    def setUp(self):
        self.dryrun_tw = tower.Tower(dryrun=True)

    @patch("subprocess.Popen")
    def test_dryrun_call(self, mock_subprocess):
        # Run a method with dryrun=True
        self.dryrun_tw.pipelines("view", "--name", "pipeline_name", to_json=True)

        # Assert that subprocess.Popen is not called
        mock_subprocess.assert_not_called()


if __name__ == "__main__":
    unittest.main()
