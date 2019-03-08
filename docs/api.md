# Batchgen Application Programming Interface (API)

Batchgen can be called directly from python itself. There are two API's available: file based, and string based. The file based API closely resembles the CLI, and calls the "deeper" string based API internally. The advantage of the string based API is that it alleviates the need to create some files.

### File based API

The base function is defined as follows:

```python
batch_from_files(command_file, config_file, pre_post_file=None, pre_com_file=None, 
  		 post_com_file=None, force_clear=False):
```

See the [CLI](cli.md) to understand what the different files are, and how they are formatted.

### String based API

The configuration file is never passed in memory, but otherwise it is the same function, except all files are turned into strings:

```python
def batch_from_strings(command_string, config_file, pre_com_string="",
                       post_com_string="", force_clear=False)
```

Again, see the [CLI](cli.md) for explanations and formats of the arguments.
