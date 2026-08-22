# agent.py
import random
import heapq
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

class SearchAgent:
    def __init__(self, active_algo='BFS'):
        self.plan = []
        self.active_algo = active_algo  # Options: 'BFS', 'DFS', 'UCS'

    def get_neighbors(self, state, grid_size, walls):
        x, y = state
        width, height = grid_size
        actions = [
            ('UP', (x, y + 1)),
            ('DOWN', (x, y - 1)),
            ('LEFT', (x - 1, y)),
            ('RIGHT', (x + 1, y))
        ]
        valid_neighbors = []
        for action, (nx, ny) in actions:
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in walls:
                valid_neighbors.append((action, (nx, ny)))
        return valid_neighbors

    def bfs_search(self, start, target, grid_size, walls):
        frontier = deque([(start, [])])
        reached = {start}

        while frontier:
            state, path = frontier.popleft()
            if state == target:
                return path

            for action, neighbor in self.get_neighbors(state, grid_size, walls):
                if neighbor not in reached:
                    reached.add(neighbor)
                    frontier.append((neighbor, path + [action]))
        return []

    def dfs_search(self, start, target, grid_size, walls):
        frontier = [(start, [])]
        reached = {start}

        while frontier:
            state, path = frontier.pop()
            if state == target:
                return path

            for action, neighbor in self.get_neighbors(state, grid_size, walls):
                if neighbor not in reached:
                    reached.add(neighbor)
                    frontier.append((neighbor, path + [action]))
        return []

    def ucs_search(self, start, target, grid_size, walls):
        counter = 0
        frontier = [(0, counter, start, [])]
        reached = {start: 0}

        while frontier:
            cost, _, state, path = heapq.heappop(frontier)
            if state == target:
                return path

            for action, neighbor in self.get_neighbors(state, grid_size, walls):
                new_cost = cost + 1
                if neighbor not in reached or new_cost < reached[neighbor]:
                    reached[neighbor] = new_cost
                    counter += 1
                    heapq.heappush(frontier, (new_cost, counter, neighbor, path + [action]))
        return []

    def sense_and_act(self, percept):
        if not self.plan:
            start = tuple(percept['agent_pos'])
            all_food = percept['all_food']
            if not all_food:
                return 'STOP'

            # Select nearest food using Manhattan distance
            target = min(all_food, key=lambda f: abs(f[0] - start[0]) + abs(f[1] - start[1]))

            grid_size = percept['grid_size']
            walls = percept['walls']

            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(start, target, grid_size, walls)
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(start, target, grid_size, walls)
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(start, target, grid_size, walls)

        return self.plan.pop(0) if self.plan else 'STOP'