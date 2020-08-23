#!/bin/env python3
# Map provider

class Map:
    """Map provider.

    Currently only square maps (ideally 10x10) are supported.
    """
    
    def __init__(self, mapfile=None):
        self._map = None
        self._stats = {
            'mapsize': None,
            'count_gold': 0,
            'count_pit': 0,
            'count_wumpus': 0
        }
        if mapfile is not None:
            self.parse_file(mapfile)

    def __str__(self):
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
        """Check if a location is within boundaries.
        """
        return not any([
            (c < 0) or (c >= self._stats['mapsize'])
            for c in loc
        ])

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
