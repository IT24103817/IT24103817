import random
import tkinter as tk

# Clockwise order used for turning: Up -> Right -> Down -> Left -> Up ...
FACING_ORDER = ['Up', 'Right', 'Down', 'Left']
DIRECTION_VECTORS = {
    'Up': (0, 1),
    'Down': (0, -1),
    'Left': (-1, 0),
    'Right': (1, 0),
}


class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None, num_traps=5, start_pos=(0, 0)):
        self.width = width
        self.height = height
        self.agent_pos = list(start_pos)  # Starting position (x, y)
        self.facing = 'Up'  # agent orientation

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}

        self.food_positions = set()
        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            pos_tuple = (fx, fy)
            if pos_tuple != tuple(self.agent_pos) and pos_tuple not in self.walls:
                self.food_positions.add(pos_tuple)

        self.toxic_traps = set()
        while len(self.toxic_traps) < num_traps:
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)
            pos_tuple = (tx, ty)
            if (pos_tuple != tuple(self.agent_pos) and
                    pos_tuple not in self.walls and
                    pos_tuple not in self.food_positions):
                self.toxic_traps.add(pos_tuple)

        self.opponents = []
        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)
            op_pos = [ox, oy]
            if (tuple(op_pos) != tuple(self.agent_pos) and
                    tuple(op_pos) not in self.walls and
                    tuple(op_pos) not in self.food_positions):
                self.opponents.append(op_pos)

        self.score = 0
        self.steps = 0
        self.collision = False

    # ---------- Partial Observability ----------
    def _direction_vector(self, facing=None):
        if facing is None:
            facing = self.facing
        return DIRECTION_VECTORS[facing]

    def _cell_in_direction(self, facing, distance=1):
        dx, dy = self._direction_vector(facing)
        return (self.agent_pos[0] + dx * distance, self.agent_pos[1] + dy * distance)

    def _is_wall_or_out(self, cell):
        x, y = cell
        in_bounds = 0 <= x < self.width and 0 <= y < self.height
        return (not in_bounds) or (cell in self.walls)

    def _nearest_food_distance_in_line(self, facing, max_dist=4):
        for d in range(1, max_dist + 1):
            c = self._cell_in_direction(facing, d)
            if self._is_wall_or_out(c):
                return 0
            if c in self.food_positions:
                return d
        return 0

    def get_percept(self) -> dict:
        current = tuple(self.agent_pos)

        ahead_facing = self.facing
        left_facing = FACING_ORDER[(FACING_ORDER.index(self.facing) - 1) % 4]
        right_facing = FACING_ORDER[(FACING_ORDER.index(self.facing) + 1) % 4]

        ahead_cell = self._cell_in_direction(ahead_facing, 1)
        left_cell = self._cell_in_direction(left_facing, 1)
        right_cell = self._cell_in_direction(right_facing, 1)

        wall_ahead = self._is_wall_or_out(ahead_cell)
        wall_left = self._is_wall_or_out(left_cell)
        wall_right = self._is_wall_or_out(right_cell)

        food_here = current in self.food_positions
        food_ahead = (not wall_ahead) and (ahead_cell in self.food_positions)
        food_left = (not wall_left) and (left_cell in self.food_positions)
        food_right = (not wall_right) and (right_cell in self.food_positions)

        food_ahead_dist = self._nearest_food_distance_in_line(ahead_facing, max_dist=4)
        food_left_dist = self._nearest_food_distance_in_line(left_facing, max_dist=4)
        food_right_dist = self._nearest_food_distance_in_line(right_facing, max_dist=4)

        return {
            'wall_ahead': wall_ahead,
            'wall_left': wall_left,
            'wall_right': wall_right,
            'food_here': food_here,
            'food_ahead': food_ahead,
            'food_left': food_left,
            'food_right': food_right,
            'food_ahead_dist': food_ahead_dist,
            'food_left_dist': food_left_dist,
            'food_right_dist': food_right_dist,
            'toxin_here': current in self.toxic_traps,
            'facing': self.facing,
            'collision': self.collision,
            'score': self.score,
            'remaining_food': len(self.food_positions),
        }

    # ---------- Actions ----------
    def _rotate(self, step):
        idx = FACING_ORDER.index(self.facing)
        self.facing = FACING_ORDER[(idx + step) % 4]

    def execute_action(self, action: str):
        self.steps += 1

        if action == 'turn_left':
            self._rotate(-1)
        elif action == 'turn_right':
            self._rotate(1)
        elif action == 'move_forward':
            dx, dy = self._direction_vector()
            new_pos = [self.agent_pos[0] + dx, self.agent_pos[1] + dy]
            in_bounds = 0 <= new_pos[0] < self.width and 0 <= new_pos[1] < self.height
            if not in_bounds or tuple(new_pos) in self.walls:
                self.score -= 5
            else:
                self.agent_pos = new_pos
        elif action == 'suck':
            pos_t = tuple(self.agent_pos)
            if pos_t in self.food_positions:
                self.food_positions.remove(pos_t)
                self.score += 20

        pos_t = tuple(self.agent_pos)
        if pos_t in self.toxic_traps:
            self.score -= 15

        for op in self.opponents:
            move = random.choice(['Up', 'Down', 'Left', 'Right', 'Stay'])
            if move == 'Up' and op[1] < self.height - 1:
                op[1] += 1
            elif move == 'Down' and op[1] > 0:
                op[1] -= 1
            elif move == 'Left' and op[0] > 0:
                op[0] -= 1
            elif move == 'Right' and op[0] < self.width - 1:
                op[0] += 1

            if op == self.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 220 or self.collision


