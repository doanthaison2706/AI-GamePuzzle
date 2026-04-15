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
_DIFFS = {"easy": "EASY", "medium": "MEDIUM", "hard": "HARD"}
_LAYOUT_DESIGN_HEIGHT = 972

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

        self.global_image   = None
        self.global_preview = None
        self._error         = ""

        self._bg = ModernBackground(W, H)
        self._layout_scale = 1.0
        self._title_y = 60
        self._line1_y = 360
        self._line2_y = 580
        self._player_row_y = 400

        def _mk(rect, text, color, hcolor):
            return RoundedButton(rect, text, self._font_btn, color=color, hover_color=hcolor)
        dim = lambda c: tuple(max(0, v - 20) for v in c)

        # --- 1. KHU VỰC CHỌN ẢNH (CĂN GIỮA TRÊN CÙNG) ---
        self._prev_rect = pygame.Rect(0, 0, _PREVIEW, _PREVIEW)
        self._prev_rect.centerx = cx
        # Đẩy khung ảnh xuống (Từ 70 -> 100)
        self._prev_rect.top = 100

        btn_w = 220
        # Đẩy nút chọn ảnh xuống (Từ 265 -> 295)
        self._btn_pick_img = _mk((cx - btn_w - 15, 295, btn_w, 46), "PICK IMAGE", dim(P1_COLOR), P1_COLOR)
        self._btn_def_img  = _mk((cx + 15, 295, btn_w, 46), "USE DEFAULT", BTN_COLOR, BTN_HOVER)

        # --- 2. KHU VỰC THIẾT LẬP NGƯỜI CHƠI (CHIA 2 CỘT) ---
        p1_cx = W // 4
        p2_cx = 3 * W // 4
        # Đẩy khu vực người chơi xuống (Từ 360 -> 400)
        p_row_y = 400

        self._btn_p1_type = _mk((p1_cx - 80, p_row_y + 35, 160, 42), "HUMAN", (60, 140, 200), (80, 160, 220))
        self._btn_p2_type = _mk((p2_cx - 80, p_row_y + 35, 160, 42), "HUMAN", (60, 140, 200), (80, 160, 220))

        def _make_diff_btns(center_x, y_pos):
            btns = {}

            bw = 70
            bx = center_x - (3 * bw + 16) // 2
            for i, (k, lbl) in enumerate(_DIFFS.items()):
                btns[k] = RoundedButton((bx + i*(bw+8), y_pos, bw, 38), lbl, self._font_btn, color=(55, 55, 100), hover_color=(75, 75, 140))
            return btns

        self._p1_diff_btns = _make_diff_btns(p1_cx, p_row_y + 85)
        self._p2_diff_btns = _make_diff_btns(p2_cx, p_row_y + 85)

        self._btn_p2_add = RoundedButton((p2_cx - 40, p_row_y + 20, 80, 80), "+", pygame.font.SysFont("Georgia", 40, bold=True), color=(45, 130, 55), hover_color=(65, 160, 75))
        self._btn_p2_remove = RoundedButton((p2_cx + 105, p_row_y - 18, 36, 36), "-", pygame.font.SysFont("Georgia", 24, bold=True), color=(200, 60, 60), hover_color=(230, 80, 80))

        # --- 3. KHU VỰC LUẬT CHƠI (CĂN GIỮA BÊN DƯỚI) ---
        # Đẩy 3 block luật chơi xuống đều nhau
        sy = 600  # Board Size
        sly = 685 # Score Limit
        tmy = 770 # Match Timer

        self._size_btns: dict[int, RoundedButton] = {}
        sizes = list(_SIZES.keys())
        for i, n in enumerate(sizes):
            x = cx - (len(sizes) * 125 // 2) + i * 125
            self._size_btns[n] = RoundedButton((x, sy + 30, 110, 42), _SIZES[n], self._font_btn, color=(55, 55, 100), hover_color=(75, 75, 140))
        self._size_label_y = sy

        self._score_label_y = sly
        self._score_dec = RoundedButton((cx - 80, sly + 30, 46, 42), "-", self._font_val)
        self._score_inc = RoundedButton((cx + 34, sly + 30, 46, 42), "+", self._font_val)
        self._score_val_y = sly + 50

        self._timer_label_y = tmy
        self._timer_toggle  = RoundedButton((cx - 140, tmy + 30, 80, 42), "", self._font_btn)
        self._timer_enabled = False
        self._timer_secs    = 180
        self._timer_dec = RoundedButton((cx - 40, tmy + 30, 46, 42), "-", self._font_val)
        self._timer_inc = RoundedButton((cx + 94, tmy + 30, 46, 42), "+", self._font_val)
        self._tdur_val_x = cx + 46
        self._tdur_val_y = tmy + 50

        self._btn_back = RoundedButton((20, H - 76, 160, 52), "BACK", self._font_btn, color=(max(0, P2_COLOR[0]-30), max(0, P2_COLOR[1]-30), max(0, P2_COLOR[2]-30)), hover_color=P2_COLOR)
        self._btn_start = RoundedButton((cx - 120, H - 76, 240, 52), "START", self._font_btn, color=BTN_COLOR, hover_color=BTN_HOVER, active_color=BTN_ACTIVE)
        self._apply_layout()

    def _scale_y(self, value: int) -> int:
        return int(round(value * self._layout_scale))

    def _apply_layout(self) -> None:
        """Keep the setup layout proportional across machines with different monitor heights."""
        W, H = self.screen.get_size()
        cx = W // 2
        p1_cx = W // 4
        p2_cx = 3 * W // 4

        self._layout_scale = H / _LAYOUT_DESIGN_HEIGHT
        self._title_y = self._scale_y(60)
        self._line1_y = self._scale_y(360)
        self._player_row_y = self._scale_y(400)
        self._line2_y = self._scale_y(580)
        self._size_label_y = self._scale_y(600)
        self._score_label_y = self._scale_y(685)
        self._timer_label_y = self._scale_y(770)
        self._score_val_y = self._scale_y(735)
        self._tdur_val_y = self._scale_y(820)
        self._tdur_val_x = cx + 46

        preview_size = max(128, self._scale_y(_PREVIEW))
        self._prev_rect.size = (preview_size, preview_size)
        self._prev_rect.centerx = cx
        self._prev_rect.top = self._scale_y(100)

        self._btn_pick_img.rect.topleft = (cx - 220 - 15, self._scale_y(295))
        self._btn_def_img.rect.topleft = (cx + 15, self._scale_y(295))

        type_y = self._player_row_y + 35
        diff_y = self._player_row_y + 85
        self._btn_p1_type.rect.topleft = (p1_cx - 80, type_y)
        self._btn_p2_type.rect.topleft = (p2_cx - 80, type_y)

        bw = 70
        bx1 = p1_cx - (3 * bw + 16) // 2
        bx2 = p2_cx - (3 * bw + 16) // 2
        for i, key in enumerate(_DIFFS.keys()):
            self._p1_diff_btns[key].rect.topleft = (bx1 + i * (bw + 8), diff_y)
            self._p2_diff_btns[key].rect.topleft = (bx2 + i * (bw + 8), diff_y)

        self._btn_p2_add.rect.topleft = (p2_cx - 40, self._player_row_y + 20)
        self._btn_p2_remove.rect.topleft = (p2_cx + 105, self._player_row_y - 18)

        for i, n in enumerate(_SIZES.keys()):
            x = cx - (len(_SIZES) * 125 // 2) + i * 125
            self._size_btns[n].rect.topleft = (x, self._size_label_y + 30)

        self._score_dec.rect.topleft = (cx - 80, self._score_label_y + 30)
        self._score_inc.rect.topleft = (cx + 34, self._score_label_y + 30)

        self._timer_toggle.rect.topleft = (cx - 140, self._timer_label_y + 30)
        self._timer_dec.rect.topleft = (cx - 40, self._timer_label_y + 30)
        self._timer_inc.rect.topleft = (cx + 94, self._timer_label_y + 30)

        footer_y = self._scale_y(_LAYOUT_DESIGN_HEIGHT - 76)
        self._btn_back.rect.topleft = (20, footer_y)
        self._btn_start.rect.topleft = (cx - 120, footer_y)

    def handle_events(self, events):
        self._apply_layout()
        for event in events:
            if self._btn_back.handle_event(event): return "MENU", None

            if not self.is_multi and self._btn_p2_add.handle_event(event):
                self.is_multi = True
                self._apply_layout()
            if self.is_multi and self._btn_p2_remove.handle_event(event):
                self.is_multi = False
                self._apply_layout()

            if self._btn_pick_img.handle_event(event): self._pick()
            if self._btn_def_img.handle_event(event): self._use_default()

            if self._btn_p1_type.handle_event(event):
                self.p_type[1] = "BOT" if self.p_type[1] == "HUMAN" else "HUMAN"

            if self.p_type[1] == "BOT":
                for k, btn in self._p1_diff_btns.items():
                    if btn.handle_event(event): self.ai_diff[1] = k

            if self.is_multi:
                if self._btn_p2_type.handle_event(event):
                    self.p_type[2] = "BOT" if self.p_type[2] == "HUMAN" else "HUMAN"
                if self.p_type[2] == "BOT":
                    for k, btn in self._p2_diff_btns.items():
                        if btn.handle_event(event): self.ai_diff[2] = k

            for n, btn in self._size_btns.items():
                if btn.handle_event(event): self.selected_size = n

            if self.is_multi:
                # Trừ 2 đơn vị, thấp nhất là 1
                if self._score_dec.handle_event(event): self.selected_score = max(1, self.selected_score - 2)
                # Cộng 2 đơn vị, cao nhất là 5
                if self._score_inc.handle_event(event): self.selected_score = min(5, self.selected_score + 2)

            if self._timer_toggle.handle_event(event): self._timer_enabled = not self._timer_enabled
            if self._timer_enabled:
                if self._timer_dec.handle_event(event): self._timer_secs = max(30, self._timer_secs - 30)
                if self._timer_inc.handle_event(event): self._timer_secs = min(600, self._timer_secs + 30)

            if self._btn_start.handle_event(event):
                data = {
                    "size":          self.selected_size,
                    "time":          self._timer_secs if self._timer_enabled else 0,
                    "score":         self.selected_score,
                    "multiplayer":   self.is_multi,
                    "image":         self.global_image,
                    "image_p2":      self.global_image,
                    "p1_type":       self.p_type[1],
                    "p2_type":       self.p_type[2] if self.is_multi else "HUMAN",
                    "p1_diff":       self.ai_diff[1],
                    "p2_diff":       self.ai_diff[2],
                    "difficulty":    self.ai_diff[1]
                }
                return "PLAYING", data

        return "SETUP_MULTI" if self.is_multi else "SETUP_SINGLE", None

    def render(self) -> None:
        self._apply_layout()
        W, H  = self.screen.get_size()
        mouse = pygame.mouse.get_pos()
        cx    = W // 2

        self._bg.draw(self.screen)
        t = self._font_h1.render("G A M E   S E T U P", True, TEXT_COLOR)
        self.screen.blit(t, t.get_rect(center=(cx, self._title_y)))

        # --- VẼ KHU VỰC ẢNH DÙNG CHUNG ---
        if self.global_preview:
            self.screen.blit(self.global_preview, self._prev_rect.topleft)
        else:
            pygame.draw.rect(self.screen, PANEL_BG, self._prev_rect, border_radius=8)
            hint = self._font_h2.render("default tiles", True, MUTED_TEXT)
            self.screen.blit(hint, hint.get_rect(center=self._prev_rect.center))
        pygame.draw.rect(self.screen, (70, 70, 110), self._prev_rect, 2, border_radius=8)

        self._btn_pick_img.draw(self.screen, mouse)
        self._btn_def_img.draw(self.screen, mouse)

        # Đẩy đường kẻ 1 xuống (Từ 335 -> 360)
        pygame.draw.line(self.screen, (55, 55, 90), (40, self._line1_y), (W - 40, self._line1_y), 1)

        # --- VẼ KHU VỰC NGƯỜI CHƠI 1 & 2 ---
        self._draw_player_section(1, W//4, P1_COLOR, self._btn_p1_type, self._p1_diff_btns, mouse, self._player_row_y)
        self._draw_player_2_section(3 * W // 4, mouse, self._player_row_y)

        # Đẩy đường kẻ 2 xuống (Từ 465 -> 510)
        pygame.draw.line(self.screen, (55, 55, 90), (40, self._line2_y), (W - 40, self._line2_y), 1)

        # --- VẼ KHU VỰC LUẬT CHƠI ---
        self._label("BOARD SIZE", cx, self._size_label_y)
        for size_n, btn in self._size_btns.items():
            btn.color = (50, 140, 70) if size_n == self.selected_size else (55, 55, 100)
            btn.hover_color = tuple(min(c + 25, 255) for c in btn.color)
            btn.draw(self.screen, mouse)

        if self.is_multi:
            self._label("FORMAT (BEST OF)", cx, self._score_label_y)
            self._score_dec.draw(self.screen, mouse)
            val = self._font_val.render(str(self.selected_score), True, ACCENT)
            self.screen.blit(val, val.get_rect(center=(cx, self._score_val_y)))
            self._score_inc.draw(self.screen, mouse)

        self._label("MATCH TIMER", cx, self._timer_label_y)
        self._timer_toggle.text = "ON" if self._timer_enabled else "OFF"
        self._timer_toggle.color = (45, 130, 55) if self._timer_enabled else (130, 50, 50)
        self._timer_toggle.hover_color = (65, 160, 75) if self._timer_enabled else (160, 70, 70)
        self._timer_toggle.draw(self.screen, mouse)

        btn_base = BTN_COLOR if self._timer_enabled else (40, 40, 40)
        btn_hov = BTN_HOVER if self._timer_enabled else (40, 40, 40)
        self._timer_dec.color = btn_base
        self._timer_dec.hover_color = btn_hov
        self._timer_inc.color = btn_base
        self._timer_inc.hover_color = btn_hov

        self._timer_dec.draw(self.screen, mouse)
        m, s = divmod(self._timer_secs, 60)
        t_text = self._font_val.render(f"{m:02d}:{s:02d}", True, ACCENT if self._timer_enabled else MUTED_TEXT)
        self.screen.blit(t_text, t_text.get_rect(center=(self._tdur_val_x, self._tdur_val_y)))
        self._timer_inc.draw(self.screen, mouse)

        self._btn_back.draw(self.screen, mouse)
        self._btn_start.draw(self.screen, mouse)

    def _draw_player_section(self, player, col_cx, color, btn_type, diff_btns, mouse, y_pos):
        lbl = self._font_h1.render(f"PLAYER {player}", True, color)
        self.screen.blit(lbl, lbl.get_rect(center=(col_cx, y_pos)))

        ptype = self.p_type[player]
        btn_type.text = "BOT" if ptype == "BOT" else "HUMAN"
        btn_type.color = (200, 80, 100) if ptype == "BOT" else (60, 140, 200)
        btn_type.hover_color = tuple(min(c+20, 255) for c in btn_type.color)
        btn_type.draw(self.screen, mouse)

        if ptype == "BOT":
            for k, btn in diff_btns.items():
                btn.color = (180, 80, 80) if k == self.ai_diff[player] else (55, 55, 100)
                btn.hover_color = tuple(min(c+25, 255) for c in btn.color)
                btn.draw(self.screen, mouse)

    def _draw_player_2_section(self, col_cx, mouse, y_pos):
        if not self.is_multi:
            lbl = self._font_h1.render("PLAYER 2", True, MUTED_TEXT)
            self.screen.blit(lbl, lbl.get_rect(center=(col_cx, y_pos)))
            self._btn_p2_add.draw(self.screen, mouse)
            return

        lbl = self._font_h1.render("PLAYER 2", True, P2_COLOR)
        self.screen.blit(lbl, lbl.get_rect(center=(col_cx, y_pos)))
        self._btn_p2_remove.draw(self.screen, mouse)

        self._draw_player_section(2, col_cx, P2_COLOR, self._btn_p2_type, self._p2_diff_btns, mouse, y_pos)

    def _label(self, text: str, cx: int, y: int) -> None:
        surf = self._font_h2.render(text, True, MUTED_TEXT)
        self.screen.blit(surf, surf.get_rect(center=(cx, y)))

    def _pick(self) -> None:
        self._error = ""
        path = open_file_dialog()
        if not path: return
        try:
            crop_ui = CropImageMenu(self.screen, path, config.BOARD_SIZE)
            cropped = crop_ui.run()
            if cropped:
                self.global_image = cropped
                self.global_preview = pygame.transform.smoothscale(cropped, self._prev_rect.size)
        except Exception as exc:
            self._error = f"Could not load: {exc}"

    def _use_default(self) -> None:
        self._error = ""
        self.global_image = None
        self.global_preview = None

class SetupMultiScreen(SetupSingleScreen):
    def __init__(self, screen):
        super().__init__(screen, start_as_multi=True)
