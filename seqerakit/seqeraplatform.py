# Copyright 2023, Seqera
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import shlex
import logging
import subprocess
import re
import json

logging.basicConfig(level=logging.DEBUG)


class SeqeraPlatform:
    """
    A Python class that serves as a wrapper for 'tw' CLI commands. # TODO update

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
            command = self.cmd.split()
            command.extend(args)
            return self.tw_instance._tw_run(command, **kwargs)

    # Constructs a new SeqeraPlatform instance
    def __init__(self, cli_args=None, dryrun=False):
        if cli_args and "--verbose" in cli_args:
            raise ValueError(
                "--verbose is not supported as a CLI argument to seqerakit."
            )
        self.cli_args = cli_args or []
        self.dryrun = dryrun

    def _construct_command(self, cmd, *args, **kwargs):
        command = ["tw"] + self.cli_args

        if kwargs.get("to_json"):
            command.extend(["-o", "json"])

        command.extend(cmd)
        command.extend(args)

        if kwargs.get("config"):
            command.append(f"--config={kwargs['config']}")

        if "params_file" in kwargs:
            command.append(f"--params-file={kwargs['params_file']}")

        return self._check_env_vars(command)

    # Checks environment variables to see that they are set accordingly
    def _check_env_vars(self, command):
        full_cmd_parts = []
        shell_constructs = ["|", ">", "<", "$(", "&", "&&", "`"]
        for arg in command:
            if any(construct in arg for construct in shell_constructs):
                full_cmd_parts.append(arg)
            elif "$" in arg:
                for env_var in re.findall(r"\$\{?[\w]+\}?", arg):
                    if re.sub(r"[${}]", "", env_var) not in os.environ:
                        raise EnvironmentError(
                            f" Environment variable {env_var} not found!"
                        )
                full_cmd_parts.append(arg)
            else:
                full_cmd_parts.append(shlex.quote(arg))
        return " ".join(full_cmd_parts)

    # Executes a 'tw' command in a subprocess and returns the output.
    def _execute_command(self, full_cmd, to_json=False):
        logging.debug(f" Running command: {full_cmd}")
        process = subprocess.Popen(
            full_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
        )
        stdout, _ = process.communicate()
        stdout = stdout.decode("utf-8").strip()

        if "ERROR: " in stdout:
            self._handle_command_errors(stdout)

        return json.loads(stdout) if to_json else stdout

    def _execute_info_command(self):
        # Directly execute 'tw info' command
        command = "tw info"
        return self._execute_command(command)

    def _handle_command_errors(self, stdout):
        logging.error(stdout)

        # Check for specific tw cli error patterns and raise custom exceptions
        if re.search(
            r"ERROR: .*already (exists|a participant)", stdout, flags=re.IGNORECASE
        ):
            raise ResourceExistsError(
                " Resource already exists. Please delete first or set 'overwrite: true'"
            )
        else:
            raise ResourceCreationError(
                f" Resource creation failed: '{stdout}'. "
                "Check your config and try again."
            )

    def _tw_run(self, cmd, *args, **kwargs):
        full_cmd = self._construct_command(cmd, *args, **kwargs)
        if not full_cmd or self.dryrun:
            logging.debug(f"DRYRUN: Running command {full_cmd}")
            return
        return self._execute_command(full_cmd, kwargs.get("to_json"))

    # Allow any 'tw' subcommand to be called as a method.
    def __getattr__(self, cmd):
        if cmd == "info":
            return self._execute_info_command
        else:
            return self.TwCommand(self, cmd.replace("_", "-"))


class ResourceExistsError(Exception):
    pass


class ResourceCreationError(Exception):
    pass
