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
COPY . /home/$MAMBA_USER
WORKDIR /home/$MAMBA_USER
## Install Python dependencies
RUN \
    micromamba install -y -n base -f environment.yml \
    && micromamba clean --all --yes
