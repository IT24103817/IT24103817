import random
import tkinter as tk

from agent import SimpleReflexAgent, ModelBasedAgent


class VisualGridHuntGame:
    """Practical 02 partially observable visual environment."""

    DIRECTIONS = {
        'Up': (0, 1),
        'Down': (0, -1),
        'Left': (-1, 0),
        'Right': (1, 0),
    }

    def __init__(
        self,
        width=8,
        height=8,
        num_food=8,
        num_opponents=0,
        custom_walls=None,
        seed=7
    ):

        if seed is not None:
            random.seed(seed)

        self.width = width
        self.height = height

        # Agent's true position is kept by the environment.
        # It is NOT exposed through get_percept().
        self.agent_pos = [0, 0]

        self.facing = 'Right'

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            self.walls = {
                (2, 2),
                (2, 3),
                (5, 5),
                (6, 5),
                (3, 7)
            }

        self.food_positions = set()

        while len(self.food_positions) < num_food:

            pos = (
                random.randint(0, width - 1),
                random.randint(0, height - 1)
            )

            if (
                pos != (0, 0)
                and pos not in self.walls
            ):
                self.food_positions.add(pos)

        self.score = 0
        self.steps = 0
        self.collision = False

        self.opponents = []

    
    # PARTIAL OBSERVABILITY
    def _ahead_position(self):

        dx, dy = self.DIRECTIONS[self.facing]

        return (
            self.agent_pos[0] + dx,
            self.agent_pos[1] + dy
        )

    def get_percept(self):
        """
        Step 1.1 - Partial Observability.

        The agent receives only local information.

        The following information is NOT given to the agent:
        - agent_pos
        - score
        - remaining food
        - complete map
        """

        ahead = self._ahead_position()

        wall_ahead = (
            ahead[0] < 0
            or ahead[0] >= self.width
            or ahead[1] < 0
            or ahead[1] >= self.height
            or ahead in self.walls
        )

        food_here = ahead in self.food_positions

        return {
            'wall_ahead': wall_ahead,
            'food_here': food_here
        }

    
    # EXECUTE ACTION
    def execute_action(self, action):

        self.steps += 1

        direction_order = [
            'Up',
            'Right',
            'Down',
            'Left'
        ]

        
        # Move forward
        if action == 'FORWARD':

            direction = self.facing

        
        # Turn left and move
        elif action == 'LEFT':

            current_index = direction_order.index(
                self.facing
            )

            direction = direction_order[
                (current_index - 1) % 4
            ]

            self.facing = direction

        
        # Turn right and move
        elif action == 'RIGHT':

            current_index = direction_order.index(
                self.facing
            )

            direction = direction_order[
                (current_index + 1) % 4
            ]

            self.facing = direction

        
        # Direct directional action
        elif action in self.DIRECTIONS:

            direction = action
            self.facing = action

        else:

            direction = self.facing

        
        # Calculate new position
        dx, dy = self.DIRECTIONS[direction]

        new_pos = [
            max(
                0,
                min(
                    self.width - 1,
                    self.agent_pos[0] + dx
                )
            ),

            max(
                0,
                min(
                    self.height - 1,
                    self.agent_pos[1] + dy
                )
            )
        ]

        
        # Wall collision
        if tuple(new_pos) in self.walls:

            self.score -= 5

        else:

            self.agent_pos = new_pos

        
        # Collect food
        current_position = tuple(
            self.agent_pos
        )

        if current_position in self.food_positions:

            self.food_positions.remove(
                current_position
            )

            self.score += 20

    
    # TERMINATION
    def is_done(self):

        return (
            len(self.food_positions) == 0
            or self.steps >= 60
            or self.collision
        )

