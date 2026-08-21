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
    Model-Based Agent
    The agent maintains internal memory of previous percepts,
    actions, and visited cells. When the same percept is received
    repeatedly, the agent changes its action to avoid repeating
    the same behaviour.
    """

    def __init__(self):

        # Internal memory
        self.visited_cells = {(0, 0)}
        self.percept_history = []
        self.action_history = []

        self.last_percept = None
        self.last_action = None

        # Estimated internal position
        self.estimated_position = [0, 0]

        # Estimated facing direction
        self.directions = ['Up', 'Right', 'Down', 'Left']
        self.direction_index = 1  # Start facing Right

        # Used to detect repeated situations
        self.repeated_percept_count = 0

    def _normalise_percept(self, percept):

        return (
            bool(percept.get('wall_ahead', False)),
            bool(percept.get('food_here', False))
        )

    def _turn_left(self):

        self.direction_index = (
            self.direction_index - 1
        ) % 4

    def _turn_right(self):

        self.direction_index = (
            self.direction_index + 1
        ) % 4

    def _update_internal_state(self, action):

        """
        Update the internal model using the previous action.
        """

        if action == 'Left':

            self._turn_left()

        elif action == 'Right':

            self._turn_right()

        elif action == 'Forward':

            direction = self.directions[
                self.direction_index
            ]

            if direction == 'Up':
                self.estimated_position[1] += 1

            elif direction == 'Down':
                self.estimated_position[1] -= 1

            elif direction == 'Left':
                self.estimated_position[0] -= 1

            elif direction == 'Right':
                self.estimated_position[0] += 1

    def sense_and_act(self, percept):

        current_percept = self._normalise_percept(
            percept
        )

        
        # 1. Update internal state using previous action
        if self.last_action is not None:

            self._update_internal_state(
                self.last_action
            )

        
        # 2. Record current state
        current_cell = tuple(
            self.estimated_position
        )

        self.visited_cells.add(
            current_cell
        )

        self.percept_history.append(
            current_percept
        )

        
        # 3. Detect repeated percept
        if self.last_percept == current_percept:

            self.repeated_percept_count += 1

        else:

            self.repeated_percept_count = 0

        
        # 4. Condition-Action Rules
        wall_ahead = current_percept[0]
        food_here = current_percept[1]

        
        # IF food is ahead THEN move forward.
        if food_here:

            action = 'Forward'

        elif self.repeated_percept_count >= 1:

            if self.last_action == 'Left':

                action = 'Right'

            elif self.last_action == 'Right':

                action = 'Left'

            elif self.last_action == 'Forward':

                action = 'Right'

            else:

                action = 'Left'

        
        # IF wall ahead THEN turn left.
        elif wall_ahead:

            action = 'Left'

        
        # ELSE move forward.
        else:

            action = 'Forward'

        
        # 5. Store the current decision in memory
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