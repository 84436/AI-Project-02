#!/bin/env python3
# WutWumpus: You don't want to play this.
# Not (Won't?) implemented: death check (i.e. the player is invisible by default), "game over" state

from functools import partial
from tkinter import *
from tkinter.filedialog import *
from tkinter.scrolledtext import *
from tkinter.font import *
from tkinter.ttk import *

from map import *

# Working directory
BASE_DIR   = os.path.dirname(os.path.realpath(__file__)) + '/..'
MAPS_DIR   = BASE_DIR + '/maps'

# Defaults
DEFAULT_MAP = '10G-10P-10W-base'
mapfile     = DEFAULT_MAP

##################################################

def map_strip_x(map_object):
    map_lines = str(map_object).replace('X', '').splitlines()
    map_lines_stripped = [
        list(map(str.strip, each_line.split('.')))
        for each_line in map_lines
    ]
    max_tile_size = max([
        len(each_tile)
        for each_row in map_lines_stripped for each_tile in each_row
    ])
    map_stripped = '\n'.join([
        '.'.join([
            each_tile.rjust(max_tile_size)
            for each_tile in each_line
        ])
        for each_line in map_lines_stripped
    ])
    return map_stripped

def status_log_intro():
    global mapfile, status, log
    mapfile_msg = 'DEFAULT ({})'.format(DEFAULT_MAP) if mapfile == DEFAULT_MAP else mapfile
    status.delete(1.0, END)
    status.insert(END, 'WutWumpus 0.21')
    log.delete(1.0, END)
    log.insert(END, 'Loaded map: {}\n'.format(mapfile_msg))
    log.insert(END, 'Press VIEW to reveal map and statuses.\n\n')

def button_opendialog():
    global m, mapfile, status, log
    mapfile = askopenfilename(
        initialdir=MAPS_DIR,
        title='Select map file',
        filetypes=(
            ('Plain text map files', '*.txt'),
            ('All files', '*.*')
        )
    )
    if mapfile != '':
        with open(mapfile, 'r') as f: m = Map(f)
        status_log_intro()

def button_callback(action):
    global m, log, status
    px, py = m._player['loc']

    # Up/Down/Left/Right/Move
    if action == 'up':
        m.orient((px, py-1))
        log.insert(END, 'Player orient UP\n')
    if action == 'down':
        m.orient((px, py+1))
        log.insert(END, 'Player orient DOWN\n\n')
    if action == 'left':
        m.orient((px-1, py))
        log.insert(END, 'Player orient LEFT\n\n')
    if action == 'right':
        m.orient((px+1, py))
        log.insert(END, 'Player orient RIGHT\n\n')
    if action == 'move':
        m.move()
        log.insert(END, 'Player moved\n')
        log.insert(END, 'Reveal: {}\n'.format(m.reveal()))
        log.insert(END, '\n')
    
    # Shoot/Gold
    if action == 'shoot':
        m.shoot()
        log.insert(END, 'Player shoot\n\n')
    if action == 'gold':
        m.get_gold()
        log.insert(END, 'Player pick up gold\n\n')
    
    # View/Clear log
    if action == 'view':
        log.insert(END, 'Map view\n{}\n\n'.format(map_strip_x(m)))
        log.insert(END, 'Reveal: {}\n'.format(m.reveal()))
        log.insert(END, '\n')
    if action == 'clear':
        log.delete(1.0, END)
    
    # Status bar update
    ms, cg, cp, cw = m._stats.values()
    lo, on, ar, sc = m._player.values()
    status.delete(1.0, END)
    status.insert(END, 'Map    : {}*{}, {}P {}W {}G\n'.format(ms, ms, cp, cw, cg))
    status.insert(END, 'Player : {} {}, arrow={}, score={}'.format(lo, on, ar, sc))

    # Scroll log
    log.see(END)

##################################################

if __name__ == "__main__":
    # Open map
    with open(MAPS_DIR + '/' + mapfile + '.txt', 'r') as f:
        m = Map(f)
    
    # Tk init
    root = Tk()
    root.title('WutWumpus')
    root.resizable(0, 0)

    # Styling
    root.configure(background='#000000')
    fixedsys_green = Font(family='FixedSys', size=18)
    Style().configure('TButton', font='FixedSys', background='#000000')

    # Text views    
    status = Text           (font=fixedsys_green, background='#00ff00', foreground='#000000', width=81, height=2)
    log    = ScrolledText   (font=fixedsys_green, background='#000000', foreground='#00ff00', width=80, height=25)

    # Buttons
    button_orient_u = Button(text='^ UP',       command=partial(button_callback, 'up')    )
    button_orient_d = Button(text='V DOWN',     command=partial(button_callback, 'down')  )
    button_orient_l = Button(text='< LEFT',     command=partial(button_callback, 'left')  )
    button_orient_r = Button(text='> RIGHT',    command=partial(button_callback, 'right') )
    button_move     = Button(text='* MOVE',     command=partial(button_callback, 'move')  )
    button_shoot    = Button(text='+ SHOOT',    command=partial(button_callback, 'shoot') )
    button_gold     = Button(text='$ GOLD',     command=partial(button_callback, 'gold')  )
    button_open     = Button(text='@ OPEN',     command=button_opendialog                 )
    button_clear    = Button(text='% CLEAR',    command=partial(button_callback, 'clear') )
    button_show     = Button(text='# VIEW',     command=partial(button_callback, 'view')  )

    # Layout
    status          .grid(row=0, columnspan=10)
    log             .grid(row=1, columnspan=10)
    button_orient_u .grid(row=2, column=0)
    button_orient_d .grid(row=2, column=1)
    button_orient_l .grid(row=2, column=2)
    button_orient_r .grid(row=2, column=3)
    button_move     .grid(row=2, column=4)
    button_shoot    .grid(row=2, column=5)
    button_gold     .grid(row=2, column=6)
    button_clear    .grid(row=2, column=7)
    button_show     .grid(row=2, column=8)
    button_open     .grid(row=2, column=9)

    # Begin
    status_log_intro()
    root.mainloop() 
