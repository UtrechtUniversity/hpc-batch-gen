"""
Created on 4 Mar 2019

@author: Raoul Schram
"""

import subprocess
import copy
from string import Template
import shlex


def _ssh_template():
    ssh = Template("""ssh -o ConnectTimeout=3 -o ServerAliveInterval=3 \
-o ServerAliveCountmax=1 ${user}${server} 'cd ${remote_dir}; batchgen \
${command_file} ${config_file}'
    """)

#     ssh = Template("""ssh -o ConnectTimeout=3 -o ServerAliveInterval=3 \
# -o ServerAliveCountmax=1 ${user}${server} \"ls -la\"
#     """)

    return ssh


def send_batch_ssh(command_file, config):
    # First copy commands/config file

    if "user" in config["CONNECTION"]:
        user = config["CONNECTION"]["user"]+"@"
    else:
        user = ""
    server = config["CONNECTION"]["server"]
    remote_dir = config["CONNECTION"]["remote_dir"]
    copy_command = "scp -q {command_file} {user}{server}:{remote_cf}"
    copy_command = copy_command.format(command_file=command_file, user=user,
                                       server=server, remote_cf=remote_dir)
    subprocess.run(copy_command.split(" "))

    new_config = copy.copy(config)
    new_config.remove_section("CONNECTION")
    new_config["BATCH_OPTIONS"]["base_dir"] = remote_dir
    new_config_file = "remote_cfg.ini"
    with open(new_config_file, "w") as f:
        new_config.write(f)

    copy_command = "scp -q {new_config_file} {user}{server}:{remote_cf}"
    copy_command = copy_command.format(new_config_file=new_config_file,
                                       user=user, server=server,
                                       remote_cf=remote_dir)
    subprocess.run(copy_command.split(" "))

    ssht = _ssh_template()
    ssh_command = ssht.safe_substitute(user=user, server=server,
                                       remote_dir=remote_dir,
                                       command_file=command_file,
                                       config_file=new_config_file)
#     print(ssh_command)
    subprocess.run(shlex.split(ssh_command))
