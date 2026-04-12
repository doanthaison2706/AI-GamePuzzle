"""Evaluate an SB3 agent on the n-puzzle."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from stable_baselines3 import PPO
from game.ai.puzzle_env import PuzzleEnv


def evaluate(model, env, episodes: int):
    solved = 0
    total_steps = 0

    for episode in range(episodes):
        obs, _ = env.reset()
        steps = 0
        done = False

        while not done and steps <= 500:
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            steps += 1

        if env.is_solved():
            solved += 1
        total_steps += steps

    print("Evaluation complete.")
    print(f"Solved {solved} out of {episodes} episodes.")
    print(f"Average steps per episode: {total_steps / episodes:.2f}")


def main():
    env = PuzzleEnv(size=3, render_mode="human")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    model_path = os.path.join(base_dir, "res", "data", "ppo_puzzle")

    try:
        model = PPO.load(model_path, env=env)
        print("Loaded PPO model for evaluation.")
    except Exception as e:
        print(f"Could not load PPO model at {model_path}. Error: {e}")
        return

    evaluate(model, env, 10)


if __name__ == "__main__":
    main()
