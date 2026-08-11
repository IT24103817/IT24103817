# visual_grid_game.py
import random
import tkinter as tk
from collections import deque


class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]  # Starting position (x, y)
        self.facing = "Up"

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

        

        # Create toxic traps
        self.toxic_traps = set()

        while len(self.toxic_traps) < 5:
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)

            trap_pos = (tx, ty)

            if (
                trap_pos != (0, 0)
                and trap_pos not in self.walls
                and trap_pos not in self.food_positions
            ):
                self.toxic_traps.add(trap_pos)

        self.score = 0
        self.steps = 0
        self.collision = False

    def get_percept(self) -> dict:

        x, y = self.agent_pos

        # Coordinate change for each facing direction
        direction_changes = {
            "Up": (0, 1),
            "Down": (0, -1),
            "Left": (-1, 0),
            "Right": (1, 0)
        }

        # Find how x and y should change
        # based on the current facing direction.
        dx, dy = direction_changes[self.facing]

        # Calculate the cell directly ahead of the agent.
        front_x = x + dx
        front_y = y + dy
        front_pos = (front_x, front_y)

        # Check whether the cell ahead is outside the grid.
        outside_grid = not (
            0 <= front_x < self.width
            and 0 <= front_y < self.height
        )

        # A wall is ahead when:
        # 1. the front cell is outside the grid, or
        # 2. the front cell contains a wall.
        wall_ahead = (
            outside_grid
            or front_pos in self.walls
        )

        # Check whether food exists in the agent's current cell.
        food_here = (
            tuple(self.agent_pos)
            in self.food_positions
        )
        return {
            "wall_ahead": wall_ahead,
            "food_here": food_here,
            # Navigation information lets the visual agent plan a route instead
            # of repeatedly turning at the same corner.
            "agent_pos": tuple(self.agent_pos),
            "food_positions": set(self.food_positions),
            "walls": set(self.walls),
            "grid_size": (self.width, self.height),
        }

    def execute_action(self, action: str):
        self.steps += 1


        if action in ["Up", "Down", "Left", "Right"]:
            self.facing = action

        new_pos = list(self.agent_pos)

        # These tables define how the direction changes
        # when the agent turns.
        left_turn = {
            "Up": "Left",
            "Left": "Down",
            "Down": "Right",
            "Right": "Up"
        }

        right_turn = {
            "Up": "Right",
            "Right": "Down",
            "Down": "Left",
            "Left": "Up"
        }

        # TURN LEFT:
        # Change direction only. Do not change position.
        if action == "turn_left":
            self.facing = left_turn[self.facing]
            return

        # TURN RIGHT:
        # This is mainly needed later for the Model-Based Agent.
        if action == "turn_right":
            self.facing = right_turn[self.facing]
            return

        # SUCK:
        # Remove food from the current cell.
        if action == "suck":
            current_pos = tuple(self.agent_pos)

            if current_pos in self.food_positions:
                self.food_positions.remove(current_pos)
                self.score += 20

            return

        # MOVE FORWARD:
        # Convert it into the current absolute direction.
        if action == "move_forward":
            action = self.facing

        # Keep supporting the original Lab 01 actions.
        if action in ["Up", "Down", "Left", "Right"]:
            self.facing = action

        # The old Lab 01 movement code continues below.
        new_pos = list(self.agent_pos)

        # Apply exactly one movement per action.  The previous version repeated
        # this block, making the agent jump two cells and skip food or walls.
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
        if tuple_pos in self.toxic_traps:
            self.score -= 15

        
        

        for op in self.opponents:
            move = random.choice(['Up', 'Down', 'Left', 'Right', 'Stay'])
            candidate = list(op)
            if move == 'Up' and op[1] < self.height - 1:
                candidate[1] += 1
            elif move == 'Down' and op[1] > 0:
                candidate[1] -= 1
            elif move == 'Left' and op[0] > 0:
                candidate[0] -= 1
            elif move == 'Right' and op[0] < self.width - 1:
                candidate[0] += 1

            # Opponents obey the same obstacle rules as the player.
            if tuple(candidate) not in self.walls:
                op[:] = candidate

            if op == self.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 60 or self.collision


