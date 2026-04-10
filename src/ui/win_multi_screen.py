import pygame
from configs import game_config as config

class WinMultiScreen:
    def __init__(self, screen, data):
        self.screen = screen
        self.winner = data.get("winner", 1)
        self.score1 = data.get("score1", 0)
        self.score2 = data.get("score2", 0)

        self.current_screen_size = (0, 0)
        self._load_resources()

    def _load_resources(self):
        try: self.bg_img = pygame.image.load("assets/images/background_win_multi.png").convert()
        except: self.bg_img = None

        try: self.title_img = pygame.image.load("assets/images/title_win_multi.png").convert_alpha()
        except: self.title_img = None

        # Dùng chung 1 ảnh nền nút giống màn chơi đơn
        try: self.img_btn_base = pygame.image.load("assets/images/btn_base.png").convert_alpha()
        except: self.img_btn_base = None

        self.c_p1 = (110, 200, 165) # Xanh lá P1
        self.c_p2 = (246, 143, 168) # Hồng P2
        self.c_bg = (255, 246, 233)

        self.btn_replay = pygame.Rect(0,0,0,0)
        self.btn_menu = pygame.Rect(0,0,0,0)

    def _update_layout(self):
        sw, sh = self.screen.get_size()
        if self.current_screen_size == (sw, sh):
            return

        self.current_screen_size = (sw, sh)
        center_x = sw // 2

        # Scale đồng bộ giống hệt màn chơi đơn
        scale = max(0.8, min(sw / 1280.0, sh / 720.0))
        self.scale = scale

        # --- UPDATE FONTS ---
        try:
            self.font_big = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", int(46 * scale))
            self.font_mid = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", int(32 * scale))
            self.font_stat = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", int(20 * scale))
            self.font_btn = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", int(20 * scale))
        except:
            self.font_big = pygame.font.SysFont("arial", int(46 * scale), True)
            self.font_mid = pygame.font.SysFont("arial", int(32 * scale), True)
            self.font_stat = pygame.font.SysFont("arial", int(20 * scale), True)
            self.font_btn = pygame.font.SysFont("arial", int(20 * scale), True)

        # --- UPDATE TỌA ĐỘ NÚT BẤM DƯỚI ĐÁY ---
        btn_w = int(160 * scale)
        btn_h = int(60 * scale)
        spacing = int(30 * scale)
        total_btns_w = (btn_w * 2) + spacing

        btn_y = sh - btn_h - int(sh * 0.15)

        self.btn_replay = pygame.Rect(center_x - total_btns_w // 2, btn_y, btn_w, btn_h)
        self.btn_menu = pygame.Rect(self.btn_replay.right + spacing, btn_y, btn_w, btn_h)

        self.title_y = int(sh * 0.08) # Neo Title ở phía trên cùng
        
        self.panel_w = int(550 * scale)
        self.panel_h = int(320 * scale)
        
        # Căn Panel nằm chính giữa
        panel_y = self.title_y + int(130 * scale)
        self.panel_rect = pygame.Rect(center_x - self.panel_w // 2, panel_y, self.panel_w, self.panel_h)

        # --- UPDATE TỌA ĐỘ NÚT BẤM (Fix khoảng cách) ---
        btn_w = int(180 * scale)
        btn_h = int(65 * scale)
        spacing = int(120 * scale) # Khoảng cách siêu rộng để không bị dính

        # Nút bám sát dưới đáy Panel
        btn_y = self.panel_rect.bottom + int(40 * scale)

        # Căn đều 2 nút từ tâm màn hình tỏa ra
        self.btn_replay = pygame.Rect(center_x - btn_w - (spacing // 2), btn_y, btn_w, btn_h)
        self.btn_menu = pygame.Rect(center_x + (spacing // 2), btn_y, btn_w, btn_h)
        
    def handle_events(self, events):
        self._update_layout() # Gọi ở đây để Hitbox luôn khớp tuyệt đối
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_replay.collidepoint(event.pos): return "REPLAY", None
                if self.btn_menu.collidepoint(event.pos): return "MENU", None
        return "WIN_MULTI", None

    def draw_image_button(self, surface, rect, text, image, blend_color=None):
        """Hàm vẽ nút bằng 1 ảnh chung, có hỗ trợ nhuộm màu"""
        if image:
            scaled_img = pygame.transform.smoothscale(image, (rect.width, rect.height))
            if blend_color:
                colored_img = scaled_img.copy()
                colored_img.fill(blend_color, special_flags=pygame.BLEND_RGB_MULT)
                surface.blit(colored_img, rect.topleft)
            else:
                surface.blit(scaled_img, rect.topleft)
        else:
            fallback_c = blend_color if blend_color else (200, 200, 200)
            pygame.draw.rect(surface, fallback_c, rect, border_radius=rect.height//2)
            pygame.draw.rect(surface, (255, 255, 255), rect, border_radius=rect.height//2, width=2)

        txt_shad = self.font_btn.render(text, True, (100, 100, 100))
        txt_surf = self.font_btn.render(text, True, (255, 255, 255))
        txt_rect = txt_surf.get_rect(center=rect.center)

        surface.blit(txt_shad, (txt_rect.x, txt_rect.y + 2))
        surface.blit(txt_surf, txt_rect)

    def render(self):
        self._update_layout()
        sw, sh = self.screen.get_size()
        center_x = sw // 2

        # 1. NỀN (ĐÃ XÓA LỚP PHỦ ĐEN CHO SÁNG SỦA)
        if self.bg_img:
            bg_scaled = pygame.transform.smoothscale(self.bg_img, (sw, sh))
            self.screen.blit(bg_scaled, (0, 0))
        else:
            self.screen.fill(self.c_bg)

        # 2. TITLE (Đã fix lệch)
        if self.title_img:
            title_w = int(450 * self.scale)
            title_h = int(title_w * self.title_img.get_height() / self.title_img.get_width())
            title_scaled = pygame.transform.smoothscale(self.title_img, (title_w, title_h))
            self.screen.blit(title_scaled, title_scaled.get_rect(centerx=center_x, top=self.title_y))
        else:
            win_title = self.font_big.render("CHIẾN THẮNG!", True, (255, 140, 0))
            shadow = self.font_big.render("CHIẾN THẮNG!", True, (255, 220, 150))
            title_rect = win_title.get_rect(centerx=center_x, top=self.title_y)
            self.screen.blit(shadow, (title_rect.x, title_rect.y + 3))
            self.screen.blit(win_title, title_rect)

        # 3. PANEL
        pygame.draw.rect(self.screen, (255, 255, 255), self.panel_rect, border_radius=25)
        border_color = self.c_p1 if self.winner == 1 else self.c_p2
        pygame.draw.rect(self.screen, border_color, self.panel_rect, width=4, border_radius=25)

        # Tên người thắng
        winner_name = "NGƯỜI CHƠI 1" if self.winner == 1 else "NGƯỜI CHƠI 2"
        name_txt = self.font_mid.render(winner_name, True, border_color)
        self.screen.blit(name_txt, name_txt.get_rect(centerx=center_x, top=self.panel_rect.top + int(40 * self.scale)))

        # Tỉ số
        score_txt = self.font_big.render(f"{self.score1} - {self.score2}", True, (120, 120, 120))
        self.screen.blit(score_txt, score_txt.get_rect(center=(center_x, self.panel_rect.centery + int(10 * self.scale))))

        lbl_txt = self.font_stat.render("TỈ SỐ CHUNG CUỘC", True, (180, 180, 180))
        self.screen.blit(lbl_txt, lbl_txt.get_rect(centerx=center_x, top=self.panel_rect.centery + int(60 * self.scale)))

        # 4. NÚT BẤM (Dùng chung ảnh btn_base.png, tự động nhuộm màu)
        self.draw_image_button(self.screen, self.btn_replay, "CHƠI LẠI", self.img_btn_base, self.c_p1) # Nhuộm xanh P1
        self.draw_image_button(self.screen, self.btn_menu, "MENU", self.img_btn_base, self.c_p2) # Nhuộm hồng P2