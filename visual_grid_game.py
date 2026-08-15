# visual_grid_game.py
import random
import sys
import tkinter as tk
from agent import SearchAgent

class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]  # Starting position (x, y)

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
        self.toxic_traps = set()
        self.agent_direction = 'Right'

    def _in_bounds(self, pos):
        return 0 <= pos[0] < self.width and 0 <= pos[1] < self.height

# global variable to track the last action taken by the agent
    def _get_ahead_position(self):
        x, y = self.agent_pos
        if self.agent_direction == 'Up':
            ahead = (x, y + 1)
        elif self.agent_direction == 'Down':
            ahead = (x, y - 1)
        elif self.agent_direction == 'Left':
            ahead = (x - 1, y)
        else:
            ahead = (x + 1, y)

        return ahead if self._in_bounds(ahead) else None
# global variable to track the last action taken by the agent
    def get_percept(self) -> dict:
        ahead_pos = self._get_ahead_position()
        opponent_positions = {tuple(op) for op in self.opponents}

        left_dir = {'Up': 'Left', 'Left': 'Down', 'Down': 'Right', 'Right': 'Up'}[self.agent_direction]
        right_dir = {'Up': 'Right', 'Right': 'Down', 'Down': 'Left', 'Left': 'Up'}[self.agent_direction]

        left_pos = None
        right_pos = None
        if left_dir == 'Up':
            left_pos = (self.agent_pos[0], self.agent_pos[1] + 1)
        elif left_dir == 'Down':
            left_pos = (self.agent_pos[0], self.agent_pos[1] - 1)
        elif left_dir == 'Left':
            left_pos = (self.agent_pos[0] - 1, self.agent_pos[1])
        else:
            left_pos = (self.agent_pos[0] + 1, self.agent_pos[1])

        if right_dir == 'Up':
            right_pos = (self.agent_pos[0], self.agent_pos[1] + 1)
        elif right_dir == 'Down':
            right_pos = (self.agent_pos[0], self.agent_pos[1] - 1)
        elif right_dir == 'Left':
            right_pos = (self.agent_pos[0] - 1, self.agent_pos[1])
        else:
            right_pos = (self.agent_pos[0] + 1, self.agent_pos[1])

        return {
            'agent_pos': tuple(self.agent_pos),
            'wall_ahead': ahead_pos is None or ahead_pos in self.walls,
            'wall_left': left_pos is None or left_pos in self.walls or not self._in_bounds(left_pos),
            'wall_right': right_pos is None or right_pos in self.walls or not self._in_bounds(right_pos),
            'food_ahead': ahead_pos is not None and ahead_pos in self.food_positions,
            'food_here': tuple(self.agent_pos) in self.food_positions,
            'toxin_ahead': ahead_pos is not None and ahead_pos in self.toxic_traps,
            'opponent_ahead': ahead_pos is not None and ahead_pos in opponent_positions,
            'collision': self.collision,
            'grid_size': (self.width, self.height),
            'walls': list(self.walls),
            'all_food': list(self.food_positions),
        
        }

    def execute_action(self, action: str):
        self.steps += 1
        new_pos = list(self.agent_pos)

        if action in {'Up', 'Down', 'Left', 'Right'}:
            self.agent_direction = action

        if action == 'Up':
            new_pos[1] = min(self.height - 1, new_pos[1] + 1)
        elif action == 'Down':
            new_pos[1] = max(0, new_pos[1] - 1)
        elif action == 'Left':
            new_pos[0] = max(0, new_pos[0] - 1)
        elif action == 'Right':
            new_pos[0] = min(self.width - 1, new_pos[0] + 1)

        if tuple(new_pos) in self.walls:
            self.score -= 5
        else:
            self.agent_pos = new_pos

        tuple_pos = tuple(self.agent_pos)
        if tuple_pos in self.food_positions:
            self.food_positions.remove(tuple_pos)
            self.score += 20

        if tuple_pos in self.toxic_traps:
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
        return len(self.food_positions) == 0 or self.steps >= 60 or self.collision

class SimpleReflexAgent:
    """A simple reflex agent that makes decisions using strict IF-THEN rules."""

    def __init__(self):
        self.heading = 'Right'
        self.visited_cells = set()
        self.last_action = None
        self.last_position = None

    def _turn_left(self, direction: str) -> str:
        turn_map = {'Up': 'Left', 'Left': 'Down', 'Down': 'Right', 'Right': 'Up'}
        return turn_map[direction]

    def _turn_right(self, direction: str) -> str:
        turn_map = {'Up': 'Right', 'Right': 'Down', 'Down': 'Left', 'Left': 'Up'}
        return turn_map[direction]

    def _next_position(self, pos, direction):
        x, y = pos
        if direction == 'Up':
            return (x, y + 1)
        if direction == 'Down':
            return (x, y - 1)
        if direction == 'Left':
            return (x - 1, y)
        
        return (x + 1, y)

    def sense_and_act(self, percept: dict) -> str:
        pos = tuple(percept['agent_pos']) if 'agent_pos' in percept else None
        if pos is not None:
            self.visited_cells.add(pos)
            self.last_position = pos

        if percept.get('food_here'):
            self.last_action = self.heading
            return self.last_action

        if pos is not None:
            ahead_cell = self._next_position(pos, self.heading)
            if percept.get('wall_ahead') or ahead_cell in self.visited_cells:
                if not percept.get('wall_left'):
                    left_cell = self._next_position(pos, self._turn_left(self.heading))
                    if left_cell not in self.visited_cells:
                        self.heading = self._turn_left(self.heading)
                    else:
                        self.heading = self._turn_right(self.heading)
                elif not percept.get('wall_right'):
                    self.heading = self._turn_right(self.heading)
                else:
                    self.heading = self._turn_right(self.heading)
            else:
                self.heading = self.heading
        else:
            self.heading = self._turn_left(self.heading)

        self.last_action = self.heading
        return self.last_action

    def get_action(self, percept: dict) -> str:
        return self.sense_and_act(percept)

