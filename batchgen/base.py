"""
Base module for generating batch scripts for arbitrary HPC environments.
See __main__ for the Command Line Interface (CLI)

@author: Raoul Schram
"""

import os
try:
    import configparser as cp
except ImportError as e:
    import ConfigParser as cp

import re

from batchgen.backend.parallel import Parallel
from batchgen.backend.slurm_lisa import SlurmLisa
from batchgen.ssh import send_batch_ssh
from batchgen.util import _read_file, _check_files, batch_dir


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
        parameters.update(dict(config.items("BACKEND")))

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
    pre_lines = ""
    post_lines = ""
    cur_position = "pre"
    with open(filename, "r") as f:
        for line in f:
            # Check for switching or pre/post commands.
            if re.match(r"## PRE_COMMANDS ##*", line):
                cur_position = "pre"
            elif re.match(r"## POST_COMMANDS ##*", line):
                cur_position = "post"
            else:
                if cur_position == "pre":
                    pre_lines += line
                else:
                    post_lines += line

    return (pre_lines, post_lines)


def batch_from_files(command_file, config_file, pre_post_file=None,
                     pre_com_file=None, post_com_file=None,
                     force_clear=False):
    """ Function to write batch scripts from command line.

    Arguments
    ---------
    """
    # Make sure all files exist.
    if _check_files(command_file, config_file, pre_post_file,
                    pre_com_file, post_com_file):
        return 1

    command_string = _read_file(command_file)
    if pre_post_file is not None:
        pre_string, post_string = _read_pre_post_file(pre_post_file)
    else:
        pre_string = _read_file(pre_com_file)
        post_string = _read_file(post_com_file)

    batch_from_strings(command_string, config_file, pre_string,
                       post_string, force_clear)


def batch_from_strings(command_string, config_file, pre_com_string="",
                       post_com_string="", force_clear=False):
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

    # Figure out the backend
    config = cp.ConfigParser()
    config.optionxform = str
    config.read(config_file)

    if config.has_section("CONNECTION"):
        send_batch_ssh(command_string, config, force_clear)
        return 0

    _replace_rel_abs_path(config, config_file)

    backend = config.get("BACKEND", "backend")

    # Set the parameters from the config file.
    param = _params(config)

    if config.has_option("BATCH_OPTIONS", "pre_post_file"):
        pre_post_file = config.get("BATCH_OPTIONS", "pre_post_file")
        pre_com_string, post_com_string = _read_pre_post_file(pre_post_file)

    # Get all the commands either from file, or from lists:

    param["pre_com_string"] = pre_com_string
    param["post_com_string"] = post_com_string

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

    batch.write_batch(command_string, param, output_dir, force_clear)
