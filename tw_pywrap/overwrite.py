import json
from tw_pywrap import utils
from tw_pywrap.tower import ResourceExistsError
import logging


class Overwrite:
    """
    Manages overwrite functionality for Tower resources.

    # TODO: When overwrite functionality becomes native to CLI,
    we can remove this class.
    """

    # Define blocks for simple overwrite with --name and --workspace
    generic_deletion = [
        "credentials",
        "secrets",
        "compute-envs",
        "datasets",
        "actions",
        "pipelines",
    ]

    def __init__(self, tw):
        """
        Initializes an Overwrite instance.

        Args:
        tw: A Tower class instance.

        Attributes:
        tw: A Tower class instance used to execute Tower CLI commands.
        cached_jsondata: A cached placeholder for JSON data. Default value is None.
        block_jsondata: A dictionary to store JSON data for each block.
        Key is the block name, and value is the corresponding JSON data.
        """
        self.tw = tw
        self.cached_jsondata = None
        self.block_jsondata = {}  # New dict to hold JSON data per block

        # Define special handlers for resources deleted with specific args
        self.block_operations = {
            "organizations": {
                "keys": ["name"],
                "method_args": self._get_organization_args,
                "name_key": "orgName",
            },
            "teams": {
                "keys": ["name", "organization"],
                "method_args": self._get_team_args,
                "name_key": "name",
            },
            "participants": {
                "keys": ["name", "type", "workspace"],
                "method_args": self._get_participant_args,
                "name_key": "email",
            },
            "workspaces": {
                "keys": ["name", "organization"],
                "method_args": self._get_workspace_args,
                "name_key": "workspaceId",
            },
        }

    def handle_overwrite(self, block, args, overwrite=False):
        """
        Handles overwrite functionality for Tower resources and
        calling the 'tw delete' method with the correct args.
        """
        if block in Overwrite.generic_deletion:
            self.block_operations[block] = {
                "keys": ["name", "workspace"],
                "method_args": self._get_generic_deletion_args,
                "name_key": "name",
            }

        if block in self.block_operations:
            operation = self.block_operations[block]
            keys_to_get = operation["keys"]
            self.cached_jsondata, tw_args = self._get_json_data(
                block, args, keys_to_get
            )

            if block == "participants":
                if tw_args.get("type") == "TEAM":
                    self.block_operations["participants"]["name_key"] = "teamName"
                else:
                    self.block_operations["participants"]["name_key"] = "email"

            if block != "pipelines" and self.check_resource_exists(
                operation["name_key"], tw_args
            ):
                # if resource exists, delete
                if overwrite:
                    logging.debug(
                        f" The attempted {block} resource already exists."
                        " Overwriting.\n"
                    )
                    self._delete_resource(block, operation, tw_args)
                else:  # return an error if resource exists, overwrite=False
                    raise ResourceExistsError(
                        f" The {block} resource already exists and"
                        " will not be created. Please set 'overwrite: True'"
                        " in your config file.\n"
                    )

    def _get_organization_args(self, args):
        """
        Returns a list of arguments for the delete() method for organizations.
        """
        return ("delete", "--name", args["name"])

    def _get_team_args(self, args):
        """
        Returns a list of arguments for the delete() method for teams. The teamId
        used to delete will be retrieved using the find_key_value_in_dict() method.
        """
        jsondata = self.block_jsondata.get("teams", None)

        if not jsondata:
            json_method = getattr(self.tw, "-o json")
            json_out = json_method("teams", "list", "-o", args["organization"])
            self.block_jsondata["teams"] = json_out
        else:
            json_out = jsondata

        # Get the teamId from the json data
        team_id = utils.find_key_value_in_dict(
            json.loads(json_out), "name", args["name"], "teamId"
        )
        return ("delete", "--id", str(team_id), "--organization", args["organization"])

    def _get_participant_args(self, args):
        """
        Returns a list of arguments for the delete() method for participants.
        Works for both teams and members where if the type is TEAM, the teamName
        is used to delete, and if the type is MEMBER, the email is used to delete.
        """
        method_args = (
            "delete",
            "--name",
            args["name"],
            "--type",
            args["type"],
            "--workspace",
            args["workspace"],
        )
        return method_args

    def _get_workspace_args(self, args):
        """
        Returns a list of arguments for the delete() method for workspaces. The
        workspaceId used to delete will be retrieved using the _find_workspace_id()
        method.
        """
        workspace_id = self._find_workspace_id(
            json.loads(self.tw.workspaces.list("-o", "json")),
            args["organization"],
            args["name"],
        )
        return ("delete", "--id", str(workspace_id))

    def _get_generic_deletion_args(self, args):
        """
        Returns a list of arguments for the delete() method for resources that
        are deleted with --name and --workspace.
        """
        return (
            "delete",
            "--name",
            args["name"],
            "--workspace",
            args["workspace"],
        )

    def _get_json_data(self, block, args, keys_to_get):
        """
        For the specified keys in the operations dictionary, get the values from
        the command line arguments and return a dictionary of values.

        Also, gets json data from Tower by calling the list() method once and caches
        the json data for that block in self.block_jsondata. If the block data already
        exists, it will be retrieved from the dictionary instead of calling the list().

        Returns a tuple of json data and a dictionary of values to run delete() on.
        """
        json_method = getattr(self.tw, "-o json")
        tw_args = []  # Default value for tw_args

        # Check if block data already exists
        if block in self.block_jsondata:
            self.cached_jsondata = self.block_jsondata[block]
            tw_args = self._get_values_from_cmd_args(args, keys_to_get)
        else:
            # Fetch the data if it does not exist
            if block == "teams":
                tw_args = self._get_values_from_cmd_args(args[0], keys_to_get)
                self.cached_jsondata = json_method(
                    block, "list", "-o", tw_args["organization"]
                )
            elif block in Overwrite.generic_deletion or block == "participants":
                tw_args = self._get_values_from_cmd_args(args, keys_to_get)
                self.cached_jsondata = json_method(
                    block, "list", "-w", tw_args["workspace"]
                )
            else:
                tw_args = self._get_values_from_cmd_args(args, keys_to_get)
                self.cached_jsondata = json_method(block, "list")

        # Store this data in the block_jsondata dict for later use
        self.block_jsondata[block] = self.cached_jsondata
        return self.cached_jsondata, tw_args

    def check_resource_exists(self, name_key, tw_args):
        """
        Check if a resource exists in Tower by looking for the name and value
        in the json data generated from the list() method.
        """
        return utils.check_if_exists(self.cached_jsondata, name_key, tw_args["name"])

    def _delete_resource(self, block, operation, tw_args):
        """
        Delete a resource in Tower by calling the delete() method and
        arguments defined in the operation dictionary.
        """
        method_args = operation["method_args"](tw_args)
        method = getattr(self.tw, block)
        method(*method_args)

    def _get_values_from_cmd_args(self, cmd_args, keys):
        """
        Return a dictionary of values from a list of command line arguments based
        on a input list of keys.
        """
        values = {key: None for key in keys}
        key = None

        for arg in cmd_args:
            if arg.startswith("--"):
                key = arg[2:]
            else:
                if key and key in keys:
                    values[key] = arg
                key = None
        return values

    def _find_workspace_id(self, organization, workspace_name):
        """
        Custom method to find a workspace ID in a nested dictionary with a given
        organization name and workspace name. This ID will be used to delete the
        workspace.
        """
        if "workspaces" in self.cached_jsondata:
            workspaces = self.cached_jsondata["workspaces"]
            for workspace in workspaces:
                if (
                    workspace.get("orgName") == organization
                    and workspace.get("workspaceName") == workspace_name
                ):
                    return workspace.get("workspaceId")
        return None
