#%% IMPORTS

import numpy as np
import queue

#%% DIRECTIONS ITEM WORLD DEF

directions = np.array([[0,-1],[0,1],[-1,0],[1,0]])

class Item:
    global_idx = 0
    def __init__(self, name, world, locations, idx=None):
        self.idx = idx
        if self.idx is None:
            Item.global_idx += 1
            self.idx = Item.global_idx
        self.name = name
        self.world = world
        self.locations = locations
        self.world.add_item(self, locations)
        
    def __str__(self):
        return self.name
    
    def copy(self, new_world):
        new_item = Item(self.name, new_world, self.locations.copy(), idx=self.idx)
        return new_item

        
class PositionError(Exception):
    def __init__(self, item, locations):
        message = f'{item.name} cannot be placed at locations {locations}.'
        super().__init__(message)
        


class World:
    
    initial_world = np.array([[-1,-1,0,0,-1,-1],
                              [-1,-1,0,0,-1,-1],
                              [0,0,0,0,0,0],
                              [0,0,0,0,0,0],
                              [-1,0,0,0,0,-1],
                              [-1,0,0,0,0,-1],
                              [-1,-1,0,0,-1,-1],
                              [-1,-1,0,0,-1,-1]])
    
    def __init__(self):
        self.world = World.initial_world.copy()
        self.max_length = max(self.world, key=len) # for printing

        self.items = []
        
        
    def add_item(self, item, locations):
        if not self.can_be_placed(item, locations):
            raise PositionError(item, locations)
        self.register_item(item)
        for location in locations:
            self[location] = item.idx

    def register_item(self, item):
        self.items.append(item)
        if item.name == 'Garbage':
            self.garbage = item

    def can_be_placed(self, item, locations):
        for location in locations:
            try:
                if not self.is_location_free(*location, ignore=item.idx):
                    return False
            except Exception as e:
                # out of bounds
                return False 
        return True

    def is_location_free(self, i, j, ignore=-2):
        return i >= 0 and j >= 0 and (self.world[i,j] == 0 or self.world[i,j] == ignore)
    
    def get_possible_moves(self):
        possible_moves = []
        for item in self.items:
            for direction in directions:
                if self.can_be_placed(item, item.locations+direction):
                    possible_moves.append((item.idx-1, direction))
        return possible_moves
                
    def move(self, item_idx, direction):
        item = self.items[item_idx]
        for location in item.locations:
            self[location] = 0
        item.locations += direction
        for location in item.locations:
            self[location] = item.idx
        return self.is_won()
    
    def is_won(self):
        return (np.sort(self.garbage.locations) == np.sort(np.array([[4,2],[4,3],[5,2],[5,3]]))).all() \
            and (self.world[6,2],self.world[6,3],self.world[7,2],self.world[7,3]) == (0,0,0,0)
    
    def copy(self):
        new_world = World()
        for item in self.items:
            new_item = item.copy(new_world=new_world)
        return new_world
    
    def __getitem__(self, i, j):
        return self.world[i,j]
    
    def __setitem__(self, location, idx):
        i,j = location
        self.world[i,j] = idx
    
    def __str__(self):
        return world_to_str(self.world)
    
def world_to_str(arr):
    s = ''
    for row in arr:
        s += '{:^20s}'.format(' '.join('{}'.format(idx) for idx in row if idx != -1))
        s += '\n'
    return s

#%% BFS ALGO

def BFS(world, max_iter=100000):
    worlds = queue.Queue()
    seen_states = [world.world]
    seen_states = {str(world.world) : True}
    worlds.put(world)
    parents = {}
    i = 0
    while not worlds.empty() and i < max_iter:
        if i % 1000 == 0:
            print("Iteration", i)
        current_world = worlds.get()
        if current_world.is_won():
            return current_world, parents
        for move in current_world.get_possible_moves():
            new_world = current_world.copy()
            new_world.move(*move)
            if not seen_states.get(str(new_world.world), False):
                seen_states[str(new_world.world)] = True
                parents[str(new_world.world)] = current_world.world
                worlds.put(new_world)
        i += 1
    raise Exception(f"No solution found in {max_iter} iterations.")

#%% BUILDING WORLD

world = World()

garbage =  Item(name="Garbage", world=world, locations=np.array([[0,2],[0,3],[1,2],[1,3]]))
purple  =  Item(name="Purple",  world=world, locations=np.array([[3,1],[3,2],[4,2]]))
orange  =  Item(name="Orange",  world=world, locations=np.array([[3,3],[3,4],[4,3]]))
yellow  =  Item(name="Yellow",  world=world, locations=np.array([[4,1],[5,1],[5,2]]))
green   =  Item(name="Green",   world=world, locations=np.array([[4,4],[5,3],[5,4]]))
blue    =  Item(name="Blue",    world=world, locations=np.array([[6,2],[6,3]]))

#%% RUNNING BFS
        
winning_world, parents = BFS(world)

#%% RETRIEVE PATH

path = []
curr_world = winning_world.world
while curr_world is not None:
    path.append(curr_world)
    curr_world = parents.get(str(curr_world), None)
path.reverse()

for world in path:
    print(world_to_str(world))