import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random
import pygame


class PuzzleEnv(gym.Env):
    """N-puzzle environment compatible with Gymnasium and Stable Baselines3."""
    
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}

    def __init__(self, size: int = 3, render_mode=None):
        super().__init__()
        self.size = size
        self.render_mode = render_mode
        self.window = None
        self.clock = None
        self.cell_size = 100
        
        # Actions: 0: UP, 1: DOWN, 2: LEFT, 3: RIGHT
        self.action_space = spaces.Discrete(4)
        
        # Observation space: 1D array of length size*size containing integers 0 to size*size-1
        self.observation_space = spaces.Box(
            low=0, 
            high=size*size - 1, 
            shape=(size * size,), 
            dtype=np.int32
        )
        
        self.board = np.zeros((size, size), dtype=np.int32)
        
    def _get_obs(self):
        return self.board.flatten()
        
    def _get_info(self):
        return {"is_solved": self.is_solved()}

    def is_solved(self) -> bool:
        count = 1
        for i in range(self.size):
            for j in range(self.size):
                if i == self.size - 1 and j == self.size - 1:
                    if self.board[i][j] != 0:
                        return False
                else:
                    if self.board[i][j] != count:
                        return False
                    count += 1
        return True

    def step(self, action):
        """Execute action on the internal board.
        Actions: 0: UP, 1: DOWN, 2: LEFT, 3: RIGHT
        (UP means moving the empty space UP, which visually might slide a tile down)
        """
        x, y = self._find_empty()
        
        # Map action to dy, dx for the empty tile
        if action == 0:   # UP
            dx, dy = -1, 0
        elif action == 1: # DOWN
            dx, dy = 1, 0
        elif action == 2: # LEFT
            dx, dy = 0, -1
        elif action == 3: # RIGHT
            dx, dy = 0, 1
        else:
            dx, dy = 0, 0
            
        nx, ny = x + dx, y + dy
        moved = False
        
        if 0 <= nx < self.size and 0 <= ny < self.size:
            self.board[x][y], self.board[nx][ny] = self.board[nx][ny], self.board[x][y]
            moved = True
            
        solved = self.is_solved()
        
        # Reward design
        if solved:
            reward = 100.0
            terminated = True
        elif not moved:
            reward = -5.0
            terminated = False
        else:
            reward = -1.0
            terminated = False

        if self.render_mode == "human":
            self._render_frame()

        return self._get_obs(), reward, terminated, False, self._get_info()

    def _find_empty(self):
        result = np.where(self.board == 0)
        if len(result[0]) > 0:
            return int(result[0][0]), int(result[1][0])
        return -1, -1

    def reset(self, seed=None, options=None):
        """Randomize the board."""
        super().reset(seed=seed)
        
        nums = list(range(self.size * self.size))
        random.shuffle(nums)
        
        # While it's unsolvable or already solved, shuffle again
        # Simplified for now: just place randomly
        k = 0
        for i in range(self.size):
            for j in range(self.size):
                self.board[i][j] = nums[k]
                k += 1
                
        if self.render_mode == "human":
            self._render_frame()
            
        return self._get_obs(), self._get_info()

    def render(self):
        if self.render_mode in ["rgb_array", "human"]:
            return self._render_frame()

    def _render_frame(self):
        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode(
                (self.size * self.cell_size, self.size * self.cell_size)
            )
            pygame.display.set_caption("RL Agent View")
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        if self.render_mode == "human":
            canvas = pygame.Surface((self.size * self.cell_size, self.size * self.cell_size))
            canvas.fill((255, 255, 255))
            font = pygame.font.SysFont("Georgia", 40)
            
            for i in range(self.size):
                for j in range(self.size):
                    val = self.board[i][j]
                    rect = pygame.Rect(
                        j * self.cell_size,
                        i * self.cell_size,
                        self.cell_size,
                        self.cell_size
                    )
                    if val != 0:
                        pygame.draw.rect(canvas, (200, 200, 200), rect)
                        pygame.draw.rect(canvas, (0, 0, 0), rect, width=2)
                        text = font.render(str(val), True, (0, 0, 0))
                        text_rect = text.get_rect(center=rect.center)
                        canvas.blit(text, text_rect)
                    else:
                        pygame.draw.rect(canvas, (50, 50, 50), rect)
                        
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()
            self.clock.tick(self.metadata["render_fps"])
        else:
            return np.zeros((self.size * self.cell_size, self.size * self.cell_size, 3), dtype=np.uint8)

    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
