# grid_game.py
import random


class GridHuntGame:
    """Small Pacman style grid environment."""

    def __init__(self, width=4, height=4):

        self.width = width
        self.height = height


        self.agent_pos = [
            0,
            0
        ]


        # FIXED - tuples instead of lists

        self.food_positions = {

            (1,2),
            (2,3),
            (3,0),
            (2,1)

        }


        self.walls = {

            (1,1),
            (2,2)

        }


        self.score = 0

        self.steps = 0




    def get_percept(self, agent):

        return {


            'agent_pos':
                list(self.agent_pos),


            'smells_food':
                tuple(self.agent_pos)
                in self.food_positions,


            'hit_wall':
                tuple(self.agent_pos)
                in self.walls,


            'score':
                self.score,


            'remaining_food':
                len(self.food_positions)

        }





    def execute_action(self, agent, action):


        self.steps += 1


        new_pos = list(self.agent_pos)



        if action == "Up":

            new_pos[1] += 1


        elif action == "Down":

            new_pos[1] -= 1


        elif action == "Left":

            new_pos[0] -= 1


        elif action == "Right":

            new_pos[0] += 1




        if (

            0 <= new_pos[0] < self.width

            and

            0 <= new_pos[1] < self.height

        ):


            if tuple(new_pos) in self.walls:

                self.score -= 5


            else:

                self.agent_pos = new_pos




        position = tuple(self.agent_pos)



        if position in self.food_positions:


            self.food_positions.remove(position)

            self.score += 20





    def is_done(self):

        return (

            len(self.food_positions)==0

            or

            self.steps >= 20

        )