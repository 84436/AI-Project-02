#!/bin/env python3
# Map generator

from random import randrange
import os

# Parameters
# No checks will be applied on parameters; please make sure it's sane.
width        = 10
height       = 10
# count_pit    = 1
# count_wumpus = 1
# count_gold   = 1
count_pit    = randrange(0, 10+1)
count_wumpus = randrange(1, 10+1)
count_gold   = randrange(0, 10+1)

# Working directory
BASE_DIR   = os.path.dirname(os.path.realpath(__file__)) + '/..'
MAPS_DIR   = BASE_DIR + '/maps'

# Storage
set_blacklist = set()  # exclude me
breeze        = []
pit           = []
stench        = []
wumpus        = []
gold          = []
player        = None

# Subroutine: Generate a random location
random_loc = lambda : (randrange(0, width), randrange(0, height))

def adjacents(loc):
    """Get adjacents of a location.
    """
    x, y = loc
    adjacent_list = []
    if (x-1 >= 0)       : adjacent_list.append((x-1, y))
    if (x+1 <= width-1) : adjacent_list.append((x+1, y))
    if (y-1 >= 0)       : adjacent_list.append((x, y-1))
    if (y+1 <= width-1) : adjacent_list.append((x, y+1))
    return adjacent_list

def generate_map():
    """Randomly generate location of items on map based on given parameters.
    """
    global count_gold, count_pit, count_wumpus
    global gold, pit, breeze, wumpus, stench, player
    
    # Player
    player = random_loc()
    set_blacklist.add(player)
    for each in adjacents(player):
        set_blacklist.add(each)
    
    # Gold
    while count_gold > 0:
        gold_i = random_loc()
        if gold_i not in set_blacklist:
            set_blacklist.add(gold_i)
            gold.append(gold_i)
            count_gold -= 1
    
    # Pit
    while count_pit > 0:
        pit_i = random_loc()
        if pit_i not in set_blacklist:
            set_blacklist.add(pit_i)
            pit.append(pit_i)
            count_pit -= 1
    
    # Wumpus
    while count_wumpus > 0:
        wumpus_i = random_loc()
        if wumpus_i not in set_blacklist:
            set_blacklist.add(wumpus_i)
            wumpus.append(wumpus_i)
            count_wumpus -= 1
    
    # Pit: surrounding breeze
    for each_pit in pit:
        for each_potential_breeze in adjacents(each_pit):
            set_blacklist.add(each_potential_breeze)
            breeze.append(each_potential_breeze)

    # Wumpus: surrounding stench
    for each_wumpus in wumpus:
        for each_potential_stench in adjacents(each_wumpus):
            set_blacklist.add(each_potential_stench)
            stench.append(each_potential_stench)

def export_map(format='readable'):
    """Serialize the current map (for writing to file)

    #### Available formats:
    - `compact`: Conform to the format given in original problem statement.
    - `readable`: The more human-readable version of `compact`, with even-width string per tiles
    """
    global width, height
    global gold, pit, breeze, wumpus, stench
    map_2d_str = ''

    if format in ['compact', 'readable']:
        # Empty map
        map_2d = [['' for _ in range(width)] for _ in range(height)]
        
        # Add objects
        for each in gold:
            map_2d[each[1]][each[0]] += 'G'
        for each in pit:
            map_2d[each[1]][each[0]] += 'P'
        for each in wumpus:
            map_2d[each[1]][each[0]] += 'W'
        for each in breeze:
            if all([
                x not in map_2d[each[1]][each[0]]
                for x in 'BPW'
            ]):
                map_2d[each[1]][each[0]] += 'B'
        for each in stench:
            if all([
                x not in map_2d[each[1]][each[0]]
                for x in 'SPW'
            ]):
                map_2d[each[1]][each[0]] += 'S'
        
        # If `readable` format: pad spaces
        if format == 'readable':
            max_tile_width = max([
                len(tile)
                for each_row in map_2d
                for tile in each_row
            ])
            map_2d = [
                [tile.rjust(max_tile_width) for tile in each_row]
                for each_row in map_2d
            ]

        # Serialize
        for each_line in map_2d:
            map_2d_str += '.'.join(each_line) + '\n'

    return map_2d_str

if __name__ == "__main__":
    # Generate map
    generate_map()

    # Some info
    filename = '{}G-{}P-{}W.txt'.format(
        len(gold), len(pit), len(wumpus)
    )
    print('Map = {} * {}\nPlayer = {}\nFilename = {}'.format(
        width, height, player, filename
    ))

    # Write to file
    with open(MAPS_DIR + '/' + filename, 'w+') as file:
        file.write('{}\n'.format(width)) # map size
        file.write(export_map(format='readable'))
        print('File written.')
    
    # Debug
    # print('All locations:', set_blacklist)
    # print('Gold:', gold)
    # print('Pit:', pit)
    # print('Wumpus:', wumpus)
    # print('Breeze:', breeze)
    # print('Stench:', stench)
