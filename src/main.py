#!/bin/env python3

import os
from sys import argv

from map import *

# Working directory
BASE_DIR   = os.path.dirname(os.path.realpath(__file__)) + '/..'
MAPS_DIR   = BASE_DIR + '/maps'

# Defaults
DEFAULT_MAP = '10G-10P-10W-base'

if __name__ == "__main__":
    if len(argv) == 1:
        mapfile = DEFAULT_MAP
    elif len(argv) == 2:
        mapfile = argv[1]
    else:
        print('Syntax: main.py [mapfile.txt, defaults to {}]'.format(DEFAULT_MAP))
        exit(-1)
    
    with open(MAPS_DIR + '/' + mapfile + '.txt', 'r') as f:
        m = Map(f)
    
    print(m)
    print(m._stats)
