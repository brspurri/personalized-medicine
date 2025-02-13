#!/usr/bin/python
import os
import sys
import shutil
import subprocess
from mando import main, command


@command('ligand-docking')
def ligand_docking(name=None,
                   complex_starting_conformation=None,
                   params=None,
                   nstruct=10,
                   runs=3,
                   output=None,
                   overwrite=False):

    # Basic error checking
    if not name:
        sys.stderr.write('Please pass --name parameter.\n')
        sys.exit(1)
    if not complex_starting_conformation:
        sys.stderr.write('Please pass --complex_starting_conformation parameter.\n')
        sys.exit(1)
    if not params:
        sys.stderr.write('Please pass --params parameter.\n')
        sys.exit(1)
    if not output:
        sys.stderr.write('Please pass --output parameter.\n')
    else:
        if not output.endswith('/'):
            output += '/'

    # Copy complex to tmp for RMSD calculations
    shutil.copy2(complex_starting_conformation, '/tmp/crystal_complex.pdb')

    # Output data
    basename = os.path.basename(complex_starting_conformation.replace('_starting_complex.pdb', ''))
    sys.stdout.write('Complex PDB: {}\n'.format(complex_starting_conformation))
    sys.stdout.write('Output basename {}\n'.format(basename))
    sys.stdout.write('Output Directory: {}\n'.format(output))

    # Prepare the run(s)
    for n in range(runs):
        output_directory_run = os.path.join(output, str(n))
        if not output_directory_run.endswith('/'):
            output_directory_run += '/'
        if not os.path.exists(output_directory_run):
            os.makedirs(output_directory_run)
        scorefile = os.path.join(output_directory_run, '{}_{}.sc'.format(name, str(n)))
        silentfile = os.path.join(output_directory_run, '{}_{}.silent'.format(name, str(n)))
        sys.stdout.write('Scorefile: {}\n'.format(scorefile))
        sys.stdout.write('Silentfile: {}\n'.format(silentfile))

        # Comand
        cmd = ('/rosetta/bin/rosetta_scripts.static.linuxgccrelease '
               '-database $ROSETTA_DATABASE '
               '-in:file:s {complex_file} '
               '-in:file:extra_res_fa {params} '
               '-nstruct {nstruct} '
               '-parser:protocol /scripts/xml/dock.xml '
               '-packing:ex1 -packing:ex2 '
               '-no_optH false '
               '-flip_HNQ true '
               '-ignore_ligand_chi true '
               '-out:prefix {output_directory_run} '
               '-out:file:scorefile {scorefile} '
               '-out:file:silent {silentfile} '
               '-out:file:fullatom '
               '-run:use_time_as_seed true '
               '-mistakes:restore_pre_talaris_2013_behavior true'.format(complex_file=complex_starting_conformation,
                                                                         params=params,
                                                                         nstruct=nstruct,
                                                                         output_directory_run=output_directory_run,
                                                                         scorefile=scorefile,
                                                                         silentfile=silentfile))
        if overwrite:
            cmd += ' -overwrite'

        # Execute
        sys.stdout.write('Command: {}\n'.format(cmd))
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for c in iter(lambda: p.stdout.read(1), ''):
            sys.stdout.write(c)
        p.wait()

        # Build the scoring select file
        selected_silentfile = os.path.basename(os.path.join(output, '{}_{}.selected.silent'.format(name, str(n))))
        score_cmd = ('/rosetta/bin/select_best_unique_ligand_poses.static.linuxgccrelease '
                     '-database $ROSETTA_DATABASE '
                     '-extra_res_fa {params} '
                     '-docking:ligand:max_poses 10 '
                     '-docking:ligand:min_rms 1.0 '
                     '-out:pdb '
                     '-in:file:silent {silentfile} '
                     '-out::file::silent {selected_silentfile}'.format(params=params,
                                                                       output=output,
                                                                       silentfile=silentfile,
                                                                       selected_silentfile=selected_silentfile))

        # Execute
        sys.stdout.write('Command: {}\n'.format(cmd))
        ps = subprocess.Popen(score_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for c in iter(lambda: ps.stdout.read(1), ''):
            sys.stdout.write(c)
        ps.wait()

    # Complete the task
    sys.exit(0)


if __name__ == "__main__":
    main()
