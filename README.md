# batchgen
Package for generating simple batch scripts in HPC environments. Currently available: GNU Parallel, SLURM backend.

### Requirements:

##### Software

- GNU Parallel (for parallel backend)
- Python 2.7+

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
python -m batchgen command_file config_file [-pre run_pre_file] [-post run_post_file]
```

##### input_script
This is a script file that you want to run/parallelize. Every line should be a simple bash command (no backgrounding necessary).

##### run\_pre\_file (optional)
This is code that is run on each of the nodes before the commands. Possible uses are: copying files to temporary directories, copying source files.

##### run\_post\_file (optional)
This code is run on each of the nodes after the commands. Possible uses are: copying results back or removing unused data. 

##### config\_file
Simple configuration file for the job to be run in standard INI format. There should be two sections: BACKEND (specifying the backend to run on such as parallel/slurm), and BATCH_OPTION (specifying options for the generated batch).

The following is an example for the configuration file:

```ini
[BACKEND]
# Use SLURM backend on hpc cluster Lisa at SURFSara.
backend = slurm_lisa

[BATCH_OPTIONS]
# Set maximum running time in hh:mm:ss.
clock_wall_time = 02:00:00

# Set number of cores per node.
num_cores = 16

# Set job name.
job_name = asr_sim
```

User defined keys under the BATCH\_OPTIONS section are possible. For example, one could define the temporary directory ${TMP_DIR} in the config file, to swiftly change between different machines.

### Example

First go to the samples directory:

```bash
cd samples
```

Then run the batch generator with the parallel backend (assuming the GNU parallel is installed):

```bash
python asr_batch.py x.csv params.csv parallel.ini
```

There should be a directory called "batch.parallel/my\_test/" in which a batch script called "batch.sh" is present.

Run the batch script:

```bash
batch.parallel/my_test/batch.sh
```

### Contributors

- Raoul Schram (r.d.schram@uu.nl, [@qubixes](github.com/qubixes))


