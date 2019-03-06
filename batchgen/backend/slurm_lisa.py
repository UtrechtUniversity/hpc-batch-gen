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

if [ ${send_mail} == "True" ]; then
    echo "Job $$SLURM_JOBID ended at `date`" | mail $$USER -s \
    "Job: ${job_name}/${batch_id} ($$SLURM_JOBID)"
fi
date
""")
        return t

    def _parse_params(self, param, script_lines, output_dir):

        # If the number of cores is not supplied, set it to the default 16.
        if "num_cores" in param:
            num_cores = int(param["num_cores"])
        else:
            num_cores = 16

        max_num_cores = max(num_cores, len(script_lines))
        num_nodes = (len(script_lines)-1) // num_cores
        cost_factor = 16*num_nodes

        param["script_lines"] = script_lines
        param["output_dir"] = output_dir
        param["num_cores"] = num_cores
        param["max_num_cores"] = max_num_cores
        param["num_nodes"] = num_nodes

        hhmmss = param["clock_wall_time"].split(":").reverse()

        new_ss = (hhmmss[0]*cost_factor)
        new_mm = new_ss // 60
        new_ss %= 60
        new_mm += (hhmmss[1]*cost_factor)
        new_hh = new_mm // 60
        new_mm %= 60
        new_hh += (hhmmss[2]*cost_factor)

        new_hhmmss = "{hh}:{mm}:{ss}".format(hh=new_hh, mm=new_mm, ss=new_ss)
        param["max_bill_time"] = new_hhmmss
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

    def print_execution(self, exec_script):
        par = self._params

        print_template = Template("""\
******************************************************
**                 Running parameters               **
******************************************************
** Job name        : {job_name}                     **
** Cores per node  : {max_num_cores}                **
** Maximum run time: {clock_wall_time}              **
** Number of nodes : {num_nodes}                    **
** Max billing time: {max_bill_time}                **
******************************************************
** Execute the following on the command line (bash) **
******************************************************

{exec_script}
        """.format(exec_script=exec_script, **par))
        print(print_template)
