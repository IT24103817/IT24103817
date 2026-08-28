# grid_game.py
class GridHuntGame:
    """A small Pacman-style grid environment (4x4) where an agent collects food."""

    _LEFT_TURN = {
        (0, 1): (-1, 0),
        (-1, 0): (0, -1),
        (0, -1): (1, 0),
        (1, 0): (0, 1),
    }
    _RIGHT_TURN = {value: key for key, value in _LEFT_TURN.items()}

    def __init__(self, width=4, height=4):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]
        self.facing_direction = (0, 1)

        self.food_positions = {(1, 2), (2, 3), (3, 0), (2, 1)}
        self.walls = {(1, 1), (2, 2)}

        self.score = 0
        self.steps = 0

    def _is_inside(self, x, y) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def is_wall(self, x, y) -> bool:
        return not self._is_inside(x, y) or (x, y) in self.walls

    def _cell_ahead(self):
        x, y = self.agent_pos
        dx, dy = self.facing_direction
        return x + dx, y + dy

    def get_percept(self, agent=None) -> dict:
        ahead_x, ahead_y = self._cell_ahead()
        return {
            'wall_ahead': self.is_wall(ahead_x, ahead_y),
            'food_here': tuple(self.agent_pos) in self.food_positions,
        }

    def execute_action(self, agent, action: str):
        self.steps += 1

        if action == 'suck':
            tuple_pos = tuple(self.agent_pos)
            if tuple_pos in self.food_positions:
                self.food_positions.remove(tuple_pos)
                self.score += 20
            return

        if action == 'turn_left':
            self.facing_direction = self._LEFT_TURN[self.facing_direction]
            return

        if action == 'turn_right':
            self.facing_direction = self._RIGHT_TURN[self.facing_direction]
            return

        if action == 'move_forward':
            dx, dy = self.facing_direction
            new_x = self.agent_pos[0] + dx
            new_y = self.agent_pos[1] + dy
            if self.is_wall(new_x, new_y):
                self.score -= 5
            else:
                self.agent_pos = [new_x, new_y]
            return

        if action == 'Up':
            new_pos = [self.agent_pos[0], min(self.height - 1, self.agent_pos[1] + 1)]
        elif action == 'Down':
            new_pos = [self.agent_pos[0], max(0, self.agent_pos[1] - 1)]
        elif action == 'Left':
            new_pos = [max(0, self.agent_pos[0] - 1), self.agent_pos[1]]
        elif action == 'Right':
            new_pos = [min(self.width - 1, self.agent_pos[0] + 1), self.agent_pos[1]]
        else:
            return

        if tuple(new_pos) in self.walls:
            self.score -= 5
        else:
            self.agent_pos = new_pos

        tuple_pos = tuple(self.agent_pos)
        if tuple_pos in self.food_positions:
            self.food_positions.remove(tuple_pos)
            self.score += 20

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 20