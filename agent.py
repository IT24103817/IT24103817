# agent.py
import random
from collections import deque


class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)


class SimpleReflexAgent:
    """A simple reflex agent that reacts to the current percept."""
    def sense_and_act(self, percept: dict) -> str:
        if percept.get('food_here'):
            return 'Up'
        if percept.get('wall_ahead'):
            return 'Left'
        return 'Right'


class ModelBasedAgent:
    """A model-based agent that maintains an internal state of the environment."""
    def __init__(self):
        self.last_action = None
        self.last_percept = None
        self.visited_states = []

    def sense_and_act(self, percept: dict) -> str:
        self.last_percept = percept

        if percept.get('food_here'):
            action = 'Up'
        elif percept.get('wall_ahead'):
            # Use one-step memory to avoid repeating the same failed wall response.
            if self.last_action == 'Left':
                action = 'Right'
            elif self.last_action == 'Right':
                action = 'Down'
            elif self.last_action == 'Down':
                action = 'Up'
            else:
                action = 'Left'
        else:
            action = 'Right'

        self.visited_states.append((percept.copy(), action))
        self.last_action = action
        return action


class SearchAgent:
    """A search-based agent that uses BFS to find the shortest path to food."""
    def bfs_search(self, start_pos, goal_pos, walls, grid_size):
        width, height = grid_size
        queue = deque([start_pos])
        parent = {start_pos: (None, None)}

        while queue:
            current = queue.popleft()
            if current == goal_pos:
                return self._reconstruct_path(parent, goal_pos)

            x, y = current
            for action, (dx, dy) in [
                ('Up', (0, 1)),
                ('Right', (1, 0)),
                ('Down', (0, -1)),
                ('Left', (-1, 0)),
            ]:
                nx, ny = x + dx, y + dy
                next_pos = (nx, ny)

                if nx < 0 or ny < 0 or nx >= width or ny >= height:
                    continue
                if next_pos in walls:
                    continue
                if next_pos in parent:
                    continue

                parent[next_pos] = (current, action)
                if next_pos == goal_pos:
                    return self._reconstruct_path(parent, goal_pos)
                queue.append(next_pos)

        return None

    def _reconstruct_path(self, parent, goal_pos):
        actions = []
        current = goal_pos

        while parent[current][0] is not None:
            prev, action = parent[current]
            actions.append(action)
            current = prev

        actions.reverse()
        return actions