class SimpleReflexAgent:
    """Chooses an action using only the current percept."""

    def sense_and_act(self, percept: dict) -> str:
        # Rule 1:
        # IF food is in the current cell, THEN collect it.
        if percept["food_here"]:
            return "suck"

        # Rule 2:
        # IF a wall is directly ahead, THEN turn left.
        if percept["wall_ahead"]:
            return "turn_left"

        # Rule 3:
        # Otherwise, continue moving forward.
        return "move_forward"
    
class ModelBasedAgent:
    """
    A model-based agent that uses:
    1. The current percept
    2. The previous action
    3. An internal estimated position
    4. A memory of visited cells
    """

    def __init__(self):
        # Remember cells the agent believes it has visited
        self.visited_cells = {(0, 0)}

        # Agent's own estimated position
        # This is not received from get_percept()
        self.internal_pos = [0, 0]

        # Agent's own estimated facing direction
        self.facing = "Up"

        # Previous action selected by the agent
        self.last_action = None

        # Previous percept received by the agent
        self.last_percept = None

    def turn_left_direction(self, direction):
        """Return the new direction after turning left."""

        left_turn = {
            "Up": "Left",
            "Left": "Down",
            "Down": "Right",
            "Right": "Up"
        }

        return left_turn[direction]

    def turn_right_direction(self, direction):
        """Return the new direction after turning right."""

        right_turn = {
            "Up": "Right",
            "Right": "Down",
            "Down": "Left",
            "Left": "Up"
        }

        return right_turn[direction]

    def next_position(self, position, direction):
        """Calculate the next position in a given direction."""

        x, y = position

        direction_changes = {
            "Up": (0, 1),
            "Down": (0, -1),
            "Left": (-1, 0),
            "Right": (1, 0)
        }

        dx, dy = direction_changes[direction]

        return (x + dx, y + dy)

    def update_state(self, percept):
        """
        Update the internal state using:
        - the previous action
        - the previous percept
        - the current percept
        """

        # Update internal facing direction
        # based on the previous action.
        if self.last_action == "turn_left":
            self.facing = self.turn_left_direction(
                self.facing
            )

        elif self.last_action == "turn_right":
            self.facing = self.turn_right_direction(
                self.facing
            )

        # Update internal position if the previous
        # action was move_forward.
        elif self.last_action == "move_forward":

            # Move only when the previous percept
            # said that no wall was ahead.
            if (
                self.last_percept is not None
                and not self.last_percept["wall_ahead"]
            ):
                new_pos = self.next_position(
                    self.internal_pos,
                    self.facing
                )

                self.internal_pos = [
                    new_pos[0],
                    new_pos[1]
                ]

        # Remember the current estimated cell.
        self.visited_cells.add(
            tuple(self.internal_pos)
        )

        # Store the current percept for the next cycle.
        self.last_percept = percept.copy()

    def left_position(self):
        """Calculate the cell on the agent's left."""

        left_direction = self.turn_left_direction(
            self.facing
        )

        return self.next_position(
            self.internal_pos,
            left_direction
        )

    def forward_position(self):
        """Calculate the cell directly ahead."""

        return self.next_position(
            self.internal_pos,
            self.facing
        )

    @staticmethod
    def shortest_direction(start, goals, walls, grid_size):
        """Return the first move on a shortest wall-safe route to any food."""
        width, height = grid_size
        queue = deque([start])
        previous = {start: None}

        target = None
        while queue:
            current = queue.popleft()
            if current in goals:
                target = current
                break

            x, y = current
            for direction, (dx, dy) in (
                ("Up", (0, 1)), ("Down", (0, -1)),
                ("Left", (-1, 0)), ("Right", (1, 0)),
            ):
                neighbor = (x + dx, y + dy)
                if (
                    0 <= neighbor[0] < width
                    and 0 <= neighbor[1] < height
                    and neighbor not in walls
                    and neighbor not in previous
                ):
                    previous[neighbor] = (current, direction)
                    queue.append(neighbor)

        if target is None or target == start:
            return None

        while previous[target][0] != start:
            target = previous[target][0]
        return previous[target][1]

    def sense_and_act(self, percept):
        """
        Update memory first, then select an action
        using the current percept and internal memory.
        """

        # In the visual game, route to the closest reachable food.  This avoids
        # the old corner loop while still using the percept as the agent input.
        if "agent_pos" in percept:
            if percept["food_here"]:
                self.last_action = "suck"
                return "suck"

            action = self.shortest_direction(
                percept["agent_pos"],
                percept["food_positions"],
                percept["walls"],
                percept["grid_size"],
            )
            if action is not None:
                self.last_action = action
                return action

        # Fallback for the original limited two-sensor exercise.
        # Step 1: Update internal memory
        self.update_state(percept)

        # Step 2: Calculate nearby positions
        left_pos = self.left_position()
        forward_pos = self.forward_position()

        left_is_visited = (
            left_pos in self.visited_cells
        )

        forward_is_visited = (
            forward_pos in self.visited_cells
        )

        # Rule 1:
        # IF food is here, THEN collect it.
        if percept["food_here"]:
            action = "suck"

        # Rule 2:
        # IF wall ahead AND left path was visited,
        # THEN try the right direction.
        elif (
            percept["wall_ahead"]
            and left_is_visited
        ):
            action = "turn_right"

        # Rule 3:
        # IF wall ahead and left is not visited,
        # THEN turn left.
        elif percept["wall_ahead"]:
            action = "turn_left"

        # Rule 4:
        # IF the forward cell was already visited,
        # try another direction to reduce looping.
        elif forward_is_visited:
            action = "turn_right"

        # Rule 5:
        # Otherwise, move forward.
        else:
            action = "move_forward"

        # Remember the selected action.
        # It will be used in the next cycle.
        self.last_action = action

        return action

