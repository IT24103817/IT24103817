import random
import tkinter as tk


class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with toxic traps."""

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}

        # Generate food positions
        self.food_positions = set()

        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)

            pos = (fx, fy)

            if pos != (0, 0) and pos not in self.walls:
                self.food_positions.add(pos)

        # Add toxic traps
        self.toxic_traps = set()

        while len(self.toxic_traps) < 5:
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)

            trap = (tx, ty)

            if (
                trap != (0, 0)
                and trap not in self.walls
                and trap not in self.food_positions
            ):
                self.toxic_traps.add(trap)

        # Generate opponents
        self.opponents = []

        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)

            op_pos = [ox, oy]

            if (
                tuple(op_pos) != (0, 0)
                and tuple(op_pos) not in self.walls
                and tuple(op_pos) not in self.food_positions
                and tuple(op_pos) not in self.toxic_traps
            ):
                self.opponents.append(op_pos)

        self.score = 0
        self.steps = 0
        self.collision = False


    def get_percept(self) -> dict:

        return {
            'agent_pos': list(self.agent_pos),
            'opponent_positions': [list(op) for op in self.opponents],
            'smells_food': tuple(self.agent_pos) in self.food_positions,
            'hit_wall': tuple(self.agent_pos) in self.walls,

            # New toxin sensor
            'smells_toxin': tuple(self.agent_pos) in self.toxic_traps,

            'collision': self.collision,
            'score': self.score,
            'remaining_food': len(self.food_positions)
        }


    def execute_action(self, action: str):

        self.steps += 1

        new_pos = list(self.agent_pos)


        if action == 'Up':
            new_pos[1] = min(self.height - 1, new_pos[1] + 1)

        elif action == 'Down':
            new_pos[1] = max(0, new_pos[1] - 1)

        elif action == 'Left':
            new_pos[0] = max(0, new_pos[0] - 1)

        elif action == 'Right':
            new_pos[0] = min(self.width - 1, new_pos[0] + 1)


        # Wall collision
        if tuple(new_pos) in self.walls:
            self.score -= 5

        else:
            self.agent_pos = new_pos


        position = tuple(self.agent_pos)


        # Food collection
        if position in self.food_positions:
            self.food_positions.remove(position)
            self.score += 20


        # Toxic trap penalty
        if position in self.toxic_traps:
            self.score -= 15



        # Move opponents
        for op in self.opponents:

            move = random.choice(
                ['Up', 'Down', 'Left', 'Right', 'Stay']
            )

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



    def is_done(self):

        return (
            len(self.food_positions) == 0
            or self.steps >= 60
            or self.collision
        )



class GridGameGUI:

    def __init__(self, root, width=10, height=10,
                 num_food=12, num_opponents=2, walls=None):

        self.root = root
        self.root.title(
            "IT3012 - Scalable Multi-Agent Grid Hunt"
        )

        self.env = VisualGridHuntGame(
            width,
            height,
            num_food,
            num_opponents,
            walls
        )


        max_canvas_dim = 600

        self.cell_size = max(
            20,
            min(
                max_canvas_dim // self.env.width,
                max_canvas_dim // self.env.height
            )
        )


        self.canvas = tk.Canvas(
            root,
            width=self.env.width*self.cell_size,
            height=self.env.height*self.cell_size,
            bg="white"
        )

        self.canvas.pack()


        self.label = tk.Label(
            root,
            text="Score: 0 | Steps: 0"
        )

        self.label.pack()


        self.btn = tk.Button(
            root,
            text="Start Simulation",
            command=self.run_loop
        )

        self.btn.pack()


        self.draw_grid()



    def draw_grid(self):

        self.canvas.delete("all")


        # Draw cells and walls
        for x in range(self.env.width):

            for y in range(self.env.height):

                x1=x*self.cell_size
                y1=(self.env.height-1-y)*self.cell_size

                x2=x1+self.cell_size
                y2=y1+self.cell_size


                color = (
                    "#64748b"
                    if (x,y) in self.env.walls
                    else "#f1f5f9"
                )


                self.canvas.create_rectangle(
                    x1,y1,x2,y2,
                    fill=color
                )


        # Draw food
        for fx,fy in self.env.food_positions:

            self.canvas.create_oval(
                fx*self.cell_size+10,
                (self.env.height-1-fy)*self.cell_size+10,
                fx*self.cell_size+30,
                (self.env.height-1-fy)*self.cell_size+30,
                fill="orange"
            )


        # Draw toxic traps (purple)
        for tx,ty in self.env.toxic_traps:

            self.canvas.create_rectangle(
                tx*self.cell_size+8,
                (self.env.height-1-ty)*self.cell_size+8,
                tx*self.cell_size+32,
                (self.env.height-1-ty)*self.cell_size+32,
                fill="purple"
            )


        # Draw opponents
        for ox,oy in self.env.opponents:

            self.canvas.create_rectangle(
                ox*self.cell_size+10,
                (self.env.height-1-oy)*self.cell_size+10,
                ox*self.cell_size+30,
                (self.env.height-1-oy)*self.cell_size+30,
                fill="red"
            )


        # Draw agent
        ax,ay=self.env.agent_pos

        self.canvas.create_oval(
            ax*self.cell_size+5,
            (self.env.height-1-ay)*self.cell_size+5,
            ax*self.cell_size+35,
            (self.env.height-1-ay)*self.cell_size+35,
            fill="blue"
        )



    def run_loop(self):

        self.btn.config(state="disabled")


        def step():

            if not self.env.is_done():

                action=random.choice(
                    ['Up','Down','Left','Right']
                )

                self.env.execute_action(action)

                self.draw_grid()

                self.label.config(
                    text=f"Score: {self.env.score} | Steps: {self.env.steps}"
                )

                self.root.after(250,step)

            else:

                self.label.config(
                    text=f"Game Over Score: {self.env.score}"
                )


        step()



if __name__ == "__main__":

    root=tk.Tk()

    app=GridGameGUI(
        root,
        width=12,
        height=12,
        num_food=15,
        num_opponents=0
    )

    root.mainloop()