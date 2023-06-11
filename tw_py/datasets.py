"""
Subclass of Tower class for datasets
"""
from .base import Tower


class Datasets(Tower):
    """
    Python wrapper for tw datasets command
    """

    @property
    def cmd(self):
        return "datasets"

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
