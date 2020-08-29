#!/bin/env python3
# The main program.

# Configurables
ASSETS_THEME      = 'thiagodnf'
TILES_SHOW_HIDDEN = True
WINDOW_TITLE      = 'Wumpus World'
FONT              = 'Consolas'
AUTOSTEP_DELAY    = 100 # ms
KEYB_OPEN         = 'z'
KEYB_RESET        = 'x'
KEYB_STEP         = 'c'
KEYB_AUTOSTEP     = 'v'

####################

import os
import controller

# Working directories
BASE_DIR   = os.path.dirname(os.path.realpath(__file__)) + '/..'
MAPS_DIR   = BASE_DIR + '/maps'
ASSETS_DIR = BASE_DIR + '/assets/' + ASSETS_THEME

# GUI: constants
TILE_SIZE   = 64
WINDOW_UNIT = 16

# GUI: onboarding messages (status, log)
ONBOARDING_MSG = [
# (Status)
"""Wumpus World
OPEN A MAP TO BEGIN.
""",

# (Log) keyboard shortcut hints
"""
Use the buttons on GUI, or press the following keys:
[Z] Open  : open a mapfile
[X] Reset : reset the game
[C] Step  : advance current game by one step
[V] Play  : toggle autostep mode

How to read the status bar:
MAP: (G)old, (W)umpus, (P)it count
PLAYER: current location and orientation,
        (a)rrows used, (s)core
"""
]

####################

if __name__ == "__main__":
    main_app = controller.Controller()
    main_app.start()
