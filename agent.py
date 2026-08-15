# agent.py
from collections import deque
import heapq

class GreedyGridAgent:
    """A simple reflex agent that follows strict condition-action rules."""
    # for example, if it smells food, it moves towards it; if it hits a wall, it turns left.
    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']
        self.toxic_traps = set({(2, 3), (4, 1), (5, 5)})
        self.heading = 'Right'
        self.visited_cells = set()
        self.last_action = None
        self.last_position = None

# this agent is designed to be a simple reflex agent that reacts to immediate percepts. 
# It does not maintain a complex internal state or plan ahead,
# but it does keep track of visited cells to avoid revisiting them unnecessarily.
    def _turn_left(self, direction: str) -> str:
        turn_map = {'Up': 'Left', 'Left': 'Down', 'Down': 'Right', 'Right': 'Up'}
        return turn_map[direction]

    def _turn_right(self, direction: str) -> str:
        turn_map = {'Up': 'Right', 'Right': 'Down', 'Down': 'Left', 'Left': 'Up'}
        return turn_map[direction]

    def _next_position(self, pos, direction):
        x, y = pos
        if direction == 'Up':
            return (x, y + 1)
        if direction == 'Down':
            return (x, y - 1)
        if direction == 'Left':
            return (x - 1, y)
        return (x + 1, y)

    def sense_and_act(self, percept: dict) -> str:
        pos = tuple(percept['agent_pos']) if 'agent_pos' in percept else None
        if pos is not None:
            self.visited_cells.add(pos)
            self.last_position = pos

        self.last_percept = percept

        if percept.get('smells_food'):
            self.last_action = self.heading
            return self.last_action

        if percept.get('hit_wall'):
            if pos is not None:
                left_cell = self._next_position(pos, self._turn_left(self.heading))
                if left_cell in self.visited_cells:
                    self.heading = self._turn_right(self.heading)
                else:
                    self.heading = self._turn_left(self.heading)
            else:
                self.heading = self._turn_left(self.heading)
            self.last_action = self.heading
            return self.last_action

        self.last_action = self.heading
        return self.last_action

# The `SimpleReflexAgent` class is a basic reflex agent that reacts to immediate percepts without maintaining a complex internal state. 
# It keeps track of its current direction, visited cells, last action, and last position. 
# The agent can turn left or right based on the percepts it receives, and it avoids revisiting cells it has already been to. 
# If it detects food in its current location, it will move in its current direction. 
# If it encounters a wall or has hit a wall, it will decide whether to turn left or right based on the presence of walls and previously visited cells.
class SimpleReflexAgent:
    """A simple reflex agent that reacts only to immediate percepts."""

    def __init__(self):
        self.direction = 'Up'
        self.visited_cells = set()
        self.last_action = None
        self.last_position = None

    def _turn_left(self, direction: str) -> str:
        turn_map = {'Up': 'Left', 'Left': 'Down', 'Down': 'Right', 'Right': 'Up'}
        return turn_map[direction]

    def _turn_right(self, direction: str) -> str:
        turn_map = {'Up': 'Right', 'Right': 'Down', 'Down': 'Left', 'Left': 'Up'}
        return turn_map[direction]

    def _next_position(self, pos, direction):
        x, y = pos
        if direction == 'Up':
            return (x, y + 1)
        if direction == 'Down':
            return (x, y - 1)
        if direction == 'Left':
            return (x - 1, y)
        return (x + 1, y)

    def sense_and_act(self, percept: dict) -> str:
        pos = tuple(percept['agent_pos']) if 'agent_pos' in percept else None
        if pos is not None:
            self.visited_cells.add(pos)
            self.last_position = pos

        if percept.get('food_here'):
            self.last_action = self.direction
            return self.last_action

        if pos is not None:
            ahead_cell = self._next_position(pos, self.direction)
            if percept.get('wall_ahead') or percept.get('hit_wall') or ahead_cell in self.visited_cells:
                if not percept.get('wall_left', False):
                    left_cell = self._next_position(pos, self._turn_left(self.direction))
                    if left_cell not in self.visited_cells:
                        self.direction = self._turn_left(self.direction)
                    else:
                        self.direction = self._turn_right(self.direction)
                elif not percept.get('wall_right', False):
                    self.direction = self._turn_right(self.direction)
                else:
                    self.direction = self._turn_right(self.direction)
            else:
                self.direction = self.direction
        else:
            self.direction = self._turn_left(self.direction)


        self.last_action = self.direction
        return self.last_action

