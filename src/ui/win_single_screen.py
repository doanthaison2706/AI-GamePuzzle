import pygame
from configs import game_config as config

class WinSingleScreen:
    def __init__(self, screen, result_data):
        self.screen = screen
        
        # Nhận dữ liệu kết quả từ ván game vừa kết thúc
        self.time_str = result_data.get("time", "00:00")
        self.moves = result_data.get("moves", 0)
        self.size = result_data.get("size", 4)
        
        self.current_screen_size = (0, 0)
        self._load_resources()

    def _load_resources(self):
        try:
            self.bg_img = pygame.image.load("assets/images/background_win_single.png").convert()
        except: self.bg_img = None

        try:
            self.title_banner = pygame.image.load("assets/images/title_win_single.png").convert_alpha()
        except: self.title_banner = None

        # --- DÙNG DUY NHẤT 1 ẢNH NỀN CHO TẤT CẢ CÁC NÚT ---
        # Khuyến nghị: Ảnh btn_base.png nên có màu trắng/xám sáng để dễ phủ màu lên
        try: self.img_btn_base = pygame.image.load("assets/images/btn_oval.png").convert_alpha()
        except: self.img_btn_base = None
        
        self.rect_replay = pygame.Rect(0,0,0,0)
        self.rect_setup = pygame.Rect(0,0,0,0)
        self.rect_menu = pygame.Rect(0,0,0,0)

    def _update_layout(self):
        sw, sh = self.screen.get_size()
        if self.current_screen_size == (sw, sh):
            return 
            
        self.current_screen_size = (sw, sh)
        center_x = sw // 2
        scale = max(0.8, min(sw / 1280.0, sh / 720.0))

        # --- UPDATE FONTS ---
        try:
            self.font_title = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", int(36 * scale))
            self.font_sub = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", int(20 * scale))
            self.font_stat_lbl = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", int(18 * scale))
            self.font_stat_val = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", int(42 * scale))
            self.font_btn = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", int(20 * scale))
        except:
            self.font_title = pygame.font.SysFont("arial", int(36 * scale), bold=True)
            self.font_sub = pygame.font.SysFont("arial", int(20 * scale), bold=True)
            self.font_stat_lbl = pygame.font.SysFont("arial", int(18 * scale), bold=True)
            self.font_stat_val = pygame.font.SysFont("arial", int(42 * scale), bold=True)
            self.font_btn = pygame.font.SysFont("arial", int(20 * scale), bold=True)

        # --- UPDATE TỌA ĐỘ NÚT BẤM DƯỚI ĐÁY ---
        btn_w = int(160 * scale)
        btn_h = int(60 * scale)
        spacing = int(25 * scale)
        total_w = (btn_w * 3) + (spacing * 2)
        start_x = center_x - (total_w // 2)
        
        btn_y = sh - btn_h - int(sh * 0.15) 

        self.rect_replay = pygame.Rect(start_x, btn_y, btn_w, btn_h)
        self.rect_setup = pygame.Rect(start_x + btn_w + spacing, btn_y, btn_w, btn_h)
        self.rect_menu = pygame.Rect(start_x + (btn_w + spacing) * 2, btn_y, btn_w, btn_h)
        
        self.scale = scale 

    def handle_events(self, events):
        self._update_layout()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if self.rect_replay.collidepoint(mouse_pos): return "PLAYING", None 
                elif self.rect_setup.collidepoint(mouse_pos): return "SETUP_SINGLE", None 
                elif self.rect_menu.collidepoint(mouse_pos): return "MENU", None 
        return "WIN_SINGLE", None

    def draw_image_button(self, surface, rect, text, image, blend_color=None):
        """Hàm vẽ nút bằng 1 ảnh chung, hỗ trợ đổi màu (blend) và chèn text ở giữa"""
        if image:
            # 1. Scale ảnh vừa khung
            scaled_img = pygame.transform.smoothscale(image, (rect.width, rect.height))
            
            # 2. Phủ màu lên ảnh (Nếu có truyền màu)
            if blend_color:
                colored_img = scaled_img.copy()
                colored_img.fill(blend_color, special_flags=pygame.BLEND_RGB_MULT)
                surface.blit(colored_img, rect.topleft)
            else:
                surface.blit(scaled_img, rect.topleft)
        else:
            # Màu dự phòng nếu chưa load được ảnh
            fallback_c = blend_color if blend_color else (200, 200, 200)
            pygame.draw.rect(surface, fallback_c, rect, border_radius=rect.height//2)
            pygame.draw.rect(surface, (255, 255, 255), rect, border_radius=rect.height//2, width=2)
        
        # 3. Vẽ chữ đè lên ảnh
        txt_shad = self.font_btn.render(text, True, (100, 100, 100)) # Bóng chữ mờ mờ
        txt_surf = self.font_btn.render(text, True, (255, 255, 255))
        txt_rect = txt_surf.get_rect(center=rect.center)
        
        surface.blit(txt_shad, (txt_rect.x, txt_rect.y + 2))
        surface.blit(txt_surf, txt_rect)

    def draw_stat_box(self, center_x, y, label, value):
        box_w = int(140 * self.scale)
        box_h = int(110 * self.scale)
        box_rect = pygame.Rect(center_x - box_w//2, y, box_w, box_h)
        
        pygame.draw.rect(self.screen, (255, 252, 248), box_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 210, 210), box_rect, border_radius=15, width=2)

        lbl_surf = self.font_stat_lbl.render(label, True, (160, 110, 130))
        self.screen.blit(lbl_surf, lbl_surf.get_rect(centerx=center_x, top=box_rect.y + int(15 * self.scale)))

        val_surf = self.font_stat_val.render(str(value), True, (230, 100, 100))
        self.screen.blit(val_surf, val_surf.get_rect(centerx=center_x, bottom=box_rect.bottom - int(10 * self.scale)))

    def render(self):
        self._update_layout()
        sw, sh = self.screen.get_size()
        center_x = sw // 2

        # 1. NỀN & TITLE
        if self.bg_img: 
            bg_scaled = pygame.transform.smoothscale(self.bg_img, (sw, sh))
            self.screen.blit(bg_scaled, (0, 0))
        else: 
            self.screen.fill((255, 240, 235))

        title_y = int(sh * 0.1) 
        
        if self.title_banner:
            t_w = int(400 * self.scale)
            t_h = int(t_w * self.title_banner.get_height() / self.title_banner.get_width())
            title_scaled = pygame.transform.smoothscale(self.title_banner, (t_w, t_h))
            self.screen.blit(title_scaled, title_scaled.get_rect(centerx=center_x, top=title_y))
        else:
            title_txt = self.font_title.render("CHÚC MỪNG!", True, (240, 100, 120))
            sub_txt = self.font_sub.render("BẠN ĐÃ HOÀN THÀNH BÀN CỜ!", True, (80, 160, 140))
            self.screen.blit(title_txt, title_txt.get_rect(centerx=center_x, top=title_y))
            self.screen.blit(sub_txt, sub_txt.get_rect(centerx=center_x, top=title_y + int(50 * self.scale)))

        # 2. PANEL THÔNG SỐ
        panel_w = int(500 * self.scale)
        panel_h = int(150 * self.scale)
        panel_y = title_y + (self.rect_menu.y - title_y) // 2 - panel_h // 2
        panel_rect = pygame.Rect(center_x - panel_w//2, panel_y, panel_w, panel_h)
        
        pygame.draw.rect(self.screen, (245, 215, 215), (panel_rect.x, panel_rect.y + 8, panel_w, panel_h), border_radius=25)
        pygame.draw.rect(self.screen, (255, 245, 235), panel_rect, border_radius=25)
        pygame.draw.rect(self.screen, (255, 200, 200), panel_rect, border_radius=25, width=3)

        box_spacing = int(160 * self.scale)
        box_y = panel_rect.y + int((panel_h - int(110 * self.scale)) // 2) 
        
        self.draw_stat_box(center_x - box_spacing, box_y, "THỜI GIAN", self.time_str)
        self.draw_stat_box(center_x, box_y, "DI CHUYỂN", self.moves)
        self.draw_stat_box(center_x + box_spacing, box_y, "CẤP ĐỘ", f"{self.size}x{self.size}")

        # 3. 3 NÚT BẤM DƯỚI ĐÁY (Dùng chung self.img_btn_base)
        # Truyền thêm màu ở cuối để tự động nhuộm màu cho ảnh nút
        self.draw_image_button(self.screen, self.rect_replay, "TRẬN MỚI", self.img_btn_base, (255, 175, 85)) # Nhuộm Cam
        self.draw_image_button(self.screen, self.rect_setup, "CHỌN MÀN", self.img_btn_base, (100, 190, 240)) # Nhuộm Xanh
        self.draw_image_button(self.screen, self.rect_menu, "THOÁT", self.img_btn_base, (190, 140, 240)) # Nhuộm Tím