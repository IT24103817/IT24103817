from collections import defaultdict
import heapq
from collections import deque

class SimpleReflexAgent:
    def sense_and_act(self, percept):
        if percept.get('food_here'):
            return 'suck'
        elif percept.get('wall_ahead'):
            return 'turn_left'
        else:
            return 'move_forward'


class ModelBasedAgent:
    def __init__(self):
        self.visit_counts = defaultdict(int)
        self.known_walls = set()
        self.current_pos = (0, 0)
        self.facing = 'Up'
        self.last_action = None

    def get_visit_count(self, cell):
        if cell in self.known_walls:
            return 999999
        return self.visit_counts[cell]

    def sense_and_act(self, percept):
        dirs = ['Up', 'Right', 'Down', 'Left']
        dir_offsets = {
            'Up': (0, 1),
            'Right': (1, 0),
            'Down': (0, -1),
            'Left': (-1, 0)
        }

        # Update agent direction and position

        if self.last_action == 'turn_left':
            idx = dirs.index(self.facing)
            self.facing = dirs[(idx - 1) % 4]
        elif self.last_action == 'turn_right':
            idx = dirs.index(self.facing)
            self.facing = dirs[(idx + 1) % 4]
        elif self.last_action == 'move_forward':
            dx, dy = dir_offsets[self.facing]
            self.current_pos = (self.current_pos[0] + dx, self.current_pos[1] + dy)

        # count visits
        self.visit_counts[self.current_pos] += 1


        # Find surrounding cells
        idx = dirs.index(self.facing)
        front_dir = dirs[idx]
        left_dir = dirs[(idx - 1) % 4]
        right_dir = dirs[(idx + 1) % 4]

        fx, fy = dir_offsets[front_dir]
        lx, ly = dir_offsets[left_dir]
        rx, ry = dir_offsets[right_dir]

        front_cell = (self.current_pos[0] + fx, self.current_pos[1] + fy)
        left_cell = (self.current_pos[0] + lx, self.current_pos[1] + ly)
        right_cell = (self.current_pos[0] + rx, self.current_pos[1] + ry)


        # Remember walls
        if percept.get('wall_ahead'):
            self.known_walls.add(front_cell)

        # Choose next action
        if percept.get('food_here'):
            action = 'suck'
        elif percept.get('wall_ahead'):
            left_count = self.get_visit_count(left_cell)
            right_count = self.get_visit_count(right_cell)
            if left_count < right_count:
                action = 'turn_left'
            else:
                action = 'turn_right'
        else:
            front_count = self.get_visit_count(front_cell)
            left_count = self.get_visit_count(left_cell)
            right_count = self.get_visit_count(right_cell)

            if front_count == 0:
                action = 'move_forward'
            elif left_count == 0:
                action = 'turn_left'
            elif right_count == 0:
                action = 'turn_right'
            else:
                min_count = min(front_count, left_count, right_count)
                if min_count == front_count:
                    action = 'move_forward'
                elif min_count == left_count:
                    action = 'turn_left'
                else:
                    action = 'turn_right'

        self.last_action = action
        return action

