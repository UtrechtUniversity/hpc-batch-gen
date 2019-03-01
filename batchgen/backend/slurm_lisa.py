"""
SLURM on Lisa (SURFSara) backend for running batch style scripts.

@author: Raoul Schram
"""

import os
from string import Template

from batchgen.backend.hpc import HPC, double_substitute


def _get_body(script_lines):
    """Function to create the body of the script files, staging their start.

    Arguments
    ---------
    script_lines: str
        List of strings where each element is one command to be submitted.

    Returns
    -------
    str:
        Joined commands.
    """

    # Stage the commands every 1 second.
    body = ""
    for line in script_lines:
        new_line = line.rstrip() + " &> /dev/null &\n"
        body = body+new_line
        body = body+"sleep 1\n"
    body += "wait\n"
    body += "wait"
    return body


class SlurmLisa(HPC):
    """ Derived class from HPC. See hpc.py for method descriptions """

    def _create_batch_template(self):
        t = Template("""
#!/bin/bash
#SBATCH -t ${clock_wall_time}
#SBATCH --tasks-per-node=${num_cores}
#SBATCH -J ${job_name}

${run_pre_compute}

${main_body}

${run_post_compute}

echo "Job $$SLURM_JOBID ended at `date`" | mail $$USER -s \
"Job: ${job_name}/${batch_id} ($$SLURM_JOBID)"
date
""")
        return t

    def _parse_params(self, param, script_lines, output_dir):

        # If the number of cores is not supplied, set it to the default 16.
        if "num_cores" in param:
            num_cores = int(param["num_cores"])
        else:
            num_cores = 16

        param["script_lines"] = script_lines
        param["output_dir"] = output_dir
        param["num_cores"] = num_cores
        return param

    def _write_batch_files(self):
        par = self._params
        script_lines = par["script_lines"]
        num_cores = par["num_cores"]
        output_dir = par["output_dir"]
        # Split the commands in batches.
        for batch_id, i in enumerate(range(0, len(script_lines), num_cores)):
            # Output file
            output_file = os.path.join(output_dir,
                                       "batch" + str(batch_id) + ".sh")
            par["main_body"] = _get_body(script_lines[i:i + num_cores])
            par["batch_id"] = batch_id
            if len(script_lines[i:i+num_cores]) < num_cores:
                par["num_cores"] = len(script_lines[i:i + num_cores])

            # Allow for one more substitution to facilitate user substitution.
            batch_script = double_substitute(self._batch_template, par)
            with open(output_file, "w") as f:
                f.write(batch_script)

        # Execute the following to submit the batch.
        my_exec = "for FILE in {output_dir}/batch*.sh; do sbatch $FILE; done"

        return my_exec.format(output_dir=output_dir)