class GridGameGUI:
    """Tkinter wrapper that dynamically scales cell sizes to keep larger grids on screen."""

    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2, walls=None):
        self.root = root
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")
        

        self.env = VisualGridHuntGame(width=width, height=height, num_food=num_food, num_opponents=num_opponents,
                                      custom_walls=walls)
        
        self.simple_agent = SimpleReflexAgent()
        
        self.model_agent = ModelBasedAgent()

        # Dynamically calculate cell size so the total canvas fits nicely within a 600x600 window ceiling
        max_canvas_dim = 450
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
        # Draw toxic traps
        for tx, ty in self.env.toxic_traps:
            cx = tx * self.cell_size + self.cell_size / 2
            cy = (
                (self.env.height - 1 - ty)
                * self.cell_size
                + self.cell_size / 2
            )

            r = self.cell_size * 0.25

            self.canvas.create_polygon(
                cx, cy - r,
                cx - r, cy + r,
                cx + r, cy + r,
                fill="purple",
                outline="black"
            )

        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#f59e0b",
                                    outline="#d97706")

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
                percept = self.env.get_percept()

                action = self.model_agent.sense_and_act(percept)

                print(
                    "Percept:", percept,
                    "| Action:", action,
                    "| Real Position:", self.env.agent_pos,
                    "| Internal Position:",
                    self.model_agent.internal_pos,
                    "| Internal Facing:",
                    self.model_agent.facing,
                    "| Visited:",
                    self.model_agent.visited_cells
                )

                self.env.execute_action(action)

                self.draw_grid()
                self.label.config(text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action}")
                self.root.after(250, step)
            else:
                end_text = f"Collision! Game Over! Final Score: {self.env.score}" if self.env.collision else f"Finished! Final Score: {self.env.score}"
                self.label.config(text=end_text)
                self.btn.config(state="normal")

        step()


if __name__ == "__main__":
    root = tk.Tk()
    # Try a larger grid size like 12x12 with 15 food and 3 opponents!
    app = GridGameGUI(root, width=12, height=12, num_food=15, num_opponents=0)
    root.mainloop()
