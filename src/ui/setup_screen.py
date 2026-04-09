"""
setup_screen.py
---------------
Unified game-setup screen (replaces SetupSingleScreen + SetupMultiScreen).

Returns from handle_events:
  ("SETUP_SINGLE", None)   — still on this screen, single-player mode
  ("SETUP_MULTI",  None)   — still on this screen, multi-player mode
  ("PLAYING",      data)   — start single-player  (data has size / time / image)
  ("PLAYING",      data)   — re-used for dual via game_app routing (see below)
  ("MENU",         None)   — back to main menu

game_app distinguishes 1P vs 2P via data["multiplayer"].
"""

import pygame

from configs.game_config import (
    TEXT_COLOR, MUTED_TEXT, ACCENT,
    BTN_COLOR, BTN_HOVER, BTN_ACTIVE,
    P1_COLOR, P2_COLOR, WIN_COLOR, PANEL_BG,
    BG_COLOR,
)
from src.ui.components import RoundedButton
from src.ui.background import ModernBackground
from src.utils.image_crop import open_file_dialog
from src.ui.crop_menu import CropImageMenu
from configs import game_config as config

_PREVIEW = 180   # preview thumbnail size (px)

# Board size options  (n → label)
_SIZES = {3: "3x3", 4: "4x4", 5: "5x5", 6: "6x6"}


