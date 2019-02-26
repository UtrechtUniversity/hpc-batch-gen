'''
Created on 26 Feb 2019

@author: qubix
'''

import pathlib
import os
from string import Template

def _batch_template():
    '''Function that generates the default template.
    
    Returns
    -------
    string.Template:
        Template for batch files on Lisa.
    '''
    t = Template("""
#!/bin/bash
#SBATCH -t ${clock_wall_time}
#SBATCH --tasks-per-node=${num_cores}
#SBATCH -J ${job_name}

${run_pre_compute}

${main_body}

${run_post_compute}

echo "Job $$SLURM_JOBID ended at `date`" | mail $$USER -s "Job: ${job_name}/${batch_id} ($$SLURM_JOBID)"
date    
""")
    return t

def _get_body(script_lines):
    '''Function to create the body of the script files, staging their start.
    
    Arguments
    ---------
    script_lines: str
        List of strings where each element is one command to be submitted.
        
    Returns
    -------
    str:
        Joined commands.
    '''
    #Stage the commands every 1 second.
    body=""
    for line in script_lines:
        new_line = line.rstrip() + " &> /dev/null &\n"
        body = body+new_line
        body = body+"sleep 1\n"
    body += "wait\n"
    body += "wait"
    return body


def write_batch_scripts(script_lines, param, output_dir):
    '''Function to write batch scripts to a directory.
    
    Arguments
    ---------
    script_lines: str
        List of string where each element is one command.
    param: dict
        Dictionary with the parameters for the batch scripts.
    output_dir: str
        Directory for batch files.
    '''
    batch_template = _batch_template()
    
    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    #If the number of cores is not supplied, set it to the default 16.
    if 'num_cores' in param:
        num_cores=int(param['num_cores'])
    else:
        num_cores=16
    
    #Split the commands in len(script_lines)/num_cores batches (rounded up).
    for batch_id,i in enumerate(range(0,len(script_lines),num_cores)):
        #Output file
        file = os.path.join(output_dir, "batch" + str(batch_id) + ".sh")
        param['main_body']=_get_body(script_lines[i:i+num_cores])
        param['batch_id']=batch_id
        if len(script_lines[i:i+num_cores]) < num_cores:
            param['num_cores']=len(script_lines[i:i+num_cores])
        #Allow for one more substitution to facilitate user defined substitution.
        recursive_template = Template(batch_template.safe_substitute(param))
        with open(file, "w") as f:
            f.write(recursive_template.safe_substitute(param))
    return f"for FILE in {output_dir}/batch*.sh; do sbatch $FILE; done"

