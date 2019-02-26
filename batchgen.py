'''
Created on 20 Feb 2019

@author: Raoul Schram

Script file to generate batch scripts for the SARA/Lisa SLURM system.
'''

import sys
import os
import pathlib
from string import Template
from idlelib import rstrip


def _params(file=None):
    '''Function to set defaults for the batch jobs.
    
    Returns
    -------
    dict:
        Dictionary of all parameters.
    '''
    
    defaults = {'clock_wall_time':"01:00:00", "num_cores":16,
                'job_name':'asr_simulation', 
                "batch_id":0, 'run_pre_compute':"", 'run_post_compute':""}
    
    #If a file is supplied, read the configuration.
    if file != None:
        with open(file, "r") as f:
            for line in f:
                (key, val) = line.split()
                defaults[key]=val
    return defaults

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
    body=""
    for line in script_lines:
        new_line = line.rstrip() + " &> /dev/null &\n"
        body = body+new_line
        body = body+"sleep 1\n"
    body += "wait\n"
    body += "wait"
    return body


def _read_script(script):
    '''Function to load either a script file or list.
    
    Arguments
    ---------
    script: str/str
        Either a file to read, or a list of strings to use.
    
    Returns
    -------
        List of strings where each element is one command.
    '''
    if not isinstance(script, (list,)):    
        with open(script, "r") as f:
            lines = f.readlines()
    else:
        lines = script
    return lines


def _write_batch_scripts(script_lines, param, output_dir):
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
    
    num_cores=int(param['num_cores'])

    for batch_id,i in enumerate(range(0,len(script_lines),num_cores)):
        file = os.path.join(output_dir, "batch" + str(batch_id) + ".sh")
        param['main_body']=_get_body(script_lines[i:i+num_cores])
        param['batch_id']=batch_id
        if len(script_lines[i:i+num_cores]) < num_cores:
            param['num_cores']=len(script_lines[i:i+num_cores])
        with open(file, "w") as f:
            recursive_template = Template(batch_template.safe_substitute(param))
            f.write(recursive_template.safe_substitute(param))
    

def generate_batch_scripts(input_script, run_pre_file, run_post_file, output_dir=None):
    '''Function to prepare for writing batch scripts.
    
    Arguments
    ---------
    input_script: str/str
        Either filename for commands to run, or list of strings with commands.
    run_pre_file: str/str
        Same for commands that are executed for every batch (before main execution).
    run_post_file: str/str
        Same, but after main execution.
    output_dir: str
        Output directory for batch jobs.
    
    '''
    script_dir = os.path.dirname(os.path.realpath(__file__))
    
    script_lines = _read_script(input_script)
    run_pre_compute = _read_script(run_pre_file)
    run_post_compute = _read_script(run_post_file)
    
    run_pre_compute  = "\n".join(run_pre_compute)
    run_post_compute = "\n".join(run_post_compute)
    param=_params(os.path.join(script_dir, "slurm.cfg"))
    param['run_pre_compute']  = run_pre_compute
    param['run_post_compute'] = run_post_compute
    
    #If no output directory is given, create one under script directory/batch/${job_name}.
    if output_dir == None:
        base_dir = script_dir
        output_dir = os.path.join(base_dir, "batch", param['job_name'])
    
    _write_batch_scripts(script_lines, param, output_dir)
    #Bash command to submit the scripts.
    print(f"for FILE in {output_dir}/batch*.sh; do sbatch $FILE; done")

#If used from the command line.
if __name__ == '__main__':
    if len(sys.argv) <= 3 :
        print("Error: need three arguments (script file)")
    else:
        generate_batch_scripts(*sys.argv[1:])
    
