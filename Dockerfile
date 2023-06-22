FROM mambaorg/micromamba:1.4.4

USER root

## Install git
RUN apt-get update -y && apt-get install -y wget git

## Install Python dependencies
RUN \
    micromamba install -y -n base -c bioconda -c conda-forge -c defaults \
    python=3.10.9 pyyaml=6.0 gitpython=3.1.31 \
    && micromamba clean --all --yes
ENV PATH /opt/conda/bin:$PATH

## Install Tower CLI
RUN wget -L https://github.com/seqeralabs/tower-cli/releases/download/v0.8.0/tw-linux-x86_64
RUN mv tw-linux-x86_64 tw
RUN chmod +x tw
RUN mv tw /usr/local/bin/