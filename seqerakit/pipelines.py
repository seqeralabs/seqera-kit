"""
Subclass of SeqeraPlatform class for overriding pipelines subcommand methods.
"""
from pathlib import Path
from seqerakit.seqeraplatform import SeqeraPlatform


class Pipelines(SeqeraPlatform):
    """
    Python wrapper for 'tw pipelines export' command. # TODO update
    """

    def export_pipeline(self, name, *args, **kwargs):
        """
        Export a pipeline
        """
        # create a Path object for the workspace directory
        workspace_dir = Path(self.workspace)

        # create the directory if it doesn't exist
        workspace_dir.mkdir(parents=True, exist_ok=True)

        # define the output file path
        outfile = str(workspace_dir / f"{name}.json")

        # Build the command
        command = [
            "pipelines",
            "export",
            "--workspace",
            self.workspace,
            "--name",
            name,
            outfile,
        ]

        # Pass the built command to the base class method in SeqeraPlatform
        return self._tw_run(command, *args, **kwargs)
