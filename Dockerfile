FROM mambaorg/micromamba:1.4.4

USER root

## Install git
RUN apt-get update -y && apt-get install -y git

## Install dependencies with mamba
USER $MAMBA_USER
COPY . /home/$MAMBA_USER
WORKDIR /home/$MAMBA_USER

RUN \
    micromamba install -y -n base -c bioconda -c conda-forge -c defaults \
    python=3.10.9 pyyaml=6.0 tower-cli=0.8.0 \
    && micromamba clean --all --yes

ENV PATH="$PATH:/opt/conda/bin"