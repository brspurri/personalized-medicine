# ====================================================================================
# Dockerfile
#
# Service:          Rosetta-LigandDocking
# Base Image:       ubuntu:14.04
# Build Cmd:        docker build -t rosetta:3.7-ligand_docking .
# Run Cmd:          docker run --rm -it
#                        -v $WORKING_DIRECTORY:/inputs
#                        -v $WORKING_DIRECTORY:/outputs
#                        -v $DATABASES:/databases
#                        rosetta:3.7-ligand_docking
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
ADD bin/rosetta_scripts.static.linuxgccrelease /rosetta/bin/rosetta_scripts.static.linuxgccrelease
ADD bin/select_best_unique_ligand_poses.static.linuxgccrelease /rosetta/bin/select_best_unique_ligand_poses.static.linuxgccrelease

# Add the entry script
ADD run.py /scripts/run.py
# COPY xml/dock.xml /scripts/xml/dock.xml
COPY xml/dock.highres.xml /scripts/xml/dock.xml
# COPY xml/dock.ligand_centric.xml /scripts/xml/dock.xml
# COPY xml/dock.protein_centric.xml /scripts/xml/dock.xml
# COPY xml/dock.3.7.xml /scripts/xml/dock.xml

# Set the DB env variable
ENV ROSETTA_DATABASE /databases/rosetta/

# Execute the entrypoint in the outputs folder
WORKDIR /working
#CMD ["bash"]
ENTRYPOINT ["python", "/scripts/run.py", "ligand-docking"]
#  --receptor_pdb /inputs/4XXX_model.pdb --ligand_pdb_starting_conformation /inputs/MyLigand2.pdb --params /inputs/MyLigand2.params --nstruct 2 --output /outputs