import os
import sys
import shutil
from commandwrapper import WrapCommand
from mando import main, command


@command('clean-pdb')
def clean_pdb(name=None, input_pdb=None, chain=None, output=None, local=False):

    # Basic error checking
    if not name:
        sys.stderr.write('Please pass --name parameter.\n')
        exit(1)
    if not input_pdb:
        sys.stderr.write('Please pass --input_pdb parameter.\n')
        exit(1)
    if not chain:
        sys.stderr.write('Please pass --chain parameter.\n')
        exit(1)
    if not output:
        sys.stderr.write('Please pass --output parameter.\n')
        exit(1)
    else:
        if not output.endswith('/'):
            output += '/'

    # Create the output directory if it does not exist
    if not os.path.exists(output):
        os.makedirs(output)

    # Copy the input PDB to a new name convention
    name_pdb = os.path.join(os.path.dirname(input_pdb), '{}.pdb'.format(name))
    if input_pdb != name_pdb:
        shutil.copy2(input_pdb, os.path.join(os.path.dirname(input_pdb), '{}.pdb'.format(name)))
        input_pdb = name_pdb

    # Inputs
    basename = os.path.basename(os.path.splitext(input_pdb)[0])
    fasta = os.path.join(output, '{}_template.fasta'.format(basename))
    chain_pdb = os.path.join(output, '{}_{}.pdb'.format(basename, chain))
    sys.stdout.write('[Input PDB: {}\n'.format(input_pdb))
    sys.stdout.write('Input PDB Chain: {}\n'.format(chain))

    # Build the command
    basepath = '/scripts'
    if local:
        basepath = os.getcwd()
    cmd = (
        'python {clean_script} {input_pdb} {chain} {output_pdb} > {fasta}'.format(
            clean_script=os.path.join(basepath, 'clean_pdb.py'),
            input_pdb=input_pdb,
            output_pdb=chain_pdb,
            chain=chain,
            fasta=fasta
        )
    )

    # Execute the command
    sys.stdout.write('Command: {}\n'.format(cmd))
    process = WrapCommand(cmd, shell=True)
    c = process.prepareToRun()

    # Stream the output to the console and stdoutfiles
    for line in iter(c.stdout.readline, ""):
        sys.stdout.write(line)

    # Output PDB
    cleaned_pdb = '{}_cleaned.pdb'.format(os.path.splitext(input_pdb)[0], chain)
    output_pdb = os.path.join(output, os.path.basename(cleaned_pdb))
    if os.path.exists(chain_pdb):
        shutil.move(chain_pdb, output_pdb)
    sys.stdout.write('Output cleaned PDB: {}\n'.format(output_pdb))
    sys.stdout.write('Output FASTA: {}\n'.format(fasta))


if __name__ == '__main__':
    '''
    Example USAGE: python run.py clean-pdb 
        --name 1234
        --input_pdb /Volumes/Seagate/Therapeutics/pipeline_test/2yhd.downloaded.pdb
        --chain A
        --output /Volumes/Seagate/Therapeutics/pipeline_test/tmp_output
        --local
    '''
    main()
