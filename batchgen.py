'''
Created on 20 Feb 2019

@author: Raoul Schram

Script file to generate batch scripts for the SARA/Lisa SLURM system.
'''

import sys
import os
import backend.parallel as parallel
import backend.slurm_lisa as slurm_lisa


def _params(file=None):
    '''Function to set defaults for the batch jobs.
    
    Returns
    -------
    dict:
        Dictionary of all parameters.
    '''
    
    defaults = {'clock_wall_time':"01:00:00", 'job_name':'asr_simulation', 
                "batch_id":0, 'run_pre_compute':"", 'run_post_compute':""}
    
    #If a file is supplied, read the configuration.
    if file != None:
        with open(file, "r") as f:
            for line in f:
                (key, val) = line.split()
                defaults[key]=val
    return defaults


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

def print_execution(exec_script):
    print(f"""
******************************************************
** Execute the following on the command line (bash) **
******************************************************

{exec_script}
""")

def generate_batch_scripts(input_script, run_pre_file, run_post_file, cfg_file_full, output_dir=None):
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
    
    #Get all the commands either from file, or from lists:
    script_lines = _read_script(input_script)
    run_pre_compute = _read_script(run_pre_file)
    run_post_compute = _read_script(run_post_file)
    
    #Merge the lists back into single strings
    run_pre_compute  = "\n".join(run_pre_compute)
    run_post_compute = "\n".join(run_post_compute)
    
    #Figure out the backend
    cfg_file = os.path.basename(cfg_file_full)
    par_method = os.path.splitext(cfg_file)[0]
    param=_params(cfg_file_full)
    param['run_pre_compute']  = run_pre_compute
    param['run_post_compute'] = run_post_compute
    
    #If no output directory is given, create one: batch.${back-end}/${job_name}/.
    if output_dir == None:
        output_dir = os.path.join("batch."+par_method, param['job_name'])
    
    if cfg_file == "slurm_lisa.cfg":
        exec_script = slurm_lisa.write_batch_scripts(script_lines, param, output_dir)
    elif cfg_file == "parallel.cfg":
        exec_script = parallel.write_batch_scripts(script_lines, param, output_dir)
    else:
        print(f"Error: no valid backend detected, supplied {cfg_file}")
        return 1
    
    print_execution(exec_script)

#If used from the command line.
if __name__ == '__main__':
    if len(sys.argv) <= 3 :
        print("Error: need three arguments (script file)")
    else:
        generate_batch_scripts(*sys.argv[1:])
    
