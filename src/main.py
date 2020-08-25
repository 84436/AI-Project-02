#!/bin/env python3
# The main program.

import os
from sys import argv

from map import *
import gui

# Working directory
BASE_DIR   = os.path.dirname(os.path.realpath(__file__)) + '/..'
MAPS_DIR   = BASE_DIR + '/maps'

# Defaults
DEFAULT_MAP = MAPS_DIR + '/10G-10P-10W-base.txt'
m           = Map()

def map_open(mapfile):
    global m
    with open(mapfile, 'r') as f:
        m = Map(f)
    gui.map_receive(m)

if __name__ == "__main__":
    map_open(DEFAULT_MAP)
    
    # test
    gui.log.insert(gui.END, 'UI Prototype?')
    gui.canvas_update()
    gui.status_update()
    gui.root.mainloop()
