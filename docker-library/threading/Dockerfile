# ====================================================================================
# Dockerfile
#
# Service:          Rosetta-Threading
# Base Image:       ubuntu:14.04
# Build Cmd:        docker build -t rosetta:3.7-threading .
# Run Cmd:          docker run --rm -it 
#                        -v $WORKING_DIRECTORY:/inputs 
#                        -v $WORKING_DIRECTORY:/outputs 
#                        -v $DATABASES:/databases 
#                        rosetta:3.7-threading 
#                                --fasta /inputs/2yhd_model.fasta 
#                                --alignment /inputs/2yhd_model.grishin.aln 
#                                --template /inputs/2yhd_template.pdb 
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

# Add Rosetta
RUN mkdir -p /rosetta/bin/
ADD bin/partial_thread.static.linuxgccrelease /rosetta/bin/partial_thread.static.linuxgccrelease

# Add the entry script
ADD run.py /scripts/run.py

# Set the DB env variable
ENV ROSETTA_DATABASE /databases/rosetta/

# Execute the entrypoint in the outputs folder
WORKDIR /outputs
CMD ["bash"]
#ENTRYPOINT ["python", "/scripts/run.py", "threading"]
