# simulator.py
from grid_game import GridHuntGame
from agent import GreedyGridAgent



def run_grid_hunt():


    env = GridHuntGame()

    agent = GreedyGridAgent()



    print(
        "=== UC Berkeley Style Small Grid Hunt Started ==="
    )



    while not env.is_done():


        percept = env.get_percept(agent)


        action = agent.sense_and_act(percept)


        env.execute_action(agent, action)



        print(

            f"Pos: {percept['agent_pos']} | "
            f"Food Left: {percept['remaining_food']} | "
            f"Score: {percept['score']}"

        )



    print(

        f"\nGame Over! Final Score: "
        f"{env.score} after {env.steps} steps."

    )



if __name__=="__main__":

    run_grid_hunt()