class ModelBasedAgent:
    """A model-based agent that remembers visited cells and avoids repeating trapped paths."""

    def __init__(self):
        self.heading = 'Right'
        self.visited_cells = set()
        self.last_action = None
        self.last_position = None

    def _turn_left(self, direction: str) -> str:
        turn_map = {'Up': 'Left', 'Left': 'Down', 'Down': 'Right', 'Right': 'Up'}
        return turn_map[direction]

    def _turn_right(self, direction: str) -> str:
        turn_map = {'Up': 'Right', 'Right': 'Down', 'Down': 'Left', 'Left': 'Up'}
        return turn_map[direction]

    def _next_position(self, pos, direction):
        x, y = pos
        if direction == 'Up':
            return (x, y + 1)
        if direction == 'Down':
            return (x, y - 1)
        if direction == 'Left':
            return (x - 1, y)
        return (x + 1, y)

    def sense_and_act(self, percept: dict) -> str:
        pos = tuple(percept['agent_pos']) if 'agent_pos' in percept else None
        if pos is not None:
            self.visited_cells.add(pos)
            self.last_position = pos

        if percept.get('food_here'):
            self.last_action = self.heading
            return self.last_action

        if percept.get('wall_ahead'):
            if pos is not None:
                left_cell = self._next_position(pos, self._turn_left(self.heading))
                right_cell = self._next_position(pos, self._turn_right(self.heading))
                if left_cell in self.visited_cells and right_cell not in self.visited_cells:
                    self.heading = self._turn_right(self.heading)
                elif left_cell not in self.visited_cells:
                    self.heading = self._turn_left(self.heading)
                else:
                    self.heading = self._turn_right(self.heading)
            else:
                self.heading = self._turn_left(self.heading)
            self.last_action = self.heading
            return self.last_action

        self.last_action = self.heading
        return self.last_action

    def get_action(self, percept: dict) -> str:
        return self.sense_and_act(percept)


def run_console_simulation(width=10, height=10, num_food=10, num_opponents=0, walls=None):
    env = VisualGridHuntGame(width=width, height=height, num_food=num_food, num_opponents=num_opponents,
                             custom_walls=walls)
    agent = SearchAgent()

    print("=== Console Grid Hunt Started ===")
    while not env.is_done():
        percept = env.get_percept()
        action = agent.get_action(percept)
        env.execute_action(action)
        print(f"Step {env.steps}: pos={tuple(env.agent_pos)} action={action} score={env.score} food_left={len(env.food_positions)}")

    print(f"Finished! Final score: {env.score} after {env.steps} steps.")


class GridGameGUI:
    """Tkinter wrapper that dynamically scales cell sizes to keep larger grids on screen."""

    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2, walls=None):
        self.root = root
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")

        self.env = VisualGridHuntGame(width=width, height=height, num_food=num_food, num_opponents=num_opponents,
                                      custom_walls=walls)
        self.agent = SearchAgent()

        # Dynamically calculate cell size so the total canvas fits nicely within a 600x600 window ceiling
        max_canvas_dim = 600
        self.cell_size = max(20, min(max_canvas_dim // self.env.width, max_canvas_dim // self.env.height))

        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack()

        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 14))
        self.label.pack(pady=10)

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop, font=("Arial", 12), bg="#000066",
                             fg="white")
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

        for tx, ty in self.env.toxic_traps:
            center_x = tx * self.cell_size + self.cell_size / 2
            center_y = (self.env.height - 1 - ty) * self.cell_size + self.cell_size / 2
            size = self.cell_size * 0.25
            self.canvas.create_polygon(
                center_x, center_y - size,
                center_x + size, center_y,
                center_x, center_y + size,
                center_x - size, center_y,
                fill="#7c3aed", outline="#5b21b6"
            )

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


    def run_loop(self):
        self.btn.config(state="disabled")

        def step():
            if not self.env.is_done():
                action = self.agent.get_action(self.env.get_percept())
                self.env.execute_action(action)

                self.draw_grid()
                self.label.config(text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action}")
                self.root.update_idletasks()
                self.root.update()
                print(f"GUI step {self.env.steps}: pos={tuple(self.env.agent_pos)} action={action} score={self.env.score}")
                self.root.after(100, step)
            else:
                end_text = f"Collision! Game Over! Final Score: {self.env.score}" if self.env.collision else f"Finished! Final Score: {self.env.score}"
                self.label.config(text=end_text)
                self.btn.config(state="normal")

        step()


if __name__ == "__main__":
    if '--console' in sys.argv:
        run_console_simulation(width=10, height=10, num_food=10, num_opponents=0)
    else:
        try:
            root = tk.Tk()
            root.withdraw()
            root.update_idletasks()
            root.deiconify()
            app = GridGameGUI(root, width=12, height=12, num_food=15, num_opponents=0)
            root.mainloop()
        except tk.TclError:
            print("Tkinter is unavailable in this environment; running console mode instead.")
            run_console_simulation(width=10, height=10, num_food=10, num_opponents=0)
