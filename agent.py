from collections import deque


class GreedyGridAgent:
    """Original Lab 01-style agent kept for compatibility."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        return self.actions_pool[0]


class SimpleReflexAgent:
    """
    Simple Reflex Agent for Practical 02.

    The agent has no __init__ method and therefore does not
    maintain any history or memory.

    It uses only the current percept and condition-action rules.
    """

    def sense_and_act(self, percept: dict) -> str:

        # IF food is ahead THEN move toward it.
        if percept.get('food_here', False):
            return 'Right'

        # IF there is a wall ahead THEN change direction.
        if percept.get('wall_ahead', False):
            return 'Up'

        # ELSE continue with the default action.
        return 'Right'


class ModelBasedAgent:
    """
    Model-Based Agent for Practical 02.

    Maintains internal memory of:
    - visited cells
    - percept history
    - action history
    - previous percept
    - previous action
    - estimated position
    - estimated direction
    """

    DIRECTIONS = ['Up', 'Right', 'Down', 'Left']

    DELTAS = {
        'Up': (0, 1),
        'Right': (1, 0),
        'Down': (0, -1),
        'Left': (-1, 0)
    }

    def __init__(self):

        
        # Internal memory
        self.visited_cells = {(0, 0)}

        self.percept_history = []

        self.action_history = []

        self.last_percept = None

        self.last_action = None

        # Estimated position and direction
        self.estimated_position = [0, 0]

        self.direction_index = 1  # Right

        # Used to detect repeated situations
        self.repeated_percept_count = 0

        self.steps_without_progress = 0

    # Helper Methods
    def _normalise_percept(self, percept):

        return (
            bool(percept.get('wall_ahead', False)),
            bool(percept.get('food_here', False))
        )

    def _direction_after_left(self):

        return (
            self.direction_index - 1
        ) % 4

    def _direction_after_right(self):

        return (
            self.direction_index + 1
        ) % 4

    def _position_after_forward(self, direction_index):

        direction = self.DIRECTIONS[
            direction_index
        ]

        dx, dy = self.DELTAS[
            direction
        ]

        return (
            self.estimated_position[0] + dx,
            self.estimated_position[1] + dy
        )

  
    # Update Internal State
    def _update_memory_after_action(self, action):

        if action == 'Left':

            self.direction_index = (
                self._direction_after_left()
            )

        elif action == 'Right':

            self.direction_index = (
                self._direction_after_right()
            )

        elif action == 'Forward':

            self.estimated_position = list(
                self._position_after_forward(
                    self.direction_index
                )
            )

   
    # Sense and Act
    def sense_and_act(self, percept: dict) -> str:

        current_percept = self._normalise_percept(
            percept
        )

        
        # Step 1:
        # Update state using previous action.
        if self.last_action is not None:

            self._update_memory_after_action(
                self.last_action
            )

        
        # Step 2:
        # Record current state.
        current_cell = tuple(
            self.estimated_position
        )

        already_visited = (
            current_cell in self.visited_cells
        )

        self.visited_cells.add(
            current_cell
        )

        self.percept_history.append(
            current_percept
        )

        
        # Detect repeated percept
        if self.last_percept == current_percept:

            self.repeated_percept_count += 1

        else:

            self.repeated_percept_count = 0

        
        # Detect repeated cell
        if already_visited:

            self.steps_without_progress += 1

        else:

            self.steps_without_progress = 0

        
        # Extract percept information
        wall_ahead = current_percept[0]

        food_here = current_percept[1]

        
        # CONDITION-ACTION RULES + MEMORY
        # IF food is ahead THEN move forward.
        if food_here:

            action = 'Forward'

        # IF wall is ahead:
        elif wall_ahead:

            left_index = (
                self._direction_after_left()
            )

            right_index = (
                self._direction_after_right()
            )

            left_cell = (
                self._position_after_forward(
                    left_index
                )
            )

            right_cell = (
                self._position_after_forward(
                    right_index
                )
            )

            left_visited = (
                left_cell in self.visited_cells
            )

            right_visited = (
                right_cell in self.visited_cells
            )

            # IF wall ahead AND left is not visited
            # THEN turn left.
            if not left_visited:

                action = 'Left'

            # ELSE IF right is not visited
            # THEN turn right.
            elif not right_visited:

                action = 'Right'

            # ELSE change direction to escape the loop.
            else:

                action = 'Right'

        
        # Repeated situation detected
        elif (
            self.repeated_percept_count >= 1
            or self.steps_without_progress >= 2
        ):

            right_index = (
                self._direction_after_right()
            )

            right_cell = (
                self._position_after_forward(
                    right_index
                )
            )

            if right_cell not in self.visited_cells:

                action = 'Right'

            else:

                action = 'Left'

        
        # Default action
        else:

            action = 'Forward'

        
        # Store action in memory
        self.last_percept = current_percept

        self.last_action = action

        self.action_history.append(
            action
        )

        return action


class SearchAgent:
    """Breadth-First Search agent for Practical 03."""

    ACTIONS = [
        ('Up', (0, 1)),
        ('Down', (0, -1)),
        ('Left', (-1, 0)),
        ('Right', (1, 0))
    ]

    def bfs_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size
    ):

        width, height = grid_size

        walls = set(
            tuple(w)
            for w in walls
        )

        start = tuple(start_pos)

        goal = tuple(goal_pos)

        # Invalid positions
        if start in walls or goal in walls:

            return None

        # Already at goal
        if start == goal:

            return []

        
        # BFS queue
        queue = deque(
            [(start, [])]
        )

        visited = {start}

        while queue:

            current, path = queue.popleft()

            for action, (dx, dy) in self.ACTIONS:

                next_position = (
                    current[0] + dx,
                    current[1] + dy
                )

                # Check boundaries
                if not (
                    0 <= next_position[0] < width
                    and
                    0 <= next_position[1] < height
                ):

                    continue

                # Check walls
                if next_position in walls:

                    continue

                # Already visited
                if next_position in visited:

                    continue

                new_path = (
                    path + [action]
                )

                # Goal reached
                if next_position == goal:

                    return new_path

                visited.add(
                    next_position
                )

                queue.append(
                    (
                        next_position,
                        new_path
                    )
                )

        # No path
        return None