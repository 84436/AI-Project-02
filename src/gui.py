#!/bin/env python3
# GUI using Tkinter
# NOTE: IT'S A CALLBACK MESS (?)

from tkinter import *
from tkinter.filedialog import *
from tkinter.scrolledtext import *
from tkinter.font import *
from tkinter.ttk import *

from os import path
from main import BASE_DIR, MAPS_DIR, ONBOARDING_MSG

# Asset theme/set
ASSETS_THEME = 'thiagodnf'
ASSETS_DIR = BASE_DIR + '/assets/' + ASSETS_THEME

class WumpusGUI():
    """Wumpus GUI instance, powered by Tk/Ttk.
    """

    def __init__(self, callback_dict, loc_invert_helper):
        """All inits go here (for now.)
        """

        # Constants
        self.TILE_SIZE      = 64
        self.WINDOW_UNIT    = 16
        self.WINDOW_TITLE   = 'Wumpus World'
        self.FONT           = 'Consolas'
        self.AUTOSTEP_DELAY = 100 # ms
        self.KEYB_OPEN      = 'z'
        self.KEYB_RESET     = 'x'
        self.KEYB_STEP      = 'c'
        self.KEYB_AUTOSTEP  = 'v'

        # Root window
        self.root = Tk()
        self.root.title(self.WINDOW_TITLE)
        self.root.geometry('{}x{}'.format(3*self.WINDOW_UNIT + 17*self.TILE_SIZE, 6*self.WINDOW_UNIT + 10*self.TILE_SIZE))
        self.root.resizable(0, 0)
        self.root.configure(background='#ffffff')

        # Buttons
        Style().configure('TButton', font=self.FONT, background='#ffffff')
        self.button_open  = Button(text='@ OPEN' , command=self.map_open_dialog)
        self.button_reset = Button(text='* RESET', command=self.game_reset)
        self.button_step  = Button(text='> STEP' , command=self.game_step)
        self.button_play  = Button(text='>> PLAY', command=self.game_play)

        # Buttons/Callbacks: Keybindings
        # On keypress, these also emit a second parameter called 'events'
        # that is not really needed here. A lambda is thus used
        # to ignore that event.
        # https://codereview.stackexchange.com/a/193357
        self.root.bind(self.KEYB_OPEN,      lambda event: self.map_open_dialog())
        self.root.bind(self.KEYB_RESET,     lambda event: self.game_reset())
        self.root.bind(self.KEYB_STEP,      lambda event: self.game_step())
        self.root.bind(self.KEYB_AUTOSTEP,  lambda event: self.game_play())

        # Buttons: External callbacks
        self.ext_map_get  = callback_dict['map_get']
        self.ext_map_open = callback_dict['map_open']
        self.ext_reset    = callback_dict['reset']
        self.ext_step     = callback_dict['step']
        self.invert_loc   = loc_invert_helper

        # Canvas
        self.canvas = Canvas (background='#000000')
        self.objects = {
            'gold'          : PhotoImage(file=ASSETS_DIR + '/gold.png'),
            'pit'           : PhotoImage(file=ASSETS_DIR + '/pit.png'),
            'wumpus'        : PhotoImage(file=ASSETS_DIR + '/wumpus.png'),
            'breeze'        : PhotoImage(file=ASSETS_DIR + '/breeze.png'),
            'stench'        : PhotoImage(file=ASSETS_DIR + '/stench.png'),
            'tile'          : PhotoImage(file=ASSETS_DIR + '/tile.png'),
            'tile_hidden'   : PhotoImage(file=ASSETS_DIR + '/tile_hidden_alpha80.png'),
            'player_up'     : PhotoImage(file=ASSETS_DIR + '/player_up.png'),
            'player_down'   : PhotoImage(file=ASSETS_DIR + '/player_down.png'),
            'player_left'   : PhotoImage(file=ASSETS_DIR + '/player_left.png'),
            'player_right'  : PhotoImage(file=ASSETS_DIR + '/player_right.png'),
        }

        # Text views
        self.status_font = Font          (family=self.FONT, size=12)
        self.log_font    = Font          (family=self.FONT, size=11)
        self.status      = Text          (font=self.status_font,  background='#f0f0f0', foreground='#000000', relief=FLAT)
        self.log         = ScrolledText  (font=self.log_font,     background='#f0f0f0', foreground='#000000', relief=FLAT)
        self.status.tag_configure        ('text-bold', font='-family {} -weight bold'.format(self.FONT))

        # Layout
        self.button_open     .place(x=(1 + 0*9.25)*self.WINDOW_UNIT, y=16, width=9.25*self.WINDOW_UNIT, height=3*self.WINDOW_UNIT)
        self.button_reset    .place(x=(2 + 1*9.25)*self.WINDOW_UNIT, y=16, width=9.25*self.WINDOW_UNIT, height=3*self.WINDOW_UNIT)
        self.button_step     .place(x=(3 + 2*9.25)*self.WINDOW_UNIT, y=16, width=9.25*self.WINDOW_UNIT, height=3*self.WINDOW_UNIT)
        self.button_play     .place(x=(4 + 3*9.25)*self.WINDOW_UNIT, y=16, width=9.25*self.WINDOW_UNIT, height=3*self.WINDOW_UNIT)
        self.canvas          .place(x=1*self.WINDOW_UNIT, y=5*self.WINDOW_UNIT, width=10*self.TILE_SIZE, height=10*self.TILE_SIZE)
        self.status          .place(x=2*self.WINDOW_UNIT + 10*self.TILE_SIZE, y=1*self.WINDOW_UNIT, width=7*self.TILE_SIZE, height=3*self.WINDOW_UNIT)
        self.log             .place(x=2*self.WINDOW_UNIT + 10*self.TILE_SIZE, y=5*self.WINDOW_UNIT, width=7*self.TILE_SIZE, height=10*self.TILE_SIZE)
        
        # Autostep / Game over
        self.__autostep_job_cancel_id = None
        self.__game_over = False

        # Run the onboarding screen
        self.__onboarding()

    def __onboarding(self):
        # Disable buttons and keys
        self.root.bind(self.KEYB_RESET, lambda event: None)
        self.root.bind(self.KEYB_STEP, lambda event: None)
        self.root.bind(self.KEYB_AUTOSTEP, lambda event: None)
        self.button_reset['state'] = DISABLED
        self.button_step['state'] = DISABLED
        self.button_play['state'] = DISABLED

        # Write messages
        self.status.insert(END, ONBOARDING_MSG[0], 'text-bold')
        self.log_write(ONBOARDING_MSG[1])

    def status_update(self):
        _, cgold, cpit, cwumpus       = self.ext_map_get()._stats.values()
        ploc, porient, parrow, pscore = self.ext_map_get()._player.values()
        self.status.delete(1.0, END)
        self.status.insert(END, 'MAP    : '  , 'text-bold')
        self.status.insert(END, '{}G {}P {}W'.format(cgold, cpit, cwumpus))
        self.status.insert(END, '\n'         )
        self.status.insert(END, 'PLAYER : '  , 'text-bold')
        self.status.insert(END, '{} {} a={} s={}'.format(self.invert_loc(ploc), porient, parrow, pscore))

    def canvas_update(self):
        self.canvas.delete('all')
        for y, each_line in enumerate(self.ext_map_get()._map):
            for x, each_tile in enumerate(each_line):
                # Draw tile first
                self.canvas.create_image(self.TILE_SIZE*x, self.TILE_SIZE*y, anchor=NW, image=self.objects['tile'])

                # Bad stuff for player:
                if any(item in each_tile for item in 'PW'):
                    if 'P' in each_tile: self.canvas.create_image(self.TILE_SIZE*x, self.TILE_SIZE*y, anchor=NW, image=self.objects['pit'])
                    if 'W' in each_tile: self.canvas.create_image(self.TILE_SIZE*x, self.TILE_SIZE*y, anchor=NW, image=self.objects['wumpus'])

                # Good stuff for player?
                elif any(item in each_tile for item in 'GBS'):
                    if 'G' in each_tile:   self.canvas.create_image(self.TILE_SIZE*x, self.TILE_SIZE*y, anchor=NW, image=self.objects['gold'])
                    if 'B' in each_tile:   self.canvas.create_image(self.TILE_SIZE*x, self.TILE_SIZE*y, anchor=NW, image=self.objects['breeze'])
                    if 'S' in each_tile:   self.canvas.create_image(self.TILE_SIZE*x, self.TILE_SIZE*y, anchor=NW, image=self.objects['stench'])
                
                # Hide the tile if not discovered
                if 'X' in each_tile:
                    self.canvas.create_image(self.TILE_SIZE*x, self.TILE_SIZE*y, anchor=NW, image=self.objects['tile_hidden'])

        # Player    
        (px, py), po = self.ext_map_get()._player['loc'], self.ext_map_get()._player['orient']
        if po == 'U':   self.canvas.create_image(self.TILE_SIZE*px, self.TILE_SIZE*py, anchor=NW, image=self.objects['player_up'])
        elif po == 'D': self.canvas.create_image(self.TILE_SIZE*px, self.TILE_SIZE*py, anchor=NW, image=self.objects['player_down'])
        elif po == 'L': self.canvas.create_image(self.TILE_SIZE*px, self.TILE_SIZE*py, anchor=NW, image=self.objects['player_left'])
        elif po == 'R': self.canvas.create_image(self.TILE_SIZE*px, self.TILE_SIZE*py, anchor=NW, image=self.objects['player_right'])

    def log_write(self, msg):
        self.log.insert(END, msg + '\n')
        self.log.see(END)
    
    def log_clear(self):
        self.log.delete(1.0, END)

    ####################

    def map_open_dialog(self):
        self.game_pause()
        mapfile = askopenfilename(
            initialdir=MAPS_DIR,
            title='Select map file',
            filetypes=(
                ('Plain text map files', '*.txt'),
                ('All files', '*.*')
            )
        )
        if mapfile != '':
            self.log_clear()
            self.ext_map_open(mapfile)
            self.log_write('Map opened: {}'.format(path.basename(mapfile)))
            self.game_reset()

    def game_reset(self):
        # Lift the flag and reset autostep
        self.__game_over = False
        self.game_pause()

        # Call external reset function (should reset map and player)
        self.ext_reset()

        # Reset all buttons and keybindings
        self.button_reset['state'] = NORMAL
        self.button_step['state'] = NORMAL
        self.button_play['state'] = NORMAL
        self.root.bind(self.KEYB_RESET, lambda event: self.game_reset())
        self.root.bind(self.KEYB_STEP, lambda event: self.game_step())
        self.root.bind(self.KEYB_AUTOSTEP, lambda event: self.game_play())

        # Update and log
        self.status_update()
        self.canvas_update()
        self.log_write('Map and player reset')

    def game_step(self):
        self.ext_step()
        self.status_update()
        self.canvas_update()
    
    def game_autostep(self):
        self.game_step()
        if not self.__game_over:
            self.__autostep_job_cancel_id = self.root.after(self.AUTOSTEP_DELAY, self.game_autostep)

    def game_play(self):
        # Log
        self.log_write('Autostep started with delay of {}ms'.format(self.AUTOSTEP_DELAY))

        # Rebind buttons and keys
        self.button_play['text'] = '|| PAUSE'
        self.button_play['command'] = self.game_pause
        self.root.bind(self.KEYB_AUTOSTEP, lambda event: self.game_pause())

        # Start autostep
        self.game_autostep()
    
    def game_pause(self):
        # Stop autostep
        if self.__autostep_job_cancel_id is not None:
            self.root.after_cancel(self.__autostep_job_cancel_id)
            self.log_write('Autostep stopped')
        
        # Rebind buttons and keys
        self.button_play['text'] = '>> PLAY'
        self.button_play['command'] = self.game_play
        self.root.bind(self.KEYB_AUTOSTEP, lambda event: self.game_play())

    def game_over(self):
        # Raise the flag (to stahp it)
        self.__game_over = True
        self.game_pause()
        self.__autostep_job_cancel_id = None

        # Disable buttons and keys
        self.button_step['state'] = DISABLED
        self.button_play['state'] = DISABLED
        self.root.bind(self.KEYB_STEP, lambda event: None)
        self.root.bind(self.KEYB_AUTOSTEP, lambda event: None)
