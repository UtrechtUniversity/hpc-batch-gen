'''
Some helpful functions.

@author: Raoul Schram
'''

import os
import re


def _read_file(script):
    """ Function to load either a script file or list.

    Arguments
    ---------
    script: str/str
        Either a file to read, or a list of strings to use.

    Returns
    -------
        List of strings where each element is one command.
    """
    if script is None:
        return ""
    with open(script, "r") as f:
        script_string = f.read()
    return script_string


def _split_commands(script):
    """ Split commands from a string into a list of commands.

    Arguments
    ---------
    script: str
        Command as read directly from a file.

    Returns
    -------
    str:
        List of commands, lines with only whitespce removed,
        and also lines starting with #.
    """
    real_commands = []
    for line in script.split("\n"):
        only_whitespace = re.match(r"\A\s*\Z", line) is not None
        sw_hash = re.match(r"^#", line) is not None
        if only_whitespace or sw_hash:
            continue
        real_commands.append(line)
    return real_commands


def _check_files(*args):
    """ Check if files exist.

    Arguments
    ---------
    args: str
        List of files to check.

    Returns
    -------
    int:
        Number of non-existing files.
    """
    n_error = 0
    for filename in args:
        if filename is None:
            continue
        if not os.path.isfile(filename) and filename != "/dev/null":
            print("Error: file {file} does not exist.".format(file=filename))
            n_error += 1
    return n_error


def batch_dir(backend, job_name, remote=False):
    """ Return a directory from the backend/job_name/remote. """
    if remote:
        new_dir = os.path.join("batch."+backend+".remote", job_name)
    else:
        new_dir = os.path.join("batch."+backend, job_name)
    return os.path.abspath(new_dir)


def mult_time(clock_wall_time, mult):
    """ Multiply times in hh:mm:ss by some multiplier.

    Arguments
    ---------
    clock_wall_time: str
        Time delta in hh:mm:ss format.
    mult
        Multiplier for the time.

    Returns
    -------
    str:
        Time delta multiplied by the multiplier in hh:mm:ss format.
    """
    hhmmss = clock_wall_time.split(":")
    hhmmss.reverse()

    new_ss = (int(hhmmss[0])*mult)
    new_mm = new_ss // 60
    new_ss %= 60
    new_mm += (int(hhmmss[1])*mult)
    new_hh = new_mm // 60
    new_mm %= 60
    new_hh += (int(hhmmss[2])*mult)

    new_hhmmss = "{hh:02d}:{mm:02d}:{ss:02d}".format(hh=new_hh, mm=new_mm,
                                                     ss=new_ss)
    return new_hhmmss
