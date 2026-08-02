# agent.py
import random
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

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        if percept.get('food_here'):
            return 'Right'
        if percept.get('wall_ahead'):
            return random.choice([a for a in self.actions_pool if a != 'Up'])
        return random.choice(self.actions_pool)


class ModelBasedAgent:
    """A model-based agent that remembers its previous failures to avoid loops."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']
        self.last_action = None
        self.last_percept = None

    def sense_and_act(self, percept: dict) -> str:
        current_percept = tuple(sorted(percept.items()))

        if self.last_percept == current_percept and self.last_action is not None:
            choices = [a for a in self.actions_pool if a != self.last_action]
            action = choices[0] if choices else random.choice(self.actions_pool)
        else:
            action = 'Left' if percept.get('wall_ahead') else random.choice(self.actions_pool)

        self.last_percept = current_percept
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

        return None