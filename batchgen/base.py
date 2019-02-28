'''
Created on 20 Feb 2019

@author: Raoul Schram

Script file to generate batch scripts with any backend.
'''

import os
import configparser

import batchgen.backend.parallel as parallel
import batchgen.backend.slurm_lisa as slurm_lisa


def _params(config=None):
    '''Function to set defaults for the batch jobs.

    Returns
    -------
    dict:
        Dictionary of all parameters.
    '''

    parameters = {'clock_wall_time': "01:00:00", 'job_name': 'asr_simulation',
                  "batch_id": 0, 'run_pre_compute': "", 'run_post_compute': ""}

    # If a file is supplied, read the configuration.
    if config is not None:
        for option in config["BATCH_OPTIONS"]:
            parameters[option] = config["BATCH_OPTIONS"][option]
#     sys.exit()
#         with open(file, "r") as f:
#             for line in f:
#                 (key, val) = line.split()
#                 defaults[key] = val
    return parameters


def _read_script(script):
    '''Function to load either a script file or list.

    Arguments
    ---------
    script: str/str
        Either a file to read, or a list of strings to use.

    Returns
    -------
        List of strings where each element is one command.
    '''
    if not isinstance(script, (list,)):
        with open(script, "r") as f:
            lines = f.readlines()
    else:
        lines = script
    return lines


def print_execution(exec_script):
    print("""
******************************************************
** Execute the following on the command line (bash) **
******************************************************

{exec_script}
""".format(exec_script=exec_script))


def generate_batch_scripts(input_script, run_pre_file, run_post_file,
                           cfg_file, output_dir=None):
    '''Function to prepare for writing batch scripts.

    Arguments
    ---------
    input_script: str/str
        Either filename for commands to run, or list of strings with commands.
    run_pre_file: str/str
        Same for commands executed for every batch (before main execution).
    run_post_file: str/str
        Same, but after main execution.
    output_dir: str
        Output directory for batch jobs.

    '''

    # Get all the commands either from file, or from lists:
    script_lines = _read_script(input_script)
    run_pre_compute = _read_script(run_pre_file)
    run_post_compute = _read_script(run_post_file)

    # Merge the lists back into single strings.
    run_pre_compute = "\n".join(run_pre_compute)
    run_post_compute = "\n".join(run_post_compute)

    # Figure out the backend
    config = configparser.ConfigParser()
    config.read(cfg_file)
    backend = config['BACKEND']['backend']

    # Set the parameters from the config file.
    param = _params(config)
    param['run_pre_compute'] = run_pre_compute
    param['run_post_compute'] = run_post_compute

    # If no output directory is given, create batch.${back-end}/${job_name}/.
    if output_dir is None:
        output_dir = os.path.join("batch."+backend, param['job_name'])

    if backend == "slurm_lisa":
        exec_script = slurm_lisa.write_batch_scripts(script_lines, param,
                                                     output_dir)
    elif backend == "parallel":
        exec_script = parallel.write_batch_scripts(script_lines, param,
                                                   output_dir)

    else:
        print("Error: no valid backend detected, supplied {cfg_file}".format(
               cfg_file=cfg_file))
        return 1

    print_execution(exec_script)
