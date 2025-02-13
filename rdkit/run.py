import os
import sys
import shutil
import glob
import subprocess

sys.path.append("/src/rdkit")

from mando import command, main
from rdkit import Chem
from rdkit.Chem import AllChem


@command('generate-conformers')
def generate(unbound_receptor_model_pdb=None,
             ligand_mol2=None,
             ligand_name=None,
             water_pdb=None,
             output=None,
             nconf=20):
    """
    Generates multiple conformations of a smiles ligand.
    
    Args:
        unbound_receptor_model_pdb: Receptor (model) pdb.    
        ligand_mol2: Extracted and refined PDB structure of the ligand.    
        ligand_name: Ligand name.
        water_pdb: PDB of water coordinates.
        nconf: Number of ligand conformations to create. Bigger moleduels should have more.
        output: Output directory.
        
    """

    if not unbound_receptor_model_pdb:
        sys.stderr.write('Please pass --unbound_receptor_model_pdb parameter.\n')
        sys.exit(1)
    if not ligand_mol2:
        sys.stderr.write('Please pass --ligand_mol2 parameter.\n')
        sys.exit(1)
    if not ligand_name:
        sys.stderr.write('Please pass --ligand_name parameter.\n')
        sys.exit(1)
    if not output:
        sys.stderr.write('Please pass --output parameter.\n')
        sys.exit(1)
    else:
        if not output.endswith('/'):
            output += '/'

    if not os.path.exists(output):
        os.makedirs(output)

    if not os.path.exists(os.path.join(output, ligand_name)):
        os.makedirs(os.path.join(output, ligand_name))

    # Set the output conformation file name
    output_combined_conformations = os.path.join(output, ligand_name + '_conformations.sdf')

    # Parse the receptor name
    receptor_name = os.path.basename(unbound_receptor_model_pdb)[0:4]

    # Build the structure and generate conformations
    m = Chem.MolFromMol2File(ligand_mol2)
    m3 = Chem.AddHs(m)

    # Energy minimize all the conformations
    cids = AllChem.EmbedMultipleConfs(m3, nconf, AllChem.ETKDG())

    # Superimpose all conformations
    rmslist = []
    AllChem.AlignMolConformers(m3, RMSlist=rmslist)

    # Output all the conformation as PDBs
    cmds = []
    sdfs = []
    for cid in cids:
        conf = m3.GetConformer(cid).GetOwningMol()

        # Write the unaligned conformation
        unaligned_conf_pdb = os.path.join(output, ligand_name, '{}_{}.pdb'.format(ligand_name, cid))
        w_h = Chem.PDBWriter(unaligned_conf_pdb)
        w_h.write(conf, cid)
        w_h.close()

        # Convert the PDB to MOL2
        unaligned_conf_mol2 = os.path.join(output, ligand_name, '{}_unaligned_{}.mol2'.format(ligand_name, cid))
        cmds.append('babel -i pdb {} -o mol2 {}'.format(unaligned_conf_pdb, unaligned_conf_mol2))

        # Align the (unaligned) MOL2 to the reference (input) MOL2
        aligned_conf_score = os.path.join(output, ligand_name, '{}_aligned_{}.score'.format(ligand_name, cid))
        aligned_conf_mol2 = os.path.join(output, ligand_name, '{}_aligned_{}.mol2'.format(ligand_name, cid))
        cmds.append('/ligsift/LIGSIFT -q {} -db {} -o {} -s {}'.format(
            ligand_mol2, unaligned_conf_mol2, aligned_conf_score, aligned_conf_mol2))

        # Convert the aligned MOL2 back to PDB
        aligned_conf_pdb = os.path.join(output, ligand_name, '{}_aligned_{}.pdb'.format(ligand_name, cid))
        cmds.append('babel -i mol2 {} -o pdb {}'.format(aligned_conf_mol2, aligned_conf_pdb))
        cmds.append('/opt/conda/envs/py27/bin/python /scripts/run.py rename-chain {}'.format(aligned_conf_pdb))
        cmds.append('/opt/conda/envs/py27/bin/python /scripts/run.py clean-output {}'.format(aligned_conf_pdb))

        # Convert the aligned PDB to SDF
        aligned_conf_sdf = os.path.join(output, ligand_name, '{}_aligned_{}.sdf'.format(ligand_name, cid))
        cmds.append('babel -i pdb {} -o sdf {}'.format(aligned_conf_pdb, aligned_conf_sdf))
        sdfs.append(aligned_conf_sdf)

        # Build the starting complex
        aligned_complex_pdb = os.path.join(output, ligand_name, '{}_complex_{}.pdb'.format(ligand_name, cid))
        if water_pdb:
            cmds.append('cat {} {} {} > {}'.format(
                unbound_receptor_model_pdb, water_pdb, aligned_conf_pdb, aligned_complex_pdb))
        else:
            cmds.append('cat {} {} > {}'.format(
                unbound_receptor_model_pdb, aligned_conf_pdb, aligned_complex_pdb))

    # Create single confomation file
    cmds.append('rm {}; cat {} > {}'.format(output_combined_conformations, ' '.join(sdfs),
                                            output_combined_conformations))

    # Build the mol2param command (this container only)
    pc = ('/opt/conda/envs/py27/bin/python '
          '/scripts/mol2params/molfile_to_params.py '
          '-p {name} '
          '--clobber '
          '--conformers-in-one-file {input} '.format(name=os.path.join(output, ligand_name),
                                                     input=output_combined_conformations))
    cmds.append(pc)

    # Execute
    for c in cmds:
        print c
    subprocess_cmd('; '.join(cmds))

    # Organize the outputs
    ligand_output = os.path.join(output, ligand_name)
    starting_complex = os.path.join(output, '{}_{}_starting_complex.pdb'.format(receptor_name, ligand_name))
    for f in glob.glob(os.path.join(ligand_output, '{}_complex_0.pdb'.format(ligand_name))):
        shutil.move(f, starting_complex)


@command('rename-chain')
def rename_chain(pdb, chain='X'):
    remapped_lines = []
    with open(pdb, 'r') as f_h:
        for l in f_h.readlines():
            if l.startswith('ATOM '):
                ll = list(l)
                ll[21] = chain
                l = ''.join(ll)
                l = l.replace('ATOM  ', 'HETATM').replace('UNL', 'LG1')
            remapped_lines.append(l)
    with open(pdb, 'w') as w_h:
        w_h.writelines(remapped_lines)


@command('clean-output')
def clean_output(pdb):
    remapped_lines = []
    with open(pdb, 'r') as f_h:
        for l in f_h.readlines():
            if l.startswith('ATOM ') or l.startswith('HETATM ') or l.startswith('TER '):
                remapped_lines.append(l)
    with open(pdb, 'w') as w_h:
        w_h.writelines(remapped_lines)


def subprocess_cmd(c):
    sys.stdout.write(c + '\n')
    process = subprocess.Popen(c, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    proc_stdout = process.communicate()[0].strip()
    sys.stdout.write(proc_stdout)


def clean(l):
    for f in l:
        os.remove(f)

if __name__ == '__main__':
    main()
