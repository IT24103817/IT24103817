# simulator.py
from grid_game import GridHuntGame
from agent import SimpleReflexAgent


def run_grid_hunt():
    env = GridHuntGame()
    agent = SimpleReflexAgent()

    print("=== UC Berkeley Style Small Grid Hunt Started ===")
    while not env.is_done():
        percept = env.get_percept(agent)
        action = agent.sense_and_act(percept)
        env.execute_action(agent, action)
        print(f"Pos: {tuple(env.agent_pos)} | Action: {action} | Score: {env.score}")

    print(f"\nGame Over! Final Score: {env.score} after {env.steps} steps.")

if __name__ == "__main__":
    run_grid_hunt()