# GUI
class GridGameGUI:
    """
    Single-agent GUI for Practical 02.

    Workflow:

    1. Run Simple Reflex
    2. Observe its behaviour
    3. Press Reset
    4. Run Model-Based
    5. Observe its memory and changed behaviour
    """

    def __init__(
        self,
        root,
        width=8,
        height=8,
        num_food=8,
        seed=7
    ):

        self.root = root

        self.width = width
        self.height = height
        self.num_food = num_food
        self.seed = seed

        self.agent = None
        self.running = False

        
        # FIXED WINDOW SIZE
        self.root.title(
            'SE3062 Practical 02 - Partial Observability'
        )

        # Slightly taller window so all controls are visible.
        self.root.geometry('650x760')

        # Prevent the window from stretching/contracts.
        self.root.resizable(False, False)

        
        # TITLE
        self.title_label = tk.Label(
            root,
            text='Practical 02: Partial Observability',
            font=('Arial', 16, 'bold'),
            width=60,
            height=2
        )

        self.title_label.pack()

        
        # GRID
        # Smaller grid: 520 x 520
        self.canvas = tk.Canvas(
            root,
            width=520,
            height=520,
            bg='white',
            highlightthickness=1
        )

        self.canvas.pack(pady=5)

        
        # INFORMATION LABEL
        self.info_label = tk.Label(
            root,
            text=' ',
            font=('Arial', 10),
            width=85,
            height=4,
            anchor='center',
            justify='center',
            wraplength=620
        )

        self.info_label.pack(pady=5)

        
        # BUTTON FRAME
        

        button_frame = tk.Frame(root)

        button_frame.pack(pady=5)

        
        # Simple Reflex Button
        

        self.simple_button = tk.Button(
            button_frame,
            text='Run Simple Reflex',
            command=lambda: self.start_agent('simple'),
            font=('Arial', 10),
            width=18
        )

        self.simple_button.pack(
            side=tk.LEFT,
            padx=5
        )

        
        # Model-Based Button
        

        self.model_button = tk.Button(
            button_frame,
            text='Run Model-Based',
            command=lambda: self.start_agent('model'),
            font=('Arial', 10),
            width=18
        )

        self.model_button.pack(
            side=tk.LEFT,
            padx=5
        )

        
        # Reset Button
        

        self.reset_button = tk.Button(
            button_frame,
            text='Reset',
            command=self.reset,
            font=('Arial', 10),
            width=10
        )

        self.reset_button.pack(
            side=tk.LEFT,
            padx=5
        )

        # Initial environment
        self.reset()

    
    # RESET
    

    def reset(self):

        self.running = False
        self.agent = None

        # Re-create the exact same environment.
        self.env = VisualGridHuntGame(
            width=self.width,
            height=self.height,
            num_food=self.num_food,
            seed=self.seed
        )

        self.simple_button.config(
            state='normal'
        )

        self.model_button.config(
            state='normal'
        )

        self.title_label.config(
            text='Practical 02 '
        )

        self.draw_grid()

    
    # START AGENT
    

    def start_agent(self, agent_type):

        if self.running:
            return

        # Always start from the same environment.
        self.reset()

        if agent_type == 'simple':

            self.agent = SimpleReflexAgent()

            agent_name = 'Simple Reflex Agent'

        else:

            self.agent = ModelBasedAgent()

            agent_name = 'Model-Based Agent'

        self.running = True

        self.simple_button.config(
            state='disabled'
        )

        self.model_button.config(
            state='disabled'
        )

        self.reset_button.config(
            state='normal'
        )

        self.title_label.config(
            text=agent_name
        )

        self.step()

    
    # SIMULATION STEP
    

    def step(self):

        if not self.running:
            return

        
        # Continue simulation
        

        if not self.env.is_done():

            # Agent receives ONLY the local percept.
            percept = self.env.get_percept()

            # Agent chooses an action.
            action = self.agent.sense_and_act(
                percept
            )

            # Environment executes the action.
            self.env.execute_action(
                action
            )

            # Redraw grid.
            self.draw_grid()

            # ----------------------------------------------------
            # Memory information
            # ----------------------------------------------------

            if isinstance(
                self.agent,
                ModelBasedAgent
            ):

                memory_text = (
                    f'Visited: '
                    f'{len(self.agent.visited_cells)} | '
                    f'Repeated: '
                    f'{self.agent.repeated_percept_count}'
                )

            else:

                memory_text = 'None'

            # ----------------------------------------------------
            # Update information panel.
            #
            # IMPORTANT:
            # The text is kept short and wrapped so that it does
            # not resize the window.
            # ----------------------------------------------------

            self.info_label.config(
                text=(
                    f'Percept: '
                    f'wall_ahead={percept["wall_ahead"]} | '
                    f'food_here={percept["food_here"]}\n'

                    f'Action: {action} | '
                    f'Facing: {self.env.facing} | '
                    f'Score: {self.env.score}\n'

                    f'Steps: {self.env.steps} | '
                    f'Food left: {len(self.env.food_positions)} | '
                    f'Memory: {memory_text}'
                )
            )

            # Run next step after 250 milliseconds.
            self.root.after(
                250,
                self.step
            )

        
        # Simulation finished
        

        else:

            self.running = False

            if len(self.env.food_positions) == 0:

                result = 'All food collected!'

            elif self.env.collision:

                result = 'Collision occurred.'

            else:

                result = '60-step limit reached.'

            self.info_label.config(
                text=(
                    f'Finished: {result}\n'

                    f'Final Score: {self.env.score} | '
                    f'Steps: {self.env.steps}\n'

                    f'Food left: '
                    f'{len(self.env.food_positions)}'
                )
            )

            self.simple_button.config(
                state='normal'
            )

            self.model_button.config(
                state='normal'
            )

    
    # DRAW GRID
    

    def draw_grid(self):

        self.canvas.delete('all')

        # IMPORTANT:
        # Use 520 instead of 560 because the canvas is 520 x 520.
        cell = 520 // max(
            self.env.width,
            self.env.height
        )

        
        # Draw grid and walls
        for x in range(self.env.width):

            for y in range(self.env.height):

                x1 = x * cell

                y1 = (
                    self.env.height - 1 - y
                ) * cell

                x2 = x1 + cell
                y2 = y1 + cell

                if (x, y) in self.env.walls:

                    fill = '#64748b'

                else:

                    fill = '#f1f5f9'

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=fill,
                    outline='#cbd5e1'
                )

        
        # Draw food
        for fx, fy in self.env.food_positions:

            offset = cell * 0.25

            x1 = (
                fx * cell
                + offset
            )

            y1 = (
                (self.env.height - 1 - fy)
                * cell
                + offset
            )

            self.canvas.create_oval(
                x1,
                y1,
                x1 + cell * 0.5,
                y1 + cell * 0.5,
                fill='#f59e0b',
                outline='#d97706'
            )

        
        # Draw agent
        ax, ay = self.env.agent_pos

        offset = cell * 0.15

        x1 = (
            ax * cell
            + offset
        )

        y1 = (
            (self.env.height - 1 - ay)
            * cell
            + offset
        )

        self.canvas.create_oval(
            x1,
            y1,
            x1 + cell * 0.7,
            y1 + cell * 0.7,
            fill='#000066',
            outline='#1e3a8a'
        )



# MAIN
if __name__ == '__main__':

    root = tk.Tk()

    app = GridGameGUI(
        root,
        width=8,
        height=8,
        num_food=8,
        seed=7
    )

    root.mainloop()