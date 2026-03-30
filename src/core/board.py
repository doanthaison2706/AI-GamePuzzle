import random
import hashlib
from enum import Enum


class Direction(Enum):
    """Direction the empty cell moves, using screen convention (y-down).

    Values are (dx, dy) offsets:
      UP    ( 0,-1): empty cell moves up    → row decreases
      DOWN  ( 0, 1): empty cell moves down  → row increases
      LEFT  (-1, 0): empty cell moves left  → col decreases
      RIGHT ( 1, 0): empty cell moves right → col increases

    Conversion: new_row = row + dy, new_col = col + dx
    """

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def dx(self) -> int:
        return self.value[0]

    @property
    def dy(self) -> int:
        return self.value[1]

    @property
    def opposite(self) -> "Direction":
        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }
        return opposites[self]


class Board:
    """Manages the N-Puzzle board matrix logic."""

    def __init__(self, size: int):
        self.size = size
        self.total_tiles = size * size - 1
        self.num_shuffles = 100
        self.solved_board = self._generate_solved_board()
        self.matrix = [row[:] for row in self.solved_board]
        self._empty_pos = (size - 1, size - 1)

    def _generate_solved_board(self) -> list[list[int]]:
        board = []
        count = 1

        for i in range(self.size):
            row = []
            for j in range(self.size):
                if i == self.size - 1 and j == self.size - 1:
                    row.append(0)
                else:
                    row.append(count)
                    count += 1
            board.append(row)
        return board

    def get_empty_pos(self) -> tuple[int, int]:
        return self._empty_pos

    def _apply_direction(self, r: int, c: int, d: Direction) -> tuple[int, int]:
        """Apply Direction (dx, dy) to matrix position (row, col)."""
        return r + d.dy, c + d.dx

    def get_valid_moves(self) -> list[Direction]:
        """Return directions the empty cell can move."""
        r, c = self._empty_pos
        moves = []
        for d in Direction:
            nr, nc = self._apply_direction(r, c, d)
            if 0 <= nr < self.size and 0 <= nc < self.size:
                moves.append(d)
        return moves

    def move_by_pos(self, r: int, c: int) -> bool:
        """Move to (r, c) if it's adjacent to the empty cell."""
        if not (0 <= r < self.size and 0 <= c < self.size):
            return False

        er, ec = self._empty_pos
        # Check if (r, c) is adjacent to the empty cell (Manhattan distance = 1)
        if abs(r - er) + abs(c - ec) == 1:
            self.matrix[er][ec], self.matrix[r][c] = self.matrix[r][c], self.matrix[er][ec]
            self._empty_pos = (r, c)
            return True
        return False

    def move(self, direction: Direction) -> bool:
        """Move the empty cell in the given direction.
        Returns True if valid, False otherwise."""
        er, ec = self._empty_pos
        nr, nc = self._apply_direction(er, ec, direction)

        if not (0 <= nr < self.size and 0 <= nc < self.size):
            return False

        self.matrix[er][ec], self.matrix[nr][nc] = self.matrix[nr][nc], self.matrix[er][ec]
        self._empty_pos = (nr, nc)
        return True

    def shuffle(self, seed: int | str | None = None):
        """Scramble by moving the empty cell randomly from the solved state.
        Seed can be an int (64-bit recommended) or a string (auto-converted)."""
        if seed == "":
            seed = None
        elif isinstance(seed, str):
            seed = self._seed_from_string(seed)

        self.matrix = [row[:] for row in self.solved_board]
        self._empty_pos = (self.size - 1, self.size - 1)
        rng = random.Random(seed)

        prev_direction = None
        for _ in range(self.num_shuffles):
            moves = self.get_valid_moves()
            if prev_direction:
                opposite = prev_direction.opposite
                if opposite in moves:
                    moves.remove(opposite)

            chosen = rng.choice(moves)
            self.move(chosen)
            prev_direction = chosen

    def _seed_from_string(text: str) -> int:
        """Convert a string to a signed 64-bit integer seed."""
        digest = hashlib.sha256(text.encode()).digest()
        return int.from_bytes(digest[:8], byteorder="big", signed=True)

    def is_solved(self) -> bool:
        """Check if the board matches the goal state."""
        return self.matrix == self.solved_board

    def count_correct_tiles(self) -> int:
        """Return number of tiles in correct position.
        Empty cell (0) is excluded from the count."""
        return sum(
            1 for r in range(self.size) for c in range(self.size)
            if self.matrix[r][c] != 0 and self.matrix[r][c] == self.solved_board[r][c]
        )

    def print_board(self):
        """Print board to terminal for debugging."""
        for row in self.matrix:
            print("\t".join(str(x) if x != 0 else " " for x in row))

        print("-" * 20)