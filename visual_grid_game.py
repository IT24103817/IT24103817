# visual_grid_game.py
import random
import tkinter as tk


class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]  # Starting position (x, y)
        self.agent_dir = 'Right'  # Facing direction: 'Up','Down','Left','Right'

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            # Generate some default scattered walls for a larger grid
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}

        # Dynamically generate random food positions avoiding walls and agent start
        self.food_positions = set()
        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            pos_tuple = (fx, fy)
            if pos_tuple != (0, 0) and pos_tuple not in self.walls:
                self.food_positions.add(pos_tuple)

        # Toxic traps: positions that penalize the agent if entered.
        # Populate while avoiding the agent start (0,0), walls, and food.
        self.toxic_traps = set()
        num_traps = max(1, num_food // 3)
        while len(self.toxic_traps) < num_traps:
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)
            tpos = (tx, ty)
            if tpos != (0, 0) and tpos not in self.walls and tpos not in self.food_positions:
                self.toxic_traps.add(tpos)

        # Generate adversarial opponents
        self.opponents = []
        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)
            op_pos = [ox, oy]
            if tuple(op_pos) != (0, 0) and tuple(op_pos) not in self.walls and tuple(op_pos) not in self.food_positions:
                self.opponents.append(op_pos)

        self.score = 0
        self.steps = 0
        self.collision = False

    def get_percept(self) -> dict:
        # Partial observability: only local booleans about the cell ahead and current cell
        # Compute cell ahead based on current facing direction
        ax, ay = self.agent_pos
        if self.agent_dir == 'Up':
            ahead = (ax, min(self.height - 1, ay + 1))
        elif self.agent_dir == 'Down':
            ahead = (ax, max(0, ay - 1))
        elif self.agent_dir == 'Left':
            ahead = (max(0, ax - 1), ay)
        else:  # Right
            ahead = (min(self.width - 1, ax + 1), ay)

        return {
            'wall_ahead': ahead in self.walls,
            'food_here': tuple(self.agent_pos) in self.food_positions,
            'facing': self.agent_dir,
            'collision': self.collision,
            'score': self.score,
            'remaining_food': len(self.food_positions)
        }

    def execute_action(self, action: str):
        self.steps += 1
        # Support high-level actions: 'Forward', 'TurnLeft', 'TurnRight', 'Stay'
        # Also accept legacy cardinal moves for convenience
        new_pos = list(self.agent_pos)

        if action == 'Forward':
            if self.agent_dir == 'Up':
                new_pos[1] = min(self.height - 1, new_pos[1] + 1)
            elif self.agent_dir == 'Down':
                new_pos[1] = max(0, new_pos[1] - 1)
            elif self.agent_dir == 'Left':
                new_pos[0] = max(0, new_pos[0] - 1)
            else:  # Right
                new_pos[0] = min(self.width - 1, new_pos[0] + 1)
        elif action == 'TurnLeft':
            order = ['Up', 'Left', 'Down', 'Right']
            idx = order.index(self.agent_dir)
            self.agent_dir = order[(idx + 1) % 4]
        elif action == 'TurnRight':
            order = ['Up', 'Right', 'Down', 'Left']
            idx = order.index(self.agent_dir)
            self.agent_dir = order[(idx + 1) % 4]
        elif action == 'Stay':
            pass
        elif action in ('Up', 'Down', 'Left', 'Right'):
            # Immediate cardinal move (legacy)
            if action == 'Up':
                new_pos[1] = min(self.height - 1, new_pos[1] + 1)
                self.agent_dir = 'Up'
            elif action == 'Down':
                new_pos[1] = max(0, new_pos[1] - 1)
                self.agent_dir = 'Down'
            elif action == 'Left':
                new_pos[0] = max(0, new_pos[0] - 1)
                self.agent_dir = 'Left'
            elif action == 'Right':
                new_pos[0] = min(self.width - 1, new_pos[0] + 1)
                self.agent_dir = 'Right'

        # If the target cell is a wall, penalise and do not move
        if tuple(new_pos) in self.walls:
            self.score -= 5
        else:
            self.agent_pos = new_pos

        # Penalise stepping on toxic traps
        if tuple(self.agent_pos) in getattr(self, 'toxic_traps', set()):
            self.score -= 15

        tuple_pos = tuple(self.agent_pos)
        if tuple_pos in self.food_positions:
            self.food_positions.remove(tuple_pos)
            self.score += 20

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
        return len(self.food_positions) == 0 or self.steps >= 60 or self.collision


class SimpleReflexAgent:
    """Simple reflex agent: no memory, condition-action rules only."""
    def sense_and_act(self, percept: dict) -> str:
        if percept.get('food_here'):
            return 'Stay'
        if percept.get('wall_ahead'):
            return 'TurnLeft'
        return 'Forward'


