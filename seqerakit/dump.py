import json
import yaml
import os


class DumpYaml:
    def __init__(self, sp, workspace):
        self.sp = sp
        self.workspace = workspace
        self.json_data = {}
        self.yaml_file_path = None
        self.workspace_objects = ["compute-envs", "pipelines"]
        self.yaml_keys = {
            "compute-envs": [
                {
                    "discriminator": "type",
                    "name": "name",
                    "workspace": "workspace",
                    "region": "region",
                    "workDir": "work-dir",
                    "waveEnabled": "wave",
                    "fusion2Enabled": "fusion-v2",
                    "nvnmeStorageEnabled": "fast-storage",
                    "type": "provisioning-model",
                    "instanceTypes": "instance-types",  # TODO
                    "minCpus": "min-cpus",
                    "maxCpus": "max-cpus",
                    "ebsAutoScale": "no-ebs-autoscale",
                    "fargateHeadEnabled": "fargate",
                    "gpuEnabled": "gpu",
                },
            ],  # TODO add missing keys
            "pipelines": [
                {
                    "pipeline": "url",
                    "description": "description",
                    "workspace": "workspace",
                    "workDir": "work-dir",
                    "revision": "revision",
                    "configProfiles": "profile",  # TODO handle YAML list representation
                    "configText": "config",
                    "paramsFile": "params-file",
                    "resume": "resume",
                    "pullLatest": "pull-latest",
                    "stubRun": "stub-run",
                    "pre-run": "pre-run",
                    "computeEnvId": "compute-env",
                },
            ],  # TODO add support for datasets
        }

    def generate_yaml_dump(self, yaml_file):
        # Get path to yaml file
        self.yaml_file_path = yaml_file

        # Initialize a dictionary to hold object names for each type of workspace object
        object_names_dict = {obj: [] for obj in self.workspace_objects}

        # Get names of objects defined in workspace_objects through CLI command
        object_names = self.get_names()

        # Append the names to the corresponding object in object_names_dict
        for obj, names in object_names.items():
            if obj in object_names_dict:
                object_names_dict[obj].extend(
                    names if isinstance(names, list) else [names]
                )

        # For each type of object, get its exports and transform the data
        for object_type, names in object_names_dict.items():
            for name in names:
                json_output = self.get_object_exports(object_type, name)
                if object_type == "compute-envs":
                    json_data = self.transform_data(
                        json_output, object_type, name, primary_key="discriminator"
                    )
                else:
                    json_data = self.transform_data(json_output, object_type, name)

                with open(
                    f"{self.yaml_file_path}_{object_type}_{name}.yaml", "w"
                ) as yaml_file:
                    yaml.dump(json_data, yaml_file, sort_keys=False)

    def get_names(self):
        object_names_dict = {}
        for object in self.workspace_objects:
            cli_method = getattr(self.sp, object)
            json_data = cli_method("list", "-w", self.workspace, to_json=True)

            # Extract names for this specific object type
            names = self._extract_values_by_key(json_data, "name")

            # Store names in dictionary under the respective object type
            object_names_dict[object] = names

        return object_names_dict

    def get_object_exports(self, object, object_name):
        # Use names retrived to export jsons through CLI command
        json_data = {}
        cli_method = getattr(self.sp, object)

        cli_method(
            "export", f"{object_name}.json", "-w", self.workspace, "-n", object_name
        )

        with open(f"{object_name}.json", "r") as json_file:
            json_data = json.load(json_file)

        # delete the json file after loading it
        os.remove(f"{object_name}.json")
        return json_data

    def transform_data(
        self, json_data, object_type, object_name=None, primary_key="name"
    ):
        mapping = self.yaml_keys[object_type][0]
        result = {object_type: []}
        ordered_env = []

        # Ensure primary_key is the first key
        primary_mapped_key = mapping.get(primary_key, primary_key)
        primary_value = (
            object_name if primary_key == "name" else json_data.get(primary_key)
        )
        if primary_value is not None:
            ordered_env.append((primary_mapped_key, primary_value))

        # Process keys based on object_type (CEs or pipelines)
        if object_type == "compute-envs":
            self._process_compute_envs(
                json_data, ordered_env, mapping, object_name, primary_key
            )

        elif object_type == "pipelines":
            self._process_pipelines(json_data, ordered_env, mapping, object_name)

        # Convert to a regular dictionary just before serialization
        env = dict(ordered_env)
        result[object_type].append(env)
        return result

    def _process_compute_envs(
        self, json_data, ordered_env, mapping, object_name, primary_key
    ):
        config_mode = next(
            (key for key in ["forge", "manual"] if key in json_data), "manual"
        )
        ordered_env.append(("config-mode", config_mode))
        ordered_env.append(("name", object_name))
        for key, new_key in mapping.items():
            if key == primary_key:
                continue
            if key in json_data:
                # Directly assign if value is a list
                value = (
                    json_data[key]
                    if isinstance(json_data[key], list)
                    else json_data[key]
                )
                ordered_env.append((new_key, value))
            if key == "workspace":
                ordered_env.append((new_key, self.workspace))
            elif config_mode in json_data:
                transformed_nested = self._transform_nested_structure(
                    json_data[config_mode], mapping
                )
                ordered_env.extend(transformed_nested.items())

    def _process_pipelines(self, json_data, ordered_env, mapping, object_name):
        launch_data = json_data["launch"]
        transformed_nested = self._transform_nested_structure(launch_data, mapping)

        for key, new_key in mapping.items():
            if key == "description":
                ordered_env.append((new_key, json_data[key]))
            elif key == "workspace":
                ordered_env.append((new_key, self.workspace))

        # Handle 'configText' and 'paramsText' in 'launch' to return files
        for special_key, file_type, new_key in [
            ("configText", "config", "config"),
            ("paramsText", "yaml", "params-file"),
        ]:
            if special_key in launch_data:
                # Write values for these keys into yaml and config files
                file_path = self._write_special_file(
                    launch_data[special_key], object_name, file_type
                )
                transformed_nested[
                    new_key
                ] = file_path  # Use the file path as value for key

        ordered_env.extend(transformed_nested.items())

    def _transform_nested_structure(self, nested_data, mapping):
        transformed_data = {}
        for key in nested_data:
            if key in mapping:
                new_key = mapping[key]
                # Directly assign the value if it's a list
                transformed_data[new_key] = (
                    nested_data[key]
                    if isinstance(nested_data[key], list)
                    else nested_data[key]
                )
        return transformed_data

    def _extract_values_by_key(self, json_data, target_key):
        def extract_recursively(data, key, collected_values):
            if isinstance(data, dict):
                for k, v in data.items():
                    if k == key:
                        collected_values.append(v)
                    else:
                        extract_recursively(v, key, collected_values)
            elif isinstance(data, list):
                for item in data:
                    extract_recursively(item, key, collected_values)

        extracted_values = []
        extract_recursively(json_data, target_key, extracted_values)
        return extracted_values

    def _write_special_file(self, content, object_name, file_type):
        file_path = f"{object_name}.{file_type}"

        with open(file_path, "w") as file:
            if file_type == "config":
                file.write(content)
            elif file_type == "yaml":
                # pyyaml is so annoying so I just write the string to the file manually
                # yaml.dump(content, file, default_flow_style=False, default_style=None)
                file.write(content)
        return file_path
