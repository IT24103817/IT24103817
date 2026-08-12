import random
from collections import deque
import heapq


class GreedyGridAgent:

    def __init__(self):
        self.actions_pool = [
            "Up",
            "Down",
            "Left",
            "Right"
        ]

    def sense_and_act(self, percept: dict) -> str:
        return random.choice(self.actions_pool)


class SearchAgent:

    def __init__(self):
        self.plan = []
        self.active_algo = "BFS"

    def bfs_search(
        self,
        start,
        goal,
        grid_size,
        walls
    ):

        width, height = grid_size

        directions = {
            "Up": (0, 1),
            "Down": (0, -1),
            "Left": (-1, 0),
            "Right": (1, 0)
        }

        frontier = deque()
        frontier.append((start, []))

        reached = {start}

        while frontier:

            current_state, path = frontier.popleft()

            if current_state == goal:
                return path

            x, y = current_state

            for action, (dx, dy) in directions.items():

                next_state = (
                    x + dx,
                    y + dy
                )

                next_x, next_y = next_state

                inside_grid = (
                    0 <= next_x < width
                    and
                    0 <= next_y < height
                )

                if (
                    inside_grid
                    and next_state not in walls
                    and next_state not in reached
                ):

                    reached.add(next_state)

                    new_path = path + [action]

                    frontier.append(
                        (
                            next_state,
                            new_path
                        )
                    )

        return []

    def dfs_search(
        self,
        start,
        goal,
        grid_size,
        walls
    ):

        width, height = grid_size

        directions = {
            "Up": (0, 1),
            "Down": (0, -1),
            "Left": (-1, 0),
            "Right": (1, 0)
        }

        frontier = []
        frontier.append((start, []))

        reached = {start}

        while frontier:

            current_state, path = frontier.pop()

            if current_state == goal:
                return path

            x, y = current_state

            for action, (dx, dy) in directions.items():

                next_state = (
                    x + dx,
                    y + dy
                )

                next_x, next_y = next_state

                inside_grid = (
                    0 <= next_x < width
                    and
                    0 <= next_y < height
                )

                if (
                    inside_grid
                    and next_state not in walls
                    and next_state not in reached
                ):

                    reached.add(next_state)

                    new_path = path + [action]

                    frontier.append(
                        (
                            next_state,
                            new_path
                        )
                    )

        return []

    def ucs_search(
        self,
        start,
        goal,
        grid_size,
        walls
    ):

        width, height = grid_size

        directions = {
            "Up": (0, 1),
            "Down": (0, -1),
            "Left": (-1, 0),
            "Right": (1, 0)
        }

        frontier = []

        heapq.heappush(
            frontier,
            (
                0,
                start,
                []
            )
        )

        reached = set()

        while frontier:

            cost, current_state, path = heapq.heappop(
                frontier
            )

            if current_state in reached:
                continue

            reached.add(current_state)

            if current_state == goal:
                return path

            x, y = current_state

            for action, (dx, dy) in directions.items():

                next_state = (
                    x + dx,
                    y + dy
                )

                next_x, next_y = next_state

                inside_grid = (
                    0 <= next_x < width
                    and
                    0 <= next_y < height
                )

                if (
                    inside_grid
                    and next_state not in walls
                    and next_state not in reached
                ):

                    new_cost = cost + 1

                    new_path = path + [action]

                    heapq.heappush(
                        frontier,
                        (
                            new_cost,
                            next_state,
                            new_path
                        )
                    )

        return []

    def sense_and_act(
        self,
        percept
    ):

        if percept["food_here"]:

            self.plan = []

            return "suck"

        if not self.plan:

            start = percept[
                "agent_pos"
            ]

            foods = percept[
                "all_food"
            ]

            if not foods:
                return None

            goal = min(
                foods,
                key=lambda food:
                    abs(
                        food[0]
                        - start[0]
                    )
                    +
                    abs(
                        food[1]
                        - start[1]
                    )
            )

            grid_size = percept[
                "grid_size"
            ]

            walls = set(
                percept["walls"]
            )

            if self.active_algo == "BFS":

                self.plan = self.bfs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            elif self.active_algo == "DFS":

                self.plan = self.dfs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            elif self.active_algo == "UCS":

                self.plan = self.ucs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            else:

                raise ValueError(
                    "Unknown search algorithm: "
                    + self.active_algo
                )

            print(
                "Algorithm:",
                self.active_algo,
                "| Start:",
                start,
                "| Goal:",
                goal,
                "| Plan:",
                self.plan
            )

        if self.plan:

            return self.plan.pop(0)

        return None