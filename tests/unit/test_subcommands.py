import unittest
from unittest.mock import patch
from seqerakit import seqeraplatform


class TestSeqeraPlatformSubcommands(unittest.TestCase):
    """
    Unit tests for the subcommands of the SeqeraPlatform base class.
    These tests check that the subcommands of the SeqeraPlatform base class
    construct the proper commands to be passed to the _tw_run method of the base class
    when dynamically called as methods of the SeqeraPlatform class.
    """

    def setUp(self):
        self.sp = seqeraplatform.SeqeraPlatform()
        self.patcher = patch.object(self.sp, "_tw_run")
        self.mock_tw_run = self.patcher.start()
        # Make the mock behave like a function
        self.mock_tw_run.side_effect = lambda *args, **kwargs: "mocked result"

    def subcommand_test(self, subcommand, args, expected_command, **kwargs):
        with self.subTest(subcommand=subcommand):
            command = getattr(self.sp, subcommand)
            result = command(*args, **kwargs)
            self.mock_tw_run.assert_called_once_with(expected_command, **kwargs)
            self.assertEqual(
                result, "mocked result"
            )  # ensure the _tw_run mock returned the correct value
            self.mock_tw_run.reset_mock()  # Reset the mock for the next subcommand

    def test_list_command(self):
        """
        Unit test for the list method of SeqeraPlatform base class.
        This test checks that the list method constructs the
        proper commands to be passed to the _tw_run method of the base class.
        """

        resource_subcommands = [
            "pipelines",
            "compute_envs",
            "actions",
            "datasets",
            "credentials",
            "participants",
            "secrets",
            "runs",
        ]
        org_subcommands = ["teams", "members", "collaborators"]
        plain_subcommands = ["organizations", "workspaces"]

        list_workspace = ["list", "--workspace", "workspace_name"]
        list_organization = ["list", "--organization", "organization_name"]
        list_plain = ["list"]

        for subcommand in resource_subcommands:
            expected_command = (
                ["compute-envs", *list_workspace]
                if subcommand == "compute_envs"
                else [subcommand, *list_workspace]
            )
            self.subcommand_test(subcommand, list_workspace, expected_command)

        for subcommand in org_subcommands:
            self.subcommand_test(
                subcommand, list_organization, [subcommand, *list_organization]
            )

        for subcommand in plain_subcommands:
            self.subcommand_test(subcommand, list_plain, [subcommand, *list_plain])

    def test_add_pipelines_command(self):
        """
        Unit test for the add method of Pipelines class, overriding the base class.
        """
        add_command_with_config = [
            "pipelines",
            "add",
            "my_git_repo",
            "--name",
            "pipeline_name",
            "--workspace",
            "workspace_name",
        ]

        self.subcommand_test(
            "pipelines",
            [
                "add",
                "my_git_repo",
                "--name",
                "pipeline_name",
                "--workspace",
                "workspace_name",
            ],
            add_command_with_config,
            params_file="config_path",
        )

    def test_add_compute_envs_command(self):
        """
        Unit test for the add method of ComputeEnvs class, overriding the base class.
        """
        add_command = [
            "compute-envs",
            "add",
            "executor_name",
            "--name",
            "my_compute_env",
            "--workspace",
            "workspace_name",
            "--workdir",
            "s3://myworkdir",
        ]
        self.subcommand_test(
            "compute_envs",
            [
                "add",
                "executor_name",
                "--name",
                "my_compute_env",
                "--workspace",
                "workspace_name",
                "--workdir",
                "s3://myworkdir",
            ],
            add_command,
        )

    def test_delete_command(self):
        """
        Unit test for the delete method of SeqeraPlatform base class.
        """
        delete_command = [
            "pipelines",
            "delete",
            "pipeline_name",
            "--workspace",
            "workspace_name",
        ]
        self.subcommand_test(
            "pipelines",
            ["delete", "pipeline_name", "--workspace", "workspace_name"],
            delete_command,
        )

    def test_view_command(self):
        """
        Unit test for the view method of SeqeraPlatform base class.
        """
        view_command = [
            "pipelines",
            "view",
            "pipeline_name",
            "--workspace",
            "workspace_name",
        ]
        self.subcommand_test(
            "pipelines",
            ["view", "pipeline_name", "--workspace", "workspace_name"],
            view_command,
        )

    def test_import_command(self):
        """
        Unit test for the import method of SeqeraPlatform base class.
        """
        import_command = [
            "pipelines",
            "import",
            "pipeline_file.json",
            "--name",
            "my_pipeline_name",
            "--workspace",
            "workspace_name",
        ]
        self.subcommand_test(
            "pipelines",
            [
                "import",
                "pipeline_file.json",
                "--name",
                "my_pipeline_name",
                "--workspace",
                "workspace_name",
            ],
            import_command,
        )
