# Source Image
FROM us.gcr.io/personalized-therapeutics/openbabel:2.4.1

# Set noninterative mode
ENV DEBIAN_FRONTEND noninteractive

# apt update and install global requirements
RUN apt-get clean all && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y  \
        git

# apt clean and remove cached source lists
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install LIGSIFT
RUN git clone https://github.com/ambrishroy/LIGSIFT.git
RUN cd LIGSIFT && \
    sed -i 's"/home/ambrish/bin/openbabel"/usr/local"g' Makefile && \
    make && \
    cp LIGSIFT /usr/local/bin

# Define default command
CMD ["LIGSIFT"]

# File Author / Maintainer
MAINTAINER Carlos Borroto <carlos.borroto@gmail.com>
