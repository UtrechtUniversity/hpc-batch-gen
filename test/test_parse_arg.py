"""
Test the argument parsing.

@author: Raoul Schram
"""


import shlex

from batchgen.__main__ import parse_arguments


def test_parse_arg():
    """ Test setting the arguments and retrieving them. """
    arguments = """command_file config_file -pre PRE_COM_FILE -post\
     POST_COM_FILE -pp PRE_POST_FILE --force-overwrite"""
    arguments = shlex.split(arguments)
    args = parse_arguments(arguments)
    assert args["command_file"] == "command_file"
    assert args["config_file"] == "config_file"
    assert args["pre_com_file"] == "PRE_COM_FILE"
    assert args["post_com_file"] == "POST_COM_FILE"
    assert args["pre_post_file"] == "PRE_POST_FILE"
    assert args["force_clear"]
