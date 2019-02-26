# batchgen
Package for generating batch scripts. Currently available: GNU Parallel, SLURM backend.

## Usage
```bash
python3 batchgen.py input_script run_pre_file run_post_file config_file
```

##### input_script
This is a script file that you want to run/parallelize. Every line should be a simple bash command (no backgrounding necessary).

##### run\_pre\_file
This is code that is run on each of the nodes before the commands. Things like copying to temporary directories, copying source files.

##### run\_pre\_file
This code is run on each of the nodes after the commands. Think, copying results back, removing unused data.

##### config\_file
Simple configuration file for the job to be run. The name of configuration file should be one of the architectures as given in the arch/ folder (right now _parallel.cfg_ or <i>slurm_lisa.cfg</i>). The following options are recommended (but not mandatory) to be set:


<i>clock_wall_timego</i>: Maximum time to run. <br> 
<i>num_cores</i>: Number of cores per node. <br>  
<i>job_name</i>: Name of the whole job.  <br>


User defined keys are also possible. For example, one could define the temporary directory ${TMP_DIR} in the config file, so one could more easily change between different machines.

## Example

First go the the working directory:

```bash
cd samples
```

Then run the batch generator

```bash
python ../batchgen.py parallel_cmd.sh /dev/null /dev/null slurm_parallel.cfg 
```

There should be a directory called "batch.parallel/my\_test/" in which a batch script called "batch.sh" is present.

Run the batch script:

```bash
batch.parallel/my_test/batch.sh
```
