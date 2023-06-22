FROM mambaorg/micromamba:1.4.4

USER root

## Install tw CLI
RUN \
    apt-get update -y && apt-get install -y wget \
    && wget -L https://github.com/seqeralabs/tower-cli/releases/download/v0.8.0/tw-linux-x86_64 \
    && mv tw-linux-x86_64 tw \
    && chmod +x tw \
    && mv tw /usr/local/bin/

## Install Python dependencies
USER $MAMBA_USER
COPY . /home/$MAMBA_USER
WORKDIR /home/$MAMBA_USER

RUN \
    micromamba install -y -n base -c bioconda -c conda-forge -c defaults \
    python=3.10.9 pyyaml=6.0 \
    && micromamba clean --all --yes
