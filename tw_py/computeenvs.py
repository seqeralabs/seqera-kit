"""
Subclass of Tower class for compute environments
"""
from pathlib import Path
from .base import Tower


class ComputeEnvs(Tower):
    """
    Python wrapper for tw compute-envs command
    """

    @property
    def cmd(self):
        return "compute-envs"

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
                str(outfile),  # Ensure the Path object is converted to a string
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
