# Functional Changes Summary

This practical implementation was updated to match the worksheet requirements for agent-environment architecture, percept-based sensing, memory, and search.

## Updated functionalities

### 1. Agent hierarchy added in `agent.py`
- Added `SimpleReflexAgent` for immediate condition-action behavior.
- Added `ModelBasedAgent` with short-term memory to avoid repeating the same failed action under the same percept.
- Added `SearchAgent` with a breadth-first search (`bfs_search`) routine to find shortest valid paths in a static maze.
- Preserved `GreedyGridAgent` as a simple simulator-friendly controller.

### 2. Environment sensing and hazard support updated in `grid_game.py`
- Added a new hazard set called `toxic_traps`.
- Extended `get_percept()` with:
  - `smells_toxin`
  - `food_here`
  - `wall_ahead`
- Updated `execute_action()` so that:
  - hitting a wall still applies a penalty,
  - collecting food gives a reward,
  - stepping on a trap subtracts points.
- This directly maps the practical worksheet's environment-state and PEAS discussions into executable code.

### 3. Visual environment upgraded in `visual_grid_game.py`
- Added trap generation that avoids walls, food, and the start cell.
- Added trap sensor data in `get_percept()`.
- Added trap penalty logic to `execute_action()`.
- Added purple triangular trap rendering inside the grid canvas to visually represent hazards.

## Run commands

### 1. Run the autograder tests
```powershell
cd "C:\Users\Dell\Desktop\SLIIT_3rd_Year_1 SEM\Intelligent_Agents\Lab_01\IT3012---Practical-Base"
python -m unittest -v
```

### 2. Run the text simulator
```powershell
cd "C:\Users\Dell\Desktop\SLIIT_3rd_Year_1 SEM\Intelligent_Agents\Lab_01\IT3012---Practical-Base"
python simulator.py
```

### 3. Launch the visual grid window
```powershell
cd "C:\Users\Dell\Desktop\SLIIT_3rd_Year_1 SEM\Intelligent_Agents\Lab_01\IT3012---Practical-Base"
python visual_grid_game.py
```

## Verification evidence

The updated code was verified with:
```powershell
python -m unittest -v
```

Observed result:
- `Ran 4 tests in 0.001s`
- `OK`
