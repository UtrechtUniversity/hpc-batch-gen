"""
GNU Parallel backend for running batch style scripts.

@author: Raoul Schram
"""

import os
from string import Template

from batchgen.backend.hpc import HPC, double_substitute


class Parallel(HPC):
    """ Derived class from HPC. See hpc.py for method descriptions """
    def _create_batch_template(self):
        t = Template("""
#!/bin/bash

${run_pre_compute}

parallel ${num_cores_w_arg} < ${command_file}

${run_post_compute}

""")
        return t

    def _parse_params(self, param, script_lines, output_dir):

        # If num_cores is not supplied let parallel auto-detect.
        if "num_cores" in param:
            param["num_cores_w_arg"] = "-j " + str(param["num_cores"])
        else:
            param["num_cores_w_arg"] = ""

        command_file = os.path.join(output_dir, "commands.sh")
        batch_file = os.path.join(output_dir, "batch.sh")
        command_file = os.path.abspath(command_file)
        batch_file = os.path.abspath(batch_file)

        param["command_file"] = command_file
        param["script_lines"] = script_lines
        param["batch_file"] = batch_file
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
