import os
import sys
import luigi
import shutil
import logging.handlers
from commandwrapper import WrapCommand
from collections import defaultdict

# Logging
rootlogger = logging.getLogger()
server_logger = logging.getLogger("luigi.server")


# ==========================================================================
#   Helper functions
# -------------------------------------------------------------------------
def which(c):
    for path in sys.path:
        if os.path.exists(os.path.join(path, c)):
                return os.path.join(path, c)
    return None


def average(s):
    return sum(s) * 1.0 / len(s)


# ==========================================================================
#   Start of Template Preparation Protocol
# --------------------------------------------------------------------------
class Clean(luigi.Task):
    """
    Step 1: Clean the downloaded PDB and prepare the receptor.
      - Select a single chain (this will likely change to support mutlichain.
      - Outputs a template FASTA file to be used for alignment: 2AX6_template.fasta
      - Outputs a template PDB structure: 4XXX_template.pdb
      - Outputs a copy of the downloaded input PDB with a consistent name: 4XXX.pdb
    """

    # Get the parameters from the pipeline command
    name = luigi.Parameter()
    chain = luigi.Parameter()
    working = luigi.Parameter()
    database = luigi.Parameter()
    pdb = luigi.Parameter()

    def requires(self):
        """
        No Prerequisites
        """
        return None

    def output(self):
        """
        Define the required outputs:
          - Template PDB: 4XXX_template.pdb
          - Template FASTA: 2AX6_template.fasta
        """
        output_template_pdb = os.path.join(self.working, '{}_cleaned.pdb'.format(self.name))
        output_template_fasta = os.path.join(self.working, '{}_template.fasta'.format(self.name))
        return [luigi.LocalTarget(output_template_pdb),
                luigi.LocalTarget(output_template_fasta)]

    def run(self):
        """
        Runs the pipeline step to clean and prepare the receptor.
        """

        # Cast the parameters as strings
        self.name = str(self.name)
        self.chain = str(self.chain)
        self.working = str(self.working)
        self.database = str(self.database)
        self.pdb = str(self.pdb)

        # Copy the input PDB to the working directory is needed
        if not str(self.working).endswith('/'):
            self.working = self.working + '/'
        if os.path.exists(self.pdb) and os.path.dirname(self.pdb) != os.path.dirname(self.working):
            shutil.copy2(self.pdb, self.working)

        # Docker command
        docker = which('docker')
        command = WrapCommand('{docker} run --rm '
                              '-v {working}:/inputs/ '
                              '-v {working}:/outputs/ '
                              'cleanpdb:latest '
                              '--name {name} '
                              '--input_pdb /inputs/{basename} '
                              '--chain {chain} '
                              '--output /outputs'.format(docker=docker,
                                                         working=self.working,
                                                         basename=os.path.basename(self.pdb),
                                                         name=self.name,
                                                         chain=self.chain), shell=True)
        sys.stdout.write('[TASK]: {}\n'.format(command.command))

        command.start()
        command.join()

        # Stream the output to the console and stdoutfiles
        sys.stdout.write(command.results[0])
        sys.stderr.write(command.results[1])


