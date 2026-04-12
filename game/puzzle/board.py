"""
board.py
--------
Sliding-puzzle board: grid state, shuffle, win-check, and drag-and-drop
rendering with pygame.

Scramble algorithm
------------------
We use a two-phase approach to guarantee a solvable state every time:

  Phase 1 – Parity-correct random permutation
    Generate a random permutation of tile indices 0 … n²-2 (plus the
    empty sentinel -1).  Check solvability via the inversion-count theorem:

    * For odd-width boards (n odd):
        A configuration is solvable iff the number of inversions in the
        tile sequence (reading left-to-right, top-to-bottom, ignoring the
        empty cell) is even.

    * For even-width boards (n even):
        A configuration is solvable iff
        (inversions + row-of-empty-from-bottom) is even.

    If the generated permutation is unsolvable we swap the last two
    non-empty tiles — this flips parity by exactly 1 inversion, making
    the puzzle solvable without any further randomisation.

  Phase 2 – Random-walk refinement
    After placing the parity-correct state we additionally perform a
    random walk of `_WALK_STEPS` valid moves.  This eliminates any
    residual visual patterns that might hint at the solution.

Drag mechanics
--------------
* Mouse-down on a tile that is adjacent to the empty slot starts a drag.
* The tile follows the cursor but is clamped to move *only toward* the
  empty slot and no further than one tile_size away.
* Mouse-up commits the move if the tile has been pulled past the midpoint;
  otherwise the tile snaps back.
"""

import random
import pygame
from game.constants import EMPTY_CELL, TILE_BORDER, PANEL_BG


