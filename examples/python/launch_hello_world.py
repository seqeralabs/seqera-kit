import logging
from twkit import tower

tw = tower.Tower()

tw.launch(
    "--workspace",
    "twkit/showcase",
    "--compute-env",
    "seqera_aws_ireland_fusionv2_nvme",
    "--name",
    "nf-core-rnaseq",
    "--revision",
    "3.12.0",
    "https://github.com/nf-core/rnaseq",
    to_json=True
)
