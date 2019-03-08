# Batchgen
Package for generating simple batch scripts in HPC environments. Currently available: GNU Parallel, SLURM backend. 

In its current implementation, it will only **create** the batch files for submission, and **not** actually submit them. This might change in future versions.

### Requirements:

##### Software

- GNU Parallel
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

There are two ways to use the *batchgen* package. 

##### [Command line interface (CLI)](doc/cli.md)

The first is using the command line interface, which does need Python and GNU Parallel to be installed, but no programming in Python is required to use it. The basic command is the following (`bash batchgen -h` for a help file):

```bash
batchgen command_file config_file [-pre pre_file] [-post post_file] [-pp pre_post_file] [-f]
```

If this returns a "command not found" error, set your PATH to include the installation directory, or use the following:

```bash
python -m batchgen command_file config_file [-pre pre_file] [-post post_file] [-f]
```

For a more detailed description see [here](doc/cli.md).

##### [Application Programming Interface (API)](doc/api.md)

The second option is to use the package directly within Python. There are two main ways to access the package. The first is similar to access provided through the CLI:

```python
batch_from_files(command_file, config_file, pre_post_file=None,
					    pre_com_file=None, post_com_file=None, force_clear=False)
```

The second method bypasses the need to create as many files by supplying the package with strings (except the configuration file):

```python
batch_from_strings(command_string, config_file, pre_com_string="",
                       post_com_string="", force_clear=False)
```

A more detailed description is available [here](doc/api.md)

### Example

First go to the samples directory:

```bash
cd samples
```

Then run the batch generator with the parallel backend (assuming the GNU parallel is installed):

```bash
batchgen command_list.sh parallel.ini
```

There should be a directory called "batch.parallel/my\_test/" in which a batch script called "batch.sh" is present.

Run the batch script:

```bash
batch.parallel/my_test/batch.sh
```

The output of this will be stored in the directory sum\_output. See the files sum.sh and command\_list.sh for what is computed.

### Contributors

- Raoul Schram (r.d.schram@uu.nl, [@qubixes](github.com/qubixes))


