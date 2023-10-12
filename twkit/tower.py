import json
import logging
import subprocess
import shlex
import re

logging.basicConfig(level=logging.DEBUG)


class Tower:
    """
    A Python class that serves as a wrapper for 'tw' CLI commands.

    The class enables the execution of 'tw' commands in an object-oriented manner.
    You can call any subcommand of 'tw' as a method on instances of this class.
    The arguments of the subcommand can be passed as arguments to the method.

    Each command is run in a subprocess, with the output being captured and returned.
    """

    class TwCommand:
        def __init__(self, tw_instance, cmd):
            self.tw_instance = tw_instance
            self.cmd = cmd

        def __call__(self, *args, **kwargs):
            command = ["tw"]

            # Prepend the CLI args if present
            # command.extend(self.tw_instance.cli_args)
            command = self.cmd.split()
            command.extend(args)
            return self.tw_instance._tw_run(command, **kwargs)

    # Constructs a new Tower instance
    def __init__(self, cli_args=None, dryrun=False):
        if cli_args and "--verbose" in cli_args:  # TODO: remove this
            raise ValueError("--verbose is not supported as a CLI argument to twkit.")
        self.cli_args = cli_args if cli_args else []
        self.dryrun = dryrun

    # Executes a 'tw' command in a subprocess and returns the output.
    def _tw_run(self, cmd, *args, **kwargs):
        """
        Run a tw command with supplied commands
        """
        command = ["tw"]

        # Prepend the CLI args if present
        command.extend(self.cli_args)

        if kwargs.get("to_json"):
            to_json = True
            command.extend(["-o", "json"])
        else:
            to_json = False
        command.extend(cmd)
        command.extend(args)
        if kwargs.get("config") is not None:
            config_path = kwargs["config"]
            command.append(f"--config={config_path}")

        if "params_file" in kwargs:
            params_path = kwargs["params_file"]
            command.append(f"--params-file={params_path}")

        full_cmd = " ".join(arg if "$" in arg else shlex.quote(arg) for arg in command)
        logging.debug(f" Running command: {full_cmd}\n")

        # Skip if --dryrun
        if self.dryrun:
            return

        # Run the command and return the stdout
        process = subprocess.Popen(
            full_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
        )
        stdout, _ = process.communicate()
        stdout = stdout.decode("utf-8").strip()

        # Error handling for stdout
        if stdout:
            if re.search(r"ERROR: .* already exists", stdout):
                raise ResourceExistsError(
                    " Resource already exists and cannot be created."
                    " Please delete first or if using a YAML, set 'overwrite: true'\n"
                )
            elif re.search(r"ERROR: .*", stdout):
                raise ResourceCreationError(
                    f" Resource creation failed with the following error: '{stdout}'.\n"
                    "Please check your config file and try again.\n"
                )
            elif to_json is True:
                return json.loads(stdout)
            else:
                return stdout

    # Allow any 'tw' subcommand to be called as a method.
    def __getattr__(self, cmd):
        """
        Magic method to allow any 'tw' subcommand to be called as a method.
        Returns a TwCommand object that can be called with arguments.
        """
        cmd = cmd.replace("_", "-")  # replace underscores with hyphens
        return self.TwCommand(self, cmd)


class ResourceExistsError(Exception):
    pass


class ResourceCreationError(Exception):
    pass
