"""
setup_screen.py
---------------
Unified game-setup screen (replaces SetupSingleScreen + SetupMultiScreen).
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

_PREVIEW = 180
_SIZES = {3: "3x3", 4: "4x4", 5: "5x5", 6: "6x6"}
_DIFFS = {"easy": "DỄ", "medium": "VỪA", "hard": "KHÓ"}

class SetupSingleScreen:
    def __init__(self, screen: pygame.Surface, start_as_multi: bool = False):
        self.screen = screen
        W, H = screen.get_size()
        cx   = W // 2

        self._font_h1   = pygame.font.SysFont("Georgia", 30, bold=True)
        self._font_h2   = pygame.font.SysFont("Georgia", 18)
        self._font_btn  = pygame.font.SysFont("Georgia", 17, bold=True)
        self._font_tiny = pygame.font.SysFont("Georgia", 13, bold=True)
        self._font_val  = pygame.font.SysFont("Georgia", 24, bold=True)

        self.is_multi       = start_as_multi
        self.selected_size  = 4
        self.selected_time  = 0
        self.selected_score = 3

        self.p_type         = {1: "HUMAN", 2: "HUMAN"}
        self.ai_diff        = {1: "medium", 2: "medium"}

        self._image_mode = {1: "DEFAULT", 2: "DEFAULT"}
        self._full_image = {1: None,      2: None}
        self._preview    = {1: None,      2: None}
        self._error      = {1: "",        2: ""}

        self._bg = ModernBackground(W, H)

        p1x_multi  = W // 4  - _PREVIEW // 2
        p2x_multi  = 3*W//4  - _PREVIEW // 2

        def _mk(rect, text, color, hcolor):
            return RoundedButton(rect, text, self._font_btn, color=color, hover_color=hcolor)
        dim = lambda c: tuple(max(0, v - 20) for v in c)

        col_type_y = 280
        diff_y     = 322
        col_btn_y  = 360
        col_def_y  = 402
        col_btn_h  = 36

        self._btn_p1_type_multi  = _mk((p1x_multi,  col_type_y, _PREVIEW, col_btn_h), "👤 HUMAN", (60, 140, 200), (80, 160, 220))
        self._btn_p2_type        = _mk((p2x_multi,  col_type_y, _PREVIEW, col_btn_h), "👤 HUMAN", (60, 140, 200), (80, 160, 220))

        def _make_diff_btns(p_cx):
            btns = {}
            bw = 56
            bx = p_cx - _PREVIEW//2
            for i, (k, lbl) in enumerate(_DIFFS.items()):
                btns[k] = RoundedButton((bx + i*(bw+6), diff_y, bw, 30), lbl, self._font_tiny, color=(55, 55, 100), hover_color=(75, 75, 140))
            return btns

        self._p1_diff_btns_multi = _make_diff_btns(W//4)
        self._p2_diff_btns       = _make_diff_btns(3*W//4)

        self._btn_p1_pick_multi    = _mk((p1x_multi,  col_btn_y, _PREVIEW, col_btn_h), "Pick Image",   dim(P1_COLOR), P1_COLOR)
        self._btn_p1_default_multi = _mk((p1x_multi,  col_def_y, _PREVIEW, col_btn_h), "Use Defaults", BTN_COLOR,     BTN_HOVER)
        self._btn_p2_pick          = _mk((p2x_multi,  col_btn_y, _PREVIEW, col_btn_h), "Pick Image",   dim(P2_COLOR), P2_COLOR)
        self._btn_p2_default       = _mk((p2x_multi,  col_def_y, _PREVIEW, col_btn_h), "Use Defaults", BTN_COLOR,     BTN_HOVER)

        self._prev_rect_multi  = {1: pygame.Rect(p1x_multi,  90, _PREVIEW, _PREVIEW), 2: pygame.Rect(p2x_multi,  90, _PREVIEW, _PREVIEW)}

        p2_prev_cx = 3*W//4
        p2_prev_cy = 90 + _PREVIEW // 2
        self._btn_p2_add = RoundedButton((p2_prev_cx - 36, p2_prev_cy - 36, 72, 72), "+", pygame.font.SysFont("Georgia", 36, bold=True), color=(45, 130, 55), hover_color=(65, 160, 75))
        self._btn_p2_remove = RoundedButton((p2_prev_cx + _PREVIEW//2 - 22, 68, 28, 28), "−", pygame.font.SysFont("Georgia", 20, bold=True), color=(160, 50, 50), hover_color=(200, 70, 70))

        sy = 480
        sly = 550
        tmy = 620

        self._size_btns: dict[int, RoundedButton] = {}
        sizes = list(_SIZES.keys())
        for i, n in enumerate(sizes):
            x = cx - (len(sizes) * 115 // 2) + i * 115
            self._size_btns[n] = RoundedButton((x, sy + 25, 100, 36), _SIZES[n], self._font_btn, color=(55, 55, 100), hover_color=(75, 75, 140))
        self._size_label_y = sy

        self._score_label_y = sly
        self._score_dec = RoundedButton((cx - 74, sly + 25, 40, 36), "−", self._font_val)
        self._score_inc = RoundedButton((cx + 34, sly + 25, 40, 36), "+", self._font_val)
        self._score_val_y = sly + 43

        self._timer_label_y = tmy
        self._timer_toggle  = RoundedButton((cx - 130, tmy + 25, 80, 36), "", self._font_btn)
        self._timer_enabled = False
        self._timer_secs    = 180
        self._timer_dec = RoundedButton((cx - 30, tmy + 25, 40, 36), "−", self._font_val)
        self._timer_inc = RoundedButton((cx + 80, tmy + 25, 40, 36), "+", self._font_val)
        self._tdur_val_y = tmy + 43

        self._btn_back = RoundedButton((20, H - 66, 140, 46), "◀  B A C K", self._font_btn, color=(max(0, P2_COLOR[0]-30), max(0, P2_COLOR[1]-30), max(0, P2_COLOR[2]-30)), hover_color=P2_COLOR)
        self._btn_start = RoundedButton((cx - 110, H - 66, 220, 46), "▶  S T A R T", self._font_btn, color=BTN_COLOR, hover_color=BTN_HOVER, active_color=BTN_ACTIVE)

    def handle_events(self, events):
        for event in events:
            if self._btn_back.handle_event(event): return "MENU", None

            if self._btn_p2_add.handle_event(event): self.is_multi = True
            if self._btn_p2_remove.handle_event(event): self.is_multi = False

            # --- DÙNG DUY NHẤT CỘT TRÁI (MULTI) CHO PLAYER 1 ĐỂ KHÔNG BỊ LỖI ---
            if self._btn_p1_type_multi.handle_event(event):
                self.p_type[1] = "BOT" if self.p_type[1] == "HUMAN" else "HUMAN"

            if self._btn_p1_pick_multi.handle_event(event): self._pick(1)
            if self._btn_p1_default_multi.handle_event(event): self._use_default(1)

            if self.is_multi:
                if self._btn_p2_type.handle_event(event):
                    self.p_type[2] = "BOT" if self.p_type[2] == "HUMAN" else "HUMAN"
                if self._btn_p2_pick.handle_event(event): self._pick(2)
                if self._btn_p2_default.handle_event(event): self._use_default(2)

            for n, btn in self._size_btns.items():
                if btn.handle_event(event): self.selected_size = n

            if self.p_type[1] == "BOT":
                for k, btn in self._p1_diff_btns_multi.items():
                    if btn.handle_event(event): self.ai_diff[1] = k

            if self.is_multi and self.p_type[2] == "BOT":
                for k, btn in self._p2_diff_btns.items():
                    if btn.handle_event(event): self.ai_diff[2] = k

            if self.is_multi:
                if self._score_dec.handle_event(event): self.selected_score = max(1, self.selected_score - 1)
                if self._score_inc.handle_event(event): self.selected_score = min(10, self.selected_score + 1)

            if self._timer_toggle.handle_event(event): self._timer_enabled = not self._timer_enabled
            if self._timer_dec.handle_event(event): self._timer_secs = max(30, self._timer_secs - 30)
            if self._timer_inc.handle_event(event): self._timer_secs = min(600, self._timer_secs + 30)

            if self._btn_start.handle_event(event):
                data = {
                    "size":          self.selected_size,
                    "time":          self._timer_secs if self._timer_enabled else 0,
                    "score":         self.selected_score,
                    "multiplayer":   self.is_multi,
                    "image":         self._full_image[1],
                    "image_p2":      self._full_image[2],
                    "p1_type":       self.p_type[1],
                    "p2_type":       self.p_type[2] if self.is_multi else "HUMAN",
                    "p1_diff":       self.ai_diff[1],
                    "p2_diff":       self.ai_diff[2],
                    "difficulty":    self.ai_diff[1]
                }
                return "PLAYING", data

        return "SETUP_MULTI" if self.is_multi else "SETUP_SINGLE", None

    def render(self) -> None:
        W, H  = self.screen.get_size()
        mouse = pygame.mouse.get_pos()
        cx    = W // 2

        self._bg.draw(self.screen)
        t = self._font_h1.render("G A M E   S E T U P", True, TEXT_COLOR)
        self.screen.blit(t, t.get_rect(center=(cx, 35)))

        # --- FIX: LUÔN GỌI HÀM NÀY ĐỂ HIỂN THỊ 2 CỘT (VÀ NÚT DẤU CỘNG) ---
        self._draw_multi_columns(W, cx, mouse)

        pygame.draw.line(self.screen, (55, 55, 90), (40, 460), (W - 40, 460), 1)

        self._label("BOARD SIZE", cx, self._size_label_y)
        for size_n, btn in self._size_btns.items():
            btn.color = (50, 140, 70) if size_n == self.selected_size else (55, 55, 100)
            btn.hover_color = tuple(min(c + 25, 255) for c in btn.color)
            btn.draw(self.screen, mouse)

        if self.is_multi:
            self._label("SCORE LIMIT", cx, self._score_label_y)
            self._score_dec.draw(self.screen, mouse)
            val = self._font_val.render(str(self.selected_score), True, ACCENT)
            self.screen.blit(val, val.get_rect(center=(cx, self._score_val_y)))
            self._score_inc.draw(self.screen, mouse)

        self._label("MATCH TIMER", cx, self._timer_label_y)
        self._timer_toggle.text = "ON" if self._timer_enabled else "OFF"
        self._timer_toggle.color = (45, 130, 55) if self._timer_enabled else (130, 50, 50)
        self._timer_toggle.hover_color = (65, 160, 75) if self._timer_enabled else (160, 70, 70)
        self._timer_toggle.draw(self.screen, mouse)

        self._timer_dec.draw(self.screen, mouse)
        m, s = divmod(self._timer_secs, 60)
        t_text = self._font_val.render(f"{m:02d}:{s:02d}", True, ACCENT if self._timer_enabled else MUTED_TEXT)
        self.screen.blit(t_text, t_text.get_rect(center=(cx + 25, self._tdur_val_y)))
        self._timer_inc.draw(self.screen, mouse)

        self._btn_back.draw(self.screen, mouse)
        self._btn_start.draw(self.screen, mouse)

    def _draw_multi_columns(self, W, cx, mouse):
        pygame.draw.line(self.screen, (55, 55, 90), (cx, 55), (cx, 450), 1)
        self._draw_player_col(1, W//4, P1_COLOR, self._prev_rect_multi[1], self._btn_p1_type_multi, self._btn_p1_pick_multi, self._btn_p1_default_multi, self._p1_diff_btns_multi, mouse)
        self._draw_p2_column(W, cx, mouse)

    def _draw_p2_column(self, W, cx, mouse):
        col_cx = 3 * W // 4
        if not self.is_multi:
            lbl = self._font_h1.render("PLAYER 2", True, MUTED_TEXT)
            self.screen.blit(lbl, lbl.get_rect(center=(col_cx, 70)))
            pr = self._prev_rect_multi[2]
            pygame.draw.rect(self.screen, (210, 210, 210), pr, border_radius=8)
            pygame.draw.rect(self.screen, (170, 170, 170), pr, 2, border_radius=8)
            self._btn_p2_add.rect.center = pr.center
            self._btn_p2_add.draw(self.screen, mouse)
            return

        lbl = self._font_h1.render("PLAYER 2", True, P2_COLOR)
        self.screen.blit(lbl, lbl.get_rect(center=(col_cx, 70)))
        self._btn_p2_remove.rect.centerx = col_cx + _PREVIEW // 2 + 18
        self._btn_p2_remove.rect.centery = 70
        self._btn_p2_remove.draw(self.screen, mouse)
        self._draw_player_col(2, col_cx, P2_COLOR, self._prev_rect_multi[2], self._btn_p2_type, self._btn_p2_pick, self._btn_p2_default, self._p2_diff_btns, mouse)

    def _draw_player_col(self, player, col_cx, color, prev_rect, btn_type, btn_pick, btn_def, diff_btns, mouse):
        if player == 1 or self.is_multi:
            lbl = self._font_h1.render(f"PLAYER {player}", True, color)
            self.screen.blit(lbl, lbl.get_rect(center=(col_cx, 70)))

        if self._preview[player]:
            self.screen.blit(self._preview[player], prev_rect.topleft)
        else:
            pygame.draw.rect(self.screen, PANEL_BG, prev_rect, border_radius=4)
            hint = self._font_h2.render("default tiles", True, MUTED_TEXT)
            self.screen.blit(hint, hint.get_rect(center=prev_rect.center))
        pygame.draw.rect(self.screen, (70, 70, 110), prev_rect, 2, border_radius=4)

        ptype = self.p_type[player]
        btn_type.text = "🤖 BOT" if ptype == "BOT" else "👤 HUMAN"
        btn_type.color = (200, 80, 100) if ptype == "BOT" else (60, 140, 200)
        btn_type.hover_color = tuple(min(c+20, 255) for c in btn_type.color)
        btn_type.draw(self.screen, mouse)

        if ptype == "BOT":
            for k, btn in diff_btns.items():
                btn.color = (180, 80, 80) if k == self.ai_diff[player] else (55, 55, 100)
                btn.hover_color = tuple(min(c+25, 255) for c in btn.color)
                btn.draw(self.screen, mouse)

        btn_pick.draw(self.screen, mouse)
        btn_def.draw(self.screen, mouse)

    # --- CÁC HÀM TIỆN ÍCH KHÔNG ĐƯỢC PHÉP THIẾU ---
    def _label(self, text: str, cx: int, y: int) -> None:
        surf = self._font_h2.render(text, True, MUTED_TEXT)
        self.screen.blit(surf, surf.get_rect(center=(cx, y)))

    def _pick(self, player: int) -> None:
        self._error[player] = ""
        path = open_file_dialog()
        if not path: return
        try:
            crop_ui = CropImageMenu(self.screen, path, config.BOARD_SIZE)
            cropped = crop_ui.run()
            if cropped:
                self._full_image[player]  = cropped
                self._image_mode[player]  = "CUSTOM"
                self._preview[player] = pygame.transform.smoothscale(cropped, (_PREVIEW, _PREVIEW))
        except Exception as exc:
            self._error[player] = f"Could not load: {exc}"

    def _use_default(self, player: int) -> None:
        self._error[player] = ""
        self._full_image[player] = None
        self._image_mode[player] = "DEFAULT"
        self._preview[player] = None

class SetupMultiScreen(SetupSingleScreen):
    def __init__(self, screen):
        super().__init__(screen, start_as_multi=True)