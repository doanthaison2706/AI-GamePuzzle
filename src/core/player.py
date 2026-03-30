from enum import Enum


class PlayerType(Enum):
    HUMAN = "human"
    BOT = "bot"


class PlayerSlot:
    """One player's identity and per-round competitive stats."""

    def __init__(self, player_id: int, player_type: PlayerType):
        self.player_id = player_id
        self.player_type = player_type
        self.reset_stats()

    def reset_stats(self):
        """Reset per-round stats (call at the start of each round)."""
        self.move_count = 0
        self.elapsed_time = 0.0
        self.correct_count = 0  # Number of tiles in correct position
