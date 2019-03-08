"""
Module for interaction with remote servers.

@author: Raoul Schram
"""

import os
import re
import copy
import shlex
try:
    import subprocess32 as subprocess
except ImportError as e:
    import subprocess

from string import Template

from batchgen.util import batch_dir
from batchgen.backend.hpc import make_check_clean_directory


def _ssh_template():
    """ SSH command to log into remote server. """
    ssh = Template("""
    ssh -q -o ConnectTimeout=10 -o ServerAliveInterval=10 ${user}${server} \
    'cd ${remote_dir}; batchgen ${command_file} ${config_file} || \
    echo "Error: while executing batchgen."'
""")
    return ssh


def _remote_submit_template():
    sub_templ = Template("""#!/bin/bash

    ssh -q -o ConnectTimeout=10 -o ServerAliveInterval=10 ${user}${server} \
    'cd ${remote_dir}; ${exec_line}'
""")
    return sub_templ


def parse_remote_msg(msg):
    """ Figure out the different components of the output of the remote script.

    Arguments
    ---------
    msg: str
        Unicode string that encodes the output.

    Returns
    -------
    error_msg: str
        List of error messages, empty list means no errors.
    exec_line: str
        Line to execute on remote (anything not starting with #/*/Error
    info_msg: str
        Anything starting with asterixes (*)
    """
    msg = msg.split("\n")
    exec_line = ""
    info_msg = ""
    error_msg = []
    for line in msg:
        sw_hash = re.match(r'^#', line) is not None
        sw_asterix = re.match(r'^\*', line) is not None
        sw_error = re.match(r'^Error', line) is not None
        if sw_asterix:
            info_msg += line+"\n"
        elif line == "" or sw_hash:
            pass
        elif sw_error:
            error_msg.append(line)
        else:
            exec_line += line

    return error_msg, exec_line, info_msg


def send_batch_ssh(command_string, config, force_clear=False):
    """ Prepare a batch on a remote server.

    Arguments
    ---------
    command_file: str
        File with commands to execute.
    config: str
        ConfigParser configuration, read from file.
    """

    if "user" in config.options("CONNECTION"):
        user = config.get("CONNECTION", "user")+"@"
    else:
        user = ""
    server = config.get("CONNECTION", "server")
    remote_dir = config.get("CONNECTION", "remote_dir")
    backend = config.get("BACKEND", "backend")
    job_name = config.get("BATCH_OPTIONS", "job_name")
    pre_post_file = config.get("BATCH_OPTIONS", "pre_post_file")

    # Write new configuration file with remote_dir as base_dir.
    # WARNING: this is not a deep copy, so the var config is also changed.
    remote_pp_file = "remote_pp_{job_name}.sh".format(job_name=job_name)
    # Absolute path (from $HOME) to copy pre_post_file.
    long_remote_pp_file = os.path.join(remote_dir, remote_pp_file)
    new_config = copy.copy(config)
    new_config.remove_section("CONNECTION")
    new_config.set("BATCH_OPTIONS", "base_dir", remote_dir)
    new_config.set("BATCH_OPTIONS", "pre_post_file", remote_pp_file)
    new_config_file = "remote_cfg.ini"
    with open(new_config_file, "w") as f:
        new_config.write(f)

    new_command_file = "remote_command_script.sh"
    with open(new_command_file, "w") as f:
        f.write(command_string)

    # Copy the command file and the configuration file to remote server.
    copy_command = "scp -q {command_file} {new_config_file} " \
                   "{user}{server}:{remote_cf}"
    copy_command = copy_command.format(command_file=new_command_file,
                                       user=user, server=server,
                                       remote_cf=remote_dir,
                                       new_config_file=new_config_file)
    # Copy pre_post_file to remote server.
    subprocess.run(shlex.split(copy_command))

    copy_command = "scp -q {pp_file} {user}{server}:{remote_pp_file}"
    copy_command = copy_command.format(pp_file=pre_post_file, user=user,
                                       server=server,
                                       remote_pp_file=long_remote_pp_file)
    subprocess.run(shlex.split(copy_command))

    # SSH into the remote server and run batchgen with new config file.
    ssht = _ssh_template()
    ssh_command = ssht.safe_substitute(user=user, server=server,
                                       remote_dir=remote_dir,
                                       command_file=new_command_file,
                                       config_file=new_config_file)
    res = subprocess.run(shlex.split(ssh_command), stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    msg = res.stdout.decode('utf-8')

    # Check for error at remote server.
    error_msg, exec_line, info_msg = parse_remote_msg(msg)
    if len(error_msg) != 0:
        print("----- Remote error at {server} -----".format(server=server))
        print(msg)
        print("----- stderr -----")
        print(res.stderr.decode('utf-8'))
        return

    # Output directory for script that remotely submits the script.
    output_dir = batch_dir(backend, job_name, remote=True)
    if not make_check_clean_directory(output_dir, force_clear=force_clear):
        return

    sub_templ = _remote_submit_template()
    sub_script = sub_templ.safe_substitute(user=user, server=server,
                                           remote_dir=remote_dir,
                                           exec_line=exec_line)
    sub_file = os.path.join(output_dir, "submit_remote.sh")
    with open(sub_file, "w") as f:
        f.write(sub_script)
    os.chmod(sub_file, 0o755)

    # Print instructions and info
    print(info_msg)
    print(sub_file)
