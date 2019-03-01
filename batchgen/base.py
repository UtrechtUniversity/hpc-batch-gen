"""
Base module for generating batch scripts for arbitrary HPC environments.
See __main__ for the Command Line Interface (CLI)

@author: Raoul Schram
"""

import os
import configparser

from batchgen.backend.parallel import Parallel
from batchgen.backend.slurm_lisa import SlurmLisa


def _params(config=None):
    """Function to set defaults for the batch jobs.

    Returns
    -------
    dict:
        Dictionary of all parameters.
    """

    parameters = {"clock_wall_time": "01:00:00", "job_name": "asr_simulation",
                  "batch_id": 0, "run_pre_compute": "", "run_post_compute": ""}

    # If a file is supplied, read the configuration.
    if config is not None:
        for option in config["BATCH_OPTIONS"]:
            parameters[option] = config["BATCH_OPTIONS"][option]

    return parameters


def _read_script(script):
    """Function to load either a script file or list.

    Arguments
    ---------
    script: str/str
        Either a file to read, or a list of strings to use.

    Returns
    -------
        List of strings where each element is one command.
    """
    if not isinstance(script, (list,)):
        with open(script, "r") as f:
            lines = f.readlines()
    else:
        lines = script
    return lines


def generate_batch_scripts(command_file, config_file, run_pre_file,
                           run_post_file, output_dir=None):
    """Function to prepare for writing batch scripts.

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

    """

    # Get all the commands either from file, or from lists:
    script_lines = _read_script(command_file)
    run_pre_compute = _read_script(run_pre_file)
    run_post_compute = _read_script(run_post_file)

    # Merge the lists back into single strings.
    run_pre_compute = "\n".join(run_pre_compute)
    run_post_compute = "\n".join(run_post_compute)

    # Figure out the backend
    config = configparser.ConfigParser()
    config.read(config_file)
    backend = config["BACKEND"]["backend"]

    # Set the parameters from the config file.
    param = _params(config)
    param["run_pre_compute"] = run_pre_compute
    param["run_post_compute"] = run_post_compute

    # If no output directory is given, create batch.${back-end}/${job_name}/.
    if output_dir is None:
        output_dir = os.path.join("batch."+backend, param["job_name"])

    if backend == "slurm_lisa":
        batch = SlurmLisa()
    elif backend == "parallel":
        batch = Parallel()
    else:
        print("Error: no valid backend detected, supplied {cfg_file}".format(
               cfg_file=config_file))
        return 1

    batch.write_batch(script_lines, param, output_dir)
