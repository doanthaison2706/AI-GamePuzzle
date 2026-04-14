import time
from .base_game_manager import BaseGameManager
from .board_factory import BoardFactory
from .player import PlayerSlot


class DualGameManager(BaseGameManager):
    """Manages a 2-player competitive game session.
    Uses two Board instances with the same shuffle seed."""

    # FIX 1: Nhận thêm biến score_limit (mặc định là 3)
    def __init__(self, size: int, p1: PlayerSlot, p2: PlayerSlot, score_limit: int = 3, time_limit: int = 0):
        super().__init__(size, time_limit)
        self.p1 = p1
        self.p2 = p2
        self.score_limit = score_limit

        self.board1 = BoardFactory.create(size)
        self.board2 = BoardFactory.create(size)

        # Scoreboard — giữ nguyên tỉ số qua các ván đấu
        self.score = {p1.player_id: 0, p2.player_id: 0}

        # Tách biệt: Thắng 1 ván vs Thắng cả trận
        self.round_winner: PlayerSlot | None = None
        self.match_winner: PlayerSlot | None = None

    @property
    def players(self) -> list[PlayerSlot]:
        return [self.p1, self.p2]

    def new_game(self):
        """Bắt đầu VÁN MỚI (Next Round). Tỉ số vẫn được giữ nguyên."""
        seed = self.generate_seed()

        self.board1.shuffle(seed=seed)
        self.board2.shuffle(seed=seed)

        self.p1.reset_stats()
        self.p2.reset_stats()
        self.p1.correct_count = self.board1.count_correct_tiles()
        self.p2.correct_count = self.board2.count_correct_tiles()

        self.is_playing = True
        self.is_paused = False
        self.elapsed_time = 0.0

        # Chỉ reset trạng thái của ván đấu
        self.round_winner = None

    def reset_match(self):
        """Nếu muốn làm lại toàn bộ trận đấu (Tỉ số về 0-0)"""
        self.score = {self.p1.player_id: 0, self.p2.player_id: 0}
        self.match_winner = None
        self.new_game()

    def process_move(self, player_id: int, r: int, c: int) -> bool:
        """Xử lý nước đi."""
        # Chặn đánh nếu ván hoặc trận đã kết thúc
        if not self.is_playing or self.round_winner is not None or self.is_paused:
            return False

        board, player = self._get_board_and_player(player_id)

        if board.move_by_pos(r, c):
            player.move_count += 1
            player.correct_count = board.count_correct_tiles()

            # Nếu 1 người giải xong bàn cờ
            if board.is_solved():
                self.round_winner = player
                self.score[player.player_id] += 1

                # FIX 2: Kiểm tra xem đã đạt mốc BO3/BO5 chưa
                if self.score[player.player_id] >= self.score_limit:
                    self.match_winner = player

                self._stop_all()

            return True

        return False

    def undo(self, player_id: int) -> bool:
        """Undo move."""
        if not self.is_playing or self.round_winner is not None or self.is_paused:
            return False

        board, player = self._get_board_and_player(player_id)

        if board.undo():
            player.move_count = max(0, player.move_count - 1)
            player.correct_count = board.count_correct_tiles()
            player.undo_count += 1
            return True
        return False

    def get_winner(self) -> PlayerSlot | None:
        """LƯU Ý: Giờ hàm này chỉ trả về kết quả khi CẢ TRẬN đã kết thúc"""
        return self.match_winner

    def is_round_over(self) -> bool:
        return self.round_winner is not None

    def update_time(self, dt: float = 0.0):
        super().update_time(dt)
        if self.time_limit > 0 and self.remaining_time <= 0 and self.round_winner is None:
            self._determine_round_winner_on_timeout()

    def _determine_round_winner_on_timeout(self):
        c1 = self.p1.correct_count
        c2 = self.p2.correct_count
        m1 = self.p1.move_count
        m2 = self.p2.move_count

        if c1 > c2:
            winner = self.p1
        elif c2 > c1:
            winner = self.p2
        else:
            if m1 < m2:
                winner = self.p1
            elif m2 < m1:
                winner = self.p2
            else:
                winner = None # Tie

        self.round_winner = winner
        if winner:
            self.score[winner.player_id] += 1
            if self.score[winner.player_id] >= self.score_limit:
                self.match_winner = winner
        else:
            self.round_winner = "TIE" # Mark as tie but obviously not a player slot

        self._stop_all()

    def is_game_over(self) -> bool:
        return self.match_winner is not None

    def get_score_text(self) -> str:
        """Return formatted score, e.g. '2 - 1'."""
        return f"{self.score[self.p1.player_id]} - {self.score[self.p2.player_id]}"

    # --- Private helpers ---

    def _get_board_and_player(self, player_id: int):
        if player_id == self.p1.player_id:
            return self.board1, self.p1
        return self.board2, self.p2

    def _stop_all(self):
        """Stop game when a round winner is determined."""
        self.update_time()
        self.is_playing = False