import time
from .base_game_manager import BaseGameManager
from .board_factory import BoardFactory
from .player import PlayerSlot


class DualGameManager(BaseGameManager):
    """Manages a 2-player competitive game session.
    Uses two Board instances with the same shuffle seed."""

    @property
    def players(self) -> list[PlayerSlot]:
        return [self.p1, self.p2]

    def __init__(self, size: int, p1: PlayerSlot, p2: PlayerSlot):
        super().__init__(size)
        self.p1 = p1
        self.p2 = p2

        self.board1 = BoardFactory.create(size)
        self.board2 = BoardFactory.create(size)

        # Scoreboard — persists across rounds
        self.score = {p1.player_id: 0, p2.player_id: 0}
        self.winner: PlayerSlot | None = None

    def new_game(self):
        """Start a new round with identical boards for both players."""
        seed = self.generate_seed()

        self.board1 = BoardFactory.create(self.size)
        self.board2 = BoardFactory.create(self.size)
        self.board1.shuffle(seed=seed)
        self.board2.shuffle(seed=seed)

        self.p1.reset_stats()
        self.p2.reset_stats()
        self.is_playing = True
        self.is_paused = False
        self.start_time = time.time()
        self.winner = None

    def get_winner(self) -> PlayerSlot | None:
        return self.winner

    def process_move(self, player_id: int, r: int, c: int) -> bool:
        """Process a move for the given player. Returns True if valid move."""
        if not self.is_playing or self.winner is not None or self.is_paused:
            return False

        board, player = self._get_board_and_player(player_id)

        if board.move_by_pos(r, c):
            player.move_count += 1
            player.correct_count = board.count_correct_tiles()

            if board.is_solved():
                self.winner = player
                self.score[player.player_id] += 1
                self._stop_all()

            return True

        return False

    def update(self):
        """Update time and progress for both players (call each frame)."""
        if not self.is_playing or self.is_paused:
            return

        elapsed = time.time() - self.start_time
        for player, board in [(self.p1, self.board1), (self.p2, self.board2)]:
            player.elapsed_time = elapsed
            player.correct_count = board.count_correct_tiles()

    def is_game_over(self) -> bool:
        return self.winner is not None

    def get_score_text(self) -> str:
        """Return formatted score, e.g. '2 - 1'."""
        return f"{self.score[self.p1.player_id]} - {self.score[self.p2.player_id]}"

    # --- Private helpers ---

    def _get_board_and_player(self, player_id: int):
        if player_id == self.p1.player_id:
            return self.board1, self.p1
        return self.board2, self.p2

    def _stop_all(self):
        """Stop game when a winner is determined."""
        self.is_playing = False
        elapsed = time.time() - self.start_time
        self.p1.elapsed_time = elapsed
        self.p2.elapsed_time = elapsed
        self.p1.correct_count = self.board1.count_correct_tiles()
        self.p2.correct_count = self.board2.count_correct_tiles()
