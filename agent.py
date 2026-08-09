import random
from collections import deque


class SimpleReflexAgent:
    """Simple reflex agent: reacts only to the current percept."""

    def sense_and_act(self, percept: dict) -> str:
        if percept.get('food_here'):
            return 'suck'
        if percept.get('wall_ahead'):
            return 'Left'
        return 'move_forward'


class ModelBasedAgent:
    """Model-based agent: stores a small internal memory to avoid repeating the same response."""

    def __init__(self):
        self.visited_states = set()
        self.last_action = None
        self._turn_preference = 'Left'

    def sense_and_act(self, percept: dict) -> str:
        state = (bool(percept.get('wall_ahead')), bool(percept.get('food_here')))
        repeated_state = state in self.visited_states
        self.visited_states.add(state)

        if percept.get('food_here'):
            action = 'suck'
        elif percept.get('wall_ahead'):
            action = 'Right' if repeated_state or self._turn_preference == 'Right' else 'Left'
            self._turn_preference = 'Right' if self._turn_preference == 'Left' else 'Left'
        else:
            action = 'move_forward'

        self.last_action = action
        return action