class SetupSingleScreen:
    """
    Single unified setup screen.
    `is_multi` is an internal toggle; game_app still instantiates this
    class for both SETUP_SINGLE and SETUP_MULTI routes.
    """

    def __init__(self, screen: pygame.Surface, start_as_multi: bool = False):
        self.screen = screen
        W, H = screen.get_size()
        cx   = W // 2

        # ── Fonts ─────────────────────────────────────────────────────────────
        self._font_h1   = pygame.font.SysFont("Georgia", 30, bold=True)
        self._font_h2   = pygame.font.SysFont("Georgia", 18)
        self._font_btn  = pygame.font.SysFont("Georgia", 17, bold=True)
        self._font_val  = pygame.font.SysFont("Georgia", 24, bold=True)
        self._font_tiny = pygame.font.SysFont("Georgia", 14)

        # ── State ─────────────────────────────────────────────────────────────
        self.is_multi       = start_as_multi
        self.selected_size  = 4        # default board size
        self.selected_time  = 0        # 0 = unlimited
        self.selected_score = 3        # best-of (only used in multi)

        # image state: each player defaults to "DEFAULT" (ready immediately)
        self._image_mode = {1: "DEFAULT", 2: "DEFAULT"}
        self._full_image = {1: None,      2: None}
        self._preview    = {1: None,      2: None}
        self._error      = {1: "",        2: ""}

        # ── Background ────────────────────────────────────────────────────────
        self._bg = ModernBackground(W, H)

        # ── Layout constants ──────────────────────────────────────────────────
        col_btn_y  = 300
        col_btn_h  = 38

        p1x_multi  = W // 4  - _PREVIEW // 2
        p2x_multi  = 3*W//4  - _PREVIEW // 2
        p1x_single = cx      - _PREVIEW // 2

        # Player-column image-pick buttons (two layouts)
        def _mk(rect, text, color, hcolor):
            return RoundedButton(rect, text, self._font_btn,
                          color=color, hover_color=hcolor)

        dim = lambda c: tuple(max(0, v - 20) for v in c)

        self._btn_p1_pick_multi    = _mk((p1x_multi,  col_btn_y,               _PREVIEW, col_btn_h), "Pick Image",   dim(P1_COLOR), P1_COLOR)
        self._btn_p1_default_multi = _mk((p1x_multi,  col_btn_y+col_btn_h+6,   _PREVIEW, col_btn_h), "Use Defaults", BTN_COLOR,     BTN_HOVER)
        self._btn_p2_pick          = _mk((p2x_multi,  col_btn_y,               _PREVIEW, col_btn_h), "Pick Image",   dim(P2_COLOR), P2_COLOR)
        self._btn_p2_default       = _mk((p2x_multi,  col_btn_y+col_btn_h+6,   _PREVIEW, col_btn_h), "Use Defaults", BTN_COLOR,     BTN_HOVER)
        self._btn_p1_pick_single   = _mk((p1x_single, col_btn_y,               _PREVIEW, col_btn_h), "Pick Image",   dim(P1_COLOR), P1_COLOR)
        self._btn_p1_default_single= _mk((p1x_single, col_btn_y+col_btn_h+6,   _PREVIEW, col_btn_h), "Use Defaults", BTN_COLOR,     BTN_HOVER)

        # Preview rects
        self._prev_rect_multi  = {
            1: pygame.Rect(p1x_multi,  90, _PREVIEW, _PREVIEW),
            2: pygame.Rect(p2x_multi,  90, _PREVIEW, _PREVIEW),
        }
        self._prev_rect_single = {1: pygame.Rect(p1x_single, 90, _PREVIEW, _PREVIEW)}

        # ── Player-2 add button (big "+") — shown when P2 is OFF ──────────────
        p2_prev_cx = 3*W//4
        p2_prev_cy = 90 + _PREVIEW // 2   # centre of preview area
        add_btn_size = 72
        self._btn_p2_add = RoundedButton(
            (p2_prev_cx - add_btn_size//2, p2_prev_cy - add_btn_size//2,
             add_btn_size, add_btn_size),
            "+", pygame.font.SysFont("Georgia", 36, bold=True),
            color=(45, 130, 55), hover_color=(65, 160, 75),
        )
        # ── Player-2 remove button (small "−") — shown when P2 is ON ────────────
        self._btn_p2_remove = RoundedButton(
            (p2_prev_cx + _PREVIEW//2 - 22, 68, 28, 28),
            "−", pygame.font.SysFont("Georgia", 20, bold=True),
            color=(160, 50, 50), hover_color=(200, 70, 70),
        )

        # ── Board-size buttons (replaces Difficulty) ──────────────────────────
        sy = 420
        self._size_btns: dict[int, RoundedButton] = {}
        sizes = list(_SIZES.keys())
        for i, n in enumerate(sizes):
            x = cx - (len(sizes) * 115 // 2) + i * 115
            self._size_btns[n] = RoundedButton(
                (x, sy + 28, 100, 38), _SIZES[n], self._font_btn,
                color=(55, 55, 100), hover_color=(75, 75, 140),
            )
        self._size_label_y = sy + 8
        self._size_note_y  = sy + 76

        # ── Score limit (multi only) ───────────────────────────────────────────
        sly = sy + 110
        self._score_label_y = sly
        self._score_dec = RoundedButton((cx - 74, sly + 22, 40, 40), "−", self._font_val)
        self._score_inc = RoundedButton((cx + 34, sly + 22, 40, 40), "+", self._font_val)
        self._score_val_y = sly + 42

        # ── Timer toggle + duration ───────────────────────────────────────────
        tmy = sly + 90
        self._timer_label_y = tmy
        self._timer_toggle  = RoundedButton((cx - 55, tmy + 22, 110, 36), "", self._font_btn)
        self._timer_enabled = False
        self._timer_secs    = 180

        tdy = tmy + 72
        self._tdur_label_y = tdy
        self._timer_dec = RoundedButton((cx - 74, tdy + 22, 40, 40), "−", self._font_val)
        self._timer_inc = RoundedButton((cx + 34, tdy + 22, 40, 40), "+", self._font_val)
        self._tdur_val_y = tdy + 42

        # ── Footer ────────────────────────────────────────────────────────────
        self._btn_back = RoundedButton(
            (20, H - 66, 140, 46), "◀  B A C K", self._font_btn,
            color=(max(0, P2_COLOR[0]-30), max(0, P2_COLOR[1]-30), max(0, P2_COLOR[2]-30)),
            hover_color=P2_COLOR,
        )
        bw_start = 220
        self._btn_start = RoundedButton(
            (cx - bw_start//2, H - 66, bw_start, 46), "▶  S T A R T", self._font_btn,
            color=BTN_COLOR, hover_color=BTN_HOVER, active_color=BTN_ACTIVE,
        )

    # ─── Public interface ─────────────────────────────────────────────────────

    def handle_events(self, events):
        """Old-style API: returns (state_str, data_or_None)."""
        for event in events:
            result = self._handle_event(event)
            if result is not None:
                return result
        # Stay on this screen
        state = "SETUP_MULTI" if self.is_multi else "SETUP_SINGLE"
        return state, None

    def render(self) -> None:
        W, H  = self.screen.get_size()
        mouse = pygame.mouse.get_pos()
        cx    = W // 2

        self._bg.draw(self.screen)

        # Title
        t = self._font_h1.render("G A M E   S E T U P", True, TEXT_COLOR)
        self.screen.blit(t, t.get_rect(center=(cx, 35)))

        # Always render both columns so the P2 toggle is always visible.
        # _draw_p2_column handles the disabled/enabled appearance internally.
        self._draw_multi_columns(W, cx, mouse)

        # Separator
        pygame.draw.line(self.screen, (55, 55, 90), (40, 400), (W - 40, 400), 1)

        # Board-size selector
        self._label("BOARD SIZE", cx, self._size_label_y)
        n = self.selected_size
        for size_n, btn in self._size_btns.items():
            active = size_n == n
            btn.color       = (50, 140, 70) if active else (55, 55, 100)
            btn.hover_color = tuple(min(c + 25, 255) for c in btn.color)
            btn.draw(self.screen, mouse)
        note = self._font_tiny.render(f"{n}x{n} grid  ({n*n-1} tiles)", True, MUTED_TEXT)
        self.screen.blit(note, note.get_rect(center=(cx, self._size_note_y)))

        # Score limit (multiplayer only)
        if self.is_multi:
            self._label("SCORE LIMIT", cx, self._score_label_y)
            self._score_dec.draw(self.screen, mouse)
            val = self._font_val.render(str(self.selected_score), True, ACCENT)
            self.screen.blit(val, val.get_rect(center=(cx, self._score_val_y)))
            self._score_inc.draw(self.screen, mouse)

        # Timer toggle
        _, H = self.screen.get_size()
        self._label("TIMER", cx, self._timer_label_y)
        self._timer_toggle.text        = "ON"  if self._timer_enabled else "OFF"
        self._timer_toggle.color       = (45, 130, 55) if self._timer_enabled else (130, 50, 50)
        self._timer_toggle.hover_color = (65, 160, 75) if self._timer_enabled else (160, 70, 70)
        self._timer_toggle.draw(self.screen, mouse)

        # Time per round
        self._label("TIME PER ROUND", cx, self._tdur_label_y)
        self._timer_dec.draw(self.screen, mouse)
        m, s   = divmod(self._timer_secs, 60)
        t_text = self._font_val.render(f"{m:02d}:{s:02d}", True, ACCENT)
        self.screen.blit(t_text, t_text.get_rect(center=(cx, self._tdur_val_y)))
        self._timer_inc.draw(self.screen, mouse)

        # Footer
        self._btn_back.draw(self.screen, mouse)
        self._btn_start.draw(self.screen, mouse)

    # ─── Private event handler ────────────────────────────────────────────────

    def _handle_event(self, event):
        """Returns (state, data) if a transition occurs, else None."""

        # Back
        if self._btn_back.handle_event(event):
            return "MENU", None

        # Player-2 toggle (add / remove)
        if self._btn_p2_add.handle_event(event):
            self.is_multi = True
        if self._btn_p2_remove.handle_event(event):
            self.is_multi = False

        # Player-1 image buttons (always multi-column layout now)
        if self._btn_p1_pick_multi.handle_event(event):
            self._pick(1)
        if self._btn_p1_default_multi.handle_event(event):
            self._use_default(1)

        # Player-2 image buttons (only when multi is on)
        if self.is_multi:
            if self._btn_p2_pick.handle_event(event):
                self._pick(2)
            if self._btn_p2_default.handle_event(event):
                self._use_default(2)

        # Board-size
        for n, btn in self._size_btns.items():
            if btn.handle_event(event):
                self.selected_size = n

        # Score limit (multiplayer only)
        if self.is_multi:
            if self._score_dec.handle_event(event):
                self.selected_score = max(1, self.selected_score - 1)
            if self._score_inc.handle_event(event):
                self.selected_score = min(10, self.selected_score + 1)

        # Timer toggle
        if self._timer_toggle.handle_event(event):
            self._timer_enabled = not self._timer_enabled
        if self._timer_dec.handle_event(event):
            self._timer_secs = max(30, self._timer_secs - 30)
        if self._timer_inc.handle_event(event):
            self._timer_secs = min(600, self._timer_secs + 30)

        # Start
        if self._btn_start.handle_event(event):
            data = {
                "size":          self.selected_size,
                "time":          self._timer_secs if self._timer_enabled else 0,
                "score":         self.selected_score,
                "multiplayer":   self.is_multi,
                "image":         self._full_image[1],   # P1 image (None = default)
                "image_p2":      self._full_image[2],   # P2 image (None = default)
            }
            return "PLAYING", data

        return None

    # ─── Private draw helpers ─────────────────────────────────────────────────

    def _draw_multi_columns(self, W, cx, mouse):
        pygame.draw.line(self.screen, (55, 55, 90), (cx, 55), (cx, 380), 1)

        # Player 1 column
        self._draw_player_col(
            player=1, col_cx=W//4, color=P1_COLOR,
            prev_rect=self._prev_rect_multi[1],
            btn_pick=self._btn_p1_pick_multi,
            btn_def=self._btn_p1_default_multi,
            mouse=mouse,
        )

        # Player 2 column — always drawn; inside we show toggle
        self._draw_p2_column(W, cx, mouse)

    def _draw_p2_column(self, W, cx, mouse):
        """Player 2 column.
        • Disabled: shows PLAYER 2 label (greyed) + big ‘+’ button to add.
        • Enabled:  shows full controls + small ‘−’ button to remove.
        """
        col_cx = 3 * W // 4
        color  = P2_COLOR

        if not self.is_multi:
            # ── P2 disabled: big "+" add button ──────────────────────────────
            lbl = self._font_h1.render("PLAYER 2", True, MUTED_TEXT)
            self.screen.blit(lbl, lbl.get_rect(center=(col_cx, 70)))

            # Light dashed preview box
            pr = self._prev_rect_multi[2]
            pygame.draw.rect(self.screen, (210, 210, 210), pr, border_radius=8)
            pygame.draw.rect(self.screen, (170, 170, 170), pr, 2, border_radius=8)

            # Big "+" button centred in the preview area
            self._btn_p2_add.rect.center = pr.center
            self._btn_p2_add.draw(self.screen, mouse)

            hint = self._font_tiny.render("Add Player 2", True, MUTED_TEXT)
            self.screen.blit(hint, hint.get_rect(center=(col_cx, pr.bottom + 14)))
            return

        # ── P2 enabled: full column ──────────────────────────────────────────
        lbl = self._font_h1.render("PLAYER 2", True, color)
        self.screen.blit(lbl, lbl.get_rect(center=(col_cx, 70)))

        # Small "−" remove button to the right of the header
        self._btn_p2_remove.rect.centerx = col_cx + _PREVIEW // 2 + 18
        self._btn_p2_remove.rect.centery = 70
        self._btn_p2_remove.draw(self.screen, mouse)

        self._draw_player_col(
            player=2, col_cx=col_cx, color=color,
            prev_rect=self._prev_rect_multi[2],
            btn_pick=self._btn_p2_pick,
            btn_def=self._btn_p2_default,
            mouse=mouse,
        )

    def _draw_single_column(self, W, cx, mouse):
        self._draw_player_col(
            player=1, col_cx=cx, color=P1_COLOR,
            prev_rect=self._prev_rect_single[1],
            btn_pick=self._btn_p1_pick_single,
            btn_def=self._btn_p1_default_single,
            mouse=mouse,
        )

    def _draw_player_col(self, player, col_cx, color, prev_rect, btn_pick, btn_def, mouse):
        lbl = self._font_h1.render(f"PLAYER {player}", True, color)
        self.screen.blit(lbl, lbl.get_rect(center=(col_cx, 70)))

        # Preview thumbnail
        if self._preview[player]:
            self.screen.blit(self._preview[player], prev_rect.topleft)
        else:
            pygame.draw.rect(self.screen, PANEL_BG, prev_rect, border_radius=4)
            hint = self._font_h2.render("default tiles", True, MUTED_TEXT)
            self.screen.blit(hint, hint.get_rect(center=prev_rect.center))
        pygame.draw.rect(self.screen, (70, 70, 110), prev_rect, 2, border_radius=4)

        # Status — always "Ready" since we default immediately
        mode_txt = "Custom image" if self._image_mode[player] == "CUSTOM" else "Default tiles"
        st = self._font_h2.render(mode_txt, True, (57, 255, 20))
        self.screen.blit(st, st.get_rect(center=(col_cx, 284)))

        if self._error[player]:
            err = self._font_tiny.render(self._error[player], True, (230, 80, 80))
            self.screen.blit(err, err.get_rect(center=(col_cx, 372)))

        btn_pick.draw(self.screen, mouse)
        btn_def.draw(self.screen, mouse)

    # ─── Private helpers ──────────────────────────────────────────────────────

    def _label(self, text: str, cx: int, y: int) -> None:
        surf = self._font_h2.render(text, True, MUTED_TEXT)
        self.screen.blit(surf, surf.get_rect(center=(cx, y)))

    def _pick(self, player: int) -> None:
        self._error[player] = ""
        path = open_file_dialog()
        if not path:
            return
        try:
            crop_ui = CropImageMenu(self.screen, path, config.BOARD_SIZE)
            cropped = crop_ui.run()
            if cropped:
                self._full_image[player]  = cropped
                self._image_mode[player]  = "CUSTOM"
                # Build a _PREVIEW x _PREVIEW thumbnail
                self._preview[player] = pygame.transform.smoothscale(
                    cropped, (_PREVIEW, _PREVIEW)
                )
        except Exception as exc:
            self._error[player] = f"Could not load: {exc}"

    def _use_default(self, player: int) -> None:
        self._error[player]      = ""
        self._full_image[player] = None
        self._image_mode[player] = "DEFAULT"
        self._preview[player]    = None


# ── Backward-compat alias so game_app.py keeps working unchanged ──────────────
class SetupMultiScreen(SetupSingleScreen):
    def __init__(self, screen):
        super().__init__(screen, start_as_multi=True)