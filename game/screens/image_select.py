"""
Game setup screen for choosing player images and match options.
"""

import pygame

from game.constants import (
    ACCENT,
    BOARD_SIZE,
    BTN_ACTIVE,
    BTN_COLOR,
    BTN_HOVER,
    DIFFICULTY_GRID,
    MUTED_TEXT,
    P1_COLOR,
    P2_COLOR,
    PANEL_BG,
    TEXT_COLOR,
)
from game.puzzle.image_processor import (
    build_full_preview,
    load_and_slice,
    make_default_tiles,
    pick_image_file,
)
from game.screens.background import ModernBackground
from game.ui.button import Button
from game.ui.wood_frame import (
    PARCHMENT,
    WOOD_DARK,
    draw_status_badge,
    draw_wood_frame,
    draw_wood_panel,
    draw_wood_plaque,
)

_PREVIEW = 180


class ImageSelectScreen:
    _DIFF_ACTIVE = {
        "Easy": (94, 148, 87),
        "Medium": (79, 116, 163),
        "Hard": (148, 88, 72),
    }

    def __init__(self, screen: pygame.Surface, options: dict):
        self.screen = screen
        self.options = options
        W, H = screen.get_size()

        self._font_title = pygame.font.SysFont("Georgia", 34, bold=True)
        self._font_card = pygame.font.SysFont("Georgia", 26, bold=True)
        self._font_label = pygame.font.SysFont("Georgia", 18, bold=True)
        self._font_body = pygame.font.SysFont("Georgia", 18)
        self._font_btn = pygame.font.SysFont("Georgia", 17, bold=True)
        self._font_val = pygame.font.SysFont("Georgia", 24, bold=True)
        self._font_tiny = pygame.font.SysFont("Georgia", 14)

        self._bg = ModernBackground(W, H, "Gemini_Generated_Image_z7r4hsz7r4hsz7r4.png")
        self._rebuild_tiles_state()
        self._build_layout()

    def _build_layout(self) -> None:
        W, H = self.screen.get_size()
        cx = W // 2

        card_w = 314
        card_h = 438
        card_y = 96
        left_x = 86
        right_x = W - left_x - card_w
        single_x = cx - card_w // 2

        self._player_cards_multi = {
            1: pygame.Rect(left_x, card_y, card_w, card_h),
            2: pygame.Rect(right_x, card_y, card_w, card_h),
        }
        self._player_cards_single = {
            1: pygame.Rect(single_x, card_y, card_w, card_h),
        }

        preview_y = card_y + 74
        self._preview_rect_multi = {
            1: pygame.Rect(left_x + (card_w - _PREVIEW) // 2, preview_y, _PREVIEW, _PREVIEW),
            2: pygame.Rect(right_x + (card_w - _PREVIEW) // 2, preview_y, _PREVIEW, _PREVIEW),
        }
        self._preview_rect_single = {
            1: pygame.Rect(single_x + (card_w - _PREVIEW) // 2, preview_y, _PREVIEW, _PREVIEW),
        }

        settings_y = card_y + card_h + 16
        self._settings_panel = pygame.Rect(170, settings_y, W - 340, 254)

        footer = pygame.Rect(42, H - 94, W - 84, 70)

        self._btn_back = Button(
            (footer.x + 22, footer.y + 15, 152, 40),
            "BACK",
            self._font_btn,
            color=(130, 91, 72),
            hover_color=(153, 108, 86),
            active_color=(98, 66, 52),
            border_radius=24,
        )
        self._btn_start = Button(
            (footer.right - 22 - 196, footer.y + 15, 196, 40),
            "START MATCH",
            self._font_btn,
            color=BTN_COLOR,
            hover_color=BTN_HOVER,
            active_color=BTN_ACTIVE,
            border_radius=24,
        )

        self._build_player_buttons()
        self._build_settings_controls()

    def _build_player_buttons(self) -> None:
        self._btn_pick = {}
        self._btn_default = {}

        for cards in (self._player_cards_multi, self._player_cards_single):
            for player, card in cards.items():
                preview = self._preview_rect_multi[player] if cards is self._player_cards_multi else self._preview_rect_single[player]
                badge_y = preview.bottom + 14
                btn_y = badge_y + 44
                btn_x = card.x + 52
                btn_w = card.width - 104
                self._btn_pick[(id(cards), player)] = Button(
                    (btn_x, btn_y, btn_w, 38),
                    "Pick Image",
                    self._font_btn,
                    color=(92, 120, 108) if player == 1 else (147, 102, 95),
                    hover_color=P1_COLOR if player == 1 else P2_COLOR,
                    active_color=(72, 98, 88) if player == 1 else (126, 81, 75),
                    border_radius=19,
                )
                self._btn_default[(id(cards), player)] = Button(
                    (btn_x, btn_y + 46, btn_w, 38),
                    "Use Default Art",
                    self._font_btn,
                    color=BTN_COLOR,
                    hover_color=BTN_HOVER,
                    active_color=BTN_ACTIVE,
                    border_radius=19,
                )

    def _build_settings_controls(self) -> None:
        panel = self._settings_panel
        self._settings_rows = {
            "difficulty": panel.y + 84,
            "score": panel.y + 126,
            "timer_toggle": panel.y + 168,
            "timer_value": panel.y + 210,
        }
        self._settings_label_x = panel.x + 70
        control_center_x = panel.centerx

        self._diff_btns = {}
        bw, bh = 104, 36
        diff_gap = 14
        diff_total_w = len(DIFFICULTY_GRID) * bw + (len(DIFFICULTY_GRID) - 1) * diff_gap
        diff_x = control_center_x - diff_total_w // 2
        for i, name in enumerate(DIFFICULTY_GRID):
            self._diff_btns[name] = Button(
                (diff_x + i * (bw + diff_gap), self._settings_rows["difficulty"] - bh // 2, bw, bh),
                name,
                self._font_btn,
                color=(79, 84, 112),
                hover_color=(101, 108, 140),
                active_color=(58, 63, 90),
                border_radius=18,
            )

        stepper_gap = 132
        stepper_left = control_center_x - (stepper_gap + 42) // 2
        self._score_dec = Button(
            (stepper_left, self._settings_rows["score"] - 21, 42, 42),
            "-",
            self._font_val,
            border_radius=21,
        )
        self._score_inc = Button(
            (stepper_left + stepper_gap, self._settings_rows["score"] - 21, 42, 42),
            "+",
            self._font_val,
            border_radius=21,
        )
        toggle_w = 148
        self._timer_toggle = Button(
            (control_center_x - toggle_w // 2, self._settings_rows["timer_toggle"] - 18, toggle_w, 36),
            "",
            self._font_btn,
            border_radius=19,
        )
        self._timer_dec = Button(
            (stepper_left, self._settings_rows["timer_value"] - 21, 42, 42),
            "-",
            self._font_val,
            border_radius=21,
        )
        self._timer_inc = Button(
            (stepper_left + stepper_gap, self._settings_rows["timer_value"] - 21, 42, 42),
            "+",
            self._font_val,
            border_radius=21,
        )

    def handle_event(self, event):
        if self._btn_back.handle_event(event):
            return "back"

        is_multi = self.options.get("multiplayer", True)
        card_key = id(self._player_cards_multi if is_multi else self._player_cards_single)

        if self._btn_pick[(card_key, 1)].handle_event(event):
            self._pick(1)
        if self._btn_default[(card_key, 1)].handle_event(event):
            self._use_default(1)

        if is_multi:
            if self._btn_pick[(card_key, 2)].handle_event(event):
                self._pick(2)
            if self._btn_default[(card_key, 2)].handle_event(event):
                self._use_default(2)

        for name, btn in self._diff_btns.items():
            if btn.handle_event(event) and self.options["difficulty"] != name:
                self.options["difficulty"] = name
                self._on_difficulty_change()

        if self._score_dec.handle_event(event):
            self.options["score_limit"] = max(1, self.options["score_limit"] - 1)
        if self._score_inc.handle_event(event):
            self.options["score_limit"] = min(10, self.options["score_limit"] + 1)

        if self._timer_toggle.handle_event(event):
            self.options["timer_enabled"] = not self.options["timer_enabled"]
        if self._timer_dec.handle_event(event):
            self.options["timer_secs"] = max(30, self.options["timer_secs"] - 30)
        if self._timer_inc.handle_event(event):
            self.options["timer_secs"] = min(600, self.options["timer_secs"] + 30)

        p1_ready = self._ready[1]
        p2_ready = self._ready[2] if is_multi else True
        if p1_ready and p2_ready and self._btn_start.handle_event(event):
            return ("start", self._tiles[1], self._tiles[2])
        return None

    def draw(self) -> None:
        W, H = self.screen.get_size()
        cx = W // 2
        mouse = pygame.mouse.get_pos()
        is_multi = self.options.get("multiplayer", True)

        self._bg.draw(self.screen)

        title_plaque = pygame.Rect(cx - 220, 18, 440, 52)
        draw_wood_plaque(self.screen, title_plaque, radius=20)
        title = self._font_title.render("GAME SETUP", True, PARCHMENT)
        self.screen.blit(title, title.get_rect(center=title_plaque.center))

        subtitle = self._font_body.render(
            "Choose artwork, then tune the match settings before starting.",
            True,
            TEXT_COLOR,
        )
        self.screen.blit(subtitle, subtitle.get_rect(center=(cx, 84)))

        if is_multi:
            for player in (1, 2):
                self._draw_player_card(player, self._player_cards_multi[player], self._preview_rect_multi[player], mouse)
        else:
            self._draw_player_card(1, self._player_cards_single[1], self._preview_rect_single[1], mouse)

        self._draw_settings(mouse)
        self._draw_footer(mouse, is_multi, W, H)

    def _draw_player_card(self, player: int, card_rect: pygame.Rect, preview_rect: pygame.Rect, mouse) -> None:
        is_multi = self.options.get("multiplayer", True)
        key = id(self._player_cards_multi if is_multi else self._player_cards_single)
        btn_pick = self._btn_pick[(key, player)]
        btn_default = self._btn_default[(key, player)]

        draw_wood_panel(self.screen, card_rect, radius=24, inset=16)

        plaque = pygame.Rect(card_rect.x + 48, card_rect.y + 18, card_rect.width - 96, 42)
        draw_wood_plaque(self.screen, plaque, radius=18)
        lbl = self._font_card.render(f"PLAYER {player}", True, PARCHMENT)
        self.screen.blit(lbl, lbl.get_rect(center=plaque.center))

        draw_wood_frame(self.screen, preview_rect, padding=7, frame_width=10, radius=10)
        if self._preview[player]:
            self.screen.blit(self._preview[player], preview_rect.topleft)
        else:
            pygame.draw.rect(self.screen, PANEL_BG, preview_rect, border_radius=10)
            hint = self._font_body.render("No image selected", True, MUTED_TEXT)
            self.screen.blit(hint, hint.get_rect(center=preview_rect.center))

        badge = pygame.Rect(card_rect.centerx - 66, preview_rect.bottom + 14, 132, 30)
        if self._ready[player]:
            draw_status_badge(self.screen, badge, fill=(90, 151, 96), border=(58, 107, 62))
            st = self._font_tiny.render("READY", True, (245, 255, 245))
        else:
            draw_status_badge(self.screen, badge, fill=(148, 128, 93), border=(112, 88, 56))
            st = self._font_tiny.render("WAITING", True, (255, 248, 235))
        self.screen.blit(st, st.get_rect(center=badge.center))

        btn_pick.draw(self.screen, mouse)
        btn_default.draw(self.screen, mouse)

        if self._error[player]:
            msg = self._truncate(self._error[player], 38)
            err = self._font_tiny.render(msg, True, (178, 72, 58))
            self.screen.blit(err, err.get_rect(center=(card_rect.centerx, card_rect.bottom - 18)))

    def _draw_settings(self, mouse) -> None:
        panel = self._settings_panel
        draw_wood_panel(self.screen, panel, radius=28, inset=18)

        plaque = pygame.Rect(panel.centerx - 156, panel.y + 16, 312, 42)
        draw_wood_plaque(self.screen, plaque, radius=18)
        title = self._font_card.render("MATCH SETTINGS", True, PARCHMENT)
        self.screen.blit(title, title.get_rect(center=plaque.center))

        rows = [
            ("Difficulty", self._settings_rows["difficulty"]),
            ("Score to win", self._settings_rows["score"]),
            ("Round timer", self._settings_rows["timer_toggle"]),
            ("Time per round", self._settings_rows["timer_value"]),
        ]
        for label, y in rows:
            surf = self._font_label.render(label, True, WOOD_DARK)
            self.screen.blit(surf, surf.get_rect(x=self._settings_label_x, centery=y))

        for name, btn in self._diff_btns.items():
            active = self.options["difficulty"] == name
            btn.color = self._DIFF_ACTIVE[name] if active else (79, 84, 112)
            btn.hover_color = tuple(min(255, c + 20) for c in btn.color)
            btn.active_color = tuple(max(0, c - 22) for c in btn.color)
            btn.draw(self.screen, mouse)

        self._score_dec.draw(self.screen, mouse)
        self._score_inc.draw(self.screen, mouse)
        score_val = self._font_val.render(str(self.options["score_limit"]), True, ACCENT)
        self.screen.blit(score_val, score_val.get_rect(center=(self._score_dec.rect.centerx + 62, self._score_dec.rect.centery)))

        enabled = self.options["timer_enabled"]
        self._timer_toggle.text = "Enabled" if enabled else "Disabled"
        self._timer_toggle.color = (92, 148, 96) if enabled else (137, 94, 84)
        self._timer_toggle.hover_color = (114, 172, 118) if enabled else (159, 111, 100)
        self._timer_toggle.active_color = (70, 118, 76) if enabled else (112, 73, 66)
        self._timer_toggle.draw(self.screen, mouse)

        self._timer_dec.draw(self.screen, mouse)
        self._timer_inc.draw(self.screen, mouse)
        m, s = divmod(self.options["timer_secs"], 60)
        timer_val = self._font_val.render(f"{m:02d}:{s:02d}", True, ACCENT)
        self.screen.blit(timer_val, timer_val.get_rect(center=(self._timer_dec.rect.centerx + 62, self._timer_dec.rect.centery)))

        n = DIFFICULTY_GRID[self.options["difficulty"]]
        note = self._font_tiny.render(
            f"Board size: {n}x{n} ({n*n-1} movable tiles)",
            True,
            MUTED_TEXT,
        )
        self.screen.blit(note, note.get_rect(right=panel.right - 46, bottom=panel.bottom - 22))

    def _draw_footer(self, mouse, is_multi: bool, W: int, H: int) -> None:
        footer = pygame.Rect(42, H - 94, W - 84, 70)
        draw_wood_panel(self.screen, footer, radius=24, inset=12)

        self._btn_back.draw(self.screen, mouse)

        p1_ready = self._ready[1]
        p2_ready = self._ready[2] if is_multi else True
        if p1_ready and p2_ready:
            self._btn_start.draw(self.screen, mouse)
            hint = "Both boards are ready. Start the match."
        else:
            hint = "Choose images or use default art before starting."

        hint_surf = self._font_body.render(hint, True, TEXT_COLOR)
        self.screen.blit(hint_surf, hint_surf.get_rect(center=(W // 2, H - 59)))

    def _rebuild_tiles_state(self) -> None:
        n = DIFFICULTY_GRID[self.options["difficulty"]]
        self._n = n
        self._tsz = BOARD_SIZE // n
        self._tiles = {1: None, 2: None}
        self._preview = {1: None, 2: None}
        self._ready = {1: False, 2: False}
        self._error = {1: "", 2: ""}

    def _on_difficulty_change(self) -> None:
        self._rebuild_tiles_state()
        self._build_layout()

    def _pick(self, player: int) -> None:
        self._error[player] = ""
        path = pick_image_file()
        if not path:
            return
        try:
            tiles = load_and_slice(path, self._n, self._tsz)
            self._tiles[player] = tiles
            self._preview[player] = build_full_preview(tiles, self._n, self._tsz, _PREVIEW)
            self._ready[player] = True
        except Exception:
            self._error[player] = "Could not load that image."

    def _use_default(self, player: int) -> None:
        self._error[player] = ""
        tiles = make_default_tiles(self._n, self._tsz)
        self._tiles[player] = tiles
        self._preview[player] = build_full_preview(tiles, self._n, self._tsz, _PREVIEW)
        self._ready[player] = True

    @staticmethod
    def _truncate(text: str, limit: int) -> str:
        if len(text) <= limit:
            return text
        return text[: limit - 3] + "..."
