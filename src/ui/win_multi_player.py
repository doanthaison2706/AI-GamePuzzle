import pygame

class WinMultiScreen:
    def __init__(self, screen, data):
        """
        data nhận từ MultiplayerScreen gồm: 
        winner (1 hoặc 2), score1, score2
        """
        self.screen = screen
        self.winner = data.get("winner", 1)
        self.score1 = data.get("score1", 0)
        self.score2 = data.get("score2", 0)
        
        self.current_screen_size = (0, 0)
        self._load_resources()
        self._update_layout()

    def _load_resources(self):
        try:
            self.font_big = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", 60)
            self.font_mid = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", 35)
            self.font_stat = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", 18)
            self.font_btn = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", 22)
        except:
            self.font_big = pygame.font.SysFont("arial", 60, True)
            self.font_mid = pygame.font.SysFont("arial", 35, True)
            self.font_stat = pygame.font.SysFont("arial", 18, True)
            self.font_btn = pygame.font.SysFont("arial", 22, True)

        self.c_p1 = (110, 200, 165)
        self.c_p2 = (246, 143, 168)
        self.c_bg = (255, 246, 233)

    def _update_layout(self):
        sw, sh = self.screen.get_size()
        if self.current_screen_size == (sw, sh): return
        self.current_screen_size = (sw, sh)
        
        center_x = sw // 2
        center_y = sh // 2
        
        # 1. Khung thông báo (Responsive theo % màn hình)
        self.panel_w = int(sw * 0.45)
        self.panel_h = int(sh * 0.55)
        self.panel_rect = pygame.Rect(center_x - self.panel_w//2, center_y - self.panel_h//2 - 30, self.panel_w, self.panel_h)

        # 2. Nút bấm (Linh hoạt theo kích thước khung)
        btn_w = int(sw * 0.12)
        btn_h = int(sh * 0.07)
        spacing = 25
        total_btns_w = btn_w * 2 + spacing
        
        self.btn_replay = pygame.Rect(center_x - total_btns_w//2, self.panel_rect.bottom + 40, btn_w, btn_h)
        self.btn_menu = pygame.Rect(self.btn_replay.right + spacing, self.btn_replay.y, btn_w, btn_h)

    def handle_events(self, events):
        self._update_layout() # Luôn cập nhật layout khi có sự thay đổi
        for event in events:
            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self._update_layout()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_replay.collidepoint(event.pos):
                    return "REPLAY", None 
                if self.btn_menu.collidepoint(event.pos):
                    return "MENU", None
        
        return "WIN_MULTI", None

    def draw_3d_button(self, rect, text, color_top, color_bot, color_shad):
        radius = 15
        # Shadow
        pygame.draw.rect(self.screen, color_shad, (rect.x, rect.y + 6, rect.width, rect.height), border_radius=radius)
        # Bottom layer
        pygame.draw.rect(self.screen, color_bot, rect, border_radius=radius)
        # Top layer
        pygame.draw.rect(self.screen, color_top, (rect.x, rect.y, rect.width, rect.height - 4), border_radius=radius)
        # Border
        pygame.draw.rect(self.screen, (255, 255, 255), rect, width=2, border_radius=radius)
        
        txt = self.font_btn.render(text, True, (255, 255, 255))
        self.screen.blit(txt, txt.get_rect(center=rect.center))

    def render(self):
        sw, sh = self.current_screen_size
        center_x = sw // 2
        
        # Nền tối mờ phía sau
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120)) 
        self.screen.blit(overlay, (0, 0))
        
        # Vẽ Panel trắng bo góc
        pygame.draw.rect(self.screen, (255, 255, 255), self.panel_rect, border_radius=25)
        border_color = self.c_p1 if self.winner == 1 else self.c_p2
        pygame.draw.rect(self.screen, border_color, self.panel_rect, width=4, border_radius=25)

        # Text Chúc mừng
        win_title = self.font_big.render("CHIẾN THẮNG!", True, (255, 140, 0))
        self.screen.blit(win_title, win_title.get_rect(centerx=center_x, top=self.panel_rect.top + 30))

        # Tên người thắng
        winner_name = "NGƯỜI CHƠI 1" if self.winner == 1 else "NGƯỜI CHƠI 2"
        name_txt = self.font_mid.render(winner_name, True, border_color)
        self.screen.blit(name_txt, name_txt.get_rect(centerx=center_x, top=self.panel_rect.top + 110))

        # Tỉ số (Phóng to giữa panel)
        score_txt = self.font_big.render(f"{self.score1} - {self.score2}", True, (120, 120, 120))
        self.screen.blit(score_txt, score_txt.get_rect(center=(center_x, self.panel_rect.centery + 40)))
        
        lbl_txt = self.font_stat.render("TỈ SỐ CHUNG CUỘC", True, (180, 180, 180))
        self.screen.blit(lbl_txt, lbl_txt.get_rect(centerx=center_x, top=self.panel_rect.centery + 90))

        # Nút bấm (Dùng đúng bảng màu của màn hình chơi)
        c_green = (165, 240, 210); c_green_b = (132, 220, 187); c_green_s = (110, 200, 165)
        c_pink = (255, 175, 198); c_pink_b = (246, 143, 168); c_pink_s = (220, 120, 145)

        self.draw_3d_button(self.btn_replay, "CHƠI LẠI", c_green, c_green_b, c_green_s)
        self.draw_3d_button(self.btn_menu, "MENU", c_pink, c_pink_b, c_pink_s)