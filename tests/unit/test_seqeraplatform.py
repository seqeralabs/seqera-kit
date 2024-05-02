import unittest
from unittest.mock import MagicMock, patch
from seqerakit import seqeraplatform
import json
import subprocess
import os


class TestSeqeraPlatform(unittest.TestCase):
    def setUp(self):
        self.sp = seqeraplatform.SeqeraPlatform(json=True)

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
        mock_subprocess.return_value = MagicMock(returncode=0)
        mock_subprocess.return_value.communicate.return_value = (
            json.dumps(mock_pipelines_json).encode(),
            b"",
        )

        # Dynamically get the pipelines command
        command = getattr(self.sp, "pipelines")

        # Run the command with arguments
        result = command("view", "--name", "pipeline_name")

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

            command = getattr(self.sp, "pipelines")

            # Check that the error is raised
            with self.assertRaises(seqeraplatform.ResourceExistsError):
                command("arg1", "arg2")

    def test_resource_exists_error_alt_error(self):
        with patch("subprocess.Popen") as mock_subprocess:
            # Simulate a 'resource already exists' error
            mock_subprocess.return_value.communicate.return_value = (
                b"ERROR: Already a participant",
                b"",
            )

            command = getattr(self.sp, "pipelines")

            # Check that the error is raised
            with self.assertRaises(seqeraplatform.ResourceExistsError):
                command("arg1", "arg2")

    def test_resource_creation_error(self):
        with patch("subprocess.Popen") as mock_subprocess:
            # Simulate a 'resource creation failed' error
            mock_subprocess.return_value.communicate.return_value = (
                b"ERROR: Resource creation failed",
                b"",
            )

            command = getattr(self.sp, "pipelines")

            # Check that the error is raised
            with self.assertRaises(seqeraplatform.ResourceCreationError):
                command("import", "my_pipeline.json", "--name", "pipeline_name")

    def test_json_parsing(self):
        with patch("subprocess.Popen") as mock_subprocess:
            # Mock the stdout of the Popen process to return JSON
            mock_subprocess.return_value = MagicMock(returncode=0)
            mock_subprocess.return_value.communicate.return_value = (
                b'{"key": "value"}',
                b"",
            )

            command = getattr(self.sp, "pipelines")

            # Check that the JSON is parsed correctly
            self.assertEqual(command("arg1", "arg2"), {"key": "value"})


class TestSeqeraPlatformCLIArgs(unittest.TestCase):
    def setUp(self):
        self.cli_args = ["--url", "http://tower-api.com", "--insecure"]
        self.sp = seqeraplatform.SeqeraPlatform(cli_args=self.cli_args)

    @patch("subprocess.Popen")
    def test_cli_args_inclusion(self, mock_subprocess):
        # Mock the stdout of the Popen process
        mock_subprocess.return_value = MagicMock(returncode=0)
        mock_subprocess.return_value.communicate.return_value = (
            json.dumps({"key": "value"}).encode(),
            b"",
        )

        # Call a method
        self.sp.pipelines("view", "--name", "pipeline_name")

        # Extract the command used to call Popen
        called_command = mock_subprocess.call_args[0][0]

        # Check if the cli_args are present in the called command
        for arg in self.cli_args:
            self.assertIn(arg, called_command)

    @patch("subprocess.Popen")
    def test_cli_args_inclusion_ssl_certs(self, mock_subprocess):
        # Add path to custom certs store to cli_args
        self.cli_args.append("-Djavax.net.ssl.trustStore=/absolute/path/to/cacerts")

        # Initialize SeqeraPlatform with cli_args
        seqeraplatform.SeqeraPlatform(cli_args=self.cli_args)

        # Mock the stdout of the Popen process
        mock_subprocess.return_value = MagicMock(returncode=0)
        mock_subprocess.return_value.communicate.return_value = (
            json.dumps({"key": "value"}).encode(),
            b"",
        )

        # Call a method
        self.sp.pipelines("view", "--name", "pipeline_name")

        # Extract the command used to call Popen
        called_command = mock_subprocess.call_args[0][0]

        # Check if the cli_args are present in the called command
        self.assertIn(
            "-Djavax.net.ssl.trustStore=/absolute/path/to/cacerts", called_command
        )

    def test_cli_args_exclusion_of_verbose(self):  # TODO: remove this test once fixed
        # Add --verbose to cli_args
        verbose_args = ["--verbose"]

        # Check if ValueError is raised when initializing SeqeraPlatform with --verbose
        with self.assertRaises(ValueError) as context:
            seqeraplatform.SeqeraPlatform(cli_args=verbose_args)

        # Check the error message
        self.assertEqual(
            str(context.exception),
            "--verbose is not supported as a CLI argument to seqerakit.",
        )


class TestKitOptions(unittest.TestCase):
    def setUp(self):
        self.dryrun_tw = seqeraplatform.SeqeraPlatform(dryrun=True)

    @patch("subprocess.Popen")
    def test_dryrun_call(self, mock_subprocess):
        # Run a method with dryrun=True
        self.dryrun_tw.pipelines("view", "--name", "pipeline_name")

        # Assert that subprocess.Popen is not called
        mock_subprocess.assert_not_called()


class TestCheckEnvVars(unittest.TestCase):
    def setUp(self):
        self.sp = seqeraplatform.SeqeraPlatform()
        self.original_environ = dict(os.environ)

    def tearDown(self):
        # Restore the original environment after each test
        os.environ.clear()
        os.environ.update(self.original_environ)

    def test_with_set_env_vars(self):
        # Set environment variables for the test
        os.environ["VAR1"] = "value1"

        command = ["tw", "pipelines", "list", "-w", "$VAR1"]
        expected = "tw pipelines list -w $VAR1"
        result = self.sp._check_env_vars(command)
        self.assertEqual(result, expected)

    def test_without_env_vars(self):
        # Test case where there are no environment variables in the command
        command = ["tw", "info"]
        expected = "tw info"  # shlex.quote() will not alter these
        result = self.sp._check_env_vars(command)
        self.assertEqual(result, expected)

    def test_error_raised_for_unset_env_vars(self):
        # Unset environment variables for this test
        unset_var = "{UNSET_VAR}"
        if "UNSET_VAR" in os.environ:
            del os.environ["UNSET_VAR"]

        command = ["tw", "pipelines", "list", "-w", "${UNSET_VAR}"]

        # Assert that EnvironmentError is raised
        with self.assertRaises(EnvironmentError) as context:
            self.sp._check_env_vars(command)
        self.assertEqual(
            str(context.exception), f" Environment variable ${unset_var} not found!"
        )


if __name__ == "__main__":
    unittest.main()
