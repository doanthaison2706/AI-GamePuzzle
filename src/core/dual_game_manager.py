import time
from .game_manager import GameManager
from .player import PlayerSlot


class DualGameManager:
    """Manages a 2-player competitive game session.
    Wraps two GameManager instances with the same shuffle seed."""

    def __init__(self, size: int, p1: PlayerSlot, p2: PlayerSlot):
        self.size = size
        self.p1 = p1
        self.p2 = p2

        self.gm1 = GameManager(size)
        self.gm2 = GameManager(size)

        # Scoreboard — persists across rounds
        self.score = {p1.player_id: 0, p2.player_id: 0}
        self.winner: PlayerSlot | None = None

    def new_game(self):
        """Start a new round with identical boards for both players."""
        seed = GameManager.generate_seed()

        self.gm1.new_game_with_seed(seed)
        self.gm2.new_game_with_seed(seed)

        self.p1.reset_stats()
        self.p2.reset_stats()
        self.winner = None

    def process_move(self, player_id: int, r: int, c: int) -> bool:
        """Process a move for the given player. Returns True if valid move."""
        if self.winner is not None:
            return False

        gm, player = self._get_gm_and_player(player_id)
        result = gm.process_move(r, c)

        if result:
            player.move_count = gm.move_count
            self._update_player_stats(player, gm)

            if gm.board.is_solved():
                self.winner = player
                self.score[player.player_id] += 1
                self._stop_all()

        return result

    def update(self):
        """Update time and progress for both players (call each frame)."""
        if self.winner is not None:
            return

        for player, gm in [(self.p1, self.gm1), (self.p2, self.gm2)]:
            gm.update_time()
            self._update_player_stats(player, gm)

    def is_game_over(self) -> bool:
        return self.winner is not None

    def get_score_text(self) -> str:
        """Return formatted score, e.g. '2 - 1'."""
        return f"{self.score[self.p1.player_id]} - {self.score[self.p2.player_id]}"

    # --- Private helpers ---

    def _get_gm_and_player(self, player_id: int) -> tuple[GameManager, PlayerSlot]:
        if player_id == self.p1.player_id:
            return self.gm1, self.p1
        return self.gm2, self.p2

    def _update_player_stats(self, player: PlayerSlot, gm: GameManager):
        player.move_count = gm.move_count
        player.elapsed_time = gm.elapsed_time
        player.correct_count = gm.board.count_correct_tiles()

    def _stop_all(self):
        """Stop both games when a winner is determined."""
        self.gm1.is_playing = False
        self.gm2.is_playing = False
        self.gm1.update_time()
        self.gm2.update_time()
        self._update_player_stats(self.p1, self.gm1)
        self._update_player_stats(self.p2, self.gm2)
