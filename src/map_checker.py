#!/bin/env python3
# Map checker (standalone): utility for (aggressively and unconditionally) fixing maps
# Note: currently only square maps are supported

from sys import argv
import os

# Working directory
BASE_DIR   = os.path.dirname(os.path.realpath(__file__)) + '/..'
MAPS_DIR   = BASE_DIR + '/maps'

# In case of both pit and wumpus in a tile, choose which one to be kept
# True = wumpus will be removed
PRIORITIZE_PITS = True

# Storage
map_size = None
map_2d   = None

# Subroutine: get adjacents of a location
def adjacents(loc):
    x, y = loc
    adjacent_list = []
    if (x-1 >= 0)          : adjacent_list.append((x-1, y))
    if (x+1 <= map_size-1) : adjacent_list.append((x+1, y))
    if (y-1 >= 0)          : adjacent_list.append((x, y-1))
    if (y+1 <= map_size-1) : adjacent_list.append((x, y+1))
    return adjacent_list

# The main routine
def check_map(file):
    global map_size, map_2d

    # Read the map
    file_lines = file.read().splitlines()
    map_size, map_lines = int(file_lines[0]), file_lines[1:]

    # Sanity check: is the map consistent?
    for each_line in map_lines:
        if len(each_line) < map_size:
            print('Inconsistent map size. Aborting.')
            exit(-1)
    
    # Sanity check: does player exist in map?
    player_exists = False
    for y, a in enumerate(map_lines):
        for x, b in enumerate(a):
            if 'A' in b:
                player_exists = True
                break
    if not player_exists:
        print('Player (Agent/A) does not exist in map. Aborting.')
        exit(-1)

    # Split
    map_2d = [
        list(map(str.strip, each_line.split('.')))
        for each_line in map_lines
    ]

    # Strip all breezes, stench and invalid golds
    for y, a in enumerate(map_2d):
        for x, b in enumerate(a):
            map_2d[y][x] = map_2d[y][x].replace('B', '')
            map_2d[y][x] = map_2d[y][x].replace('S', '')
            if any(x in b for x in 'PW'):
                map_2d[y][x] = map_2d[y][x].replace('G', '')

    # Add back breeze and stench
    for y, a in enumerate(map_2d):
        for x, b in enumerate(a):
            if ('P' in b) and ('W' in b):
                if PRIORITIZE_PITS:
                    map_2d[y][x] = map_2d[y][x].replace('W', '')
                else:
                    map_2d[y][x] = map_2d[y][x].replace('P', '')
                b = map_2d[y][x] # ugly hack
            if 'P' in b:                
                for a in adjacents((x, y)):
                    if all(
                        item not in map_2d[a[1]][a[0]]
                        for item in 'BPW'
                    ):
                        map_2d[a[1]][a[0]] += 'B'
            if 'W' in b:
                for a in adjacents((x, y)):
                    if all(
                        item not in map_2d[a[1]][a[0]]
                        for item in 'SPW'
                    ):
                        map_2d[a[1]][a[0]] += 'S'
    
    # Serialize
    max_tile_width = max([
        len(tile)
        for each_row in map_2d
        for tile in each_row
    ])
    map_2d = [
        [tile.rjust(max_tile_width) for tile in each_row]
        for each_row in map_2d
    ]
    map_2d_str = ''
    for each_line in map_2d:
        map_2d_str += '.'.join(each_line) + '\n'
    return map_2d_str

if __name__ == "__main__":
    if len(argv) != 2:
        print('Pass exactly one argument: mapfile to be checked.')
        exit(-1)
    
    # Open file and check
    with open(MAPS_DIR + '/' + argv[1], 'r') as file:
        new_map = check_map(file)
    
    # Show info
    print('Filename =', argv[1])
    print('Map size =', map_size)

    with open(MAPS_DIR + '/' + argv[1], 'w') as file:
        file.write(str(map_size) + '\n' + new_map)
