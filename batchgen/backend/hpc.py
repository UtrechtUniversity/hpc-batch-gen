"""
Base class for HPC backends.

@author Raoul Schram
"""

import os
from string import Template

import pathlib2


def double_substitute(template, param):
    first_batch_str = template.safe_substitute(param)
    recursive_template = Template(first_batch_str)
    final_batch_str = recursive_template.safe_substitute(param)
    return final_batch_str


def make_check_clean_directory(output_dir, force_clear=False):
    """ Check if batch output directory is empty.

    Arguments
    ---------
    output_dir: str
        Directory to check.
    force_clear: str
        Remove old .sh files if they exist.

    Returns
    -------
    bool:
        True if empty (now), False if unable to empty.
    """
    # First create the directory.
    pathlib2.Path(output_dir).mkdir(parents=True, exist_ok=True)

    if os.listdir(output_dir):
        if not force_clear:
            print("Error: directory {dir} is not empty.\n"
                  "Change the name of the job, or...\n"
                  "Use -f/--force-overwrite to ignore "
                  "previous batch files.\nContents:\n"
                  .format(dir=output_dir))
            print(os.listdir(output_dir))
            return False

        for cur_file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, cur_file)
            if not os.path.isfile(file_path):
                print("Error: directory {dir} contains sub-directories.\n"
                      "Remove by hand to continue.\n"
                      .format(dir=output_dir))
                return False
            elif os.path.splitext(file_path)[1] != ".sh":
                print("Error: non shell script {file} detected in {dir}\n"
                      "Remove by hand to continue\n"
                      .format(file=cur_file, dir=output_dir))
                return False
            # Remove file
            os.unlink(file_path)
    return True


class HPC(object):
    """ Abstract base class for manipulating HPC backends. """

    def __init__(self):
        self._params = None
        self._batch_template = None

    def write_batch(self, script_lines, param, output_dir, force_clear=False):
        """ Function to create submitable batch scripts.

        Arguments
        ---------
        script_lines: str
            List of string where each element is one command.
        param: dict
            Dictionary with the parameters for the batch scripts.
        output_dir: str
            Directory for batch files.
        """

        if not make_check_clean_directory(output_dir, force_clear):
            return

        self._batch_template = self._create_batch_template()
        self._params = self._parse_params(param, script_lines, output_dir)

        my_exec = self._write_batch_files()
        self._print_execution(my_exec)

    def _create_batch_template(self):
        """ Function to generate a batch template.
        Mandatory implementation for derived classes.
        """

        raise NotImplementedError(
            "Error: broken module; implement _create_batch_template.")

    def _parse_params(self, param, script_lines, output_dir):
        """ Parse parameters to obtain specific substitutions, which
            are not necessarily the same for different backends.
            Mandatory implementation for derived classes.

        Arguments
        ---------
        param: dict
            Dictionary of parameters read from the configuration file.
        script_lines: str
            List of commands that we want to run in parallel.
        output_dir: str
            Output directory for the batch files.
        """

        raise NotImplementedError(
            "Error: broken module; implement _parse_params method.")

    def _write_batch_files(self):
        """ Write batch scripts, helper files, and return command
            for submission. Mandatory implementation for derived classes.

        Arguments
        ---------
        batch_str: str
            What to write in the batch file.

        Returns
        -------
        str:
            Command to execute in bash.
        """

        raise NotImplementedError(
            "Error: broken module; implement _write_batch_files method.")

    def print_execution(self, exec_script):
        print("""
******************************************************
** Execute the following on the command line (bash) **
******************************************************

{exec_script}
        """.format(exec_script=exec_script))
