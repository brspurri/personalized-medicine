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
        curl

# apt clean and remove cached source lists
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install ClustalW
RUN mkdir /clustalw && \
    cd /clustalw && \
    curl -L -O http://www.clustal.org/download/2.1/clustalw-2.1.tar.gz \
    && tar xvf clustalw-2.1.tar.gz && \
    rm clustalw-2.1.tar.gz && \
    cd clustalw-2.1 && \
    ./configure && \
    make && \
    make install

# Define default command
CMD ["clustalw2"]

# File Author / Maintainer
MAINTAINER Carlos Borroto <carlos.borroto@gmail.com>
