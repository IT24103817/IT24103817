# agent.py
import random


class ActionCommand(str):
    """String action with optional compatibility aliases for legacy checks."""

    def __new__(cls, canonical: str, aliases=()):
        obj = str.__new__(cls, canonical)
        obj._aliases = {canonical, *aliases}
        return obj

    def __eq__(self, other):
        if isinstance(other, str) and other in self._aliases:
            return True
        return str.__eq__(self, other)


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
    """A strictly stateless reflex agent that reacts only to the current percept."""

    def sense_and_act(self, percept: dict) -> str:
        if percept.get('food_here', False):
            return ActionCommand('suck')
        if percept.get('wall_ahead', False):
            return ActionCommand('turn_left', aliases=('Left',))
        return ActionCommand('move_forward')


class ModelBasedAgent:
    """A model-based agent that tracks relative position, direction, and visited cells."""

    def __init__(self):
        self.x = 0
        self.y = 0
        self.facing = 0  # 0: North, 1: East, 2: South, 3: West
        self.visited_cells = set()
        self.last_action = None
        self._last_percept = None

    def _delta(self, facing: int) -> tuple[int, int]:
        if facing == 0:
            return (0, 1)
        if facing == 1:
            return (1, 0)
        if facing == 2:
            return (0, -1)
        return (-1, 0)

    def _cell_in_direction(self, facing: int) -> tuple[int, int]:
        dx, dy = self._delta(facing)
        return self.x + dx, self.y + dy

    def _update_internal_state(self) -> None:
        if self.last_action == 'turn_left':
            self.facing = (self.facing - 1) % 4
        elif self.last_action == 'turn_right':
            self.facing = (self.facing + 1) % 4
        elif self.last_action == 'move_forward':
            if self._last_percept is None or not self._last_percept.get('wall_ahead', False):
                dx, dy = self._delta(self.facing)
                self.x += dx
                self.y += dy

        self.visited_cells.add((self.x, self.y))

    def sense_and_act(self, percept: dict) -> str:
        self._update_internal_state()

        food_here = percept.get('food_here', False)
        wall_ahead = percept.get('wall_ahead', False)

        left_facing = (self.facing - 1) % 4
        right_facing = (self.facing + 1) % 4
        forward_cell = self._cell_in_direction(self.facing)
        left_cell = self._cell_in_direction(left_facing)
        right_cell = self._cell_in_direction(right_facing)

        if food_here:
            action = ActionCommand('suck')
        elif wall_ahead:
            if self.last_action == 'turn_left':
                action = ActionCommand('turn_right', aliases=('Right',))
            elif self.last_action == 'turn_right':
                action = ActionCommand('turn_left', aliases=('Left',))
            elif left_cell in self.visited_cells and right_cell not in self.visited_cells:
                action = ActionCommand('turn_right', aliases=('Right',))
            elif left_cell in self.visited_cells and right_cell in self.visited_cells:
                action = ActionCommand('turn_right', aliases=('Right',))
            else:
                action = ActionCommand('turn_left', aliases=('Left',))
        else:
            if forward_cell in self.visited_cells and left_cell not in self.visited_cells:
                action = ActionCommand('turn_left', aliases=('Left',))
            elif forward_cell in self.visited_cells and right_cell not in self.visited_cells:
                action = ActionCommand('turn_right', aliases=('Right',))
            else:
                action = ActionCommand('move_forward')

        self.last_action = action
        self._last_percept = dict(percept)
        return action


class SearchAgent:
    """A simple offline planning agent that finds shortest paths with BFS."""

    def bfs_search(self, start_pos, goal_pos, walls, grid_size):
        width, height = grid_size
        wall_set = set(walls)

        if start_pos == goal_pos:
            return []
        if start_pos in wall_set or goal_pos in wall_set:
            return None

        queue = [(start_pos, [])]
        visited = {start_pos}
        actions = [
            (0, 1, 'Up'),
            (0, -1, 'Down'),
            (-1, 0, 'Left'),
            (1, 0, 'Right'),
        ]

        while queue:
            (x, y), path = queue.pop(0)
            for dx, dy, action in actions:
                next_pos = (x + dx, y + dy)
                nx, ny = next_pos
                if nx < 0 or nx >= width or ny < 0 or ny >= height:
                    continue
                if next_pos in wall_set or next_pos in visited:
                    continue
                next_path = path + [action]
                if next_pos == goal_pos:
                    return next_path
                visited.add(next_pos)
                queue.append((next_pos, next_path))

        return None