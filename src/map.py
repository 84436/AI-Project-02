#!/bin/env python3
# Map provider

from random import randrange

class Map:
    """Map provider.
    Currently only square maps (ideally 10x10) are supported.
    """
    
    def __init__(self, mapfile=None):
        # Map
        self._map = None

        # Map stats
        self._stats = {
            'mapsize': None,
            'count_gold': 0,
            'count_pit': 0,
            'count_wumpus': 0
        }

        # Player stats
        self._player = {
            'loc': None,
            'orient': 'R',
            'arrow': 0,
            'score': 0,
        }

        # Scoring rules for player's actions
        self.__score_table = {
            'MOVE': -10,
            'ARROW': -100,
            'DIE': -1000,
            'GOLD': +100,
            'CAVE_OUT': +10
        }

        # Map: init using this mapfile
        if mapfile is not None:
            self.parse_file(mapfile)

    def __str__(self):
        """String-ify current map for printing.
        This is meant to be used in debugging-by-print; don't use this
        for rendering the actual map.
        """

        # Get largest tile size
        max_tile_size = max([
            len(each_tile)
            for each_row in self._map for each_tile in each_row
        ])

        # Stringify
        r = '\n'.join([
            '.'.join([
                each_tile.rjust(max_tile_size)
                for each_tile in each_line
            ])
            for each_line in self._map
        ])
        return r
    
    def __inmap(self, loc):
        """`INTERNAL` Check if a location is within boundaries.
        """
        return not any([
            (c < 0) or (c >= self._stats['mapsize'])
            for c in loc
        ])
    
    def __update_score(self, event):
        """`INTERNAL` Update player's score
        """
        self._player['score'] += self.__score_table.get(event, 0)

    def parse_file(self, mapfile):
        """Parse a mapfile.
        """

        # Read file
        file_lines = mapfile.read().splitlines()
        self._stats['mapsize'], map_lines = int(file_lines[0]), file_lines[1:]

        # Sanity check
        self._map = [
            list(map(str.strip, each_line.split('.')))
            for each_line in map_lines
        ]
        for each_line in map_lines:
            if len(each_line) < self._stats['mapsize']:
                print('WARNING: inconsistent map')
                break

        # Populate stats
        for each_line in map_lines:
            for each_tile in each_line:
                if 'G' in each_tile: self._stats['count_gold'] += 1
                if 'P' in each_tile: self._stats['count_pit'] += 1
                if 'W' in each_tile: self._stats['count_wumpus'] += 1

        # Choose a random place as player init
        random_loc = lambda : (
            randrange(0, self._stats['mapsize']),
            randrange(0, self._stats['mapsize'])
        )
        px, py = self._player['loc'] = random_loc()
        
        # Reassign player's location until clear of obstacles
        while any(
            items in self._map[py][px]
            for items in 'PW'
        ) or any(
            items in self._map[ty][tx]
            for items in 'PW'
            for ty, tx in self.adjacents()
        ):
            px, py = self._player['loc'] = random_loc()
        
        # Cover all tiles except player's init
        for x, a in enumerate(self._map):
            for y, b in enumerate(a):
                self._map[y][x] += 'X'
        self._map[py][px] = self._map[py][px].replace('X', '')
    
    def reveal(self):
        """Reveal what's on the current tile
        """
        x, y = self._player['loc']
        return self._map[y][x]
    
    def get_gold(self):
        """Collect gold on the current tile (if available)
        """
        if 'G' in self.reveal():
            x, y = self._player['loc']
            self._map[y][x] = self._map[y][x].replace('G', '')
            self.__update_score('GOLD')
            self._stats['count_gold'] -= 1
        pass
    
    def adjacents(self):
        """Get adjacents of a location.
        """
        x, y = self._player['loc']
        size = self._stats['mapsize']
        adjacent_list = []
        if (x-1 >= 0)      : adjacent_list.append((x-1, y))
        if (x+1 <= size-1) : adjacent_list.append((x+1, y))
        if (y-1 >= 0)      : adjacent_list.append((x, y-1))
        if (y+1 <= size-1) : adjacent_list.append((x, y+1))
        return adjacent_list
    
    def orient(self, new_loc):
        """Change player's orientation according to the new location.
        Only accepts location that are adjacent to the player.
        """
        if new_loc in self.adjacents():
            x, y = self._player['loc']
            nx, ny = new_loc
            if (nx - x == -1): self._player['orient'] = 'L'
            if (nx - x == +1): self._player['orient'] = 'R'
            if (ny - y == -1): self._player['orient'] = 'U'
            if (ny - y == +1): self._player['orient'] = 'D'

    def shoot(self):
        """Shoot an arrow following current orientation
        """
        # Orient
        x, y = self._player['loc']
        orientation = self._player['orient']
        target_tile = None
        if orientation == 'L': target_tile = (x-1, y)
        if orientation == 'R': target_tile = (x+1, y)
        if orientation == 'U': target_tile = (x, y-1)
        if orientation == 'D': target_tile = (x, y+1)
        pass

        # Sanity check before shooting
        if self.__inmap(target_tile):
            nx, ny = target_tile
            
            if 'W' in self._map[ny][nx]:
                # WORKAROUND: temporarily move the player to where wumpus was,
                # remove all the stench, then move back to the old location.
                # THIS NO GOOD CODE

                # remove stench from wumpus surrounding
                self._player['loc'] = target_tile
                for each in self.adjacents():
                    ex, ey = each
                    if 'S' in self._map[ey][ex]:
                        self._map[ey][ex] = self._map[ey][ex].replace('S', '')
                self._player['loc'] = (x, y)
                
                # remove wumpus itself
                self._map[ny][nx] = self._map[ny][nx].replace('W', '')
                
                # reveal tile in orientation
                self._map[ny][nx] = self._map[ny][nx].replace('X', '')

                # update count of wumpus in map
                self._stats['count_wumpus'] -= 1
            
        # Update score and used arrow count (regardless of checks)
        self.__update_score('ARROW')
        self._player['arrow'] += 1

    def move(self):
        """Move the player one step forward following current orientation
        """
        # Orient
        x, y = self._player['loc']
        orientation = self._player['orient']
        new_loc = None
        if orientation == 'L': new_loc = (x-1, y)
        if orientation == 'R': new_loc = (x+1, y)
        if orientation == 'U': new_loc = (x, y-1)
        if orientation == 'D': new_loc = (x, y+1)

        # Sanity check before moving
        if self.__inmap(new_loc):
            self._player['loc'] = new_loc
            
            # Update
            self.__update_score('MOVE')
            x, y = self._player['loc']
            self._map[y][x] = self._map[y][x].replace('X', '')
