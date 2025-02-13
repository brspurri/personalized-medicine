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
        cmake \
        curl \
        libcairo2-dev \
        libeigen2-dev \
        libperl-dev \
        libxml2-dev \
        python-dev \
        zlib1g-dev

# apt clean and remove cached source lists
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Open Babel
RUN mkdir /openbable && \
    cd /openbable && \
    curl -L -O https://github.com/openbabel/openbabel/archive/openbabel-2-4-1.tar.gz \
    && tar xvf openbabel-2-4-1.tar.gz && \
    rm openbabel-2-4-1.tar.gz && \
    cd openbabel-openbabel-2-4-1 && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make && \
    make install

# Define default command
CMD ["babel"]

# File Author / Maintainer
MAINTAINER Carlos Borroto <carlos.borroto@gmail.com>
