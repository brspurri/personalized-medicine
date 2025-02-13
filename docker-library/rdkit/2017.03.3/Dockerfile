# Source Image
FROM ubuntu:16.04

# Set noninterative mode
ENV DEBIAN_FRONTEND noninteractive

# apt update and install global requirements
RUN apt-get clean all && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y  \
        build-essential \
        curl \
        python-numpy \
        cmake \
        python-dev \
        sqlite3 \
        libsqlite3-dev \
        libboost-dev \
        libboost-system-dev \
        libboost-thread-dev \
        libboost-serialization-dev \
        libboost-python-dev \
        libboost-regex-dev

# apt clean and remove cached source lists
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install RDKit
RUN mkdir /rdkit && \
    cd /rdkit && \
    curl -L -O https://github.com/rdkit/rdkit/archive/Release_2017_03_3.tar.gz \
    && tar xvf Release_2017_03_3.tar.gz && \
    rm Release_2017_03_3.tar.gz && \
    cd rdkit-Release_2017_03_3/ && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make && \
    make install
ENV RDBASE=/rdkit/rdkit-Release_2017_03_3
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$RDBASE/lib
ENV PYTHONPATH=$PYTHONPATH:$RDBASE

# File Author / Maintainer
MAINTAINER Carlos Borroto <carlos.borroto@gmail.com>
