#!/bin/env python3
# Dummy logic

from random import choice

class RandomPlayer():
    def __init__(self):
        self.__shoot_queue = []
    
    def reset(self):
        self.__shoot_queue.clear()

    def make_move(self, map_object):
        # If action queue is still there
        if self.__shoot_queue:
            return self.__shoot_queue.pop()

        current = map_object.reveal()
        adjacents = map_object.adjacents()
        
        # Gold
        if 'G' in current:
            return 'gold'
        
        # Wumpus
        if 'S' in current:
            if not self.__shoot_queue:
                for each in adjacents:
                    self.__shoot_queue.append(('shoot', each))
            return self.__shoot_queue.pop()
        
        # If no other options
        return choice(adjacents)