# lab 3 - 1.2
class SearchAgent:
    DIRECTIONS = [ 
        ('Up', (0, 1)), 
        ('Down', (0, -1)), 
        ('Left', (-1, 0)), 
        ('Right', (1, 0)) 
    ]

    def __init__(self, active_algo='BFS'):
        self.plan = []
        self.active_algo = active_algo  # 'BFS', 'DFS', or 'UCS'
        self.current_pos = (0, 0)
    
    def sense_and_act(self, percept: dict) -> str:
        # If the current plan is exhausted, compute a new offline plan
        if not self.plan:
            grid_size = percept['grid_size']
            walls = percept['walls']
            all_food = percept['all_food']

            if not all_food:
                return 'suck'  # No more food left

            # Select the search method based on self.active_algo
            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(self.current_pos, all_food, grid_size, walls)
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(self.current_pos, all_food, grid_size, walls)
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(self.current_pos, all_food, grid_size, walls)

            # Fallback if no path is reachable to any food
            if not self.plan:
                return 'suck'

        # Pop and execute the next planned action
        action = self.plan.pop(0)

        # Update internal tracking of agent coordinates
        dir_offsets = {'Up': (0, 1), 'Down': (0, -1), 'Left': (-1, 0), 'Right': (1, 0)}
        if action in dir_offsets:
            dx, dy = dir_offsets[action]
            self.current_pos = (self.current_pos[0] + dx, self.current_pos[1] + dy)

        return action
        
    # get valid neighbouring states
    def get_successors(self, state, grid_size, walls):
        successors = []
        x, y = state
        width, height = grid_size

        for action, (dx, dy) in self.DIRECTIONS:
            next_state = ( x + dx, y + dy )
            nx, ny = next_state

            # Check grid boundaries
            if nx < 0 or nx >= width:
                continue
            if ny < 0 or ny >= height:
                continue

            # Check walls
            if next_state in walls:
                continue

            # Add valid state
            # Format:
            # (next_state, action, cost)
            successors.append( (next_state, action, 1) )
        return successors

    # reconstruct path
    def reconstruct_path(self, parent, start, goal):
        path = []
        current = goal

        # Move backwards from goal to start
        while current != start:
            previous_state, action = parent[current]
            path.append(action)
            current = previous_state

        # Reverse to get start to goal
        path.reverse()
        return path

    # BREADTH-FIRST SEARCH (BFS)
    def bfs_search(self, start, goals, grid_size, walls):
        goals = set(goals)
        walls = set(walls)


        frontier = deque([start]) # FIFO Queue

        reached = {start}
        parent = {} # remember where each state came from
        
        while frontier:
            current = frontier.popleft() # FIFO - first in, first out
            
            # check if we reached any food
            if current in goals:
                return self.reconstruct_path(parent, start, current)
            
            # get successors
            for next_state, action, cost in self.get_successors(current, grid_size, walls):
                if next_state not in reached:
                    reached.add(next_state)
                    parent[next_state] = (current, action) # remember the action that got here
                    frontier.append(next_state) # add to the end of the queue
        return [] # no path found
    
    # DEPTH-FIRST SEARCH (DFS)
    def dfs_search(self, start, goals, grid_size, walls):
        goals = set(goals)
        walls = set(walls)

        frontier = [start] # LIFO Stack

        reached = {start} # Track visited/reached states
        parent = {} # Store parent information

        while frontier:
            # Remove last element
            # LIFO - Last In, First Out
            current = frontier.pop()
            
            # Check if goal is found
            if current in goals:
                return self.reconstruct_path(parent, start, current)
            
            # Explore neighbouring cells
            for next_state, action, cost in self.get_successors(current, grid_size, walls):
                if next_state not in reached:
                    reached.add(next_state)

                    # Remember parent and action
                    parent[next_state] = (current, action)

                    # Add to stack
                    frontier.append(next_state)
        
        # No path found
        return []

    # UNIFORM-COST SEARCH (UCS)
    def ucs_search(self, start, goals, grid_size, walls):
        goals = set(goals)
        walls = set(walls)

        # Priority Queue
        # Format: (total_cost, state)

        frontier = [(0, start)]

        # Store lowest cost to each state
        reached = {start: 0}

        parent = {}

        while frontier:
            # Remove state with lowest cost
            current_cost, current = heapq.heappop(frontier)

            # Ignore old entries
            if current_cost > reached[current]:
                continue

            # Check if goal is found
            if current in goals:
                return self.reconstruct_path(parent, start, current)
            
            # Explore neighbouring cells
            for next_state, action, cost in self.get_successors(current, grid_size, walls):
                
                # Step cost
                step_cost = 1

                # Calculate new total cost
                new_cost = (
                    current_cost + step_cost
                )

                # Check if a cheaper path is found
                if ( next_state not in reached or new_cost < reached[next_state] ):
                    reached[next_state] = new_cost
                    parent[next_state] = (current, action)

                    # Add to priority queue
                    heapq.heappush(frontier, (new_cost, next_state))
            
        return []