from agent import SimpleReflexAgent, ModelBasedAgent
from grid_game import GridHuntGame


def run_agent(agent, name, seed=7):
    env = GridHuntGame(seed=seed)

    print(f"=== {name} ===")

    while not env.is_done():
        # Only the local percept is passed to the agent.
        percept = env.get_percept()
        action = agent.sense_and_act(percept)
        env.execute_action(action)

        print(
            f"Step {env.steps:02d}: "
            f"percept={percept} action={action:<7} "
            f"score={env.score} food_left={len(env.food_positions)}"
        )

    print(
        f"Final score: {env.score}; "
        f"steps: {env.steps}; "
        f"food left: {len(env.food_positions)}\n"
    )


def demonstrate_memory():
    """Demonstrate that repeated percepts can produce different actions."""
    agent = ModelBasedAgent()
    percept = {'wall_ahead': True, 'food_here': False}

    first = agent.sense_and_act(percept)
    second = agent.sense_and_act(percept)

    print("=== Model-Based Memory Demonstration ===")
    print(f"Same percept #1 -> {first}")
    print(f"Same percept #2 -> {second}")
    print(f"Different actions: {first != second}\n")


if __name__ == '__main__':
    run_agent(SimpleReflexAgent(), 'Simple Reflex Agent')
    run_agent(ModelBasedAgent(), 'Model-Based Agent')
    demonstrate_memory()
