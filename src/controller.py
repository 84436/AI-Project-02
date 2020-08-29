#!/bin/env python3
# Game controller (GUI x Map x Player)

from map import *
from gui import *
from logic_random import *

class Controller():
    def __init__(self):
        self.map = Map()
        self.player = SupperInteligentPlayer()
        self.gui = WumpusGUI(
            {
                'map_get': self.cb_map_get,
                'map_open': self.cb_map_open,
                'reset': self.cb_reset,
                'step': self.cb_step
            },
            self.loc_invert_helper
        )
    
    def start(self):
        self.gui.root.mainloop()

    def loc_invert_helper(self, loc):
        mapsize = self.map._stats['mapsize']
        x, y = loc
        return (x + 1, mapsize - y)

    def cb_map_get(self):
        return self.map

    def cb_map_open(self, mapfile):
        with open(mapfile, 'r') as f: self.map = Map(f)    

    def cb_reset(self):
        self.map.reset()
        self.player.reset()

    def cb_step(self):
        # Player: make a move
        move = self.player.make_move(self.map)

        # Player: leave
        if move == 'leave':
            self.map.leave()
            self.gui.log_write('Player left the cave.')
            self.gui.game_over()
        
        # Player: pick up gold
        elif move == 'gold':
            self.map.get_gold()
            self.gui.log_write('GOLD: Picked up')

        # Player: shoot
        elif type(move) == tuple and move[0] == 'shoot':
            self.map.orient(move[1])
            self.map.shoot()
            self.gui.log_write('SHOOT: {}'.format(self.loc_invert_helper(move[1])))
        
        # Player: move
        elif type(move) == tuple:
            self.map.orient(move)
            self.map.move()
            self.gui.log_write('MOVE: {}, SENSE: {}'.format(self.loc_invert_helper(move), self.map.reveal()))

        # Game over check, player dead
        if any(x in self.map.reveal() for x in 'PW'):
            self.gui.log_write('Player dead')
            self.gui.game_over()
        
        # Game over check, player survived (out of wumpus and gold)
        if all(item == 0 for item in [self.map._stats['count_gold'], self.map._stats['count_wumpus']]):
            self.gui.log_write('Player survived.')
            self.gui.game_over()
