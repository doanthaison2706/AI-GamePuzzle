import time
from .board_factory import BoardFactory

class GameManager:

    def __init__(self, size: int = 3):
        self.size = size
        self.board = BoardFactory.create(size)

        self.is_playing = False
        self.move_count = 0

        self.start_time = 0.0
        self.elapsed_time = 0.0

    def start_game(self):
        if not self.is_playing and not self.board.is_solved():
            self.is_playing = True
            self.start_time = time.time() - self.elapsed_time

    def reset_game(self):
        self.board = BoardFactory.create(self.size)
        self.is_playing = False
        self.move_count = 0
        self.start_time = 0.0
        self.elapsed_time = 0.0

    def new_game(self):
        self.board = BoardFactory.create(self.size)
        self.board.shuffle()

        self.is_playing = True
        self.move_count = 0
        self.start_time = time.time()
        self.elapsed_time = 0.0

    def process_move(self, r: int, c: int) -> bool:
        if not self.is_playing:
            return False
        if self.board.move(r, c):
            self.move_count += 1

            if self.board.is_solved():
                self.is_playing = False
                self.update_time()
            return True

        return False

    def get_formatted_time(self) -> str:
        self.update_time()
        minutes = int(self.elapsed_time // 60)
        seconds = int(self.elapsed_time % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def update_time(self):
        if self.is_playing:
            self.elapsed_time = time.time() - self.start_time