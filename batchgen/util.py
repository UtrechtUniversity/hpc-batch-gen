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
