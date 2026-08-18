# agent.py
import random

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
    """Step 1.2: Simple Reflex Agent with NO memory - pure IF-THEN rules."""
    
    def sense_and_act(self, percept: dict) -> str:
        # Rule 1: IF food_here THEN Suck
        if percept['food_here']:
            return 'Suck'
        
        # Rule 2: IF wall_ahead THEN Left
        elif percept['wall_ahead']:
            return 'Left'
        
        # Rule 3: ELSE Forward
        else:
            return 'Forward'


class ModelBasedAgent:
    """Step 1.3: Model-Based Agent with internal memory/state."""
    
    def __init__(self):
        # ✅ INTERNAL STATE (Memory)
        self.position_history = []      # Tracks actions taken
        self.action_counter = {}        # Counts each action
        self.stuck_counter = 0          # How long stuck
        self.last_action = None
    
    def sense_and_act(self, percept: dict) -> str:
        # Rule 1: Always collect food
        if percept['food_here']:
            return 'Suck'
        
        # Rule 2: Detect if stuck (memory check)
        if len(self.position_history) >= 5:
            last_5 = self.position_history[-5:]
            if len(set(last_5)) <= 2:   # Only 1-2 unique actions
                self.stuck_counter += 1
            else:
                self.stuck_counter = 0
            
            # If stuck, try different strategy
            if self.stuck_counter >= 3:
                return 'Right'  # Turn right instead of left
        
        # Rule 3: Check wall ahead with memory
        if percept['wall_ahead']:
            # Check last action from memory
            if len(self.position_history) >= 2:
                last_action = self.position_history[-1]
                if last_action == 'Left':
                    return 'Right'  # Try turning right
                elif last_action == 'Right':
                    return 'Left'   # Try turning left
            
            # Default to left turn
            return 'Left'
        
        # Rule 4: Default move forward
        return 'Forward'
    
    # ✅ TRANSITION MODEL: Update state before next action
    def update_memory(self, action: str):
        """Update internal state (Transition & Sensor Model)."""
        self.last_action = action
        self.position_history.append(action)
        
        # Count actions
        self.action_counter[action] = self.action_counter.get(action, 0) + 1
        
        # Keep history manageable
        if len(self.position_history) > 50:
            self.position_history.pop(0)
    
    # ✅ SENSOR MODEL: Get memory stats
    def get_memory_stats(self) -> dict:
        """Return current memory state."""
        return {
            'total_actions': len(self.position_history),
            'action_counts': self.action_counter,
            'is_stuck': self.stuck_counter >= 3,
            'last_action': self.last_action
        }