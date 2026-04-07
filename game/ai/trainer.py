"""
Train an SB3 agent on the n-puzzle.
Run this script from the terminal to train longer sessions:
Example: python game/ai/trainer.py --size 4 --timesteps 1000000
"""

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from stable_baselines3 import PPO
from game.ai.puzzle_env import PuzzleEnv

def train_size(size: int, timesteps: int):
    # No render_mode to run silently in the background
    env = PuzzleEnv(size=size, render_mode=None)

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    model_path = os.path.join(base_dir, "res", "data", f"ppo_puzzle_{size}x{size}")
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    print(f"\n--- Training {size}x{size} Puzzle ---")
    try:
        model = PPO.load(model_path, env=env)
        print(f"Loaded existing PPO model for {size}x{size}.")
    except Exception:
        print(f"No existing model found for {size}x{size}, starting fresh with PPO.")
        model = PPO("MlpPolicy", env, verbose=1)

    print(f"Starting training for {timesteps} timesteps...")
    try:
        model.learn(total_timesteps=timesteps)
    except KeyboardInterrupt:
        print("\nTraining interrupted by user. Saving current progress...")

    model.save(model_path)
    print(f"Model for {size}x{size} saved to {model_path}!")

def main():
    parser = argparse.ArgumentParser(description="Train PPO RL Agent for N-Puzzle")
    parser.add_argument("--size", type=int, default=3, choices=[3, 4, 5], 
                        help="Board size to train (3, 4, or 5). Default is 3.")
    parser.add_argument("--timesteps", type=int, default=50000, 
                        help="Number of timesteps to train. Default is 50000. Use >1000000 for good 4x4 results.")
    parser.add_argument("--all", action="store_true", 
                        help="Train all sizes (3, 4, and 5) sequentially using the timesteps specified.")
    
    args = parser.parse_args()

    if args.all:
        print(f"Training ALL sizes (3x3, 4x4, 5x5) for {args.timesteps} timesteps each...")
        for s in [3, 4, 5]:
            train_size(s, args.timesteps)
    else:
        train_size(args.size, args.timesteps)
        
    print("\nTraining session completed. You can safely close this terminal.")

if __name__ == "__main__":
    main()
