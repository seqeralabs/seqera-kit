import logging

# Import the seqerakit package
from seqerakit import seqeraplatform

logging.basicConfig(level=logging.DEBUG)

# Construct a new seqerakit SeqeraPlatform instance
tw = seqeraplatform.SeqeraPlatform()

# Customise the entries below as required
workspace = "<YOUR_WORKSPACE>"  # Name of your Workspace
compute_env = "<YOUR_COMPUTE_ENVIRONMENT>"  # Name of your Compute Environment

# Specify a human-readable run name
run_name = "hello-world-seqerakit"

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
)
