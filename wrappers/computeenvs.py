"""
Python wrapper for tw compute-envs command
"""

from .utils import tw_run
from pathlib import Path


class ComputeEnvs:
    """
    Python wrapper for tw compute-envs command
    """

    cmd = "compute-envs"

    def __init__(self, workspace_name):
        self.workspace = workspace_name

    def _tw_run(self, command, *args, **kwargs):
        return tw_run(command, *args, **kwargs)

    def list(self, *args, **kwargs):
        """
        List compute environments
        """
        return self._tw_run(
            [self.cmd, "list", "--workspace", self.workspace],
            *args,
            **kwargs,
        )

    def view(self, name, *args, **kwargs):
        """
        View a compute environment
        """
        return self._tw_run(
            [self.cmd, "view", "--name", name, "--workspace", self.workspace],
            to_json=True,
            *args,
            **kwargs,
        )

    def delete(self, name, *args):
        """
        Delete a compute environment
        """
        self._tw_run([self.cmd, "delete", "--name", name], *args)

    def export_ce(self, name, *args, **kwargs):
        """
        Export a compute environment
        """
        # create a Path object for the workspace directory
        workspace_dir = Path(self.workspace)

        # create the directory if it doesn't exist
        workspace_dir.mkdir(parents=True, exist_ok=True)

        # define the output file path
        outfile = workspace_dir / f"{name}.json"

        return self._tw_run(
            [
                self.cmd,
                "export",
                "--workspace",
                self.workspace,
                "--name",
                name,
                outfile,
            ],
            to_json=True,
            *args,
            **kwargs,
        )

    def import_ce(self, name, config, credentials, *args, **kwargs):
        """
        Import a compute environment
        """
        command = [
            self.cmd,
            "import",
            "--name",
            name,
            config,
            "--credentials",
            credentials,
            "--workspace",
            self.workspace,
        ]
        self._tw_run(command, *args, **kwargs)

    def set_default(self, name, *args):
        """
        Set a compute environment as default
        """
        self._tw_run([self.cmd, "primary", "set", "--name", name], *args)
