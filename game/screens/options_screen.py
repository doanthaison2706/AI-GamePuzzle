"""
options_screen.py
-----------------
Settings screen: game mode, music volume, move sound volume, and brightness.
handle_event returns 'back' when the player is done.
"""

import pygame
from game.ui.button import Button
from game.screens.background import ModernBackground
from game.constants import (
    TEXT_COLOR, MUTED_TEXT, ACCENT,
    BTN_COLOR, BTN_HOVER, BTN_ACTIVE,
    P1_COLOR, P2_COLOR, WIN_COLOR
)


class OptionsScreen:

    def __init__(self, screen: pygame.Surface, options: dict):
        self.screen  = screen
        self.options = options
        W, H = screen.get_size()

        options.setdefault("music_volume", 80)
        options.setdefault("move_volume", 70)
        options.setdefault("brightness", 100)
        options.setdefault("multiplayer", True)

        self._font_h1  = pygame.font.SysFont("Georgia", 42, bold=True)
        self._font_h2  = pygame.font.SysFont("Georgia", 20)
        self._font_val = pygame.font.SysFont("Georgia", 28, bold=True)
        self._font_btn = pygame.font.SysFont("Georgia", 19, bold=True)

        cx = W // 2

        # ── Mode (1P / 2P toggle) ──────────────────────────────────────────────
        bw_mode = 160
        self._btn_1p = Button(
            (cx - bw_mode - 6, 195, bw_mode, 46), "1  P L A Y E R", self._font_btn,
            color=(P1_COLOR[0]-20, P1_COLOR[1]-20, P1_COLOR[2]-20), hover_color=P1_COLOR, border_radius=23
        )
        self._btn_2p = Button(
            (cx + 6, 195, bw_mode, 46), "2  P L A Y E R S", self._font_btn,
            color=(P1_COLOR[0]-20, P1_COLOR[1]-20, P1_COLOR[2]-20), hover_color=P1_COLOR, border_radius=23
        )
        self._mode_label_y = 168

        # ── Music volume ──────────────────────────────────────────────────────
        self._vol_dec = Button((cx - 90, 300, 46, 46), "−", self._font_val, border_radius=23,
                               color=(P2_COLOR[0]-20, P2_COLOR[1]-20, P2_COLOR[2]-20), hover_color=P2_COLOR)
        self._vol_inc = Button((cx + 44, 300, 46, 46), "+", self._font_val, border_radius=23,
                               color=(P2_COLOR[0]-20, P2_COLOR[1]-20, P2_COLOR[2]-20), hover_color=P2_COLOR)

        # ── Move sound volume ─────────────────────────────────────────────────
        self._move_dec = Button((cx - 90, 440, 46, 46), "−", self._font_val, border_radius=23,
                                color=(WIN_COLOR[0]-20, WIN_COLOR[1]-20, WIN_COLOR[2]-20), hover_color=WIN_COLOR)
        self._move_inc = Button((cx + 44, 440, 46, 46), "+", self._font_val, border_radius=23,
                                color=(WIN_COLOR[0]-20, WIN_COLOR[1]-20, WIN_COLOR[2]-20), hover_color=WIN_COLOR)

        # ── Brightness ────────────────────────────────────────────────────────
        self._bright_dec = Button((cx - 90, 580, 46, 46), "−", self._font_val, border_radius=23,
                                  color=BTN_COLOR, hover_color=BTN_HOVER)
        self._bright_inc = Button((cx + 44, 580, 46, 46), "+", self._font_val, border_radius=23,
                                  color=BTN_COLOR, hover_color=BTN_HOVER)

        # ── Back ──────────────────────────────────────────────────────────────
        self._btn_back = Button(
            (cx - 95, H - 90, 190, 52), "◀  B A C K", self._font_btn,
            color=(max(0, P2_COLOR[0]-30), max(0, P2_COLOR[1]-30), max(0, P2_COLOR[2]-30)),
            hover_color=P2_COLOR,
            active_color=(max(0, P2_COLOR[0]-40), max(0, P2_COLOR[1]-40), max(0, P2_COLOR[2]-40)),
            border_radius=26
        )

        self._bg = ModernBackground(W, H)

    # ─── Public interface ─────────────────────────────────────────────────────

    def handle_event(self, event) -> str | None:
        # Mode buttons
        if self._btn_1p.handle_event(event):
            self.options["multiplayer"] = False
        if self._btn_2p.handle_event(event):
            self.options["multiplayer"] = True

        if self._vol_dec.handle_event(event):
            self.options["music_volume"] = max(0, self.options["music_volume"] - 10)
        if self._vol_inc.handle_event(event):
            self.options["music_volume"] = min(100, self.options["music_volume"] + 10)

        if self._move_dec.handle_event(event):
            self.options["move_volume"] = max(0, self.options["move_volume"] - 10)
        if self._move_inc.handle_event(event):
            self.options["move_volume"] = min(100, self.options["move_volume"] + 10)

        if self._bright_dec.handle_event(event):
            self.options["brightness"] = max(0, self.options["brightness"] - 10)
        if self._bright_inc.handle_event(event):
            self.options["brightness"] = min(100, self.options["brightness"] + 10)

        if self._btn_back.handle_event(event):
            return "back"
        return None

    def draw(self) -> None:
        W, H  = self.screen.get_size()
        mouse = pygame.mouse.get_pos()
        self._bg.draw(self.screen)

        cx = W // 2

        title = self._font_h1.render("O P T I O N S", True, TEXT_COLOR)
        self.screen.blit(title, title.get_rect(center=(cx, 100)))

        # ── Game Mode ─────────────────────────────────────────────────────────
        self._label("GAME MODE", cx, self._mode_label_y)
        is_multi = self.options["multiplayer"]

        # Highlight active button
        active_col   = (ACCENT[0], ACCENT[1], ACCENT[2])
        inactive_col = (P1_COLOR[0]-20, P1_COLOR[1]-20, P1_COLOR[2]-20)
        
        self._btn_1p.color       = active_col   if not is_multi else inactive_col
        self._btn_1p.hover_color = active_col   if not is_multi else P1_COLOR
        self._btn_2p.color       = active_col   if is_multi     else inactive_col
        self._btn_2p.hover_color = active_col   if is_multi     else P1_COLOR

        self._btn_1p.draw(self.screen, mouse)
        self._btn_2p.draw(self.screen, mouse)

        # ── Music volume ──────────────────────────────────────────────────────
        self._label("MUSIC VOLUME", cx, 272)
        self._vol_dec.draw(self.screen, mouse)
        vol_text = self._font_val.render(f"{self.options['music_volume']}%", True, TEXT_COLOR)
        self.screen.blit(vol_text, vol_text.get_rect(center=(cx, 323)))
        self._vol_inc.draw(self.screen, mouse)
        self._draw_bar(cx, 356, self.options["music_volume"], color=P2_COLOR)

        # ── Move sound volume ──────────────────────────────────────────────────
        self._label("MOVE SOUND VOLUME", cx, 412)
        self._move_dec.draw(self.screen, mouse)
        move_text = self._font_val.render(f"{self.options['move_volume']}%", True, TEXT_COLOR)
        self.screen.blit(move_text, move_text.get_rect(center=(cx, 463)))
        self._move_inc.draw(self.screen, mouse)
        self._draw_bar(cx, 496, self.options["move_volume"], color=WIN_COLOR)

        # ── Brightness ──────────────────────────────────────────────────────────
        self._label("BRIGHTNESS", cx, 552)
        self._bright_dec.draw(self.screen, mouse)
        pct = self._font_val.render(f"{self.options['brightness']}%", True, TEXT_COLOR)
        self.screen.blit(pct, pct.get_rect(center=(cx, 603)))
        self._bright_inc.draw(self.screen, mouse)
        self._draw_bar(cx, 636, self.options["brightness"], color=BTN_COLOR)

        self._btn_back.draw(self.screen, mouse)

        if self.options["brightness"] < 100:
            dim = pygame.Surface((W, H), pygame.SRCALPHA)
            alpha = int(255 * (1 - self.options["brightness"] / 100))
            dim.fill((0, 0, 0, alpha))
            self.screen.blit(dim, (0, 0))

    # ─── Private ──────────────────────────────────────────────────────────────

    def _label(self, text: str, cx: int, y: int) -> None:
        surf = self._font_h2.render(text, True, MUTED_TEXT)
        self.screen.blit(surf, surf.get_rect(center=(cx, y)))

    def _draw_bar(self, cx: int, y: int, value: int, color=None) -> None:
        bar_w  = 260
        bar_h  = 12
        bar_x  = cx - bar_w // 2
        fill_w = int(bar_w * value / 100)
        pygame.draw.rect(self.screen, (220, 215, 210), (bar_x, y, bar_w, bar_h), border_radius=6)
        if fill_w > 0:
            fill_color = color if color else ACCENT
            pygame.draw.rect(self.screen, fill_color, (bar_x, y, fill_w, bar_h), border_radius=4)
            tip_x = bar_x + fill_w - 4
            pygame.draw.rect(self.screen, (255, 255, 255), (tip_x, y, 4, bar_h), border_radius=2)
