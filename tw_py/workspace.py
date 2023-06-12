"""
Subclass of Tower class for workspaces
"""
from .base import Tower


class Workspace(Tower):
    """
    Python wrapper for tw workspaces command
    """

    @property
    def cmd(self):
        return "workspaces"

    def update(self, workspace_id, *args, **kwargs):
        """
        Update a workspace by workspace id.
        """
        self._tw_run([self.cmd, "update", workspace_id], *args, **kwargs)

    def leave(self, workspace_id=None, name=None, *args, **kwargs):
        """
        Leave a workspace with the given workspace id or name.
        """
        if workspace_id:
            command = [self.cmd, "leave", "--id", workspace_id]
        elif name:
            command = [self.cmd, "leave", "--name", name]
        self._tw_run(command, *args, **kwargs)
