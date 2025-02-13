#!/usr/bin/python
import os
import sys
import shutil
import subprocess
from mando import main, command


@command('threading')
def threading(fasta=None, alignment=None, template=None, output=None):

    # Basic error checking
    if not fasta:
        sys.stderr.write('Please pass --fasta parameter.\n')
    if not alignment:
        sys.stderr.write('Please pass --alignment parameter.\n')
    if not template:
        sys.stderr.write('Please pass --template parameter.\n')
    if not output:
        sys.stderr.write('Please pass --output parameter.\n')

    # Output data
    sys.stdout.write('Model Fasta: {}\n'.format(fasta))
    sys.stdout.write('Grishin Alignment: {}\n'.format(alignment))
    sys.stdout.write('Template PDB: {}\n'.format(template))
    sys.stdout.write('Output Directory: {}\n'.format(output))

    # Command
    cmd = ('/rosetta/bin/partial_thread.static.linuxgccrelease '
           '-database $ROSETTA_DATABASE '
           '-in:file:fasta {} '
           '-in:file:alignment {} '
           '-in:file:template_pdb {}'.format(fasta, alignment, template))

    # Execute
    sys.stdout.write('Command: {}\n'.format(cmd))
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for c in iter(lambda: p.stdout.read(1), ''):
        sys.stdout.write(c)

    # Complete the task
    retval = p.wait()

    # Check the output
    source = '{}.pdb'.format(template)
    filename = os.path.basename('{}.pdb'.format(os.path.splitext(fasta)[0]))
    destination = os.path.join(output, filename)
    sys.stdout.write('Moving {} to {}\n'.format(source, destination))
    if os.path.exists(source):
        shutil.move(source, destination)

if __name__ == "__main__":
    main()