"""
Base module for generating batch scripts for arbitrary HPC environments.
See __main__ for the Command Line Interface (CLI)

@author: Raoul Schram
"""

import os
import configparser as cp
import re

from batchgen.backend.parallel import Parallel
from batchgen.backend.slurm_lisa import SlurmLisa
from batchgen.ssh import send_batch_ssh
from batchgen.util import _read_script, _check_files, batch_dir


def _params(config=None):
    """Function to set defaults for the batch jobs.

    Returns
    -------
    dict:
        Dictionary of all parameters.
    """

    parameters = {"clock_wall_time": "01:00:00", "job_name": "asr_simulation",
                  "batch_id": 0, "run_pre_compute": "", "run_post_compute": "",
                  "send_mail": "False"
                  }

    # If a file is supplied, read the configuration.
    if config is not None:
        parameters.update(dict(config.items("BATCH_OPTIONS")))

    return parameters


def _replace_rel_abs_path(config, config_file):
    """ Variables in the config file ending with dir|file
        are replaced with an absolute file path.

    Arguments
    ---------
    config: configparser
        Configuration read from a .ini file.
    config_file: str
        Path to the configuration file (can be relative).
    """
    config_dir = os.path.dirname(config_file)
    config_dir_abs = os.path.abspath(config_dir)

    for key in config.options("BATCH_OPTIONS"):
        dir_file = config.get("BATCH_OPTIONS", key)
        is_dir_file = (re.match(r'.+?_(dir|file)', dir_file) is not None)
        start_w_dollar = (re.match(r'^\$', dir_file) is not None)
        if is_dir_file and not start_w_dollar:
            # Create the absolute path from a possible relative path.
            newp = os.path.join(config_dir_abs, dir_file)
            config.set("BATCH_OPTIONS", key, newp)


def _read_pre_post_file(filename):
    """ Read the combined pre/post commands file.

    Arguments
    ---------
    filename: str
        Path to pre/post commands file.

    Returns
    -------
    str:
        Pre-commands split up per line.
    str:
        Post-commands split up per line.
    """
    pre_lines = []
    post_lines = []
    cur_lines = pre_lines
    with open(filename, "r") as f:
        for cur_line in f:
            # Check for switching or pre/post commands.
            if re.match(r"## PRE_COMMANDS ##*", cur_line):
                cur_lines = pre_lines
            elif re.match(r"## POST_COMMANDS ##*", cur_line):
                cur_lines = post_lines
            else:
                cur_lines.append(cur_line)
    return (pre_lines, post_lines)


def generate_batch_scripts(command_file, config_file, run_pre_file="/dev/null",
                           run_post_file="/dev/null", pre_post_file=None,
                           force_clear=False):
    """ Function to prepare for writing batch scripts.

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
    # Make sure all files exist.
    if _check_files(command_file, config_file, run_pre_file, run_post_file):
        return 1

    # Figure out the backend
    config = cp.SafeConfigParser()
    config.read(config_file)

    if config.has_section("CONNECTION"):
        send_batch_ssh(command_file, config, force_clear)
        return 0

    _replace_rel_abs_path(config, config_file)

    backend = config.get("BACKEND", "backend")

    # Set the parameters from the config file.
    param = _params(config)

    if config.has_option("BATCH_OPTIONS", "pre_post_file"):
        pre_post_file = config.get("BATCH_OPTIONS", "pre_post_file")

    if pre_post_file is not None:
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
    output_dir = batch_dir(backend, param["job_name"])

    if backend == "slurm_lisa":
        batch = SlurmLisa()
    elif backend == "parallel":
        batch = Parallel()
    else:
        print("Error: no valid backend detected, supplied in file {cfg_file}".
              format(cfg_file=config_file))
        return 1

    batch.write_batch(script_lines, param, output_dir, force_clear)
