# batchgen
Package for generating batch scripts

## Usage
```bash
python3 batchgen.py input_script run_pre_file run_post_file
```

##### input_script
This is a script file that you want to run/parallelize. Every line should be a simple bash command (no backgrounding necessary).

##### run\_pre\_file
This is code that is run on each of the nodes before the commands. Things like copying to temporary directories, copying source files.

##### run\_pre\_file
This code is run on each of the nodes after the commands. Think, copying results back, removing unused data.

##### slurm.cfg
Simple configuration file for the job to be run. The following options are recommended (but not mandatory) to be set:


<i>clock_wall_timego</i>: Maximum time to run. <br> 
<i>num_cores</i>: Number of cores per node. <br>  
<i>job_name</i>: Name of the whole job.  <br>


User defined keys are also possible. For example, one could define the temporary directory ${TMP_DIR} in the config file, so one could more easily change between different machines.

## Example

First copy the files in the samples directory to the base directory:

```bash
cp samples/* .
```

Then run the asr script:

```bash
python3 asr_batch.py x.csv params.csv
```

There should be a directory called "batch/asr_sim" in which batch scripts are present batch[0-18].sh

The output of the python script is a bash command to submit all the batch scripts:

```bash
for FILE in $BASE_DIR/batch/asr_sim/batch*.sh; do 
	sbatch $FILE; 
done
```
