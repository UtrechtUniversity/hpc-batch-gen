"""
Module for interaction with remote servers.

@author: Raoul Schram
"""

import subprocess32 as subprocess
import copy
from string import Template
import shlex


def _ssh_template():
    """ SSH command to log into remote server. """
    ssh = Template("""ssh -q -o ConnectTimeout=3 -o ServerAliveInterval=3 \
-o ServerAliveCountmax=1 ${user}${server} 'cd ${remote_dir}; batchgen \
${command_file} ${config_file}'
    """)
    return ssh


def send_batch_ssh(command_file, config):
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

    # Write new configuration file with remote_dir as base_dir.
    new_config = copy.copy(config)
    new_config.remove_section("CONNECTION")
    new_config.set("BATCH_OPTIONS", "base_dir", remote_dir)
    new_config_file = "remote_cfg.ini"
    with open(new_config_file, "w") as f:
        new_config.write(f)

    # Copy the command file and the configuration file to remote server.
    copy_command = "scp -q {command_file} {new_config_file} " \
                   "{user}{server}:{remote_cf}"
    copy_command = copy_command.format(command_file=command_file, user=user,
                                       server=server, remote_cf=remote_dir,
                                       new_config_file=new_config_file)
    subprocess.run(shlex.split(copy_command))

    # SSH into the remote server and run batchgen with new config file.
    ssht = _ssh_template()
    ssh_command = ssht.safe_substitute(user=user, server=server,
                                       remote_dir=remote_dir,
                                       command_file=command_file,
                                       config_file=new_config_file)

    subprocess.run(shlex.split(ssh_command))
