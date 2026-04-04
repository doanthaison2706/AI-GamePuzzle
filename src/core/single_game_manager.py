import time
from .base_game_manager import BaseGameManager
from .board_factory import BoardFactory
from .player import PlayerSlot, PlayerType


class SingleGameManager(BaseGameManager):
    """Manages a single-player game session using a PlayerSlot."""

    def __init__(self, size: int = 3, player: PlayerSlot | None = None):
        super().__init__(size)
        self.player = player or PlayerSlot(player_id=1, player_type=PlayerType.HUMAN)
        self.board = BoardFactory.create(size)

    @property
    def players(self) -> list[PlayerSlot]:
        return [self.player]

    def new_game(self):
        self.board.shuffle()

        self.player.reset_stats()
        self.player.correct_count = self.board.count_correct_tiles()
        self.is_playing = True
        self.is_paused = False
        self.elapsed_time = 0.0

    def process_move(self, r: int, c: int) -> bool:
        if not self.is_playing or self.is_paused:
            return False

        if self.board.move_by_pos(r, c):
            self.player.move_count += 1
            self.player.correct_count = self.board.count_correct_tiles()

            if self.board.is_solved():
                self.update_time()
                self.is_playing = False

            return True

        return False

    def undo(self) -> bool:
        if getattr(self, 'winner', None) is not None or not self.is_playing or self.is_paused:
            return False

        if self.board.undo():
            self.player.move_count = max(0, self.player.move_count - 1)
            self.player.correct_count = self.board.count_correct_tiles()
            return True
        return False

    def get_winner(self) -> PlayerSlot | None:
        if self.board.is_solved():
            return self.player
        return None

    def start_game(self):
        if not self.is_playing and not self.board.is_solved():
            self.is_playing = True

    def reset_game(self):
        self.is_playing = False
        self.elapsed_time = 0.0
        self.player.reset_stats()

    def get_formatted_time(self) -> str:
        return self.format_time(self.player.elapsed_time)