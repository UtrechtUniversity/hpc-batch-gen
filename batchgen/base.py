"""
Base module for generating batch scripts for arbitrary HPC environments.
See __main__ for the Command Line Interface (CLI)

@author: Raoul Schram
"""

import os
import configparser as cp
import re
from string import Template

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


def _replace_rel_abs_path(config, config_file):
    config_dir = os.path.dirname(config_file)
    config_dir_abs = os.path.abspath(config_dir)

    for key in config["BATCH_OPTIONS"]:
        if re.match(r'.+?_(dir|file)', key):
            newp = os.path.join(config_dir_abs, config["BATCH_OPTIONS"][key])
            config["BATCH_OPTIONS"][key] = newp


def _read_pre_post_file(filename):
    pre_lines = []
    post_lines = []
    cur_lines = pre_lines
    with open(filename, "r") as f:
        for cur_line in f:
            if re.match(r"## PRE_COMMANDS ##*", cur_line):
                cur_lines = pre_lines
            elif re.match(r"## POST_COMMANDS ##*", cur_line):
                cur_lines = post_lines
            else:
                cur_lines.append(cur_line)
    return (pre_lines, post_lines)


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


def generate_batch_scripts(command_file, config_file, run_pre_file="/dev/null",
                           run_post_file="/dev/null", force_clear=False):
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

    # Figure out the backend
    config = cp.ConfigParser(interpolation=cp.ExtendedInterpolation())
    config.read(config_file)
    _replace_rel_abs_path(config, config_file)

    backend = config["BACKEND"]["backend"]

    # Set the parameters from the config file.
    param = _params(config)

    # Read options for pre/post commands from config file.
    for pre_post in ["run_pre_file", "run_post_file"]:
        if pre_post in config["BATCH_OPTIONS"]:
            pp_file = config["BATCH_OPTIONS"][pre_post]
            pp_file_sub = Template(pp_file).safe_substitute(param)
            if pre_post == "run_pre_file":
                run_pre_file = pp_file_sub
            else:
                run_post_file = pp_file_sub

    if "pre_post_file" in config["BATCH_OPTIONS"]:
        pre_post_file = config["BATCH_OPTIONS"]["pre_post_file"]
        run_pre_compute, run_post_compute = _read_pre_post_file(pre_post_file)

        run_pre_compute = "".join(run_pre_compute)
        run_post_compute = "".join(run_post_compute)
    else:
        run_pre_compute = _read_script(run_pre_file)
        run_post_compute = _read_script(run_post_file)

        # Merge the lists back into single strings.
        run_pre_compute = "\n".join(run_pre_compute)
        run_post_compute = "\n".join(run_post_compute)

    # Get all the commands either from file, or from lists:
    script_lines = _read_script(command_file)

    param["run_pre_compute"] = run_pre_compute
    param["run_post_compute"] = run_post_compute

    # If no output directory is given, create batch.${back-end}/${job_name}/.
    output_dir = os.path.join("batch."+backend, param["job_name"])

    if backend == "slurm_lisa":
        batch = SlurmLisa()
    elif backend == "parallel":
        batch = Parallel()
    else:
        print("Error: no valid backend detected, supplied {cfg_file}".format(
               cfg_file=config_file))
        return 1

    batch.write_batch(script_lines, param, output_dir, force_clear)
