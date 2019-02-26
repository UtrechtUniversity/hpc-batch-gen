'''Created on 26 Feb 2019

@author: Raoul Schram

Example script file to generate batch scripts.
'''

import os
import pathlib
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

${run_pre_compute}

parallel ${num_cores_w_arg} < ${command_file}

${run_post_compute}

""")
    return t


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
    
    #If num_cores is not supplied let parallel auto-detect.
    if 'num_cores' in param:
        param['num_cores_w_arg']="-j "+str(param['num_cores'])
    else:
        param['num_cores_w_arg']=""
    
    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    command_file = os.path.join(output_dir, "commands.sh")
    batch_file = os.path.join(output_dir, "batch.sh")
    
    param['command_file'] = command_file
    recursive_template = Template(batch_template.safe_substitute(param))
    
    #Write all the commands executed in parallel.
    with open(command_file, "w") as f:
        f.writelines(script_lines)
    
    #Write the batch script (including pre/post commands that are not in parallel).
    with open(batch_file, "w") as f:
        f.write(recursive_template.safe_substitute(param))
    
    #make the batch script executable.
    os.chmod(batch_file, 0o755)
    
    #Bash command to submit the scripts.
    return f'{batch_file}'
    