class SimpleReflexAgent:
    def sense_and_act(self, percept: dict) -> str:
        if percept['food_here']:
            return 'suck'
        elif percept['wall_ahead']:
            return 'turn_left'
        else:
            return 'move_forward'


class ModelBasedAgent:
    def __init__(self):
        self.believed_pos = (0, 0)
        self.believed_facing = 'Up'
        self.visited_cells = {(0, 0)}
        self.blocked_edges = set()
        self.toxin_cells = set()
        self.last_action = None

        self.state_counts = {}
        self.escape_mode_steps = 0
        self.force_forward_steps = 0
        self.empty_view_counts = {}

        # NEW: short action history to penalize immediate undo
        self.action_history = []

    def _peek_facing(self, step):
        idx = FACING_ORDER.index(self.believed_facing)
        return FACING_ORDER[(idx + step) % 4]

    def _cell_ahead(self, facing):
        dx, dy = DIRECTION_VECTORS[facing]
        return (self.believed_pos[0] + dx, self.believed_pos[1] + dy)

    def _update_state(self, percept: dict):
        if self.last_action == 'turn_left':
            self.believed_facing = self._peek_facing(-1)
        elif self.last_action == 'turn_right':
            self.believed_facing = self._peek_facing(1)
        elif self.last_action == 'move_forward':
            if percept['wall_ahead']:
                self.blocked_edges.add((self.believed_pos, self.believed_facing))
            else:
                self.believed_pos = self._cell_ahead(self.believed_facing)

        self.visited_cells.add(self.believed_pos)
        if percept.get('toxin_here', False):
            self.toxin_cells.add(self.believed_pos)

        key = (self.believed_pos, self.believed_facing)
        self.state_counts[key] = self.state_counts.get(key, 0) + 1
        if self.state_counts[key] >= 4 and self.escape_mode_steps == 0:
            self.escape_mode_steps = 4

        no_food_visible = (
            percept.get('food_ahead_dist', 0) == 0 and
            percept.get('food_left_dist', 0) == 0 and
            percept.get('food_right_dist', 0) == 0
        )
        if no_food_visible:
            self.empty_view_counts[key] = self.empty_view_counts.get(key, 0) + 1

    def _remember_action(self, action):
        self.action_history.append(action)
        if len(self.action_history) > 4:
            self.action_history.pop(0)

    def _candidate(self, rel_turn):
        if rel_turn == 0:
            next_facing = self.believed_facing
            action = 'move_forward'
            next_pos = self._cell_ahead(next_facing)
            blocked = (self.believed_pos, next_facing) in self.blocked_edges
        elif rel_turn == -1:
            next_facing = self._peek_facing(-1)
            action = 'turn_left'
            next_pos = self.believed_pos
            blocked = False
        else:
            next_facing = self._peek_facing(1)
            action = 'turn_right'
            next_pos = self.believed_pos
            blocked = False
        return next_pos, next_facing, blocked, action

    def sense_and_act(self, percept: dict) -> str:
        self._update_state(percept)

        # 1) Immediate collection
        if percept['food_here']:
            action = 'suck'
            self.last_action = action
            self._remember_action(action)
            return action

        # 2) Commit forward once after directional turn
        if self.force_forward_steps > 0:
            if not percept['wall_ahead']:
                action = 'move_forward'
                self.force_forward_steps -= 1
                self.last_action = action
                self._remember_action(action)
                return action
            else:
                self.force_forward_steps = 0

        # 3) Strong food-targeting by nearest visible direction
        ahead_d = percept.get('food_ahead_dist', 0)
        left_d = percept.get('food_left_dist', 0)
        right_d = percept.get('food_right_dist', 0)

        candidates = []
        if ahead_d > 0 and not percept['wall_ahead']:
            candidates.append(('ahead', ahead_d))
        if left_d > 0 and not percept['wall_left']:
            candidates.append(('left', left_d))
        if right_d > 0 and not percept['wall_right']:
            candidates.append(('right', right_d))

        if candidates:
            candidates.sort(key=lambda x: x[1])
            direction = candidates[0][0]
            if direction == 'ahead':
                action = 'move_forward'
            elif direction == 'left':
                action = 'turn_left'
                self.force_forward_steps = 1
            else:
                action = 'turn_right'
                self.force_forward_steps = 1

            self.last_action = action
            self._remember_action(action)
            return action

        # 4) Late-game aggressive mode (step minimizer)
        if percept['remaining_food'] <= 3:
            if not percept['wall_ahead']:
                action = 'move_forward'
            elif not percept['wall_right']:
                action = 'turn_right'
            else:
                action = 'turn_left'
            self.last_action = action
            self._remember_action(action)
            return action

        # 5) Escape mode
        if self.escape_mode_steps > 0:
            if not percept['wall_ahead']:
                action = 'move_forward'
            elif not percept['wall_right']:
                action = 'turn_right'
            else:
                action = 'turn_left'
            self.escape_mode_steps -= 1
            self.last_action = action
            self._remember_action(action)
            return action

        # 6) Memory-guided scoring
        options = []
        for rel_turn in (0, -1, 1):
            next_pos, next_facing, blocked, candidate_action = self._candidate(rel_turn)
            score = 0

            if candidate_action == 'move_forward' and (blocked or percept['wall_ahead']):
                score -= 100

            if candidate_action == 'move_forward':
                if next_pos not in self.visited_cells:
                    score += 16
                else:
                    score -= 5

            if candidate_action == 'move_forward' and next_pos in self.toxin_cells:
                score -= 30

            # Stronger forward preference (fewer turns)
            if candidate_action == 'move_forward':
                score += 6
            else:
                score += 0

            score -= 2 * self.state_counts.get((next_pos, next_facing), 0)
            score -= 3 * self.empty_view_counts.get((next_pos, next_facing), 0)

            # Penalize immediate turn-undo patterns
            if len(self.action_history) >= 1:
                last = self.action_history[-1]
                if (last == 'turn_left' and candidate_action == 'turn_right') or \
                   (last == 'turn_right' and candidate_action == 'turn_left'):
                    score -= 4

            options.append((score, candidate_action))

        options.sort(reverse=True, key=lambda x: x[0])
        action = options[0][1]

        if percept['wall_ahead'] and action == 'move_forward':
            action = 'turn_right'

        self.last_action = action
        self._remember_action(action)
        return action


