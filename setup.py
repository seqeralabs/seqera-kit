#!/usr/bin/env python

from setuptools import find_packages, setup

version = "0.0.1"

with open("README.md") as f:
    readme = f.read()

setup(
    name="tw-pywrap",
    version=version,
    description="""Automation of resource creation to be able 
    to setup and run pipelines on Nextflow Tower.""",
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords=["nextflow", "bioinformatics", "workflow", "pipeline", "nextflow-tower"],
    author="Esha Joshi, Adam Talbot, Harshil Patel",
    author_email="esha.joshi@seqera.io, adam.talbot@seqera.io, harshil.patel@seqera.io",
    url="https://github.com/ejseqera/tw-pywrap",
    license="MIT",
    entry_points={"console_scripts": ["tw-pywrap=tw_pywrap.cli:main"]},
    python_requires=">=3.8, <4",  # untested
    install_requires=["pyyaml>=6.0.0"],
    packages=find_packages(exclude=("docs")),
    include_package_data=True,
    zip_safe=False,
)
