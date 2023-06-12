"""
Subclass of Tower class for pipelines
"""
from pathlib import Path
from .base import Tower


class Pipelines(Tower):
    """
    Python wrapper for tw pipelines command
    """

    @property
    def cmd(self):
        return "pipelines"

    def add(self, name, config, repository, *args, **kwargs):
        """
        Add a pipeline to the workspace
        Overrides the base class add method
        """
        command = [
            self.cmd,
            repository,
            "add",
            "--name",
            name,
            "--workspace",
            self.workspace,
        ]
        if config is not None:
            command.extend(["--params-file", config])
        self._tw_run(command, *args, **kwargs)

    def import_pipeline(self, name, config, *args, **kwargs):
        """
        Import a pipeline
        """
        self._tw_run(
            [self.cmd, "import", "--name", name, config, "--workspace", self.workspace],
            *args,
            **kwargs,
        )

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