class Relax(luigi.Task):
    """
    Step 2: Prepacks (via relax) the cleaned receptor PDB.
      - Outputs a template PDB structure: 4XXX_template.pdb
      - Outputs a copy of the downloaded input PDB with a consistent name: 4XXX.pdb
    """

    # Get the parameters from the pipeline command
    name = luigi.Parameter()
    chain = luigi.Parameter()
    working = luigi.Parameter()
    database = luigi.Parameter()
    pdb = luigi.Parameter()
    nstruct = luigi.IntParameter()

    def requires(self):
        """
        No Prerequisites
        """
        return Clean(name=self.name,
                     chain=self.chain,
                     working=self.working,
                     database=self.database,
                     pdb=self.pdb)

    def output(self):
        """
        Define the required outputs:
          - Relaxed PDBs: [4XXX_cleaned_000n.pdb, ]
          - Relaxed scorefile: 4XXX_relax.sc
        """
        scorefile = os.path.join(self.working, 'relax', '{}_relax_score.sc'.format(self.name))
        return luigi.LocalTarget(scorefile)

    def run(self):
        """
        Runs the pipeline step to prepack the receptor.
        """

        # Cast the parameters as strings
        self.name = str(self.name)
        self.chain = str(self.chain)
        self.working = str(self.working)
        self.database = str(self.database)
        self.pdb = str(self.pdb)

        # Copy the input PDB to the working directory is needed
        if not str(self.working).endswith('/'):
            self.working = self.working + '/'
        if os.path.exists(self.pdb) and os.path.dirname(self.pdb) != os.path.dirname(self.working):
            shutil.copy2(self.pdb, self.working)

        # Docker command
        docker = which('docker')
        command = WrapCommand('{docker} run --rm '
                              '-v {working}:/inputs/ '
                              '-v {working}:/outputs/ '
                              '-v {database}:/databases/ '
                              'rosetta:3.7-relax '
                              '--input_pdb /inputs/{name}_cleaned.pdb '
                              '--output /outputs '
                              '--nstruct {nstruct}'.format(docker=docker,
                                                           working=self.working,
                                                           database=self.database,
                                                           basename=os.path.basename(self.pdb),
                                                           name=self.name,
                                                           nstruct=self.nstruct), shell=True)
        sys.stdout.write('[TASK]: {}\n'.format(command.command))
        command.start()
        command.join()

        # Stream the output to the console and stdoutfiles
        sys.stdout.write(command.results[0])
        sys.stderr.write(command.results[1])


class Template(luigi.Task):
    """
    Step 3: Chooses a template from a previously build collection of prepacked (via relax) PDBs.
      - Outputs a template PDB structure: 4XXX_template.pdb
      - Outputs a copy of the downloaded input PDB with a consistent name: 4XXX.pdb
    """

    # Get the parameters from the pipeline command
    name = luigi.Parameter()
    chain = luigi.Parameter()
    working = luigi.Parameter()
    database = luigi.Parameter()
    pdb = luigi.Parameter()
    nstruct = luigi.IntParameter()

    def requires(self):
        """
        No Prerequisites
        """
        return Relax(name=self.name,
                     chain=self.chain,
                     working=self.working,
                     database=self.database,
                     pdb=self.pdb,
                     nstruct=self.nstruct)

    def output(self):
        """
        Define the required outputs:
          - Template PDB: 4XXX_template.pdb
          - Template FASTA: 2AX6_template.fasta (from Initialization step)
        """
        template = os.path.join(self.working, '{}_template.pdb'.format(self.name))
        return luigi.LocalTarget(template)

    def run(self):
        """
        Runs the pipeline step to prepack the receptor.
        """

        # Cast the parameters as strings
        self.name = str(self.name)
        self.chain = str(self.chain)
        self.working = str(self.working)
        self.database = str(self.database)
        self.pdb = str(self.pdb)

        # Set the working directory properly
        if not str(self.working).endswith('/'):
            self.working = self.working + '/'

        # Read/parse the scorefile
        with open(self.input().path, 'r') as f_h:
            headers = []

            # Parse the individual run data
            data = defaultdict()
            for l in f_h.readlines():
                if l.lower().startswith('sequence'):
                    continue
                elif not headers:
                    headers = l.split()
                else:
                    model_data = l.split()
                    data[os.path.basename(model_data[-1])] = dict(zip(headers, model_data))

        # Total scores
        scores = [(k, v['total_score']) for k, v in data.iteritems()]
        min_score = 0.0
        min_struture = None
        for f, s in scores:
            if float(s) < min_score:
                min_score = float(s)
                min_struture = f

        # Copy the minimzed
        if min_struture:
            relax_path = os.path.join(self.working, 'relax', min_struture + '.pdb')
            template_pdb = os.path.join(self.working, '{}_template.pdb'.format(self.name))
            shutil.copy2(relax_path, template_pdb)

        pass


if __name__ == '__main__':
    luigi.run()
