import pygame
from configs import game_config as config


class WinDualScreen:
    """Màn hình thông báo kết quả chế độ 2 người chơi."""

    def __init__(self, screen, result_data: dict):
        self.screen = screen

        self.winner_id = result_data.get("winner_id", 0)
        self.time_str = result_data.get("time", "00:00")
        self.p1_moves = result_data.get("p1_moves", 0)
        self.p2_moves = result_data.get("p2_moves", 0)
        self.score = result_data.get("score", "0 - 0")
        self.size = result_data.get("size", 3)

        # Fonts
        try:
            self.font_title = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", 38)
            self.font_sub = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", 20)
            self.font_stat_lbl = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", 15)
            self.font_stat_val = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", 32)
            self.font_btn = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", 18)
        except Exception:
            self.font_title = pygame.font.SysFont("arial", 36, bold=True)
            self.font_sub = pygame.font.SysFont("arial", 20, bold=True)
            self.font_stat_lbl = pygame.font.SysFont("arial", 15, bold=True)
            self.font_stat_val = pygame.font.SysFont("arial", 30, bold=True)
            self.font_btn = pygame.font.SysFont("arial", 18, bold=True)

        # Background
        try:
            self.bg_img = pygame.image.load("assets/images/bg_win.png").convert()
            self.bg_img = pygame.transform.scale(self.bg_img, screen.get_size())
        except Exception:
            self.bg_img = None

        # Nút
        w = screen.get_width()
        h = screen.get_height()
        btn_w, btn_h = 140, 50
        spacing = 20
        total = btn_w * 2 + spacing
        start_x = (w - total) // 2
        btn_y = h - 100

        self.rect_replay = pygame.Rect(start_x, btn_y, btn_w, btn_h)
        self.rect_menu = pygame.Rect(start_x + btn_w + spacing, btn_y, btn_w, btn_h)

        self.colors = {
            "orange": {"top": (255, 210, 130), "bot": (255, 175, 85), "shad": (220, 140, 60)},
            "purple": {"top": (220, 180, 255), "bot": (190, 140, 240), "shad": (160, 110, 210)},
        }

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.rect_replay.collidepoint(event.pos):
                    return "PLAYING_DUAL", None
                elif self.rect_menu.collidepoint(event.pos):
                    return "MENU", None
        return "WIN_DUAL", None

    def _draw_gradient_btn(self, surface, rect, c_top, c_bot, c_shad):
        shad = pygame.Rect(rect.x, rect.y + 5, rect.width, rect.height)
        pygame.draw.rect(surface, c_shad, shad, border_radius=rect.height // 2)
        grad = pygame.Surface((1, 2), pygame.SRCALPHA)
        grad.set_at((0, 0), c_top)
        grad.set_at((0, 1), c_bot)
        grad = pygame.transform.smoothscale(grad, (rect.width, rect.height))
        mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=rect.height // 2)
        grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(grad, rect.topleft)
        pygame.draw.rect(surface, (255, 255, 255), rect, border_radius=rect.height // 2, width=2)

    def _draw_pill_button(self, surface, rect, text, theme):
        self._draw_gradient_btn(surface, rect, theme["top"], theme["bot"], theme["shad"])
        txt = self.font_btn.render(text, True, (255, 255, 255))
        surface.blit(txt, txt.get_rect(center=rect.center))

    def _draw_stat_box(self, cx, y, label, value):
        box_w, box_h = 145, 100
        rect = pygame.Rect(cx - box_w // 2, y, box_w, box_h)
        pygame.draw.rect(self.screen, (255, 252, 248), rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 210, 210), rect, border_radius=15, width=2)
        lbl = self.font_stat_lbl.render(label, True, (160, 110, 130))
        self.screen.blit(lbl, lbl.get_rect(centerx=cx, top=rect.y + 12))
        val = self.font_stat_val.render(str(value), True, (230, 100, 100))
        self.screen.blit(val, val.get_rect(centerx=cx, bottom=rect.bottom - 10))

    def render(self):
        w, h = self.screen.get_size()
        cx = w // 2

        if self.bg_img:
            self.screen.blit(self.bg_img, (0, 0))
        else:
            self.screen.fill((255, 240, 235))

        # Tiêu đề
        if self.winner_id:
            title_text = f"NGƯỜI CHƠI {self.winner_id} THẮNG!"
        else:
            title_text = "HÒA!"
        title = self.font_title.render(title_text, True, (240, 100, 120))
        self.screen.blit(title, title.get_rect(centerx=cx, top=40))

        sub = self.font_sub.render(f"Tỉ số tổng: {self.score}", True, (80, 160, 140))
        self.screen.blit(sub, sub.get_rect(centerx=cx, top=95))

        # Panel thống kê
        panel_w, panel_h = 500, 140
        panel_rect = pygame.Rect(cx - panel_w // 2, 145, panel_w, panel_h)
        pygame.draw.rect(self.screen, (245, 215, 215), (panel_rect.x, panel_rect.y + 8, panel_w, panel_h), border_radius=25)
        pygame.draw.rect(self.screen, (255, 245, 235), panel_rect, border_radius=25)
        pygame.draw.rect(self.screen, (255, 200, 200), panel_rect, border_radius=25, width=3)

        spacing = 160
        self._draw_stat_box(cx - spacing, panel_rect.y + 20, "THỜI GIAN", self.time_str)
        self._draw_stat_box(cx, panel_rect.y + 20, "P1 BƯỚC", self.p1_moves)
        self._draw_stat_box(cx + spacing, panel_rect.y + 20, "P2 BƯỚC", self.p2_moves)

        # Nút
        self._draw_pill_button(self.screen, self.rect_replay, "TRẬN MỚI", self.colors["orange"])
        self._draw_pill_button(self.screen, self.rect_menu, "THOÁT", self.colors["purple"])
