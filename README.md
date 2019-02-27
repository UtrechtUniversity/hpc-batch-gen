# batchgen
Package for generating simple batch scripts in HPC environments. Currently available: GNU Parallel, SLURM backend.

### Requirements:

##### Software

- GNU Parallel (for parallel backend)
- Python 3.x

### Installation:

The easiest way to install the batchgen package is to use the following command in a terminal:

``` bash
pip install git+https://github.com/UtrechtUniversity/hpc-batch-gen.git
```

Use the following in case you have no administrator access:

``` bash
pip install --user git+https://github.com/UtrechtUniversity/hpc-batch-gen.git
```

### Usage
```bash
python3 -m batchgen input_script run_pre_file run_post_file config_file
```

##### input_script
This is a script file that you want to run/parallelize. Every line should be a simple bash command (no backgrounding necessary).

##### run\_pre\_file
This is code that is run on each of the nodes before the commands. Possible uses are: copying files to temporary directories, copying source files. Use /dev/null to supply no commands here.

##### run\_post\_file
This code is run on each of the nodes after the commands. Possible uses are: copying results back or removing unused data. Use /dev/null to supply no commands here.

##### config\_file
Simple configuration file for the job to be run. The name of configuration file should be one of the architectures as given in the arch/ folder (right now _parallel.cfg_ or <i>slurm_lisa.cfg</i>). The following options are recommended (but not mandatory) to be set:

<i>clock_wall_time</i>: Maximum time to run. <br> 
<i>num_cores</i>: Number of cores per node/CPU. <br>  
<i>job_name</i>: Name of the whole job. <br>

User defined keys are also possible. For example, one could define the temporary directory ${TMP_DIR} in the config file, to swiftly change between different machines.

### Example

First go to the samples directory:

```bash
cd samples
```

Then run the batch generator with the parallel backend (assuming the parallel software is installed):

```bash
python3 asr_batch.py x.csv params.csv parallel.cfg
```

There should be a directory called "batch.parallel/my\_test/" in which a batch script called "batch.sh" is present.

Run the batch script:

```bash
batch.parallel/my_test/batch.sh
```

