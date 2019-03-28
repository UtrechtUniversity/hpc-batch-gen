"""
SLURM on Lisa (SURFSara) backend for running batch style scripts.

@author: Raoul Schram
"""

import os
from string import Template

from batchgen.backend.hpc import HPC, double_substitute
from batchgen.util import mult_time


def _get_body(script_lines, num_cores_simul, silence=False):
    """Function to create the body of the script files, staging their start.

    Arguments
    ---------
    script_lines: str
        List of strings where each element is one command to be submitted.
    sum_cores_simul: int
        Number of cores used simultaneously.
    Returns
    -------
    str:
        Joined commands.
    """

    # Stage the commands every 1 second.
    body = "parallel -j {num_cores_simul} << EOF_PARALLEL\n"
    body = body.format(num_cores_simul=num_cores_simul)
    if silence:
        redirect = "&> /dev/null"
    else:
        redirect = ""
    for i, line in enumerate(script_lines):
        new_line = line.rstrip() + redirect + "\n"
        if i < num_cores_simul:
            new_line = "sleep {i}; ".format(i=i) + new_line
        body = body+new_line
    body += "EOF_PARALLEL\n"
    return body


class SlurmLisa(HPC):
    """ Derived class from HPC. See hpc.py for method descriptions """

    def _create_batch_template(self):
        t = Template("""\
#!/bin/bash
#SBATCH -t ${clock_wall_time}
#SBATCH --tasks-per-node=${num_cores}
#SBATCH -J ${job_name}
#SBATCH --output=${batch_dir}/${job_name}_${batch_id}.out
#SBATCH --error=${batch_dir}/${job_name}_${batch_id}.err

${pre_com_string}
${main_body}
${post_com_string}

if [ "${send_mail}" == "True" ]; then
    echo "Job $$SLURM_JOBID ended at `date`" | mail $$USER -s \
"Job: ${job_name}/${batch_id} ($$SLURM_JOBID)"
fi
date
""")
        return t

    def _parse_params(self, param):

        # If the number of cores is not supplied, set it to the default 16.
        if "num_cores" in param:
            num_cores = int(param["num_cores"])
        else:
            num_cores = 16
        if "num_cores_simul" not in param:
            param["num_cores_simul"] = num_cores
        if "num_tasks_per_node" not in param:
            param["num_tasks_per_node"] = param["num_cores_simul"]
        param["num_cores_simul"] = int(param["num_cores_simul"])
        param["num_tasks_per_node"] = int(param["num_tasks_per_node"])

        tasks_per_node = param["num_tasks_per_node"]
        num_tasks = len(param["script_lines"])
        max_num_cores = num_cores
        num_nodes = (num_tasks-1) // tasks_per_node + 1
        cost_factor = 16*num_nodes

        param["num_cores"] = num_cores
        param["max_num_cores"] = max_num_cores
        param["num_nodes"] = num_nodes
        param["num_tasks"] = num_tasks

        param["max_bill_time"] = mult_time(param["clock_wall_time"],
                                           cost_factor)

        return param

    def _write_batch_files(self):
        par = self._params
        script_lines = par["script_lines"]
        num_cores = par["num_cores"]
        batch_dir = par["batch_dir"]
        num_tasks = par["num_tasks"]
        tpn = par["num_tasks_per_node"]
        ncs = par["num_cores_simul"]
        # Split the commands in batches.
        for batch_id, i in enumerate(range(0, num_tasks, tpn)):
            # Output file
            batch_file = os.path.join(batch_dir,
                                      "batch_" + str(batch_id) + ".sh")
            par["main_body"] = _get_body(script_lines[i:i+tpn], ncs)
            par["batch_id"] = batch_id
            if len(script_lines[i:i+tpn]) < tpn:
                num_task_remain = len(script_lines[i:i+tpn])
                cores_per_task = (num_cores-1)//ncs+1
                par["num_cores"] = min(num_cores,
                                       num_task_remain*cores_per_task)

            # Allow for one more substitution to facilitate user substitution.
            batch_script = double_substitute(self._batch_template, par)
            with open(batch_file, "w") as f:
                f.write(batch_script)

        # Execute the following to submit the batch.
        my_exec = "for FILE in {batch_dir}/batch_*.sh; do sbatch $FILE; done"

        return my_exec.format(batch_dir=batch_dir)

    def _print_execution(self, exec_script):
        par = self._params

        print_template = """\
******************************************************
**                 Running parameters               **
******************************************************
** Job name          : {job_name: <29}**
** Number of tasks   : {num_tasks: <29}**
** Tasks per node    : {num_tasks_per_node: <29}**
** Cores per node    : {max_num_cores: <29}**
** Simultaneous tasks: {num_cores_simul: <29}**
** Maximum run time  : {clock_wall_time: <29}**
** Number of nodes   : {num_nodes: <29}**
** Max billing time  : {max_bill_time: <29}**
******************************************************
** Execute the following on the command line (bash) **
******************************************************

{exec_script}
        """.format(exec_script=exec_script, **par)
        print(print_template)
