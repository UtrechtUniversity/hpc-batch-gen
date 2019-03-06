'''
Some helpful functions.

@author: Raoul Schram
'''

import os


def _read_script(script):
    """ Function to load either a script file or list.

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
    return new_dir


def mult_time(clock_wall_time, mult):
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
