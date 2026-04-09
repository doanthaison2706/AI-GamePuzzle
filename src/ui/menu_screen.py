"""
menu_screen.py
--------------
Main menu screen — redesigned with a bright, minimalist, creative aesthetic.
Replaces the old image-based menu with the animated ModernBackground + Button system.
"""

import math
import sys
import pygame

from configs.game_config import (
    TEXT_COLOR, MUTED_TEXT, ACCENT,
    BTN_COLOR, BTN_HOVER, BTN_ACTIVE,
    P1_COLOR, P2_COLOR,
)
from src.ui.components import Button
from src.ui.background import ModernBackground

TITLE = "P U Z Z L E"


class MainMenuScreen:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        W, H = screen.get_size()

        self._font_title = pygame.font.SysFont("Georgia", 96, bold=True)
        self._font_sub   = pygame.font.SysFont("Georgia",  22, italic=True)
        self._font_btn   = pygame.font.SysFont("Georgia",  18, bold=True)

        self._tick = 0

        bw, bh = 260, 56
        cx     = W // 2

        self.btn_play = Button(
            (cx - bw // 2, 460, bw, bh), "P L A Y", self._font_btn,
            color=BTN_COLOR, hover_color=BTN_HOVER, active_color=BTN_ACTIVE,
            border_radius=28
        )
        self.btn_exit = Button(
            (cx - bw // 2, 540, bw, bh), "T H O Á T", self._font_btn,
            color=(max(0, P2_COLOR[0]-20), max(0, P2_COLOR[1]-20), max(0, P2_COLOR[2]-20)),
            hover_color=P2_COLOR,
            active_color=(max(0, P2_COLOR[0]-40), max(0, P2_COLOR[1]-40), max(0, P2_COLOR[2]-40)),
            border_radius=28
        )

        self._bg = ModernBackground(W, H)

    # ─── Public interface ─────────────────────────────────────────────────────

    def handle_events(self, events):
        for event in events:
            if self.btn_play.handle_event(event):
                return "SETUP", None
            if self.btn_exit.handle_event(event):
                pygame.quit()
                sys.exit()
        return "MAIN_MENU", None

    def render(self) -> None:
        self._tick += 1
        W, H  = self.screen.get_size()
        mouse = pygame.mouse.get_pos()

        self._bg.draw(self.screen)
        self._draw_title(W)

        sub = self._font_sub.render("Slide into creativity", True, TEXT_COLOR)
        self.screen.blit(sub, sub.get_rect(center=(W // 2, 340)))

        divider = pygame.Surface((300, 2), pygame.SRCALPHA)
        divider.fill((*MUTED_TEXT, 100))
        self.screen.blit(divider, divider.get_rect(center=(W // 2, 370)))

        self.btn_play.draw(self.screen, mouse)
        self.btn_exit.draw(self.screen, mouse)

    # ─── Private ──────────────────────────────────────────────────────────────

    def _draw_title(self, W: int) -> None:
        t = self._tick
        cy = 220

        words = list(TITLE.replace(" ", ""))
        num_chars = len(words)

        char_surfs  = [self._font_title.render(ch, True, TEXT_COLOR) for ch in words]
        char_widths = [s.get_width() for s in char_surfs]
        total_width = sum(char_widths) + (num_chars - 1) * 20

        start_x   = W // 2 - total_width // 2
        current_x = start_x

        shadow_col = tuple(min(255, c + 50) for c in MUTED_TEXT)

        for i, (surf, ch_w) in enumerate(zip(char_surfs, char_widths)):
            offset_y = 15 * math.sin(t * 0.05 + i * 0.5)

            color_blend = abs(math.sin(t * 0.02 + i * 0.3))
            c_r = int(TEXT_COLOR[0] * (1 - color_blend) + ACCENT[0] * color_blend * 0.8)
            c_g = int(TEXT_COLOR[1] * (1 - color_blend) + ACCENT[1] * color_blend * 0.8)
            c_b = int(TEXT_COLOR[2] * (1 - color_blend) + ACCENT[2] * color_blend * 0.8)

            colored_surf = self._font_title.render(words[i], True, (c_r, c_g, c_b))

            shadow = self._font_title.render(words[i], True, shadow_col)
            self.screen.blit(shadow, (current_x + 3, cy + offset_y + 3))
            self.screen.blit(colored_surf, (current_x, cy + offset_y))

            current_x += ch_w + 20