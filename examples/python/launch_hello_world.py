import logging

# Import the twkit package
from twkit import tower

logging.basicConfig(level=logging.DEBUG)

# Construct a new twkit Tower instance
tw = tower.Tower()

# Customise the entries below as required
workspace = "<YOUR_WORKSPACE>"  # Name of your Workspace
compute_env = "<YOUR_COMPUTE_ENVIRONMENT>"  # Name of your Compute Environment

# Specify a human-readable run name
run_name = "hello-world-twkit"

# Launch the 'hello-world' pipeline using the 'launch' method
pipeline_run = tw.launch(
    "--workspace",
    workspace,
    "--compute-env",
    compute_env,
    "--name",
    run_name,
    "--revision",
    "master",
    "--wait",
    "SUBMITTED",
    "https://github.com/nextflow-io/hello",
    to_json=True,
)
