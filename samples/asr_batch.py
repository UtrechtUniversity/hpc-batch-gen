'''
Created on 22 Feb 2019

@author: Raoul Schram

Example script file to generate batch scripts.
'''

import sys

import pandas as pd

from batchgen import generate_batch_scripts


def pre_compute_defaults():
    '''Define default the pre-compute commands

    Returns
    -------
    str:
        List of lines to execute before computation.
    '''
    mydef = """module load eb
module load Python/3.6.1-intel-2016b

cd $HOME/asr
mkdir -p "$TMPDIR"/output
cp -r $HOME/asr/data_tmp "$TMPDIR"
cp -r $HOME/asr/hpc "$TMPDIR"
cp -r $HOME/asr/src "$TMPDIR"
cd "$TMPDIR"
""".splitlines()
    return mydef


def post_compute_defaults():
    '''Definition of post-compute commands
    Returns
    -------
    str:
        List of lines to execute after computation.
    '''
    mydef = """cp -r "$TMPDIR"/output  $HOME/asr
""".splitlines()
    return mydef


def generate_shell_script(file_data, file_params, config_file):
    '''Create commands from a parameter (CSV) file.
    Arguments
    ---------
    file_data: str
        File with data to simulate.
    file_params: str
        File with parameter grid (CSV).
    '''
    params = pd.read_csv(file_params)

    base_exec = "python3 -m asr simulate"
    script = []
    # Parse parameter table
    for row in params.itertuples():
        execute = base_exec

        if 'n_included' in params:
            execute += " --n_prior_included " + str(getattr(row, "n_included"))
        if 'query_strategy' in params:
            execute += " -q " + str(getattr(row, 'query_strategy'))

        execute += " " + file_data
        script.append(execute + "\n")

    generate_batch_scripts(script, pre_compute_defaults(),
                           post_compute_defaults(), config_file)


# If used from the command line.
if __name__ == '__main__':
    if len(sys.argv) <= 3:
        print("Error: need two arguments: simulation file, parameter file, \
               config file")
    else:
        generate_shell_script(*sys.argv[1:])
