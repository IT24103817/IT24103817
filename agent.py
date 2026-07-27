import random
from collections import deque


class GreedyGridAgent:
    """A simple agent that moves randomly around the grid."""

    def __init__(self):
        self.actions_pool = [
            'Up',
            'Down',
            'Left',
            'Right'
        ]

    def sense_and_act(self, percept: dict) -> str:

        return random.choice(self.actions_pool)



class SimpleReflexAgent:
    """Condition-action based agent."""

    def __init__(self):

        self.actions = [
            "Up",
            "Down",
            "Left",
            "Right"
        ]


    def sense_and_act(self, percept):

        if percept.get("food_here", False):
            return "Up"

        if percept.get("wall_ahead", False):
            return "Right"

        return "Up"



class ModelBasedAgent:
    """Agent with memory."""

    def __init__(self):

        self.previous_action = None

        self.actions = [
            "Up",
            "Down",
            "Left",
            "Right"
        ]


    def sense_and_act(self, percept):

        if percept.get("wall_ahead"):

            choices = [
                a for a in self.actions
                if a != self.previous_action
            ]

            action = random.choice(choices)

        else:

            action = random.choice(self.actions)


        self.previous_action = action

        return action




class SearchAgent:
    """BFS problem solving agent."""

    def bfs_search(self, start, goal, walls, grid_size):

        queue = deque()

        queue.append(
            (
                start,
                []
            )
        )


        visited = set()

        visited.add(start)


        width, height = grid_size


        moves = [

            ((0,1),"Up"),
            ((0,-1),"Down"),
            ((1,0),"Right"),
            ((-1,0),"Left")

        ]


        while queue:


            current, path = queue.popleft()


            if current == goal:

                return path



            for move, action in moves:


                nx = current[0] + move[0]
                ny = current[1] + move[1]


                next_pos = (nx, ny)


                if (

                    0 <= nx < width

                    and

                    0 <= ny < height

                    and

                    next_pos not in walls

                    and

                    next_pos not in visited

                ):

                    visited.add(next_pos)


                    queue.append(

                        (
                            next_pos,
                            path + [action]
                        )

                    )


        return None