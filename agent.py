import random


class GreedyGridAgent:
    """Agent that tries to explore while avoiding hazards."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:

        # Current position
        pos = percept['agent_pos']

        # If currently on toxic trap, escape
        if percept.get('smells_toxin', False):

            if pos[1] < 3:
                return 'Up'

            elif pos[0] < 3:
                return 'Right'

            else:
                return 'Down'


        # If wall detected, choose another direction
        if percept.get('hit_wall', False):
            return random.choice(
                ['Up', 'Down', 'Left', 'Right']
            )


        # Normal exploration
        return random.choice(self.actions_pool)