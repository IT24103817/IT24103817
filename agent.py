from collections import deque


class GreedyGridAgent:
    """Original Lab 01-style agent kept for compatibility."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        return self.actions_pool[0]


class SimpleReflexAgent:
    """
    Simple Reflex Agent
    It has NO __init__ and stores NO history.
    It uses only the current local percept and condition-action rules.
    """

    def sense_and_act(self, percept: dict) -> str:
        # IF food is ahead THEN continue forward to collect it.
        if percept.get('food_here', False):
            return 'FORWARD'

        # IF there is a wall ahead THEN turn left.
        if percept.get('wall_ahead', False):
            return 'LEFT'

        # ELSE move forward.
        return 'FORWARD'


class ModelBasedAgent:
    """
    Model-Based Agent
    The agent receives only local percepts, so it maintains an internal
    relative movement model. It remembers visited relative positions,
    previous percepts and actions, and changes direction when it detects
    repetition.
    """

    DIRECTIONS = ['UP', 'RIGHT', 'DOWN', 'LEFT']
    DELTAS = {
        'UP': (0, 1),
        'RIGHT': (1, 0),
        'DOWN': (0, -1),
        'LEFT': (-1, 0),
    }

    def __init__(self):
        # Required internal memory.
        self.visited_cells = {(0, 0)}
        self.percept_history = []
        self.action_history = []
        self.last_percept = None
        self.last_action = None

        # Internal estimate of position/orientation.
        self.estimated_position = [0, 0]
        self.direction_index = 1  # RIGHT

        self.repeated_percept_count = 0
        self.steps_without_progress = 0

    def _normalise_percept(self, percept):
        return (
            bool(percept.get('wall_ahead', False)),
            bool(percept.get('food_here', False)),
        )

    def _direction_after_turn_left(self):
        return (self.direction_index - 1) % 4

    def _direction_after_turn_right(self):
        return (self.direction_index + 1) % 4

    def _position_after_forward(self, direction_index):
        direction = self.DIRECTIONS[direction_index]
        dx, dy = self.DELTAS[direction]
        return (
            self.estimated_position[0] + dx,
            self.estimated_position[1] + dy,
        )

    def _update_memory_after_action(self, action):
        """
        Update the internal state using the action chosen at the
        previous decision. FORWARD moves the estimated position;
        LEFT/RIGHT changes the estimated facing direction.
        """
        if action == 'LEFT':
            self.direction_index = self._direction_after_turn_left()
        elif action == 'RIGHT':
            self.direction_index = self._direction_after_turn_right()
        elif action == 'FORWARD':
            self.estimated_position = list(
                self._position_after_forward(self.direction_index)
            )

    def sense_and_act(self, percept: dict) -> str:
        current_percept = self._normalise_percept(percept)

        # Step 1: update the internal state from the previous action.
        if self.last_action is not None:
            self._update_memory_after_action(self.last_action)

        # Step 2: record the current percept and estimated position.
        current_cell = tuple(self.estimated_position)
        already_visited = current_cell in self.visited_cells
        self.visited_cells.add(current_cell)

        self.percept_history.append(current_percept)

        if self.last_percept == current_percept:
            self.repeated_percept_count += 1
        else:
            self.repeated_percept_count = 0

        if already_visited:
            self.steps_without_progress += 1
        else:
            self.steps_without_progress = 0

        # Step 3: condition-action rules using memory.
        food_here = current_percept[1]
        wall_ahead = current_percept[0]

        # If the same percept is repeated immediately, deliberately choose
        # an alternative action to break the cycle.
        if self.last_percept == current_percept and self.last_action is not None:
            if self.last_action == 'LEFT':
                action = 'RIGHT'
            elif self.last_action == 'RIGHT':
                action = 'LEFT'
            else:
                action = 'RIGHT'

        elif food_here:
            action = 'FORWARD'

        elif wall_ahead:
            # If forward is blocked, try a direction whose estimated
            # neighbouring cell has not been visited.
            left_index = self._direction_after_turn_left()
            right_index = self._direction_after_turn_right()

            left_cell = self._position_after_forward(left_index)
            right_cell = self._position_after_forward(right_index)

            left_visited = left_cell in self.visited_cells
            right_visited = right_cell in self.visited_cells

            if not left_visited:
                action = 'LEFT'
            elif not right_visited:
                action = 'RIGHT'
            else:
                # Both alternatives are known: change direction anyway
                # to break a repeated cycle.
                action = 'RIGHT'

        elif self.repeated_percept_count >= 1 or self.steps_without_progress >= 2:
            # Same local percept / visited state has repeated.
            # Choose an alternative action rather than blindly continuing.
            right_index = self._direction_after_turn_right()
            right_cell = self._position_after_forward(right_index)

            if right_cell not in self.visited_cells:
                action = 'RIGHT'
            else:
                action = 'LEFT'

        else:
            action = 'FORWARD'

        self.last_percept = current_percept
        self.last_action = action
        self.action_history.append(action)

        return action


class SearchAgent:
    """Breadth-First Search agent retained for the supplied test suite."""

    ACTIONS = [
        ('Up', (0, 1)),
        ('Down', (0, -1)),
        ('Left', (-1, 0)),
        ('Right', (1, 0)),
    ]

    def bfs_search(self, start_pos, goal_pos, walls, grid_size):
        width, height = grid_size
        walls = set(tuple(w) for w in walls)
        start = tuple(start_pos)
        goal = tuple(goal_pos)

        if start in walls or goal in walls:
            return None

        if start == goal:
            return []

        queue = deque([(start, [])])
        visited = {start}

        while queue:
            current, path = queue.popleft()

            for action, (dx, dy) in self.ACTIONS:
                nxt = (current[0] + dx, current[1] + dy)

                if not (0 <= nxt[0] < width and 0 <= nxt[1] < height):
                    continue

                if nxt in walls or nxt in visited:
                    continue

                new_path = path + [action]

                if nxt == goal:
                    return new_path

                visited.add(nxt)
                queue.append((nxt, new_path))

        return None
