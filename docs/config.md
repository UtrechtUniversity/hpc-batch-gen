# Configuration files [parallel.ini, slurm_lisa.ini]

Configuration files are setting the parameters for batch creation. While they are not completely agnositic to the batch system used (you'll probably need different files for different backends), they should have similar options and sections. 

The configuration files uses a structure similar to the Windows INI format, and is readable by the [configparser](https://docs.python.org/3/library/configparser.html) Python package. The structure is simple enough to be understandable without any previous knowledge of the INI format or the Python language. Lines that start with a "#" are comments and are ignored by the program.

Our configuration files are divided into 2 or 3 sections, which are denoted by square brackets **[ ]**.

### [BACK_END] (mandatory)

Under this section there is just a single option, namely its backend.

##### backend

Should be set to one of the available backends, which right now is *parallel* (GNU Parallel), or *slurm_lisa* (SLURM batch system on Lisa HPC cluster at SURFSara). 


### [BATCH_OPTIONS] (mandatory)

In this section options that relate to the specifics such as hardware, node configuration, file structure etc.

##### num\_cores (recommended)

In case of the batch system, this is the number of (usable) processor cores per node. In the case of local execution (GNU Parallel), this is the number of (virtual) cores to be used, defaulting to the number of available ones.

##### job\_name (recommended)

This is the name of the job. The directory where batchfiles are stored is named with this job name.


##### pre\_post\_file (recommended)

File in which the commands are put that are run for each node, before or after computation (see [readme](README.md)). Pre-commands are prefaced by:


##### clock\_wall\_time [SLURM] (recommended)

The maximum running time of the batch, format hh:mm:ss. Default is 1 hour. In the case of batch systems it is highly recommended to set this to the appropriate amount. Not too long, because it might have a lower priority in the queue, and definitely not too short, since that will cause the batch to be prematurely aborted.


##### num\_cores\_simul [SLURM] (optional)

The number of tasks to run simultaneous on a node. Should most probably equal or less than *num_cores*.

##### num\_tasks\_per\_node [SLURM] (optional)

The number of tasks to be run in total per node. If this is bigger than *num_cores_simul*, the commands are partly serialized.

```
### PRE_COMMANDS ###
```

on an empty line, while the post-commands are started by:

```
### POST_COMMANDS ###
```

##### base\_dir (optional)

This gets replaced by *remote\_dir* from the 


##### *User defined keys* (optional)

You can define more keys, which don't have a special meaning. As an example, tmp\_dir is defined as the directory where the individual results are stored, before copying them back to the final destination. This way, one can use ${tmp\_dir} in the pre\_post\_file, which is back-substituted from the configuration file.

### [CONNECTION] (optional)

This section is only necessary for remote batch creation. The batchgen package needs to be installed on the target server for it to work. It uses SSH and scp to connect to the server and copy files, so evidently a user account on that server is necessary. 

##### server (mandatory)

Remote server to connect to. Any aliases defined in the SSH configuration file (~/.ssh/config) are valid.

##### remote\_dir (mandatory)

The commandsfile and updated configuration file are copied to this location, and batch creation is also done there. The directory is relative to the user home directory (if not given a absolute path).

##### user (recommended)

This is the user name on the remote server. You can also define it in the SSH configuration file, and not supply it here.


The following is an example for the configuration file:

```ini
[BACKEND]

# Set backend to SLURM system on HPC cluster Lisa (SURFSara).
backend = slurm_lisa


[BATCH_OPTIONS]

# Set maximum running time to two hours.
clock_wall_time = 02:00:00

# Set number of cores per node to 16.
num_cores = 16

# Set number of simultaneously running tasks.
num_cores_simul = 15

# Set maxim number of tasks per node.
num_tasks_per_node = 30

# Set job name to "asr_sim"
job_name = asr_sim

# Here are the configuration/script/executable files.
base_dir = .

# Define the temporary directory (can use scratch as well of course).
tmp_dir = ${TMP_DIR}

# Define the output directory to which the results are copied.
output_dir = sum_output

# This is the script that defines pre-/post-processing of data.
pre_post_file = pp_sum.sh


[CONNECTION]

# The base directory at the remote server, relative to the user home directory.
remote_dir = batchgen/samples

# Remote server name
server = lisa.surfsara.nl

# User name on remote server (comment to leave at default).
# user = rdschram
```
