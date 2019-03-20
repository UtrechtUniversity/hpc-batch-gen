"""
GNU Parallel backend for running batch style scripts.

@author: Raoul Schram
"""

import os
from string import Template
from multiprocessing import cpu_count

from batchgen.backend.hpc import HPC, double_substitute


class Parallel(HPC):
    """ Derived class from HPC. See hpc.py for method descriptions """
    def _create_batch_template(self):
        t = Template("""\
#!/bin/bash

${pre_com_string}
parallel ${num_cores_w_arg}< ${command_file}
${post_com_string}
""")
        return t

    def _parse_params(self, param):
        # If num_cores is not supplied let parallel auto-detect.
        if "num_cores" in param:
            param["num_cores_w_arg"] = "-j " + str(param["num_cores"]) + " "
        else:
            param["num_cores_w_arg"] = ""
            param["num_cores"] = cpu_count()

        batch_dir = param["batch_dir"]
        command_file = os.path.join(batch_dir, "commands.sh")
        batch_file = os.path.join(batch_dir, "batch.sh")
        command_file = os.path.abspath(command_file)
        batch_file = os.path.abspath(batch_file)

        param["command_file"] = command_file
        param["batch_file"] = batch_file
        param["num_jobs"] = len(param["script_lines"])

        return param

    def _write_batch_files(self):
        par = self._params
        batch_str = double_substitute(self._batch_template, par)
        script_lines = Template("\n".join(par["script_lines"]))
        script_lines = double_substitute(script_lines, par)
        batch_file = par["batch_file"]
        # Write all the commands executed in parallel.
        with open(par["command_file"], "w") as f:
            f.write(script_lines)

        # Write batch script (inc. pre/post commands that are not in parallel).
        with open(batch_file, "w") as f:
            f.write(batch_str)

        # Make the batch script executable.
        os.chmod(batch_file, 0o755)

        # Bash command to submit the scripts.
        return batch_file

    def _print_execution(self, exec_script):
        par = self._params
        print_template = """\
******************************************************
**                 Running parameters               **
******************************************************
** Job name        : {job_name: <31}**
** Number of jobs  : {num_jobs: <31}**
** Number of cores : {num_cores: <31}**
** Running time    : {clock_wall_time: <31}**
******************************************************
** Execute the following on the command line (bash) **
******************************************************

{exec_script}
        """.format(exec_script=exec_script, **par)
        print(print_template)
