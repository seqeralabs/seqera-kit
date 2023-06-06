"""
Python wrapper for tw datasets command
"""
from .utils import tw_run


class Datasets:
    """
    Python wrapper for tw datasets command
    """

    cmd = "datasets"

    def __init__(self, dataset_name):
        self.name = dataset_name

    def _tw_run(self, command):
        return tw_run(command)

    def list(self):
        """
        List datasets in a workspace
        """
        return self._tw_run([self.cmd, "list"])

    def view(self):
        """
        View a dataset
        """
        return self._tw_run([self.cmd, "view", "--name", self.name])

    def delete(self):
        """
        Delete a dataset
        """
        self._tw_run([self.cmd, "delete", "--name", self.name])

    def add(self, description, header_opt, dataset_path):
        """
        Add a dataset to the workspace
        """
        if header_opt:
            self._tw_run(
                [
                    self.cmd,
                    "add",
                    "--name",
                    self.name,
                    "--description",
                    description,
                    "--header",
                    dataset_path,
                ]
            )
        else:
            self._tw_run(
                [
                    self.cmd,
                    "add",
                    "--name",
                    self.name,
                    "--description",
                    description,
                    dataset_path,
                ]
            )

    def get_url(self):
        """
        Get URL for dataset
        """
        return self._tw_run([self.cmd, "url", "--name", self.name])


# TODO: add tw download method
# TODO: add tw update method
