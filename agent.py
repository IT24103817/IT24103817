from collections import deque
import random


class SimpleReflexAgent:
    """Practical 1: Simple Reflex Agent - Reacts purely to immediate percepts."""

    def sense_and_act(self, percept: dict) -> str:
        if percept.get('smells_food', False):
            return 'Eat'
        elif percept.get('hit_wall', False):
            return 'Turn'
        elif percept.get('smells_toxin', False):
            return 'Avoid'
        return random.choice(['Up', 'Down', 'Left', 'Right'])


class ModelBasedAgent:
    """Practical 2: Model-Based Agent - Maintains internal memory."""

    def __init__(self):
        self.visited = set()

    def sense_and_act(self, percept: dict) -> str:
        agent_pos = percept.get('agent_pos')
        if agent_pos is not None:
            self.visited.add(tuple(agent_pos))

        if percept.get('smells_food', False):
            return 'Eat'
        if percept.get('smells_toxin', False):
            return 'Avoid'

        return random.choice(['Up', 'Down', 'Left', 'Right'])


class SearchAgent:
    """Practical 3: Search Agent - Implements Breadth-First Search (BFS)."""

    def bfs_search(self, start, goal, walls, grid_size):
        width, height = grid_size
        queue = deque([(start, [])])
        visited = {start}

        moves = {
            'Up': (0, 1),
            'Down': (0, -1),
            'Left': (-1, 0),
            'Right': (1, 0)
        }

        while queue:
            (x, y), path = queue.popleft()

            if (x, y) == goal:
                return path

            for action, (dx, dy) in moves.items():
                nx, ny = x + dx, y + dy
                next_pos = (nx, ny)

                if (0 <= nx < width and 0 <= ny < height and 
                        next_pos not in walls and next_pos not in visited):
                    visited.add(next_pos)
                    queue.append((next_pos, path + [action]))

        return None


class GreedyGridAgent:
    """Integrated Agent for visual simulation that remembers traps."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']
        self.known_traps = set()
        self.last_action = None

    def get_next_position(self, current_pos: list, action: str) -> tuple:
        x, y = current_pos
        if action == 'Up':
            return (x, y + 1)
        elif action == 'Down':
            return (x, y - 1)
        elif action == 'Left':
            return (x - 1, y)
        elif action == 'Right':
            return (x + 1, y)
        return (x, y)

    def sense_and_act(self, percept: dict) -> str:
        agent_pos = percept.get('agent_pos')
        if agent_pos is None:
            return random.choice(self.actions_pool)

        current_pos = tuple(agent_pos)
        if percept.get('smells_toxin', False):
            self.known_traps.add(current_pos)

        safe_actions = []
        for action in self.actions_pool:
            next_pos = self.get_next_position(agent_pos, action)
            if next_pos not in self.known_traps:
                safe_actions.append(action)

        if safe_actions:
            selected_action = random.choice(safe_actions)
        else:
            selected_action = random.choice(self.actions_pool)

        self.last_action = selected_action
        return selected_action