"""
puzzle_hint_solver.py
---------------------
Provides hints or Auto-Solve capabilities using either the Optimal A* Puzzle Solver
or a trained PPO Stable Baselines3 model.
"""
import os
import numpy as np
from stable_baselines3 import PPO
from game.ai.puzzle_solver import solve_puzzle_optimal

class PuzzleHintSolver:
    """Uses A* or Trained AI (PPO) to find the next best move."""

    def __init__(self, board_grid_2d):
        """
        board_grid_2d should be a list of lists of ints
        where -1 or 0 represents the empty cell.
        """
        self.size = len(board_grid_2d)
        self.board = [row[:] for row in board_grid_2d]
        
        # Load PPO Model
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        model_path = os.path.join(base_dir, "res", "data", f"ppo_puzzle_{self.size}x{self.size}.zip")
        self.model = None
        if os.path.exists(model_path):
            try:
                self.model = PPO.load(model_path)
                print(f"Loaded PPO model for {self.size}x{self.size} auto-solve.")
            except Exception as e:
                print(f"Failed to load PPO model: {e}")

    def get_optimal_path(self, timeout=30.0):
        """
        Returns the full list of minimal actions ["UP", "LEFT", ...] to solve the puzzle using A*.
        Returns None if timed out.
        """
        path = solve_puzzle_optimal(self.board, timeout=timeout)
        return path

    def get_ai_next_move(self):
        """
        Uses the trained PPO model to predict the single next best move.
        Returns one of: "UP", "DOWN", "LEFT", "RIGHT".
        """
        if not self.model:
            return None
            
        # Convert board to flat observation expected by PuzzleEnv
        # Note: in board.py, empty is -1. In PuzzleEnv, empty is 0.
        obs = []
        for r in range(self.size):
            for c in range(self.size):
                val = self.board[r][c]
                if val == -1:
                    val = 0
                else:
                    val += 1
                obs.append(val)
                
        obs_array = np.array(obs, dtype=np.int32)
        
        # Predict action (deterministic=True for greedy best path)
        action, _ = self.model.predict(obs_array, deterministic=True)
        
        # Map back to string
        if action == 0: return "UP"
        elif action == 1: return "DOWN"
        elif action == 2: return "LEFT"
        elif action == 3: return "RIGHT"
        
        return None
