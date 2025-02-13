# ====================================================================================
# Dockerfile
#
# Service:          Clean PDB
# Base Image:       ubuntu:16.04
# Build Cmd:        docker build -t cleanpdb .
# Run Cmd:          docker run --rm -it cleanpdb
#   docker run --rm -it -v $WORKING_DIRECTORY:/inputs/ -v $WORKING_DIRECTORY:/outputs/ cleanpdb:latest python /scripts/run.py clean-pdb--name 1234 --input_pdb /inputs/2yhd.downloaded.pdb --chain A --output /outputs
# Run Exec:
#   python run.py clean-pdb --input_pdb /inputs/2yhd.downloaded.pdb --chain A --output /outputs/ --name 1234
# -----------------------------------------------------------------------------------
# Source Image
FROM ubuntu:16.04

# Set noninterative mode
ENV DEBIAN_FRONTEND noninteractive

# apt update and install global requirements
RUN apt-get clean all && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y  \
        python-pip

# apt clean and remove cached source lists
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install python packages
RUN pip install mando commandwrapper

# Add the clean pdb script(s)
RUN mkdir -p /scripts
COPY scripts/clean_pdb.py /scripts/clean_pdb.py
COPY scripts/amino_acids.py /scripts/amino_acids.py
COPY run.py /scripts/run.py

WORKDIR /scripts

CMD ["python", "/scripts/run.py", "clean-pdb"]

MAINTAINER Brett Spurrier <brett.spurrier@gmail.com>

