"""
Main execution file for batchgen tools.
Python programs can directly access generate_batch_scripts,
without going through the CLI.

@author: Raoul Schram
"""

import argparse
import sys

from batchgen import batch_from_files
from batchgen import __version__


def parse_arguments(args):
    # Parse the arguments.
    parser = argparse.ArgumentParser(
        prog="batchgen",
        description="Create batch files for HPC environments.",
    )

    parser.add_argument(
        "command_file",
        type=str,
        default=None,
        help="Commands to be executed in parallel.",
    )

    parser.add_argument(
        "config_file",
        type=str,
        default=None,
        help="Configuration file (e.g. parallel.ini).",
    )

    parser.add_argument(
        "-pre", "--pre-commands",
        type=str,
        default=None,
        dest="pre_com_file",
        help="File with commands to be executed on all nodes before command "
             "execution.",
    )

    parser.add_argument(
        "-post", "--post-commands",
        type=str,
        default=None,
        dest="post_com_file",
        help="File with commands to be executed on all nodes after command "
             "execution.",
    )

    parser.add_argument(
        "-pp", "--pre-post-commands",
        type=str,
        default=None,
        dest="pre_post_file",
        help="File with commands to be executed before and after command "
             "execution.",
    )

    parser.add_argument(
        "-f", "--force-overwrite",
        dest="force_clear",
        action="store_const",
        const=True,
        default=False,
        help="If batch directory exists, clear contents.",
    )

    # Version
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__))

    args = parser.parse_args(args)
    return vars(args)


def main():
    args = parse_arguments(sys.argv[1:])
    batch_from_files(**args)


# If used from the command line.
if __name__ == "__main__":
    main()
