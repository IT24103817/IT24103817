import random


class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        pos = percept['agent_pos']
        return random.choice(self.actions_pool)


class SimpleReflexAgent:
    def sense_and_act(self, percept: dict) -> str:
        if percept['food_here']:
            return 'Up'
        elif percept['wall_ahead']:
            return 'Left'
        else:
            return 'Up'


class ModelBasedAgent:

    def __init__(self):
        self.visited_cells = set()
        self.last_action = None
        self.current_position = (0, 0)

    def sense_and_act(self, percept: dict) -> str:
        self.visited_cells.add(self.current_position)

        if percept['food_here']:
            action = 'Up'
        elif percept['wall_ahead']:
            if self.last_action == 'Left':
                action = 'Right'
            else:
                action = 'Left'
        else:
            action = 'Up'

        self.last_action = action
        return action