# Batchgen Command Line Interface (CLI)

The batchgen CLI can be invoked from the command line. It requires Python and Parallel to be installed, but no understanding of either. It is invoked by:

```bash
batchgen command_file config_file ${OPTIONS}
```

### Arguments

##### command_file

This is a script file that you want to run/parallelize. Every line should be a simple shell command (no backgrounding (&) necessary). Lines with a "#", and lines with only whitespace are ignored.

##### [config_file](config.md)

Configuration file for the job to be run in standard INI format. Readable by humans and configparser (Python). Templates are available in the samples/ folder. For a detailed description of how to construct configuration files, see [here](config.md)

### Options

##### -f, --force-overwrite

With this option enabled, batchgen will clear out the batch directory from any *.sh files. Not supplying it is the more safe option, and should never overwrite or delete anything.

##### -pre, --pre-commands PRE\_COM\_FILE 

This is code that is run on each of the node(s) before the commands. Possible uses are: copying files to temporary directories, copying source files.

##### -post, --post-commands POST\_COM\_FILE 

This code is run on each of the nodes after the commands. Possible uses are: copying results back or removing unused data.

##### -pp, --pre-post-commands PRE\_POST\_FILE

The PRE\_POST\_FILE should be a combination of the pre- and post-command files. It overrides any pre- or post-commands, so provide one or the other. An example of such a file is:

```bash
## PRE_COMMANDS ##

if [ "${backend}" == "slurm_lisa" ]; then
    module load eb
    module load Python/3.6.1-intel-2016b
fi

mkdir -p ${tmp_dir}
cd ${base_dir}

## POST_COMMANDS ##

mkdir -p ${output_dir}
cp ${tmp_dir}/sum*.dat ${output_dir}
```

Notice the headers "## PRE\_COMMANDS ##" and "## POST\_COMMANDS ##", which denote the start of their respective sections.