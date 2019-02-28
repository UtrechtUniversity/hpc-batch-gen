'''
Created on 27 Feb 2019

@author: qubix
'''

import argparse

from batchgen.base import generate_batch_scripts
from batchgen import __version__


def main():
    # Parse the arguments.
    parser = argparse.ArgumentParser(
        prog='batchgen',
        description="Create batch files for HPC environments.",
    )

    parser.add_argument(
        'command_file',
        type=str,
        default=None,
        help='Commands to be executed in parallel',
    )

    parser.add_argument(
        'config_file',
        type=str,
        default=None,
        help='Configuration file (e.g. parallel.ini)'
    )

    parser.add_argument(
        '-pre', '--pre-commands',
        type=str,
        default='/dev/null',
        dest='run_pre_file',
        help='Commands to be executed for all nodes before command execution',
    )

    parser.add_argument(
        '-post', '--post-commands',
        type=str,
        default='/dev/null',
        dest='run_post_file',
        help='Commands to be executed for all nodes after command execution',
    )

    # Version
    parser.add_argument(
        "-v", "--version",
        action='version',
        version='%(prog)s {version}'.format(version=__version__))

    args = parser.parse_args()

    generate_batch_scripts(**vars(args))


# If used from the command line.
if __name__ == '__main__':
    main()
