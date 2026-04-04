import time
import random
from abc import ABC, abstractmethod
from .board_factory import BoardFactory
from .player import PlayerSlot


class BaseGameManager(ABC):
    """Base class for all game managers.
    Holds shared attributes and common utility methods."""

    def __init__(self, size: int):
        self.size = size
        self.is_playing = False
        self.is_paused = False
        self.elapsed_time = 0.0

    @property
    @abstractmethod
    def players(self) -> list[PlayerSlot]:
        """Return a list of all current players."""
        ...

    @abstractmethod
    def new_game(self):
        """Start a new game round."""
        ...

    @abstractmethod
    def process_move(self, *args, **kwargs) -> bool:
        """Process a player move."""
        ...

    @abstractmethod
    def get_winner(self) -> PlayerSlot | None:
        """Returns the winning PlayerSlot if the game is over, otherwise None."""
        ...

    @abstractmethod
    def undo(self, *args, **kwargs) -> bool:
        """Undo the last move."""
        ...

    def pause(self):
        """Pause the game timer and block moves."""
        if self.is_playing and not self.is_paused:
            self.is_paused = True

    def resume(self):
        """Resume the game timer and allow moves."""
        if self.is_paused:
            self.is_paused = False

    def is_game_over(self) -> bool:
        """Check if the game has ended."""
        return not self.is_playing

    def update_time(self, dt: float = 0.0):
        """Update game time and sync player stats (call each frame)."""
        if self.is_playing and not self.is_paused:
            self.elapsed_time += dt
            for player in self.players:
                player.elapsed_time = self.elapsed_time

    @staticmethod
    def generate_seed() -> int:
        """Generate a random seed for synchronized shuffling."""
        return random.randint(0, 2**63 - 1)

    @staticmethod
    def format_time(elapsed: float) -> str:
        """Format elapsed seconds to MM:SS string."""
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        return f"{minutes:02d}:{seconds:02d}"