class ModelBasedAgent:
    """Model-based agent: keeps an internal visited map and last action to avoid loops."""
    def __init__(self):
        self.visited = set()
        self.pos = (0, 0)  # internal estimate of position (assume start at origin)
        self.facing = 'Right'
        self.last_action = None

    def _forward_pos(self, pos, facing):
        x, y = pos
        if facing == 'Up':
            return (x, y + 1)
        if facing == 'Down':
            return (x, y - 1)
        if facing == 'Left':
            return (x - 1, y)
        return (x + 1, y)

    def _left_of(self, facing):
        return {'Up': 'Left', 'Left': 'Down', 'Down': 'Right', 'Right': 'Up'}[facing]

    def _right_of(self, facing):
        return {'Up': 'Right', 'Right': 'Down', 'Down': 'Left', 'Left': 'Up'}[facing]

    def _left_pos(self, pos, facing):
        left = self._left_of(facing)
        return self._forward_pos(pos, left)

    def sense_and_act(self, percept: dict) -> str:
        # Update internal model from the last action
        if self.last_action == 'Forward':
            self.pos = self._forward_pos(self.pos, self.facing)
        elif self.last_action == 'TurnLeft':
            self.facing = self._left_of(self.facing)
        elif self.last_action == 'TurnRight':
            self.facing = self._right_of(self.facing)

        # Record visited cell
        self.visited.add(self.pos)

        # Decision logic using memory
        if percept.get('food_here'):
            action = 'Stay'
        elif percept.get('wall_ahead'):
            left_cell = self._left_pos(self.pos, self.facing)
            if left_cell in self.visited:
                action = 'TurnRight'
            else:
                action = 'TurnLeft'
        else:
            action = 'Forward'

        self.last_action = action
        return action


class GridGameGUI:
    """Tkinter wrapper that dynamically scales cell sizes to keep larger grids on screen."""

    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2, walls=None):
        self.root = root
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")

        self.env = VisualGridHuntGame(width=width, height=height, num_food=num_food, num_opponents=num_opponents,
                                      custom_walls=walls)

        # Dynamically calculate cell size so the total canvas fits nicely within a 600x600 window ceiling
        max_canvas_dim = 600
        self.cell_size = max(20, min(max_canvas_dim // self.env.width, max_canvas_dim // self.env.height))

        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack()

        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 14))
        self.label.pack(pady=10)

        # Buttons to start with different agent architectures
        self.btn_simple = tk.Button(root, text="Run Simple Reflex Agent",
                        command=lambda: self.run_loop(SimpleReflexAgent()), font=("Arial", 12), bg="#0b6623",
                        fg="white")
        self.btn_simple.pack(pady=4)

        self.btn_model = tk.Button(root, text="Run Model-Based Agent",
                       command=lambda: self.run_loop(ModelBasedAgent()), font=("Arial", 12), bg="#1f4e79",
                       fg="white")
        self.btn_model.pack(pady=4)

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

                # Only draw text if cell is large enough
                if self.cell_size >= 40 and (x, y) in self.env.walls:
                    self.canvas.create_text(x1 + self.cell_size / 2, y1 + self.cell_size / 2, text="W", fill="white",
                                            font=("Arial", 8, "bold"))

        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#f59e0b",
                                    outline="#d97706")

        # Draw toxic traps as purple diamond shapes
        for tx, ty in self.env.toxic_traps:
            cx = tx * self.cell_size + self.cell_size / 2
            cy = (self.env.height - 1 - ty) * self.cell_size + self.cell_size / 2
            size = self.cell_size * 0.25
            points = [
                cx, cy - size,
                cx + size, cy,
                cx, cy + size,
                cx - size, cy
            ]
            self.canvas.create_polygon(points, fill="#7c3aed", outline="#5b21b6")

        for ox, oy in self.env.opponents:
            offset = self.cell_size * 0.2
            x1 = ox * self.cell_size + offset
            y1 = (self.env.height - 1 - oy) * self.cell_size + offset
            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size * 0.6, y1 + self.cell_size * 0.6, fill="#990000",
                                         outline="#7a0000")

        ax, ay = self.env.agent_pos
        offset = self.cell_size * 0.15
        x1 = ax * self.cell_size + offset
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset
        self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.7, y1 + self.cell_size * 0.7, fill="#000066",
                                outline="#1e3a8a")

    def run_loop(self, agent):
        # disable both control buttons while running
        try:
            self.btn_simple.config(state="disabled")
            self.btn_model.config(state="disabled")
        except Exception:
            pass

        def step():
            if not self.env.is_done():
                percept = self.env.get_percept()
                action = agent.sense_and_act(percept)
                self.env.execute_action(action)

                self.draw_grid()
                self.label.config(text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action}")
                self.root.after(200, step)
            else:
                end_text = f"Collision! Game Over! Final Score: {self.env.score}" if self.env.collision else f"Finished! Final Score: {self.env.score}"
                self.label.config(text=end_text)
                # re-enable buttons
                try:
                    self.btn_simple.config(state="normal")
                    self.btn_model.config(state="normal")
                except Exception:
                    pass

        step()


if __name__ == "__main__":
    root = tk.Tk()
    # Try a larger grid size like 12x12 with 15 food and 3 opponents!
    app = GridGameGUI(root, width=12, height=12, num_food=15, num_opponents=0)
    root.mainloop()