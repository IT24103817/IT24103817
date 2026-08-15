# simulator.py
from grid_game import GridHuntGame
from agent import GreedyGridAgent

# this is the simulation part of the code, where we run the agent in the environment
def run_grid_hunt():
    env = GridHuntGame()
    agent = GreedyGridAgent()

    print("=== UC Berkeley Style Small Grid Hunt Started ===")
    while not env.is_done():
        percept = env.get_percept(agent)
        action = agent.sense_and_act(percept)
        env.execute_action(agent, action)
        print(f"Pos: {percept['agent_pos']} | Food Left: {percept['remaining_food']} | Score: {percept['score']}")

    print(f"\nGame Over! Final Score: {env.score} after {env.steps} steps.")

# main part of the code, calls the run_grid_hunt function
# this part is only executed when the script is run directly
if __name__ == "__main__":
    run_grid_hunt()