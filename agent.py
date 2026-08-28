# agent.py
import random
import math
import heapq

class GreedyGridAgent:
    def __init__(self):
        self.actions_pool = ['up', 'down', 'left', 'right']
    
    def sense_and_act(self, percept):
        return random.choice(self.actions_pool)


class SearchAgent:
    def __init__(self):
        self.active_algo = 'AStar'
        self.plan = []
        self.target_food = None  # Track current target
    
    def manhattan_distance(self, pos, goal):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
    
    def euclidean_distance(self, pos, goal):
        return math.sqrt((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2)
    
    def astar_search(self, start_pos, goal_pos, walls, grid_size, heuristic_type='manhattan'):
        if start_pos == goal_pos:
            return []
        
        frontier = []
        h_start = self.manhattan_distance(start_pos, goal_pos) if heuristic_type == 'manhattan' else self.euclidean_distance(start_pos, goal_pos)
        heapq.heappush(frontier, (h_start, 0, start_pos, []))
        reached = set([start_pos])
        
        # NOTE: these MUST match the real movement deltas used by
        # VisualGridHuntGame.execute_action(), or A* will plan paths in a
        # coordinate system that doesn't match what actually happens on screen.
        # up   -> y increases
        # down -> y decreases
        directions = {'up': (0, 1), 'down': (0, -1), 'left': (-1, 0), 'right': (1, 0)}
        
        while frontier:
            f_cost, g_cost, current_pos, path = heapq.heappop(frontier)
            
            if current_pos == goal_pos:
                return path
            
            for action, (dx, dy) in directions.items():
                new_pos = (current_pos[0] + dx, current_pos[1] + dy)
                
                if not (0 <= new_pos[0] < grid_size[0] and 0 <= new_pos[1] < grid_size[1]):
                    continue
                if new_pos in walls or new_pos in reached:
                    continue
                
                new_g = g_cost + 1
                new_h = self.manhattan_distance(new_pos, goal_pos) if heuristic_type == 'manhattan' else self.euclidean_distance(new_pos, goal_pos)
                new_f = new_g + new_h
                
                heapq.heappush(frontier, (new_f, new_g, new_pos, path + [action]))
                reached.add(new_pos)
        
        return None
    
    def sense_and_act(self, percept):
        if self.active_algo == 'AStar':
            agent_pos = tuple(percept['agent_pos'])
            food_positions = percept.get('food_positions', [])
            walls = set(percept.get('walls', []))
            grid_size = percept.get('grid_size', (10, 10))

            # Defensive: ignore any food the agent is already standing on.
            # (Not expected to occur given this environment's step order,
            # since get_percept() is called before the food is eaten each
            # tick — but this guards against any future timing changes and
            # avoids a dead-end retarget loop if it ever does.)
            food_positions = [f for f in food_positions if tuple(f) != agent_pos]

            # If no food left, keep moving randomly
            if not food_positions:
                self.plan = []
                self.target_food = None
                return random.choice(['up', 'down', 'left', 'right'])

            # Find closest food
            closest_food = min(food_positions, key=lambda f: self.manhattan_distance(agent_pos, f))

            # If target food changed or no plan left, recalculate
            if self.target_food != closest_food or not self.plan:
                self.target_food = closest_food
                self.plan = self.astar_search(agent_pos, closest_food, walls, grid_size)
                if not self.plan:
                    # No path found (e.g. fully walled off) — don't get stuck
                    return random.choice(['up', 'down', 'left', 'right'])

            # Execute next action from plan
            return self.plan.pop(0)

        return random.choice(['up', 'down', 'left', 'right'])


class SimpleReflexAgent:
    def __init__(self):
        self.actions_pool = ['up', 'down', 'left', 'right']
        self.last_action = None
    
    def sense_and_act(self, percept):
        if percept.get('wall_ahead', False):
            return random.choice(['left', 'right'])
        if percept.get('food_here', False):
            return random.choice(self.actions_pool)
        return random.choice(self.actions_pool)


class ModelBasedAgent:
    def __init__(self):
        self.actions_pool = ['up', 'down', 'left', 'right']
        self.last_action = None
        self.tried_actions = set()
        self.position_history = []
    
    def sense_and_act(self, percept):
        current_pos = tuple(percept.get('agent_pos', [0, 0]))
        self.position_history.append(current_pos)
        
        if self.position_history.count(current_pos) > 3:
            self.tried_actions = set()
            self.position_history = []
            return random.choice(self.actions_pool)
        
        if percept.get('wall_ahead', False):
            available_actions = [a for a in self.actions_pool if a != self.last_action]
            if not available_actions:
                self.tried_actions = set()
                available_actions = self.actions_pool
            action = random.choice(available_actions)
            self.last_action = action
            return action
        
        if percept.get('food_here', False):
            self.last_action = random.choice(self.actions_pool)
            return self.last_action
        
        action = random.choice(self.actions_pool)
        self.last_action = action
        return action