class Board:
    EMPTY = -1          # sentinel value for the empty slot
    _WALK_STEPS = 300   # random-walk refinement steps after parity fix

    # ------------------------------------------------------------------ #
    #  Construction                                                        #
    # ------------------------------------------------------------------ #

    def __init__(
        self,
        tiles: list,        # flat list of n*n-1 pygame.Surface objects
        n: int,             # grid size (3, 4, or 5)
        rect: pygame.Rect,  # on-screen bounding box for the whole board
        tile_size: int,     # pixel size of each square tile
    ):
        self.tiles     = tiles
        self.n         = n
        self.rect      = pygame.Rect(rect)
        self.tile_size = tile_size
        self.moves     = 0
        self.solved    = False

        # Build grid and scramble it.
        self.grid = self._make_solved_grid()
        self._scramble()

        # ── Drag state ──────────────────────────────────────────────────
        self._drag             = False
        self._drag_pos         = None   # (row, col) of the tile being dragged
        self._drag_dir         = None   # 'H' (horizontal) or 'V' (vertical)
        self._drag_origin      = (0, 0) # pixel top-left of tile at drag start
        self._drag_px          = (0, 0) # current pixel top-left during drag
        self._drag_mouse_start = (0, 0)

    # ------------------------------------------------------------------ #
    #  Public interface                                                    #
    # ------------------------------------------------------------------ #

    def handle_mousedown(self, pos) -> None:
        """Start a drag if pos lands on a tile adjacent to the empty slot."""
        if self.solved:
            return
        er, ec = self._empty_pos()
        mx, my = pos
        for r in range(self.n):
            for c in range(self.n):
                if self.grid[r][c] == self.EMPTY:
                    continue
                tr = self._cell_rect(r, c)
                if not tr.collidepoint(mx, my):
                    continue
                adj_h = (r == er and abs(c - ec) == 1)
                adj_v = (c == ec and abs(r - er) == 1)
                if adj_h or adj_v:
                    self._drag             = True
                    self._drag_pos         = (r, c)
                    self._drag_dir         = "H" if adj_h else "V"
                    self._drag_origin      = (tr.x, tr.y)
                    self._drag_px          = (tr.x, tr.y)
                    self._drag_mouse_start = pos
                return   # only one tile can be under the cursor

    def handle_mousemove(self, pos) -> None:
        """Update the dragged tile's pixel position, clamped to valid range."""
        if not self._drag:
            return
        r, c   = self._drag_pos
        er, ec = self._empty_pos()
        ox, oy = self._drag_origin
        mx, my = pos
        smx, smy = self._drag_mouse_start

        if self._drag_dir == "H":
            sign = 1 if ec > c else -1
            dx   = (mx - smx) * sign
            dx   = max(0, min(self.tile_size, dx))
            self._drag_px = (ox + dx * sign, oy)
        else:  # "V"
            sign = 1 if er > r else -1
            dy   = (my - smy) * sign
            dy   = max(0, min(self.tile_size, dy))
            self._drag_px = (ox, oy + dy * sign)

    def handle_mouseup(self, _pos) -> bool:
        """
        Commit the move if the tile passed the midpoint, else snap back.
        Returns True if a move was committed.
        """
        if not self._drag:
            return False

        r, c   = self._drag_pos
        er, ec = self._empty_pos()
        ox, oy = self._drag_origin
        moved  = False

        if self._drag_dir == "H":
            if abs(self._drag_px[0] - ox) >= self.tile_size // 2:
                self.grid[er][ec], self.grid[r][c] = (
                    self.grid[r][c], self.grid[er][ec]
                )
                self.moves += 1
                moved = True
        else:
            if abs(self._drag_px[1] - oy) >= self.tile_size // 2:
                self.grid[er][ec], self.grid[r][c] = (
                    self.grid[r][c], self.grid[er][ec]
                )
                self.moves += 1
                moved = True

        self._drag     = False
        self._drag_pos = None
        if moved:
            self.solved = self._check_win()
        return moved

    def draw(self, surface) -> None:
        """Render the entire board onto *surface*."""
        pygame.draw.rect(surface, PANEL_BG, self.rect, border_radius=12)

        drag_r = self._drag_pos[0] if self._drag else None
        drag_c = self._drag_pos[1] if self._drag else None

        for r in range(self.n):
            for c in range(self.n):
                idx = self.grid[r][c]
                tr  = self._cell_rect(r, c)

                if idx == self.EMPTY:
                    pygame.draw.rect(surface, EMPTY_CELL, tr, border_radius=8)
                    pygame.draw.rect(surface, TILE_BORDER, tr, 1, border_radius=8)
                    continue

                if self._drag and r == drag_r and c == drag_c:
                    continue   # drawn on top after the loop

                surface.blit(self.tiles[idx], (tr.x, tr.y))
                pygame.draw.rect(surface, TILE_BORDER, tr, 1, border_radius=8)

        # Draw the dragged tile last so it floats above everything
        if self._drag and drag_r is not None:
            idx = self.grid[drag_r][drag_c]
            px, py = self._drag_px
            surface.blit(self.tiles[idx], (px, py))
            drag_rect = pygame.Rect(px, py, self.tile_size, self.tile_size)
            pygame.draw.rect(surface, (255, 215, 0), drag_rect, 3)

        # Light green overlay when solved
        if self.solved:
            overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            overlay.fill((100, 255, 150, 55))
            surface.blit(overlay, self.rect.topleft)

    def force_solve(self) -> None:
        """Instantly arrange all tiles into the solved state."""
        self.grid   = self._make_solved_grid()
        self.solved = True

    # ------------------------------------------------------------------ #
    #  Scramble algorithm (guaranteed solvable)                           #
    # ------------------------------------------------------------------ #

    def _scramble(self) -> None:
        """
        Two-phase scramble that always produces a solvable puzzle.

        Phase 1 – Parity-correct random permutation
        --------------------------------------------
        We build a flat sequence of all cell values (0 … n²-2 for tiles,
        EMPTY for the blank) and shuffle it.  If the resulting position is
        not solvable we perform a single adjacent swap of two non-empty
        tiles, which flips the inversion count parity by exactly 1 and
        makes the puzzle solvable.

        Phase 2 – Random-walk refinement
        ---------------------------------
        _WALK_STEPS additional legal moves are applied to eliminate any
        leftover visual structure without breaking solvability.
        """
        # ── Phase 1: build a solvable random permutation ────────────────
        n    = self.n
        flat = list(range(n * n - 1)) + [self.EMPTY]

        while True:
            random.shuffle(flat)
            if self._is_solvable(flat, n):
                break
            # Flip parity by swapping the last two non-empty elements
            non_empty = [i for i, v in enumerate(flat) if v != self.EMPTY]
            # Swap the last two non-empty positions
            i, j = non_empty[-2], non_empty[-1]
            flat[i], flat[j] = flat[j], flat[i]
            if self._is_solvable(flat, n):
                break
            # Should never need a third attempt, but guard anyway

        # Place the flat list into self.grid
        for r in range(n):
            for c in range(n):
                self.grid[r][c] = flat[r * n + c]

        # ── Phase 2: random-walk refinement ─────────────────────────────
        self._random_walk(self._WALK_STEPS)

    @staticmethod
    def _is_solvable(flat: list, n: int) -> bool:
        """
        Check whether the given flat tile sequence represents a solvable
        n-puzzle configuration.

        Theory
        ------
        Let `inv` = number of inversions in the sequence (pairs (i, j) with
        i < j, flat[i] > flat[j] > 0, ignoring the empty cell).

        Let `blank_row_from_bottom` = distance of the empty cell from the
        bottom row (0-indexed, so the bottom row has distance 0).

        * n is odd  →  solvable iff inv is even.
        * n is even →  solvable iff (inv + blank_row_from_bottom) is even.
        """
        # Count inversions (ignore the empty sentinel)
        tiles_only = [v for v in flat if v != Board.EMPTY]
        inversions = 0
        for i in range(len(tiles_only)):
            for j in range(i + 1, len(tiles_only)):
                if tiles_only[i] > tiles_only[j]:
                    inversions += 1

        if n % 2 == 1:
            # Odd-width board: solvable iff inversions is even
            return inversions % 2 == 0
        else:
            # Even-width board: need blank row from bottom
            blank_idx           = flat.index(Board.EMPTY)
            blank_row           = blank_idx // n
            blank_row_from_bot  = (n - 1) - blank_row
            return (inversions + blank_row_from_bot) % 2 == 0

    def _random_walk(self, steps: int) -> None:
        """
        Perform `steps` random legal moves (sliding a neighbour of the
        blank into the blank).  Every move produced here is by definition
        legal, so solvability is preserved throughout.
        """
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        prev_move  = None   # avoid immediately reversing the last move

        for _ in range(steps):
            er, ec    = self._empty_pos()
            candidates = []

            for dr, dc in directions:
                nr, nc = er + dr, ec + dc
                if 0 <= nr < self.n and 0 <= nc < self.n:
                    # Skip the reverse of the previous move to avoid
                    # getting stuck in a 2-step oscillation
                    if prev_move and (nr, nc) == prev_move:
                        continue
                    candidates.append((nr, nc))

            if not candidates:
                # Fallback (shouldn't happen for n ≥ 2)
                candidates = [
                    (er + dr, ec + dc)
                    for dr, dc in directions
                    if 0 <= er + dr < self.n and 0 <= ec + dc < self.n
                ]

            nr, nc = random.choice(candidates)
            self.grid[er][ec], self.grid[nr][nc] = (
                self.grid[nr][nc],
                self.grid[er][ec],
            )
            prev_move = (er, ec)   # previous blank position = tile we just moved

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #

    def _make_solved_grid(self) -> list:
        """Return a 2-D grid in the solved (goal) configuration."""
        n    = self.n
        flat = list(range(n * n - 1)) + [self.EMPTY]
        return [flat[i * n: (i + 1) * n] for i in range(n)]

    def _cell_rect(self, row: int, col: int) -> pygame.Rect:
        x = self.rect.x + col * self.tile_size
        y = self.rect.y + row * self.tile_size
        return pygame.Rect(x, y, self.tile_size, self.tile_size)

    def _empty_pos(self) -> tuple:
        for r in range(self.n):
            for c in range(self.n):
                if self.grid[r][c] == self.EMPTY:
                    return r, c
        raise RuntimeError("Board has no empty cell — this should never happen.")

    def _check_win(self) -> bool:
        idx = 0
        for r in range(self.n):
            for c in range(self.n):
                if r == self.n - 1 and c == self.n - 1:
                    return self.grid[r][c] == self.EMPTY
                if self.grid[r][c] != idx:
                    return False
                idx += 1
        return True
