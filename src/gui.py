#!/bin/env python3
# GUI using Tkinter
# NOTE: IT'S AN IMPORT MESS

from tkinter import *
from tkinter.filedialog import *
from tkinter.scrolledtext import *
from tkinter.font import *
from tkinter.ttk import *

import main

# Asset theme/set
ASSETS_THEME = 'thiagodnf'
ASSETS_DIR = main.BASE_DIR + '/assets/' + ASSETS_THEME

####################

# Propagate map object to this module
GUI_MAP_OBJECT = None
def map_receive(map_object):
    global GUI_MAP_OBJECT
    GUI_MAP_OBJECT = map_object

# File open dialog
def file_open():
    mapfile = askopenfilename(
        initialdir=main.MAPS_DIR,
        title='Select map file',
        filetypes=(
            ('Plain text map files', '*.txt'),
            ('All files', '*.*')
        )
    )
    if mapfile != '':
        main.map_open(mapfile)
        status_update()
        canvas_update()

####################
# Tk init

# Constants
TILE_SIZE    = 64
WINDOW_UNIT  = 16
WINDOW_TITLE = 'Wumpus World'
FONT         = 'Consolas'

# Root window
root = Tk()
root.title(WINDOW_TITLE)
root.geometry('{}x{}'.format(3*WINDOW_UNIT + 15*TILE_SIZE, 6*WINDOW_UNIT + 10*TILE_SIZE))
root.resizable(0, 0)
root.configure(background='#ffffff')

# Buttons
Style().configure('TButton', font=FONT, background='#ffffff')
button_open  = Button(text='@ OPEN' , command=file_open)
button_reset = Button(text='* RESET')
button_step  = Button(text='> STEP' )
button_play  = Button(text='>> PLAY')
button_pause = Button(text='|| PAUSE')

# Canvas
canvas = Canvas (background='#000000')

# Text views
status_font = Font          (family=FONT, size=12)
log_font    = Font          (family=FONT, size=12)
status      = Text          (font=status_font,  background='#f0f0f0', foreground='#000000', relief=FLAT)
log         = ScrolledText  (font=log_font,     background='#f0f0f0', foreground='#000000', relief=FLAT)
status.tag_configure        ('text-center'      , justify='center')
status.tag_configure        ('text-center-bold' , justify='center', font='-family {} -weight bold'.format(FONT))
status.tag_configure        ('text-bold'                          , font='-family {} -weight bold'.format(FONT))

# Layout
button_open     .place(x=(1 + 0*9.25)*WINDOW_UNIT, y=16, width=9.25*WINDOW_UNIT, height=3*WINDOW_UNIT)
button_reset    .place(x=(2 + 1*9.25)*WINDOW_UNIT, y=16, width=9.25*WINDOW_UNIT, height=3*WINDOW_UNIT)
button_step     .place(x=(3 + 2*9.25)*WINDOW_UNIT, y=16, width=9.25*WINDOW_UNIT, height=3*WINDOW_UNIT)
button_play     .place(x=(4 + 3*9.25)*WINDOW_UNIT, y=16, width=9.25*WINDOW_UNIT, height=3*WINDOW_UNIT)
canvas          .place(x=1*WINDOW_UNIT, y=5*WINDOW_UNIT, width=10*TILE_SIZE, height=10*TILE_SIZE)
status          .place(x=2*WINDOW_UNIT + 10*TILE_SIZE, y=1*WINDOW_UNIT, width=5*TILE_SIZE, height=3*WINDOW_UNIT)
log             .place(x=2*WINDOW_UNIT + 10*TILE_SIZE, y=5*WINDOW_UNIT, width=5*TILE_SIZE, height=10*TILE_SIZE)

# Images
objects = {
    'gold'          : PhotoImage(file=ASSETS_DIR + '/gold.png'),
    'pit'           : PhotoImage(file=ASSETS_DIR + '/pit.png'),
    'wumpus'        : PhotoImage(file=ASSETS_DIR + '/wumpus.png'),
    'tile'          : PhotoImage(file=ASSETS_DIR + '/tile.png'),
    'tile_hidden'   : PhotoImage(file=ASSETS_DIR + '/tile_hidden.png'),
    'player_up'     : PhotoImage(file=ASSETS_DIR + '/player_up.png'),
    'player_down'   : PhotoImage(file=ASSETS_DIR + '/player_down.png'),
    'player_left'   : PhotoImage(file=ASSETS_DIR + '/player_left.png'),
    'player_right'  : PhotoImage(file=ASSETS_DIR + '/player_right.png'),
}

####################
# GUI utilities

def status_update():
    _, cgold, cpit, cwumpus       = GUI_MAP_OBJECT._stats.values()
    ploc, porient, parrow, pscore = GUI_MAP_OBJECT._player.values()
    status.delete(1.0, END)
    status.insert(END, 'MAP    : '  , 'text-bold')
    status.insert(END, '{}G {}P {}W'.format(cgold, cpit, cwumpus))
    status.insert(END, '\n'         )
    status.insert(END, 'PLAYER : '  , 'text-bold')
    status.insert(END, '{} {} a={} s={}'.format(ploc, porient, parrow, pscore))

def canvas_update():
    canvas.delete('all')
    for y, each_line in enumerate(GUI_MAP_OBJECT._map):
        for x, each_tile in enumerate(each_line):
            # Draw tile first
            canvas.create_image(TILE_SIZE*x, TILE_SIZE*y, anchor=NW, image=objects['tile'])

            # Hidden tile
            #if 'X' in each_tile:
            #    canvas.create_image(TILE_SIZE*x, TILE_SIZE*y, anchor=NW, image=objects['tile_hidden'])

            # Objects
            #else:
            if 'G' in each_tile:   canvas.create_image(TILE_SIZE*x, TILE_SIZE*y, anchor=NW, image=objects['gold'])
            elif 'P' in each_tile: canvas.create_image(TILE_SIZE*x, TILE_SIZE*y, anchor=NW, image=objects['pit'])
            elif 'W' in each_tile: canvas.create_image(TILE_SIZE*x, TILE_SIZE*y, anchor=NW, image=objects['wumpus'])

    # Player    
    (px, py), po = GUI_MAP_OBJECT._player['loc'], GUI_MAP_OBJECT._player['orient']
    if po == 'U':   canvas.create_image(TILE_SIZE*px, TILE_SIZE*py, anchor=NW, image=objects['player_up'])
    elif po == 'D': canvas.create_image(TILE_SIZE*px, TILE_SIZE*py, anchor=NW, image=objects['player_down'])
    elif po == 'L': canvas.create_image(TILE_SIZE*px, TILE_SIZE*py, anchor=NW, image=objects['player_left'])
    elif po == 'R': canvas.create_image(TILE_SIZE*px, TILE_SIZE*py, anchor=NW, image=objects['player_right'])
