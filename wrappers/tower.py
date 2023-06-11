from pathlib import Path
import subprocess
import shlex
from abc import ABC, abstractmethod


class Tower(ABC):
    """
    Abstract base class wrapper for tw commands
    """

    @property
    @abstractmethod
    def cmd(self):
        pass

    def __init__(self, workspace_name):
        self.workspace = workspace_name

    def _tw_run(self, cmd, *args, **kwargs):
        """
        Run a tw command with supplied commands
        """
        command = ["tw"]
        if kwargs.get("to_json"):
            command.extend(["-o", "json"])
        command.extend(cmd)
        command.extend(args)

        if kwargs.get("config") is not None:
            config_path = kwargs["config"]
            command.append(f"--config={config_path}")

        if "params_file" in kwargs:
            params_path = kwargs["params_file"]
            command.append(f"--params-file={params_path}")

        full_cmd = " ".join(shlex.quote(arg) for arg in command)

        # Run the command and return the stdout
        process = subprocess.Popen(full_cmd, stdout=subprocess.PIPE, shell=True)
        stdout, _ = process.communicate()
        stdout = stdout.decode("utf-8").strip()

        return stdout

    def get_list(self, *args, **kwargs):
        """
        List entities (pipelines, compute envs, etc.)
        # List is a reserved keyword in Python, so we use get_list instead
        """
        return self._tw_run(
            [self.cmd, "list", "--workspace", self.workspace], *args, **kwargs
        )

    def view(self, name, *args, **kwargs):
        """
        View entities (pipelines, compute envs, etc.)
        """
        return self._tw_run([self.cmd, "view", "--name", name], *args, **kwargs)

    def delete(self, name, *args, **kwargs):
        """
        Delete an entity (pipelines, compute envs, etc.)
        """
        self._tw_run([self.cmd, "delete", "--name", name], *args, **kwargs)

    def add(self, name, *args, **kwargs):
        """
        Add an entity (pipelines, compute envs, etc.)
        """
        self._tw_run([self.cmd, "add", "--name", name], *args, **kwargs)


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
