from collections import defaultdict

class SimpleReflexAgent:
    def sense_and_act(self, percept):
        if percept.get('food_here'):
            return 'suck'
        elif percept.get('wall_ahead'):
            return 'turn_left'
        else:
            return 'move_forward'


class ModelBasedAgent:
    def __init__(self):
        self.visit_counts = defaultdict(int)
        self.known_walls = set()
        self.current_pos = (0, 0)
        self.facing = 'Up'
        self.last_action = None

    def get_visit_count(self, cell):
        if cell in self.known_walls:
            return 999999
        return self.visit_counts[cell]

    def sense_and_act(self, percept):
        dirs = ['Up', 'Right', 'Down', 'Left']
        dir_offsets = {
            'Up': (0, 1),
            'Right': (1, 0),
            'Down': (0, -1),
            'Left': (-1, 0)
        }

        if self.last_action == 'turn_left':
            idx = dirs.index(self.facing)
            self.facing = dirs[(idx - 1) % 4]
        elif self.last_action == 'turn_right':
            idx = dirs.index(self.facing)
            self.facing = dirs[(idx + 1) % 4]
        elif self.last_action == 'move_forward':
            dx, dy = dir_offsets[self.facing]
            self.current_pos = (self.current_pos[0] + dx, self.current_pos[1] + dy)

        self.visit_counts[self.current_pos] += 1

        idx = dirs.index(self.facing)
        front_dir = dirs[idx]
        left_dir = dirs[(idx - 1) % 4]
        right_dir = dirs[(idx + 1) % 4]

        fx, fy = dir_offsets[front_dir]
        lx, ly = dir_offsets[left_dir]
        rx, ry = dir_offsets[right_dir]

        front_cell = (self.current_pos[0] + fx, self.current_pos[1] + fy)
        left_cell = (self.current_pos[0] + lx, self.current_pos[1] + ly)
        right_cell = (self.current_pos[0] + rx, self.current_pos[1] + ry)

        if percept.get('wall_ahead'):
            self.known_walls.add(front_cell)

        if percept.get('food_here'):
            action = 'suck'
        elif percept.get('wall_ahead'):
            left_count = self.get_visit_count(left_cell)
            right_count = self.get_visit_count(right_cell)
            if left_count < right_count:
                action = 'turn_left'
            else:
                action = 'turn_right'
        else:
            front_count = self.get_visit_count(front_cell)
            left_count = self.get_visit_count(left_cell)
            right_count = self.get_visit_count(right_cell)

            if front_count == 0:
                action = 'move_forward'
            elif left_count == 0:
                action = 'turn_left'
            elif right_count == 0:
                action = 'turn_right'
            else:
                min_count = min(front_count, left_count, right_count)
                if min_count == front_count:
                    action = 'move_forward'
                elif min_count == left_count:
                    action = 'turn_left'
                else:
                    action = 'turn_right'

        self.last_action = action
        return action