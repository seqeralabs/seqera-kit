"""
Subclass of SeqeraPlatform class for overriding compute environments subcommand methods.
"""
from pathlib import Path
from seqerakit.seqeraplatform import SeqeraPlatform


class ComputeEnvs(SeqeraPlatform):
    """
    Python wrapper for tw compute-envs export command.
    """

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

        # Build the command
        command = [
            "compute-envs",
            "export",
            "--workspace",
            self.workspace,
            "--name",
            name,
            str(outfile),
        ]

        # Pass the built command to the base class method in SeqeraPlatform
        return self._tw_run(command, *args, **kwargs, to_json=True)
