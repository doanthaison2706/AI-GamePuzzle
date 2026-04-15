import pygame
from configs import game_config as config
from src.ui.components import PillButton

class WinDualScreen:
    """Màn hình thông báo kết quả chế độ 2 người chơi (Có Lịch Sử Bảng Điểm)."""

    def __init__(self, screen, result_data: dict):
        self.screen = screen

        self.winner_id = result_data.get("winner_id", 0)
        self.score = result_data.get("score", "0 - 0")
        self.history = result_data.get("history", []) # Nhận danh sách lịch sử

        # Fonts
        try:
            self.font_title = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", 38)
            self.font_sub = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", 20)
            self.font_table_hdr = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", 15)
            self.font_table_row = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", 18)
            self.font_btn = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", 18)
        except Exception:
            self.font_title = pygame.font.SysFont("arial", 36, bold=True)
            self.font_sub = pygame.font.SysFont("arial", 20, bold=True)
            self.font_table_hdr = pygame.font.SysFont("arial", 14, bold=True)
            self.font_table_row = pygame.font.SysFont("arial", 16, bold=True)
            self.font_btn = pygame.font.SysFont("arial", 18, bold=True)

        # Background
        try:
            self.bg_img = pygame.image.load("assets/images/bg_win.png").convert()
            self.bg_img = pygame.transform.scale(self.bg_img, screen.get_size())
        except Exception:
            self.bg_img = None

        # Nút bấm (Đẩy xuống dưới cùng)
        w = screen.get_width()
        h = screen.get_height()
        btn_w, btn_h = 160, 50
        spacing = 20
        start_x = (w - (btn_w * 2 + spacing)) // 2
        btn_y = h - 90

        self.btn_replay = PillButton(
            (start_x, btn_y, btn_w, btn_h), "NEW MATCH", self.font_btn,
            color_top=(255, 210, 130), color_bot=(255, 175, 85), shadow_color=(220, 140, 60),
        )
        self.btn_menu = PillButton(
            (start_x + btn_w + spacing, btn_y, btn_w, btn_h), "MAIN MENU", self.font_btn,
            color_top=(220, 180, 255), color_bot=(190, 140, 240), shadow_color=(160, 110, 210),
        )

    def handle_events(self, events):
        for event in events:
            if self.btn_replay.handle_event(event): return "PLAYING_DUAL", None
            if self.btn_menu.handle_event(event):   return "MENU", None
        return "WIN_DUAL", None

    def render(self):
        w, h = self.screen.get_size()
        cx = w // 2

        if self.bg_img: self.screen.blit(self.bg_img, (0, 0))
        else: self.screen.fill((255, 240, 235))

        # 1. TIÊU ĐỀ
        title_text = f"PLAYER {self.winner_id} IS THE CHAMPION!" if self.winner_id else "MATCH TIED!"
        title = self.font_title.render(title_text, True, (240, 100, 120))
        self.screen.blit(title, title.get_rect(centerx=cx, top=35))

        sub = self.font_sub.render(f"Final Score: {self.score}", True, (80, 160, 140))
        self.screen.blit(sub, sub.get_rect(centerx=cx, top=85))

        # 2. BẢNG LỊCH SỬ VÁN ĐẤU
        panel_w = 640
        # Chiều cao bảng tự động co giãn theo số ván đã đánh
        panel_h = 70 + len(self.history) * 45
        panel_rect = pygame.Rect(cx - panel_w // 2, 135, panel_w, panel_h)
        
        # Vẽ nền bảng
        pygame.draw.rect(self.screen, (245, 215, 215), (panel_rect.x, panel_rect.y + 8, panel_w, panel_h), border_radius=20)
        pygame.draw.rect(self.screen, (255, 248, 240), panel_rect, border_radius=20)
        pygame.draw.rect(self.screen, (255, 200, 200), panel_rect, border_radius=20, width=3)

        # Cột (X-coordinates)
        c_rnd = cx - 230
        c_tim = cx - 100
        c_p1  = cx + 20
        c_p2  = cx + 130
        c_win = cx + 240

        # Vẽ Header Bảng
        hdr_y = panel_rect.y + 20
        headers = [(c_rnd, "ROUND"), (c_tim, "TIME"), (c_p1, "P1 MOVES"), (c_p2, "P2 MOVES"), (c_win, "RESULT")]
        for x, txt in headers:
            surf = self.font_table_hdr.render(txt, True, (160, 110, 130))
            self.screen.blit(surf, surf.get_rect(centerx=x, top=hdr_y))

        pygame.draw.line(self.screen, (255, 200, 200), (panel_rect.x + 20, hdr_y + 30), (panel_rect.right - 20, hdr_y + 30), 2)

        # Vẽ Từng Hàng Lịch Sử
        row_y = hdr_y + 45
        for rd in self.history:
            # Màu xen kẽ mờ nhạt cho dễ nhìn
            if rd['round'] % 2 == 0:
                pygame.draw.rect(self.screen, (255, 240, 230), (panel_rect.x + 10, row_y - 10, panel_w - 20, 40), border_radius=8)

            def draw_cell(x, text, color=(80, 80, 80)):
                surf = self.font_table_row.render(str(text), True, color)
                self.screen.blit(surf, surf.get_rect(centerx=x, top=row_y))

            draw_cell(c_rnd, f"#{rd['round']}")
            draw_cell(c_tim, rd['time'])
            
            # Đánh dấu số bước nhỏ hơn (người đi tối ưu hơn) bằng màu xanh
            c1 = (40, 140, 80) if rd['p1_moves'] <= rd['p2_moves'] else (100, 100, 100)
            c2 = (40, 140, 80) if rd['p2_moves'] <= rd['p1_moves'] else (100, 100, 100)
            draw_cell(c_p1, rd['p1_moves'], c1)
            draw_cell(c_p2, rd['p2_moves'], c2)

            # Phù hiệu người thắng
            win_id = rd['winner_id']
            if win_id > 0:
                win_txt = f"P{win_id} WIN"
                bg_color = (130, 200, 150) if win_id == 1 else (230, 150, 150)
            else:
                win_txt = "TIE"
                bg_color = (200, 200, 200)

            badge_rect = pygame.Rect(0, 0, 70, 26)
            badge_rect.center = (c_win, row_y + 12)
            pygame.draw.rect(self.screen, bg_color, badge_rect, border_radius=12)
            b_surf = self.font_table_hdr.render(win_txt, True, (255, 255, 255))
            self.screen.blit(b_surf, b_surf.get_rect(center=badge_rect.center))

            row_y += 45

        # 3. NÚT BẤM
        mouse = pygame.mouse.get_pos()
        self.btn_replay.draw(self.screen, mouse)
        self.btn_menu.draw(self.screen, mouse)