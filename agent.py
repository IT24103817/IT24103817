# agent.py
import random
import heapq
from collections import deque


class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']
        self.last_action = None

    def sense_and_act(self, percept: dict) -> str:
        """Choose an action based on immediate percept information."""
        pos = percept.get('agent_pos', [0, 0])
        if percept.get('smells_food'):
            return random.choice(self.actions_pool)

        if percept.get('hit_wall'):
            alternative_actions = [a for a in self.actions_pool if a != self.last_action]
            return alternative_actions[0] if alternative_actions else random.choice(self.actions_pool)

        self.last_action = random.choice(self.actions_pool)
        return self.last_action


class SimpleReflexAgent:
    """A simple condition-action agent driven only by the current percept."""

    def sense_and_act(self, percept: dict) -> str:
        facing = percept.get('facing_direction', 'Right')
        if percept.get('wall_ahead'):
            turns = {'Up': 'Right', 'Right': 'Down', 'Down': 'Left', 'Left': 'Up'}
            return turns[facing]
        return facing


class ModelBasedAgent:
    """A model-based agent that remembers its previous failures to avoid loops."""

    def __init__(self):
        self.visited_relative_cells = set()
        self.current_relative_pos = [0, 0]
        self.last_action = None

    def sense_and_act(self, percept: dict) -> str:
        if self.last_action == 'Up':
            self.current_relative_pos[1] += 1
        elif self.last_action == 'Down':
            self.current_relative_pos[1] -= 1
        elif self.last_action == 'Left':
            self.current_relative_pos[0] -= 1
        elif self.last_action == 'Right':
            self.current_relative_pos[0] += 1

        if percept.get('hit_wall') and self.last_action:
            if self.last_action == 'Up':
                self.current_relative_pos[1] -= 1
            elif self.last_action == 'Down':
                self.current_relative_pos[1] += 1
            elif self.last_action == 'Left':
                self.current_relative_pos[0] += 1
            elif self.last_action == 'Right':
                self.current_relative_pos[0] -= 1

        current_pos_tuple = tuple(self.current_relative_pos)
        self.visited_relative_cells.add(current_pos_tuple)
        
        facing = percept.get('facing_direction', 'Right')
        
        ahead_pos = list(self.current_relative_pos)
        if facing == 'Up':
            ahead_pos[1] += 1
        elif facing == 'Down':
            ahead_pos[1] -= 1
        elif facing == 'Left':
            ahead_pos[0] -= 1
        elif facing == 'Right':
            ahead_pos[0] += 1
            
        ahead_visited = tuple(ahead_pos) in self.visited_relative_cells
        
        if percept.get('wall_ahead') or ahead_visited:
            turns = {'Up': 'Right', 'Right': 'Down', 'Down': 'Left', 'Left': 'Up'}
            action = turns[facing]
            for _ in range(3):
                test_pos = list(self.current_relative_pos)
                if action == 'Up': test_pos[1] += 1
                elif action == 'Down': test_pos[1] -= 1
                elif action == 'Left': test_pos[0] -= 1
                elif action == 'Right': test_pos[0] += 1
                
                if tuple(test_pos) not in self.visited_relative_cells:
                    break
                action = turns[action]
        else:
            action = facing
            
        self.last_action = action
        return action


class SearchAgent:
    """A problem-solving agent that uses breadth-first search to find a route in a static maze."""

    def __init__(self):
        self.actions = {
            'Up': (0, 1),
            'Down': (0, -1),
            'Left': (-1, 0),
            'Right': (1, 0),
        }
        self.plan = []
        self.active_algo = 'BFS'

    def bfs_search(self, start_pos, goal_pos, walls, grid_size):
        start = tuple(start_pos)
        goal = tuple(goal_pos)
        wall_set = set(walls)
        width, height = grid_size
        queue = deque([(start, [])])
        visited = {start}

        while queue:
            (x, y), path = queue.popleft()
            if (x, y) == goal:
                return path

            for action, (dx, dy) in self.actions.items():
                nx = x + dx
                ny = y + dy
                next_pos = (nx, ny)

                if 0 <= nx < width and 0 <= ny < height and next_pos not in wall_set and next_pos not in visited:
                    visited.add(next_pos)
                    queue.append((next_pos, path + [action]))

        return []

    def dfs_search(self, start_pos, goal_pos, walls, grid_size):
        start = tuple(start_pos)
        goal = tuple(goal_pos)
        wall_set = set(walls)
        width, height = grid_size
        stack = [(start, [])]
        visited = set()

        while stack:
            (x, y), path = stack.pop()
            if (x, y) == goal:
                return path

            if (x, y) in visited:
                continue
            visited.add((x, y))

            for action, (dx, dy) in self.actions.items():
                nx = x + dx
                ny = y + dy
                next_pos = (nx, ny)

                if 0 <= nx < width and 0 <= ny < height and next_pos not in wall_set and next_pos not in visited:
                    stack.append((next_pos, path + [action]))

        return []

    def ucs_search(self, start_pos, goal_pos, walls, grid_size):
        start = tuple(start_pos)
        goal = tuple(goal_pos)
        wall_set = set(walls)
        width, height = grid_size
        pq = [(0, start, [])]  # (cost, pos, path)
        visited = set()

        while pq:
            cost, (x, y), path = heapq.heappop(pq)
            if (x, y) == goal:
                return path
            
            if (x, y) in visited:
                continue
            visited.add((x, y))

            for action, (dx, dy) in self.actions.items():
                nx = x + dx
                ny = y + dy
                next_pos = (nx, ny)

                if 0 <= nx < width and 0 <= ny < height and next_pos not in wall_set and next_pos not in visited:
                    heapq.heappush(pq, (cost + 1, next_pos, path + [action]))

        return []

    def sense_and_act(self, percept: dict) -> str:
        if not self.plan:
            all_food = percept.get('all_food', [])
            agent_pos = percept.get('agent_pos', [0, 0])
            
            if not all_food:
                return 'Right'  # No food left
                
            # Find the closest food pellet using Manhattan distance
            closest_food = min(all_food, key=lambda f: abs(f[0] - agent_pos[0]) + abs(f[1] - agent_pos[1]))
            walls = percept.get('walls', [])
            grid_size = percept.get('grid_size', (10, 10))

            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(agent_pos, closest_food, walls, grid_size)
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(agent_pos, closest_food, walls, grid_size)
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(agent_pos, closest_food, walls, grid_size)
                
            if not self.plan:
                return 'Right'  # Fallback if no path is found
                
        return self.plan.pop(0)