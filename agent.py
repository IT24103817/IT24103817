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
    """Problem-Solving Search Agent (for Practical 3)."""
    pass


