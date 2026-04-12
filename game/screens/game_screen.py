"""
Puzzle game supporting both 1-player and 2-player modes.
"""

import time

import pygame

from game.constants import (
    ACCENT,
    BOARD_SIZE,
    BOARD_Y,
    BTN_ACTIVE,
    BTN_COLOR,
    BTN_HOVER,
    DIFFICULTY_GRID,
    LEFT_BOARD_X,
    MUTED_TEXT,
    P1_COLOR,
    P2_COLOR,
    RIGHT_BOARD_X,
    TEXT_COLOR,
    WIN_COLOR,
)
from game.puzzle.board import Board
from game.puzzle.image_processor import build_full_preview
from game.screens.background import ModernBackground
from game.ui.button import Button
from game.ui.wood_frame import PARCHMENT, WOOD_DARK, draw_wood_frame, draw_wood_panel, draw_wood_plaque


class GameScreen:
    def __init__(
        self,
        screen: pygame.Surface,
        options: dict,
        tiles_p1: list,
        tiles_p2: list,
        move_sfx=None,
    ):
        self.screen = screen
        self.options = options
        self._raw_p1 = tiles_p1
        self._raw_p2 = tiles_p2
        self._move_sfx = move_sfx
        self._multiplayer = options.get("multiplayer", True)
        W, H = screen.get_size()
        cx = W // 2

        self._font_huge = pygame.font.SysFont("Georgia", 48, bold=True)
        self._font_big = pygame.font.SysFont("Georgia", 30, bold=True)
        self._font_hud = pygame.font.SysFont("Georgia", 20, bold=True)
        self._font_body = pygame.font.SysFont("Georgia", 17)
        self._font_small = pygame.font.SysFont("Georgia", 14)
        self._font_btn = pygame.font.SysFont("Georgia", 18, bold=True)

        self._n = DIFFICULTY_GRID[options["difficulty"]]
        self._tsz = BOARD_SIZE // self._n
        board_px = self._n * self._tsz
        self._board_y = BOARD_Y + 16

        if self._multiplayer:
            self._rect_p1 = pygame.Rect(LEFT_BOARD_X, self._board_y, board_px, board_px)
            self._rect_p2 = pygame.Rect(RIGHT_BOARD_X, self._board_y, board_px, board_px)
        else:
            self._rect_p1 = pygame.Rect((W - board_px) // 2, self._board_y, board_px, board_px)
            self._rect_p2 = None

        self._score = {1: 0, 2: 0}
        self._score_limit = options["score_limit"]
        self._round = 1
        self._timer_on = options["timer_enabled"]
        self._timer_full = options["timer_secs"]
        self._time_left = float(self._timer_full)
        self._last_tick = time.monotonic()
        self._round_over = False
        self._game_over = False
        self._rnd_winner = None
        self._winner = None

        self._bg = ModernBackground(W, H, "Gemini_Generated_Image_437nvr437nvr437n.png")
        self._ref_size = 108
        self._ref_p1 = build_full_preview(tiles_p1, self._n, self._tsz, self._ref_size)
        self._ref_p2 = build_full_preview(tiles_p2, self._n, self._tsz, self._ref_size) if tiles_p2 else None

        self._toolbar = pygame.Rect(W // 2 - 258, H - 90, 516, 72)

        self._btn_back = Button(
            (self._toolbar.x + 20, self._toolbar.y + 15, 120, 38),
            "BACK",
            self._font_btn,
            color=(130, 91, 72),
            hover_color=(153, 108, 86),
            active_color=(98, 66, 52),
            border_radius=22,
        )
        self._btn_restart = Button(
            (self._toolbar.x + 156, self._toolbar.y + 15, 128, 38),
            "RESTART",
            self._font_btn,
            color=BTN_COLOR,
            hover_color=BTN_HOVER,
            active_color=BTN_ACTIVE,
            border_radius=22,
        )
        self._btn_next = Button(
            (cx - 110, H - 70, 220, 50),
            "NEXT ROUND",
            self._font_btn,
            color=BTN_COLOR,
            hover_color=BTN_HOVER,
            active_color=BTN_ACTIVE,
            border_radius=24,
        )
        self._btn_menu_final = Button(
            (cx - 126, H - 70, 252, 50),
            "MAIN MENU",
            self._font_btn,
            color=(130, 91, 72),
            hover_color=(153, 108, 86),
            active_color=(98, 66, 52),
            border_radius=24,
        )

        self._start_round()

    def handle_event(self, event) -> str | None:
        if self._game_over:
            if self._btn_menu_final.handle_event(event):
                return "menu"
            return None

        if self._round_over:
            if self._btn_next.handle_event(event):
                self._start_round()
            return None

        if self._btn_back.handle_event(event):
            return "setup"
        if self._btn_restart.handle_event(event):
            self._start_round()
            return None

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d):
                self._handle_keyboard_move(self._board1, event.key)
            if self._multiplayer and event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                self._handle_keyboard_move(self._board2, event.key)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._rect_p1.collidepoint(event.pos):
                self._board1.handle_mousedown(event.pos)
            if self._multiplayer and self._rect_p2 and self._rect_p2.collidepoint(event.pos):
                self._board2.handle_mousedown(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            if self._board1._drag:
                self._board1.handle_mousemove(event.pos)
            if self._multiplayer and self._board2 and self._board2._drag:
                self._board2.handle_mousemove(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            moved1 = self._board1.handle_mouseup(event.pos)
            moved2 = self._board2.handle_mouseup(event.pos) if self._multiplayer and self._board2 else False
            if (moved1 or moved2) and self._move_sfx:
                self._move_sfx.play()
            self._check_win_conditions()

        return None

    def update(self) -> None:
        if self._game_over or self._round_over:
            return
        if self._timer_on:
            now = time.monotonic()
            self._time_left -= now - self._last_tick
            self._last_tick = now
            if self._time_left <= 0:
                self._time_left = 0.0
                self._on_time_up()

    def draw(self) -> None:
        W, H = self.screen.get_size()
        cx = W // 2
        mouse = pygame.mouse.get_pos()

        self._bg.draw(self.screen)
        self._draw_top_hud(W, cx)

        if self._multiplayer:
            self._draw_player_area(self._rect_p1, self._board1, self._ref_p1, "PLAYER 1", "WASD", P1_COLOR)
            self._draw_player_area(self._rect_p2, self._board2, self._ref_p2, "PLAYER 2", "ARROWS", P2_COLOR)
        else:
            self._draw_player_area(self._rect_p1, self._board1, self._ref_p1, "PLAYER 1", "WASD", P1_COLOR, single=True)

        self._draw_bottom_toolbar(W, H, mouse)

        if self._round_over and not self._game_over:
            self._draw_overlay(f"Round {self._round - 1} complete", self._rnd_winner)
            self._btn_next.draw(self.screen, mouse)
        if self._game_over:
            self._draw_overlay("Match Over", self._winner, final=True)
            self._btn_menu_final.draw(self.screen, mouse)

    def _draw_top_hud(self, W: int, cx: int) -> None:
        if self._multiplayer:
            hud = pygame.Rect(cx - 240, 8, 480, 76)
            draw_wood_panel(self.screen, hud, radius=24, inset=12)
            title = self._font_big.render(f"{self._score[1]}  :  {self._score[2]}", True, TEXT_COLOR)
            self.screen.blit(title, title.get_rect(center=(hud.centerx, hud.y + 27)))
            sub = self._font_body.render(f"Round {self._round}  |  First to {self._score_limit}", True, MUTED_TEXT)
            self.screen.blit(sub, sub.get_rect(center=(hud.centerx, hud.y + 50)))
        else:
            hud = pygame.Rect(cx - 196, 10, 392, 82)
            draw_wood_panel(self.screen, hud, radius=24, inset=12)
            title = self._font_big.render(f"Wins {self._score[1]} / {self._score_limit}", True, TEXT_COLOR)
            self.screen.blit(title, title.get_rect(center=(hud.centerx, hud.y + 26)))
            line = self._font_body.render(f"Round {self._round}  |  {self._format_timer()}", True, MUTED_TEXT)
            self.screen.blit(line, line.get_rect(center=(hud.centerx, hud.y + 56)))

    def _draw_player_area(
        self,
        rect: pygame.Rect,
        board: Board,
        ref_img: pygame.Surface,
        label: str,
        controls: str,
        color,
        *,
        single: bool = False,
    ) -> None:
        outer = draw_wood_frame(self.screen, rect, padding=8, frame_width=14, radius=14)
        if not single:
            plaque = pygame.Rect(rect.centerx - 112, outer.y - 16, 224, 36)
            draw_wood_plaque(self.screen, plaque, radius=16)
            name = self._font_hud.render(label, True, PARCHMENT)
            self.screen.blit(name, name.get_rect(center=plaque.center))

        board.draw(self.screen)

        info_h = 162
        info_rect = pygame.Rect(rect.x, rect.bottom + 18, rect.width, info_h)
        draw_wood_panel(self.screen, info_rect, radius=24, inset=16)

        top_line = f"{label}  |  Moves: {board.moves}" if single else f"Moves: {board.moves}"
        moves = self._font_hud.render(top_line, True, color)
        self.screen.blit(moves, moves.get_rect(x=info_rect.x + 24, y=info_rect.y + 22))

        controls_surf = self._font_small.render(f"Controls: {controls}", True, MUTED_TEXT)
        self.screen.blit(controls_surf, controls_surf.get_rect(right=info_rect.right - 24, y=info_rect.y + 26))

        goal_label = self._font_small.render("GOAL BOARD", True, WOOD_DARK)
        self.screen.blit(goal_label, goal_label.get_rect(x=info_rect.x + 24, y=info_rect.y + 54))

        preview_area = pygame.Rect(info_rect.centerx - 60, info_rect.y + 20, 120, 120)
        scaled_ref = pygame.transform.smoothscale(ref_img, preview_area.size)
        self.screen.blit(scaled_ref, preview_area.topleft)

    def _draw_bottom_toolbar(self, W: int, H: int, mouse) -> None:
        if self._round_over or self._game_over:
            return

        toolbar = self._toolbar
        draw_wood_panel(self.screen, toolbar, radius=24, inset=12)
        self._btn_back.draw(self.screen, mouse)
        self._btn_restart.draw(self.screen, mouse)

        timer_text = self._font_hud.render(self._format_timer(), True, TEXT_COLOR)
        self.screen.blit(timer_text, timer_text.get_rect(center=(toolbar.right - 98, toolbar.centery)))

    def _start_round(self) -> None:
        self._board1 = Board([t.copy() for t in self._raw_p1], self._n, self._rect_p1, self._tsz)
        if self._multiplayer and self._raw_p2:
            self._board2 = Board([t.copy() for t in self._raw_p2], self._n, self._rect_p2, self._tsz)
        else:
            self._board2 = None

        self._time_left = float(self._timer_full)
        self._last_tick = time.monotonic()
        self._round_over = False
        self._rnd_winner = None

    def _handle_keyboard_move(self, board: Board, key: int) -> None:
        if not board or board.solved:
            return
        er, ec = board._empty_pos()
        dr, dc = 0, 0
        if key in (pygame.K_w, pygame.K_UP):
            dr = 1
        elif key in (pygame.K_s, pygame.K_DOWN):
            dr = -1
        elif key in (pygame.K_a, pygame.K_LEFT):
            dc = 1
        elif key in (pygame.K_d, pygame.K_RIGHT):
            dc = -1

        nr, nc = er + dr, ec + dc
        if 0 <= nr < board.n and 0 <= nc < board.n:
            board.grid[er][ec], board.grid[nr][nc] = board.grid[nr][nc], board.grid[er][ec]
            board.moves += 1
            if self._move_sfx:
                self._move_sfx.play()
            if board._check_win():
                board.solved = True
                self._check_win_conditions()

    def _check_win_conditions(self) -> None:
        if self._round_over:
            return

        p1 = self._board1.solved
        if self._multiplayer and self._board2:
            p2 = self._board2.solved
            if p1 and p2:
                self._end_round(1 if self._board1.moves <= self._board2.moves else 2)
            elif p1:
                self._end_round(1)
            elif p2:
                self._end_round(2)
        elif p1:
            self._end_round(1)

    def _end_round(self, winner: int) -> None:
        self._score[winner] += 1
        self._rnd_winner = winner
        self._round += 1
        self._round_over = True
        if self._score[winner] >= self._score_limit:
            self._game_over = True
            self._winner = winner

    def _on_time_up(self) -> None:
        if self._round_over:
            return
        if self._multiplayer and self._board2:
            c1 = self._count_correct(self._board1)
            c2 = self._count_correct(self._board2)
            self._end_round(1 if c1 >= c2 else 2)
        else:
            self._end_round(2)

    @staticmethod
    def _count_correct(board: Board) -> int:
        count = 0
        for r in range(board.n):
            for c in range(board.n):
                expected = r * board.n + c
                if r == board.n - 1 and c == board.n - 1:
                    if board.grid[r][c] == board.EMPTY:
                        count += 1
                elif board.grid[r][c] == expected:
                    count += 1
        return count

    def _draw_overlay(self, heading: str, winner: int | None, final: bool = False) -> None:
        W, H = self.screen.get_size()
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((26, 16, 10, 176))
        self.screen.blit(dim, (0, 0))

        panel = pygame.Rect(W // 2 - 290, H // 2 - 164, 580, 238)
        draw_wood_panel(self.screen, panel, radius=30, inset=18)

        heading_surf = self._font_big.render(heading, True, TEXT_COLOR)
        self.screen.blit(heading_surf, heading_surf.get_rect(center=(panel.centerx, panel.y + 56)))

        if winner:
            if self._multiplayer:
                color = P1_COLOR if winner == 1 else P2_COLOR
                message = f"Player {winner} wins the round"
            else:
                color = WIN_COLOR if winner == 1 else (188, 86, 76)
                message = "Puzzle solved" if winner == 1 else "Time expired"
            win_surf = self._font_huge.render(message, True, color)
            self.screen.blit(win_surf, win_surf.get_rect(center=(panel.centerx, panel.y + 116)))

        if final:
            if self._multiplayer:
                summary = f"Final score {self._score[1]} - {self._score[2]}"
            else:
                summary = f"Total wins: {self._score[1]}"
            summary_surf = self._font_hud.render(summary, True, WOOD_DARK)
            self.screen.blit(summary_surf, summary_surf.get_rect(center=(panel.centerx, panel.y + 172)))

    def _format_timer(self) -> str:
        if not self._timer_on:
            return "Timer off"
        secs = max(0, int(self._time_left))
        mm, ss = divmod(secs, 60)
        return f"Time {mm:02d}:{ss:02d}"
