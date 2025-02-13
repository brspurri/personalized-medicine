
### Pipeline Flow
![alt text](screenshots/pipeline_flow.png?raw=true "Title")


Environment Setup
-----------------

There are several steps to get this setup. This can likely be very streamlined, but I don't know how often this will be needed. The steps below should be cut-and-paste worthy.

#### Download place the Pipeline Tools in their correct location for building Docker images.

1. Clone this repo: `git clone https://github.com/brspurri/personalized-therapeutics.git`

2. Change into the project directory: `cd personalized-therapeutics`

3. [Download the pipeline tools](https://drive.google.com/file/d/0B-3-AEb8cEhdaHhkRnAyTEJzNDA/view?usp=sharing "Pipeline Tools") (254 MB)

4. Extract tools to a temporary directory: `tar zxvf pipeline_tools.tar.gz -C /tmp`

5. Copy the individual tools to their respective component hierarchy:
  - **Rosetta Scripts** Linux binary: `mkdir -p docking/bin && mv /tmp/pipeline_tools/rosetta_scripts.static.linuxgccrelease docking/bin/rosetta_scripts.static.linuxgccrelease`
  - **Rosetta Unique Selection** Linux binary: `mv /tmp/pipeline_tools/select_best_unique_ligand_poses.static.linuxgccrelease docking/bin/select_best_unique_ligand_poses.static.linuxgccrelease`
  - **LigSIFT** source code: `mkdir -p rdkit/install && mv /tmp/pipeline_tools/ligsift-v1.3.tar.gz rdkit/install/ligsift-v1.3.tar.gz`
  - **OpenBABEL** source code: `mv /tmp/pipeline_tools/openbabel-2.4.1.tar.gz rdkit/install/openbabel-2.4.1.tar.gz`
  - **Rosetta Minimize** Linux binary: `mkdir -p relax/bin && mv /tmp/pipeline_tools/minimize_with_cst.static.linuxgccrelease  relax/bin/minimize_with_cst.static.linuxgccrelease`
  - **Rosetta Relax** Linux binary: `mv /tmp/pipeline_tools/relax.static.linuxgccrelease  relax/bin/relax.static.linuxgccrelease`
  - **Rosetta Threading (Standard)** Linux binary: `mkdir -p threading/bin && mv /tmp/pipeline_tools/minirosetta.static.linuxgccrelease  threading/bin/minirosetta.static.linuxgccrelease`
  - **Rosetta Threading (Partial)** Linux binary: `mv /tmp/pipeline_tools/partial_thread.static.linuxgccrelease  threading/bin/partial_thread.static.linuxgccrelease`
  
6. [Download the Rosetta Database](https://drive.google.com/file/d/0B-3-AEb8cEhdREs5b1FmTVhOeGs/view?usp=sharing "Rosetta 3.7 Database") (672 MB)
  -  Extract and put the database in any folder you like. The path will be passed as a command line parameter to the pipeline.
  
#### Build the docker files

-  `cd clean; docker build -t cleanpdb:latest . ; cd ..`
-  `cd docker-library/clustalw/2.1; docker build -t clustalw:latest . ; cd ../../..`
-  `cd docking; docker build -t rosetta-docking:latest . ; cd ..`
-  `cd rdkit; docker build -t rdkit:latest . ; cd ..` (this one takes a while)
-  `cd relax; docker build -t rosetta-relax:latest . ; cd ..`
-  `cd threading; docker build -t rosetta-threading:latest . ; cd ..`

#### Install the Python Dependencies

-  `pip install -r requirements.txt` into a Python 2.7.x environment of your choice.

Prepare the Target Receptor
===========================

#### Clean a PDB and create a fasta from the template

```
python pipeline_stage1.py Clean \
    --local-scheduler \
    --name 1XXX \
    --working ~/path/to/ \
    --database ~/databases/ \
    --pdb ~/structures/ABCD.downloaded.pdb \
    --chain A
```

Where

-  `local-scheduler`: a needed **Luigi** execution parameter.
-  `name`: a unique identifier for the run. Unfortunately, this **needs to be a 4 digit alphanumerical currently**:
-  `working`: the working directory of the host machine. This directory is mapped to each container's `/input` **and** `/output` folders.
-  `database`: Path to the Rosetta database.
-  `pdb`: A starting, uncleaned, (usually) downloaded PDB template for the target being investigated. Does **not** need to be exact, but **does** need to be in the same family as the target being investigated.
-  `chain`: Currently, only single chain PDBs are supported. This will change if this project goes forward.

Expected Outputs:

- `ABCD_template.fasta`
- `ABCD_template.pdb`

#### Example:

Download the [example EGFR structure](https://drive.google.com/file/d/0B-3-AEb8cEhdOHY0R25xNEppbGM/view?usp=sharing). Save it to **~/downloaded_structures/3BBT.pdb** (or anywhere, just note the location is passed to the `--pdb` flag below. This is an uncleaned, unminimized, often very messy input. The **Phase 1** protocol will clean this template and prepare it for use in **Phase 2**. This only needs to be done once per each target protein.

```
python pipeline_stage1.py Clean \
    --local-scheduler \
    --name 3BBT \
    --working ~/testing/ \
    --database ~/rosetta_database/ \
    --pdb ~/downloaded_structures/3BBT.pdb \
    --chain B
```

Your outputs will be located in your working directory:
-  **3BBT.pdb**: The original input file.
-  **3BBT_cleaned.pdb**: A cleaned form of the input file.
-  **3BBT_template.fasta**: A Fasta sequence file corresponding to **chain B** of the input protein.

**NOTE**: There is an optional "Relax" step that needs to go here, however, it needs a little more work, so I'll document it when complete. To bypass the relax step for now, simply rename the "cleaned" file to a "template" by:

-  `mv 3BBT_cleaned.pdb 3BBT_template.pdb`

Run the "Personalized" Ligand/Target Simulations
================================================


```
python pipeline_stage2.py Scoring \
    --local-scheduler \
    --name 4XXX \
    --working /path/to/ \
    --database ~/databases/ \
    --FastaAlignment-model-sequence <FULL_PROTEIN_SEQUENCE_CONTAINING_MUTATIONS \
    --Ligand-ligand-template-mol2 ~/ligand.mol2 \
    --ligand-name MyLigand \
    --Docking-nstruct 1000 \
    --runs 1 \
    --Ligand-water-pdb ~/ABCD_waters.pdb

```

Where

-  `local-scheduler`: a needed **Luigi** execution parameter.
-  `name`: a unique identifier for the run. Unfortunately, this **needs to be a 4 digit alphanumerical currently**:
-  `working`: the working directory of the host machine. This directory is mapped to each container's `/input` **and** `/output` folders.
-  `database`: Path to the Rosetta database.
-  `FastaAlignment-model-sequence`: This is the **full protein sequence to be threaded over the template structure. So it should contain all the "personalized" mutations.** And yeah, this is a long input parameter.
-  `Ligand-ligand-template-mol2`: Mol2 file representing the 2D ligand. Can be obtained from PubChem. Can also be converted from PDF using Molsoft ICM or other software.
-  `ligand-name`: Custom ligand name. No restrictions.
-  `Docking-nstruct`: Number of docking simulations to perform within the sample space. For testing, set this low (ie., 5). For a real experiment, set it greater than 1000.
-  `runs`: Number of runs to repeat. Not necessary, but will allow for future error bars. I don't believe `Scoring` step utilizes this yet, so best to leave it at `1` for now.
-  `Ligand-water-pdb`: (Optional) PDB of water coordinates. Inclusion of water coordinates have been show to increase accuracy for hydrophilic binding pockets. These coordinates will come from the downloaded PDB but need to manually nb put into their own coordinate file.


Expected Outputs:

- `4XXX.sc` Output score file for all similations.
- A PDB for each simulated docked complex.


#### Example:

1.  Download the [water coordinates](https://drive.google.com/open?id=0B-3-AEb8cEhdb0pQckk4ZUhHYVU) for the example EGFR structure. Save it to **~/downloaded_structures/3BBT_water.pdb** (or anywhere, just note the location is passed to the `--Ligand-water-pdb` flag below. These coordinates are obtained manually for now. I am looking into automating this process in **Phase 1**. 

2.  Download the [ligand definition](https://drive.google.com/open?id=0B-3-AEb8cEhdSHlHQmtkX2FnREk) for the **Lapatinib** ligand in which this simulation will bind to the EGFR receptor. Save it to **~/downloaded_structures/lapatinib.mol2** (or anywhere, just note the location is passed to the `--Ligand-ligand-template-mol2` flag below. 

3.  **Mapping the mutations to the FASTA file is a manual step currently.** I'm looking into automating this, but for now, perform the following commands:

  ```
  $ cat ~/testing/3BBT_template.fasta
  >3BBT_template
  AQLRILKETELKRVKVLGSGAFGTVYKGIWVPEGETVKIPVAIKILNEGPKANVEFMDEALIMASMDHPHLVRLLGVCLSPTIQLVTQLMPHGCLLEYVHEHKDNIGSQLLLNWCVQIAKGMMYLEERRLVHRDLAARNVLVKSPNHVKITDFGLARLLPIKWMALECIHYRKFTHQSDVWSYGVTIWELMTFGGKPYDGIPTREIPDLLEKGERLPQPPICTIDVYMVMVKCWMIDADSRPKFKELAAEFSRMARDPQRYLVIQDDRMKLPSP
  ```

  Note the location where the new amino acid changes will occur, and manually edit the fasta file to reflect the changes. More than amino acid mutation can be modelled here as well. Indels are **not yet** supported. For example, the mutation `K44F` would look like: VAI**K**ILN -> VAI**F**ILN. This entire sequence string (containing the amino acid mutations) is passed as an input parameter in the **Phase 2** command.

4. Run the Python **Phase 2** command. This will execute the docking simulation pipeline.

	```
	python pipeline_stage2.py Scoring \
    	--local-scheduler \
    	--name 3BBT \
    	--working ~/testing/ \
    	--database ~/rosetta_database/ \
    	--FastaAlignment-model-sequence AQLRILKETELKRVKVLGSGAFGTVYKGIWVPEGETVKIPVAIFILNEGPKANVEFMDEALIMASMDHPHLVRLLGVCLSPTIQLVTQLMPHGCLLEYVHEHKDNIGSQLLLNWCVQIAKGMMYLEERRLVHRDLAARNVLVKSPNHVKITDFGLARLLPIKWMALECIHYRKFTHQSDVWSYGVTIWELMTFGGKPYDGIPTREIPDLLEKGERLPQPPICTIDVYMVMVKCWMIDADSRPKFKELAAEFSRMARDPQRYLVIQDDRMKLPSP \
    	--Ligand-ligand-template-mol2 ~/downloaded_structures/lapatinib.mol2 \
    	--ligand-name Lapatinib \
    	--Docking-nstruct 15 \
    	--runs 1 \
    	--Ligand-water-pdb ~/downloaded_structures/3BBT_waters.pdb
	```

	NOTE: A in a **real** simulation, you should use `-Docking-nstruct 1000` or higher.