# this is the model based agent implementation 
# it is a reflex agent with minimal internal state to avoid repeating the same failed move
# it is also a simple agent that follows strict condition-action rules. 
class ModelBasedAgent:
    """A reflex agent with minimal internal state to avoid repeating the same failed move."""

    def __init__(self):
        self.direction = 'Up'
        self.last_turn = None
        self.visited_cells = set()
        self.last_position = None

    def _turn_left(self, direction: str) -> str:
        turn_map = {'Up': 'Left', 'Left': 'Down', 'Down': 'Right', 'Right': 'Up'}
        return turn_map[direction]

    def _turn_right(self, direction: str) -> str:
        turn_map = {'Up': 'Right', 'Right': 'Down', 'Down': 'Left', 'Left': 'Up'}
        return turn_map[direction]

    def _next_position(self, pos, direction):
        x, y = pos
        if direction == 'Up':
            return (x, y + 1)
        if direction == 'Down':
            return (x, y - 1)
        if direction == 'Left':
            return (x - 1, y)
        return (x + 1, y)

    def sense_and_act(self, percept: dict) -> str:
        pos = tuple(percept['agent_pos']) if 'agent_pos' in percept else None
        if pos is not None:
            self.visited_cells.add(pos)
            self.last_position = pos

        if percept.get('wall_ahead') or percept.get('hit_wall'):
            if pos is not None:
                left_cell = self._next_position(pos, self._turn_left(self.direction))
                if left_cell in self.visited_cells:
                    self.direction = self._turn_right(self.direction)
                else:
                    self.direction = self._turn_left(self.direction)
            elif self.last_turn == 'Left':
                self.direction = self._turn_left(self._turn_left(self.direction))
            else:
                self.direction = self._turn_left(self.direction)
            self.last_turn = 'Left'
            return self.direction

        return self.direction

# this is the search agent implementation 
# it is a problem solving agent that plans paths using bfs, dfs, and ucs. 
# it is also a offline planning agent that plans paths in a static environment.
class SearchAgent:
    """A search agent that plans paths using BFS, DFS, and UCS."""

    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'

    def sense_and_act(self, percept: dict) -> str:
        if not self.plan:
            start_pos = percept['agent_pos']
            all_food = percept.get('all_food', [])
            walls = set(percept.get('walls', []))
            grid_size = percept.get('grid_size', (10, 10))

            if not all_food:
                return 'Stay'

            # Sort food by Manhattan distance from agent to find closest target
            sorted_food = sorted(all_food, key=lambda f: abs(f[0] - start_pos[0]) + abs(f[1] - start_pos[1]))
            
            # Find a path to the closest reachable food
            path = []
            for food in sorted_food:
                if self.active_algo == 'BFS':
                    path = self.bfs_search(start_pos, food, walls, grid_size)
                elif self.active_algo == 'DFS':
                    path = self.dfs_search(start_pos, food, walls, grid_size)
                elif self.active_algo == 'UCS':
                    path = self.ucs_search(start_pos, food, walls, grid_size)
                
                if path:
                    self.plan = path
                    break
            
            if not self.plan:
                return 'Stay'

        return self.plan.pop(0)

    def get_action(self, percept: dict) -> str:
        return self.sense_and_act(percept)

    def bfs_search(self, start_pos, goal_pos, walls, grid_size):
        start = tuple(start_pos)
        goal = tuple(goal_pos)
        width, height = grid_size

        queue = deque([(start, [])])
        reached = {start}

        while queue:
            current, path = queue.popleft()
            if current == goal:
                return path

            x, y = current
            for action, (dx, dy) in [('Up', (0, 1)), ('Down', (0, -1)), ('Left', (-1, 0)), ('Right', (1, 0))]:
                nxt = (x + dx, y + dy)
                if not (0 <= nxt[0] < width and 0 <= nxt[1] < height):
                    continue
                if nxt in walls or nxt in reached:
                    continue
                reached.add(nxt)
                queue.append((nxt, path + [action]))

        return []

# this is the dfs search algorithm implementation 
    def dfs_search(self, start_pos, goal_pos, walls, grid_size):
        start = tuple(start_pos)
        goal = tuple(goal_pos)
        width, height = grid_size

        stack = [(start, [])]
        reached = set()

        while stack:
            current, path = stack.pop()
            if current == goal:
                return path

            if current not in reached:
                reached.add(current)
                x, y = current
                for action, (dx, dy) in [('Up', (0, 1)), ('Down', (0, -1)), ('Left', (-1, 0)), ('Right', (1, 0))]:
                    nxt = (x + dx, y + dy)
                    if not (0 <= nxt[0] < width and 0 <= nxt[1] < height):
                        continue
                    if nxt in walls or nxt in reached:
                        continue
                    stack.append((nxt, path + [action]))

        return []

# this is the ucs search algorithm implementation for shortest path.
    def ucs_search(self, start_pos, goal_pos, walls, grid_size):
        start = tuple(start_pos)
        goal = tuple(goal_pos)
        width, height = grid_size

        # Priority queue elements: (cost, tie_breaker, current_node, path)
        pq = []
        heapq.heappush(pq, (0, 0, start, []))
        reached = set()
        tie_breaker = 0

        while pq:
            cost, _, current, path = heapq.heappop(pq)
            if current == goal:
                return path

            if current not in reached:
                reached.add(current)
                x, y = current
                for action, (dx, dy) in [('Up', (0, 1)), ('Down', (0, -1)), ('Left', (-1, 0)), ('Right', (1, 0))]:
                    nxt = (x + dx, y + dy)
                    if not (0 <= nxt[0] < width and 0 <= nxt[1] < height):
                        continue
                    if nxt in walls or nxt in reached:
                        continue
                    tie_breaker += 1
                    heapq.heappush(pq, (cost + 1, tie_breaker, nxt, path + [action]))

        return []


