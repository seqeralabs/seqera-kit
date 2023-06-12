"""
Subclass of Tower class for organizations
"""
from .base import Tower


class Organizations(Tower):
    """
    Python wrapper for tw organizations command.
    """

    @property
    def cmd(self):
        return "organizations"

    def update(self, organization_id=None, name=None, *args, **kwargs):
        """
        Update an organization by organization id or name.
        """
        if organization_id:
            command = [self.cmd, "update", "--id", organization_id]
        elif name:
            command = [self.cmd, "update", "--name", name]
        self._tw_run(command, *args, **kwargs)
