#!/usr/bin/env python

from setuptools import find_packages, setup

VERSION = "0.3.1"

with open("README.md") as f:
    readme = f.read()

setup(
    name="twkit",
    version=VERSION,
    description="twkit is now seqerakit",
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords=["nextflow", "bioinformatics", "workflow", "pipeline", "nextflow-tower"],
    author="Esha Joshi, Adam Talbot, Harshil Patel",
    author_email="esha.joshi@seqera.io, adam.talbot@seqera.io, harshil.patel@seqera.io",
    url="https://github.com/seqeralabs/seqera-kit",
    license="MIT",
    install_requires=["seqerakit"],
    packages=find_packages(exclude=("docs")),
    classifiers=["Development Status :: 7 - Inactive"],
)