class GridGameGUI:
    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2, walls=None, agent_type='model', start_pos=(0, 0)):
        self.root = root
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")
        self.env = VisualGridHuntGame(
            width=width,
            height=height,
            num_food=num_food,
            num_opponents=num_opponents,
            custom_walls=walls,
            start_pos=start_pos
        )

        if agent_type == 'simple':
            self.agent = SimpleReflexAgent()
        else:
            self.agent = ModelBasedAgent()

        max_canvas_dim = 600
        self.cell_size = max(20, min(max_canvas_dim // self.env.width, max_canvas_dim // self.env.height))
        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack()

        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 14))
        self.label.pack(pady=10)

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop, font=("Arial", 12), bg="#000066", fg="white")
        self.btn.pack(pady=5)

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")

        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (self.env.height - 1 - y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "#f1f5f9" if (x, y) not in self.env.walls else "#64748b"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cbd5e1")

                if self.cell_size >= 40 and (x, y) in self.env.walls:
                    self.canvas.create_text(
                        x1 + self.cell_size / 2,
                        y1 + self.cell_size / 2,
                        text="W",
                        fill="white",
                        font=("Arial", 8, "bold")
                    )

        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_oval(
                x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5,
                fill="#f59e0b", outline="#d97706"
            )

        for tx, ty in self.env.toxic_traps:
            offset = self.cell_size * 0.25
            x1 = tx * self.cell_size + offset
            y1 = (self.env.height - 1 - ty) * self.cell_size + offset
            self.canvas.create_polygon(
                x1 + self.cell_size * 0.25, y1,
                x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5,
                x1, y1 + self.cell_size * 0.5,
                fill="#9333ea", outline="#581c87"
            )

        for ox, oy in self.env.opponents:
            offset = self.cell_size * 0.2
            x1 = ox * self.cell_size + offset
            y1 = (self.env.height - 1 - oy) * self.cell_size + offset
            self.canvas.create_rectangle(
                x1, y1, x1 + self.cell_size * 0.6, y1 + self.cell_size * 0.6,
                fill="#990000", outline="#7a0000"
            )

        ax, ay = self.env.agent_pos
        offset = self.cell_size * 0.15
        x1 = ax * self.cell_size + offset
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset
        self.canvas.create_oval(
            x1, y1, x1 + self.cell_size * 0.7, y1 + self.cell_size * 0.7,
            fill="#000066", outline="#1e3a8a"
        )

        cx = ax * self.cell_size + self.cell_size / 2
        cy = (self.env.height - 1 - ay) * self.cell_size + self.cell_size / 2
        dx, dy = DIRECTION_VECTORS[self.env.facing]
        tip_x = cx + dx * self.cell_size * 0.4
        tip_y = cy - dy * self.cell_size * 0.4
        self.canvas.create_line(cx, cy, tip_x, tip_y, fill="#ffffff", width=3, arrow=tk.LAST)

    def run_loop(self):
        self.btn.config(state="disabled")

        def step():
            if not self.env.is_done():
                percept = self.env.get_percept()
                action = self.agent.sense_and_act(percept)

                # print(f"Step {self.env.steps}: percept={percept}, action={action}")

                self.env.execute_action(action)
                self.draw_grid()
                self.label.config(
                    text=f"Score: {self.env.score} | Steps: {self.env.steps} | Facing: {self.env.facing} | Action: {action}"
                )
                self.root.after(250, step)
            else:
                end_text = (
                    f"Collision! Game Over! Final Score: {self.env.score}"
                    if self.env.collision else
                    f"Finished! Final Score: {self.env.score}"
                )
                self.label.config(text=end_text)
                self.btn.config(state="normal")

        step()


if __name__ == "__main__":
    root = tk.Tk()

    loop_walls = {(8, 8), (7, 4), (5, 4), (6, 8), (7, 5), (4, 7)}
    app = GridGameGUI(
        root,
        width=12,
        height=12,
        num_food=15,
        num_opponents=0,
        walls=loop_walls,
        start_pos=(6, 6),
        agent_type='model'
    )

    root.mainloop()