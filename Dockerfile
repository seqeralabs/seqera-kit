FROM mambaorg/micromamba:1.4.4

USER root

## Install git
RUN apt-get update -y && apt-get install -y git

## Install dependencies with mamba
USER $MAMBA_USER
COPY . /home/$MAMBA_USER
WORKDIR /home/$MAMBA_USER

RUN \
    micromamba install -y -n base -f environment.yml \
    && micromamba clean --all --yes

ENV PATH="$PATH:/opt/conda/bin"