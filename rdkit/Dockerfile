# ====================================================================================
# Dockerfile
#
# Service:          Ligand conformation generation
# Base Image:       centos:centos7
# Build Cmd:        docker build -t rdkit .
# Run Cmd:          docker run --rm -it rdkit:latest
# docker run --rm -it -v $WORKING_DIRECTORY:/inputs/ -v $WORKING_DIRECTORY:/outputs/ rdkit:latest --unbound_receptor_model_pdb /inputs/2AX6_model.pdb --ligand_mol2 /inputs/AR_hydroxyflutamide.mol2 --output /outputs --ligand_name hydroxyflutamide

# -----------------------------------------------------------------------------------
FROM centos:centos7
MAINTAINER Brett Spurrier <brett.spurrier@gmail.com>

# Add external name servers
#RUN echo "nameserver 8.8.8.8" >> /etc/resolv.conf;
#RUN echo "nameserver 8.8.4.4" >> /etc/resolv.conf;

RUN yum update -y && yum install -y \
  wget \
  unzip \
  gcc-c++ \
  git \
  cairo \
  libXext \
  patch \
  cmake \
  bzip2 \
  pcre-devel \
  cairo \
  cairo-devel

RUN yum group install -y "Development Tools"

# conda
RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.continuum.io/miniconda/Miniconda3-4.2.12-Linux-x86_64.sh && \
    /bin/bash /Miniconda3-4.2.12-Linux-x86_64.sh -b -p /opt/conda && \
    rm Miniconda3-4.2.12-Linux-x86_64.sh

ENV PATH /opt/conda/bin:$PATH
ENV LANG C

# actually do the conda install
RUN conda config --add channels  https://conda.anaconda.org/rdkit
RUN conda install -y nomkl numpy=1.10 boost=1.56
RUN conda install -y -c conda-forge eigen

RUN mkdir /src
WORKDIR /src
ENV RDBASE=/src/rdkit
ENV RDKIT_BRANCH=Release_2016_09_1
RUN git clone https://github.com/rdkit/rdkit.git
WORKDIR $RDBASE
RUN git checkout $RDKIT_BRANCH

# need /opt/conda/lib here because that's where the boost libs are
# put /lib64 at the front to make sure we don't pick up the conda stuff
# by default
ENV LD_LIBRARY_PATH=/lib64:$RDBASE/lib:/opt/conda/lib

RUN conda create -p /opt/conda/envs/py27 -y python=2.7 nomkl numpy=1.10 pillow cairocffi pandas boost=1.56
RUN source activate /opt/conda/envs/py27 && \
    conda install -y -c conda-forge eigen

RUN mkdir $RDBASE/build
WORKDIR $RDBASE/build
RUN  CONDA_PY=2.7 cmake -DEIGEN3_INCLUDE_DIR=/opt/conda/envs/py27/include/eigen3 -DPYTHON_EXECUTABLE=/opt/conda/envs/py27/bin/python -DPYTHON_INCLUDE_DIR=/opt/conda/envs/py27/include/python2.7 -DPYTHON_LIBRARY=/opt/conda/envs/py27/lib/libpython2.7.so -DPYTHON_NUMPY_INCLUDE_PATH=/opt/conda/envs/py27/lib/python2.7/site-packages/numpy/core/include -D BOOST_ROOT=/opt/conda/envs/py27 -D Boost_NO_SYSTEM_PATHS=ON -D RDK_BUILD_AVALON_SUPPORT=ON -D RDK_BUILD_INCHI_SUPPORT=ON -DRDK_BUILD_THREADSAFE_SSS=on -DRDK_TEST_MULTITHREADED=ON -DRDK_BUILD_PYTHON_WRAPPERS=ON .. && \
  make -j2 install
ENV PYTHONPATH=$RDBASE
ENV PATH=/opt/conda/envs/py27/bin:$PATH
RUN ctest -j2 --output-on-failure

WORKDIR $RDBASE

# Install OpenBabel
ADD install/openbabel-2.4.1.tar.gz /openbabel
RUN mkdir -p /openbabel/openbabel-2.4.1/build
RUN cd /openbabel/openbabel-2.4.1/build
WORKDIR /openbabel/openbabel-2.4.1/build
RUN cmake ../
RUN make
RUN make install

# Install LigSIFT
RUN mkdir -p /ligsift/
ADD install/ligsift-v1.3.tar.gz /ligsift
#RUN tar zxvf /ligsift/ligsift-v1.3.tar.gz

# Add the chain rename script
ADD tools/renamechain.pl /scripts/renamechain.pl

# Copy Rosetta molfile_to_params.py
COPY mol2params/ /scripts/mol2params/

# Add the dev libraries
RUN pip install mando
RUN mkdir -p /scripts
ADD run.py /scripts/run.py

RUN mkdir /inputs
RUN mkdir /outputs

#WORKDIR /working
#MD ["bash"]
# generate-conformers --unbound_receptor_model_pdb /inputs/2AX6_model.pdb --ligand_mol2 /inputs/AR_hydroxyflutamide.mol2 --output /outputs --ligand_name hydroxyflutamide
ENTRYPOINT ["/opt/conda/envs/py27/bin/python", "/scripts/run.py", "generate-conformers"]





