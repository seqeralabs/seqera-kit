#!/usr/bin/env python

from setuptools import find_packages, setup

VERSION = "0.5.1"

with open("README.md") as f:
    readme = f.read()

setup(
    name="seqerakit",
    version=VERSION,
    description="Automate creation of Seqera Platform resources",
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords=[
        "nextflow",
        "bioinformatics",
        "workflow",
        "pipeline",
        "seqera-platform",
        "seqera",
    ],
    author="Esha Joshi, Adam Talbot, Harshil Patel",
    author_email="esha.joshi@seqera.io, adam.talbot@seqera.io, harshil.patel@seqera.io",
    url="https://github.com/seqeralabs/seqera-kit",
    license="Apache 2.0",
    entry_points={"console_scripts": ["seqerakit=seqerakit.cli:main"]},
    python_requires=">=3.8, <4",  # untested
    install_requires=["pyyaml>=6.0.0"],
    packages=find_packages(exclude=("docs")),
    include_package_data=True,
    zip_safe=False,
)
