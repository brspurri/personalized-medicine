import os
import sys
import subprocess
import shutil
from mando import main, command


@command('relax')
def relax(input_pdb=None, output=None):
    """
    Runs the Rosetta Suite Relax to prepare the receptor structure.
    Prereqs: the input_pdb must be cleaned.

    :param input_pdb: Cleaned PDB structure.
    :param output: Output directory.
    """

    # Basic error checking
    if not input_pdb:
        sys.stderr.write('Please pass --input_pdb parameter.\n')
    if not output:
        sys.stderr.write('Please pass --output parameter.\n')
    else:
        if not output.endswith('/'):
            output += '/'

    # Output data
    name = os.path.splitext(os.path.basename(input_pdb))[0]
    logfile = os.path.join(output, name + '.log')
    intermediate_pdb = os.path.join(output, name + '_0001.pdb')
    output_pdb = os.path.join(output, name.replace('cleaned', 'template') + '.pdb')
    sys.stdout.write('Input PDB: {}\n'.format(input_pdb))
    sys.stdout.write('Output PDB {}\n'.format(output_pdb))

    # Command
    cmd = ('/rosetta/bin/relax.static.linuxgccrelease '
           '-database $ROSETTA_DATABASE '
           '-relax:constrain_relax_to_start_coords '
           '-relax:coord_constrain_sidechains '
           '-relax:ramp_constraints false '
           '-s {input_pdb} '
           '-ex1 '
           '-ex2 '
           '-use_input_sc '
           '-flip_HNQ '
           '-no_optH false '
           '-out:prefix {output} '
           '--overwrite '.format(input_pdb=input_pdb,
                                 output=output))

    # Execute
    sys.stdout.write('Command: {}\n'.format(cmd))
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    with open(logfile, 'w') as w_h:
        for c in iter(lambda: p.stdout.read(1), ''):
            sys.stdout.write(c)
            w_h.write(c)
            w_h.flush()

    # Complete the task
    p.wait()
    shutil.move(intermediate_pdb, output_pdb)
    sys.stdout.write('Completed Rosetta Relax\n')


if __name__ == "__main__":
    """
    Usage: python /scripts/run.py relax --input_pdb /inputs/4XXX_cleaned.pdb --output /outputs/
      Input: /inputs/4XXX_cleaned.pdb
      Expected Output: /outputs/4XXX_template.pdb
    """
    main()
