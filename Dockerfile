FROM mambaorg/micromamba:1.4.4

USER root

## Install git
RUN \
    apt-get update -y && apt-get install -y wget git \
    && wget -L https://github.com/seqeralabs/tower-cli/releases/download/v0.8.0/tw-linux-x86_64 \
    && mv tw-linux-x86_64 tw \
    && chmod +x tw \
    && mv tw /usr/local/bin/

USER $MAMBA_USER
## Install Python dependencies
RUN \
    micromamba install -y -n base -c bioconda -c conda-forge -c defaults \
    python=3.10.9 pyyaml=6.0 gitpython=3.1.31 \
    && micromamba clean --all --yes

ARG MAMBA_DOCKERFILE_ACTIVATE=1
COPY . /opt/twpy
RUN pip install /opt/twpy
