

##### input_script
This is a script file that you want to run/parallelize. Every line should be a simple bash command (no backgrounding necessary).

##### [config_file](config.md)
Configuration file for the job to be run in standard INI format. Readable by humans and configparser (Python) alike. Templates are available in the samples/ folder. For a detailed description of how to construct configuration files, see [here](config.md)

##### run\_pre\_file (optional)
This is code that is run on each of the nodes before the commands. Possible uses are: copying files to temporary directories, copying source files. Overridden by pre\_post\_file option in the configuration file.

##### run\_post\_file (optional)
This code is run on each of the nodes after the commands. Possible uses are: copying results back or removing unused data. Overridden by pre\_post\_file option in the configuration file.

