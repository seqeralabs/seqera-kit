"""
Python wrapper for tw pipelines command
"""
from .utils import tw_run
from pathlib import Path


class Pipelines:
    """
    Python wrapper for tw pipelines command
    """

    cmd = "pipelines"

    def __init__(self, workspace_name):
        self.workspace = workspace_name

    def _tw_run(self, command, *args, **kwargs):
        return tw_run(command, *args, **kwargs)

    def list(self, *args, **kwargs):
        """
        List pipelines
        """
        return self._tw_run(
            [self.cmd, "list", "--workspace", self.workspace], *args, **kwargs
        )

    def view(self, name, *args, **kwargs):
        """
        View a pipeline
        """
        return self._tw_run([self.cmd, "view", "--name", name], *args, **kwargs)

    def delete(self, name, *args, **kwargs):
        """
        Delete a pipeline
        """
        self._tw_run([self.cmd, "delete", "--name", name], *args, **kwargs)

    def export_pipeline(self, name, *args, **kwargs):
        """
        Export a pipeline
        """
        workspace_dir = Path(self.workspace)
        workspace_dir.mkdir(parents=True, exist_ok=True)
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
            *args,
            **kwargs,
        )

    def import_pipeline(self, name, config, *args, **kwargs):
        """
        Import a pipeline
        """
        self._tw_run(
            [self.cmd, "import", "--name", name, config, "--workspace", self.workspace],
            *args,
            **kwargs,
        )

    def add(self, name, config, repository, *args, **kwargs):
        """
        Add a pipeline to the workspace
        """
        self._tw_run(
            [
                self.cmd,
                "add",
                "--name",
                name,
                "--params-file",
                config,
                repository,
                "--workspace",
                self.workspace,
            ],
            *args,
            **kwargs,
        )

    def launch(self, name, *args, **kwargs):
        """
        Launch a pipeline
        """
        command = [
            "launch",
            name,
            "--workspace",
            self.workspace,
        ]
        return self._tw_run(command, *args, **kwargs)

    # TODO: add labels method
