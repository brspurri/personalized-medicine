# ====================================================================================
# Dockerfile
#
# Service:          Rosetta-Relax
# Base Image:       ubuntu:14.04
# Build Cmd:        docker build -t rosetta:3.7-relax .
# Run Cmd:          docker run --rm -it 
#                        -v $WORKING_DIRECTORY:/inputs 
#                        -v $WORKING_DIRECTORY:/outputs 
#                        -v $DATABASES:/databases 
#                        rosetta:3.7-relax
#                                --input_pdb /inputs/2yhd.pdb
#                                --nstruct 100
#                                --output /outputs 
#
# -----------------------------------------------------------------------------------
FROM python:2.7.13

MAINTAINER Brett Spurrier <brett.spurrier@gmail.com>

# Add external name servers
#RUN echo "nameserver 8.8.8.8" >> /etc/resolv.conf;
#RUN echo "nameserver 8.8.4.4" >> /etc/resolv.conf;

# Python package(s) install
RUN pip install mando

# Create a working directory
RUN mkdir -p /working

# Add Rosetta (minimize_with_cst) application
RUN mkdir -p /rosetta/bin/
RUN wget https://storage.googleapis.com/personalized-therapeutics/binaries/rosetta-3.7/relax/relax.static.linuxgccrelease -P /rosetta/bin/
RUN chmod +x /rosetta/bin/relax.static.linuxgccrelease

# Add the entry script
ADD run.py /scripts/run.py

# Set the DB env variable
ENV ROSETTA_DATABASE /databases/rosetta/

# Execute the entrypoint in the outputs folder
WORKDIR /working
CMD ["bash"]
# ENTRYPOINT ["python", "/scripts/run.py", "relax"]
