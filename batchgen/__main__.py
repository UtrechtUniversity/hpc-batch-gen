'''
Created on 27 Feb 2019

@author: qubix
'''

import sys

from batchgen.base import generate_batch_scripts


def main():
    if len(sys.argv) <= 3:
        print("Error: need three arguments (script file)")
    else:
        generate_batch_scripts(*sys.argv[1:])


# If used from the command line.
if __name__ == '__main__':
    main()
