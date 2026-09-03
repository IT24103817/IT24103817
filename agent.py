import random
import heapq
import math
from collections import deque


# agent.py
class SimpleReflexAgent:
    """Select an action from the current percept using condition-action rules."""

    def sense_and_act(self, percept: dict) -> str:
        if percept['food_here']:
            return 'Suck'
        if percept['wall_ahead']:
            return 'Left'
        return 'Right'



class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)


class ModelBasedAgent:
    """Model-based reflex agent maintaining internal memory of visited states and actions."""

    def __init__(self):
        self.visited_cells = set()
        self.last_action = None
        self.history = []

    def sense_and_act(self, percept: dict) -> str:
        # Check percepts
        food_here = percept.get('food_here', False)
        wall_ahead = percept.get('wall_ahead', False)

        if food_here:
            action = 'Suck'
        elif wall_ahead:
            # If wall ahead, check if left was already tried or visited
            left_is_visited = ('Left' in self.history) or (self.last_action == 'Left')
            if left_is_visited:
                action = 'Right'
            else:
                action = 'Left'
        else:
            action = 'Up'

        self.last_action = action
        self.history.append(action)
        return action


class SearchAgent:
    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'
        self.moves = [
            ('Up', (0, 1)),
            ('Down', (0, -1)),
            ('Left', (-1, 0)),
            ('Right', (1, 0))
        ]

    def manhattan_distance(self, pos, goal):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal):
        return math.sqrt((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2)

    def _get_neighbors(self, current_pos, walls, grid_size):

        neighbors = []
        w, h = grid_size
        wall_set = set(tuple(p) for p in walls)
        x, y = current_pos

        for action, (dx, dy) in self.moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in wall_set:
                neighbors.append((action, (nx, ny)))
        return neighbors

    def bfs_search(self, start_pos, goal_pos, walls, grid_size):
        start = tuple(start_pos)
        goal = tuple(goal_pos)
        if start == goal:
            return []

        frontier = deque([(start, [])])
        reached = {start}

        while frontier:
            current, path = frontier.popleft()
            if current == goal:
                return path

            for action, next_pos in self._get_neighbors(current, walls, grid_size):
                if next_pos not in reached:
                    reached.add(next_pos)
                    frontier.append((next_pos, path + [action]))
        return None

    def dfs_search(self, start_pos, goal_pos, walls, grid_size):
        start = tuple(start_pos)
        goal = tuple(goal_pos)
        if start == goal:
            return []

        frontier = [(start, [])]
        reached = {start}

        while frontier:
            current, path = frontier.pop()
            if current == goal:
                return path

            for action, next_pos in self._get_neighbors(current, walls, grid_size):
                if next_pos not in reached:
                    reached.add(next_pos)
                    frontier.append((next_pos, path + [action]))
        return None

    def ucs_search(self, start_pos, goal_pos, walls, grid_size):
        start = tuple(start_pos)
        goal = tuple(goal_pos)
        if start == goal:
            return []

        frontier = []
        heapq.heappush(frontier, (0, start, []))
        cost_so_far = {start: 0}

        while frontier:
            cost, current, path = heapq.heappop(frontier)
            if current == goal:
                return path

            if cost > cost_so_far.get(current, float('inf')):
                continue

            for action, next_pos in self._get_neighbors(current, walls, grid_size):
                new_cost = cost + 1
                if new_cost < cost_so_far.get(next_pos, float('inf')):
                    cost_so_far[next_pos] = new_cost
                    heapq.heappush(frontier, (new_cost, next_pos, path + [action]))
        return None

    def astar_search(self, start_pos, goal_pos, walls, grid_size, heuristic_type='manhattan'):
        start = tuple(start_pos)
        goal = tuple(goal_pos)
        if start == goal:
            return []

        heuristic_fn = self.manhattan_distance if heuristic_type == 'manhattan' else self.euclidean_distance

        frontier = []
        reached_states = set()

        h_start = heuristic_fn(start, goal)
        heapq.heappush(frontier, (h_start, 0, start, []))

        while frontier:
            f_cost, g_cost, current_pos, path_taken = heapq.heappop(frontier)

            if current_pos == goal:
                return path_taken

            if current_pos in reached_states:
                continue
            reached_states.add(current_pos)

            for action, next_pos in self._get_neighbors(current_pos, walls, grid_size):
                if next_pos not in reached_states:
                    g_new = g_cost + 1
                    h_new = heuristic_fn(next_pos, goal)
                    f_new = g_new + h_new
                    heapq.heappush(frontier, (f_new, g_new, next_pos, path_taken + [action]))
        return None

    def sense_and_act(self, percept: dict) -> str:
        if not self.plan:
            all_food = percept.get('all_food', [])
            if not all_food:
                return 'Stay'

            agent_pos = percept['agent_pos']
            walls = percept.get('walls', [])
            grid_size = percept.get('grid_size', (10, 10))

            closest_food = min(
                all_food,
                key=lambda f: abs(f[0] - agent_pos[0]) + abs(f[1] - agent_pos[1])
            )

            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(agent_pos, closest_food, walls, grid_size) or []
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(agent_pos, closest_food, walls, grid_size) or []
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(agent_pos, closest_food, walls, grid_size) or []
            elif self.active_algo == 'AStar':
                self.plan = self.astar_search(agent_pos, closest_food, walls, grid_size, 'manhattan') or []

        if self.plan:
            return self.plan.pop(0)
        return 'Stay'





