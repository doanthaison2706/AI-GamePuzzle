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
        self.start_time = 0.0

    @abstractmethod
    def new_game(self):
        """Start a new game round."""
        ...

    @abstractmethod
    def process_move(self, *args, **kwargs) -> bool:
        """Process a player move."""
        ...

    @property
    @abstractmethod
    def players(self) -> list[PlayerSlot]:
        """Return a list of all current players."""
        ...

    def is_game_over(self) -> bool:
        """Check if the game has ended."""
        return not self.is_playing

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
