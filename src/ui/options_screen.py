import pygame
from src.ui.components import RoundedButton
from src.ui.background import ModernBackground
from configs.game_config import (
    TEXT_COLOR, MUTED_TEXT, ACCENT,
    BTN_COLOR, BTN_HOVER, BTN_ACTIVE,
    P1_COLOR, P2_COLOR, WIN_COLOR,
    update_configs # Thật ra không cần gọi nếu fixed
)
from src.core.settings_manager import SettingsManager

class OptionsScreen:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.settings_mgr = SettingsManager()

        # Load local state from settings config
        self.music_volume = self.settings_mgr.get("music_volume")
        self.move_volume = self.settings_mgr.get("move_volume")

        self._font_h1 = pygame.font.SysFont("Georgia", 42, bold=True)
        self._font_h2 = pygame.font.SysFont("Georgia", 20)
        self._font_val = pygame.font.SysFont("Georgia", 28, bold=True)
        self._font_btn = pygame.font.SysFont("Georgia", 19, bold=True)

        # Common layout sizes
        self.btn_w, self.btn_h = 46, 46
        self.wide_btn_w = 160

        self._bg = ModernBackground(*self.screen.get_size())
        self._build_buttons()

    def _build_buttons(self):
        W, H = self.screen.get_size()
        cx = W // 2

        # ── Center Column (Sound) ────────────────────────────────────────────────
        # Music Volume
        self._vol_dec = RoundedButton((cx - 90, 260, self.btn_w, self.btn_h), "-", self._font_val,
                                      color=(BTN_COLOR[0]-20, BTN_COLOR[1]-20, BTN_COLOR[2]-20), hover_color=BTN_COLOR)
        self._vol_inc = RoundedButton((cx + 44, 260, self.btn_w, self.btn_h), "+", self._font_val,
                                      color=(BTN_COLOR[0]-20, BTN_COLOR[1]-20, BTN_COLOR[2]-20), hover_color=BTN_COLOR)

        # Move Sound Volume
        self._move_dec = RoundedButton((cx - 90, 420, self.btn_w, self.btn_h), "-", self._font_val,
                                       color=(BTN_COLOR[0]-20, BTN_COLOR[1]-20, BTN_COLOR[2]-20), hover_color=BTN_COLOR)
        self._move_inc = RoundedButton((cx + 44, 420, self.btn_w, self.btn_h), "+", self._font_val,
                                       color=(BTN_COLOR[0]-20, BTN_COLOR[1]-20, BTN_COLOR[2]-20), hover_color=BTN_COLOR)

        # ── Bottom (Control) ────────────────────────────────────────────────
        self._btn_back = RoundedButton(
            (cx - 200, H - 120, 180, 52), "B A C K", self._font_btn,
            color=(max(0, P2_COLOR[0]-30), max(0, P2_COLOR[1]-30), max(0, P2_COLOR[2]-30)),
            hover_color=P2_COLOR
        )

        self._btn_apply = RoundedButton(
            (cx + 20, H - 120, 180, 52), "A P P L Y", self._font_btn,
            color=(max(0, WIN_COLOR[0]-30), max(0, WIN_COLOR[1]-30), max(0, WIN_COLOR[2]-30)),
            hover_color=WIN_COLOR
        )

    def _apply_changes(self):
        self.settings_mgr.update({
            "music_volume": self.music_volume,
            "move_volume": self.move_volume
        })
        self._bg = ModernBackground(*self.screen.get_size())

    def handle_events(self, events):
        for event in events:
            # Sound Controls
            if self._vol_dec.handle_event(event):
                self.music_volume = max(0, self.music_volume - 10)
            if self._vol_inc.handle_event(event):
                self.music_volume = min(100, self.music_volume + 10)

            if self._move_dec.handle_event(event):
                self.move_volume = max(0, self.move_volume - 10)
            if self._move_inc.handle_event(event):
                self.move_volume = min(100, self.move_volume + 10)

            # Actions
            if self._btn_apply.handle_event(event):
                self._apply_changes()
                return "MENU", None

            if self._btn_back.handle_event(event):
                return "MENU", None

        return "OPTIONS", None

    def render(self) -> None:
        W, H = self.screen.get_size()
        mouse = pygame.mouse.get_pos()
        self._bg.draw(self.screen)

        cx = W // 2

        # Title
        title = self._font_h1.render("O P T I O N S", True, TEXT_COLOR)
        self.screen.blit(title, title.get_rect(center=(W // 2, 80)))

        # ── Draw Center Column (Sound)
        self._label("SOUND", cx, 180, bold=True)
        self._label("MUSIC VOLUME", cx, 232)
        self._vol_dec.draw(self.screen, mouse)
        vol_text = self._font_val.render(f"{self.music_volume}%", True, TEXT_COLOR)
        self.screen.blit(vol_text, vol_text.get_rect(center=(cx, 283)))
        self._vol_inc.draw(self.screen, mouse)
        self._draw_bar(cx, 316, self.music_volume, color=BTN_COLOR)

        self._label("MOVE SOUND VOLUME", cx, 392)
        self._move_dec.draw(self.screen, mouse)
        move_text = self._font_val.render(f"{self.move_volume}%", True, TEXT_COLOR)
        self.screen.blit(move_text, move_text.get_rect(center=(cx, 443)))
        self._move_inc.draw(self.screen, mouse)
        self._draw_bar(cx, 476, self.move_volume, color=BTN_COLOR)

        # Bottom Buttons
        self._btn_back.draw(self.screen, mouse)
        self._btn_apply.draw(self.screen, mouse)

    def _label(self, text: str, cx: int, y: int, bold=False) -> None:
        font = self._font_h2 if not bold else self._font_val
        color = MUTED_TEXT if not bold else TEXT_COLOR
        surf = font.render(text, True, color)
        self.screen.blit(surf, surf.get_rect(center=(cx, y)))

    def _draw_bar(self, cx: int, y: int, value: int, color=None) -> None:
        bar_w = 260
        bar_h = 12
        bar_x = cx - bar_w // 2
        fill_w = int(bar_w * value / 100)
        pygame.draw.rect(self.screen, (220, 215, 210), (bar_x, y, bar_w, bar_h), border_radius=6)
        if fill_w > 0:
            fill_color = color if color else ACCENT
            pygame.draw.rect(self.screen, fill_color, (bar_x, y, fill_w, bar_h), border_radius=4)
            tip_x = bar_x + fill_w - 4
            pygame.draw.rect(self.screen, (255, 255, 255), (tip_x, y, 4, bar_h), border_radius=2)
