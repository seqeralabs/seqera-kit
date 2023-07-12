import logging

# Import the tw_pywrap package
from tw_pywrap import tower

logging.basicConfig(level=logging.DEBUG)

# Constructs a new tw_pywrap Tower instance
tw = tower.Tower()

# Specify the workspace to use
workspace = "my_workspace"  # name of the workspace
compute_env_name = "my_compute_env"  # name of your compute env

# Specify a human-readable run name
run_name = "hello-world-tw-pywrap"

# Launch 'hello-world' pipeline using the 'launch' method
pipeline_run = tw.launch(
    "--workspace",
    workspace,
    "--compute-env",
    compute_env_name,
    "--name",
    run_name,
    "--revision",
    "master",
    "--wait",
    "SUBMITTED",
    "https://github.com/nextflow-io/hello",
    to_json=True,
)
