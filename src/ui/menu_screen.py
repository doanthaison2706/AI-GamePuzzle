import pygame
import sys
from configs import game_config as config

class MainMenuScreen:
    def __init__(self, screen):
        self.screen = screen
        self.last_size = (0, 0)
        
        # --- 1. TẢI TÀI NGUYÊN (4 ảnh nút đã có sẵn chữ) ---
        try:
            self.original_bg = pygame.image.load("assets/images/background_menu.png").convert()
            self.logo_image = pygame.image.load("assets/images/title_logo.png").convert_alpha()
            
            # Load 4 file ảnh nút riêng biệt (Ảnh đã có chữ)
            self.img_single = pygame.image.load("assets/images/btn_single.png").convert_alpha()
            self.img_multi = pygame.image.load("assets/images/btn_multi.png").convert_alpha()
            self.img_setting = pygame.image.load("assets/images/btn_option.png").convert_alpha()
            self.img_exit = pygame.image.load("assets/images/btn_exit.png").convert_alpha()
            
        except Exception as e:
            print("⚠️ Lỗi tải ảnh Menu:", e)
            self.original_bg = self.logo_image = None
            self.img_single = self.img_multi = self.img_setting = self.img_exit = None

        # Khởi tạo các Rect rỗng
        self.rects = {
            "single": pygame.Rect(0,0,0,0),
            "multi": pygame.Rect(0,0,0,0),
            "setting": pygame.Rect(0,0,0,0),
            "exit": pygame.Rect(0,0,0,0)
        }

    def _update_layout(self):
        sw, sh = self.screen.get_size()
        if self.last_size == (sw, sh):
            return
        
        self.last_size = (sw, sh)
        center_x = sw // 2
        self.scale = max(0.7, min(sw / 1200, sh / 800))

        # Kích thước nút (Tỷ lệ 350x75 là chuẩn cho các nút của bạn)
        btn_w = int(380 * self.scale)
        btn_h = int(85 * self.scale)
        
        # --- CĂN CHỈNH VỊ TRÍ ---
        # Đẩy cụm nút xuống dưới Logo
        start_y = int(sh * 0.52) 
        gap = int(sh * 0.11)

        self.rects["single"] = pygame.Rect(center_x - btn_w//2, start_y, btn_w, btn_h)
        self.rects["multi"] = pygame.Rect(center_x - btn_w//2, start_y + gap, btn_w, btn_h)
        self.rects["setting"] = pygame.Rect(center_x - btn_w//2, start_y + gap * 2, btn_w, btn_h)
        self.rects["exit"] = pygame.Rect(center_x - btn_w//2, start_y + gap * 3, btn_w, btn_h)

    def draw_custom_button(self, surface, rect, image):
        """Chỉ vẽ ảnh nút (Vì ảnh đã có sẵn text)"""
        if image:
            scaled_img = pygame.transform.smoothscale(image, (rect.width, rect.height))
            surface.blit(scaled_img, rect.topleft)
        else:
            # Dự phòng nếu lỗi ảnh: Vẽ khung xám
            pygame.draw.rect(surface, (200, 200, 200), rect, border_radius=15)

    def handle_events(self, events):
        self._update_layout()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if self.rects["single"].collidepoint(pos): return "SETUP_SINGLE", None
                if self.rects["multi"].collidepoint(pos): return "SETUP_MULTI", None
                if self.rects["setting"].collidepoint(pos): return "SETTING", None
                if self.rects["exit"].collidepoint(pos):
                    pygame.quit()
                    sys.exit()
                    
        return "MAIN_MENU", None

    def render(self):
        self._update_layout()
        sw, sh = self.screen.get_size()
        center_x = sw // 2

        # 1. Vẽ Nền
        if self.original_bg:
            bg_scaled = pygame.transform.smoothscale(self.original_bg, (sw, sh))
            self.screen.blit(bg_scaled, (0, 0))
        else:
            self.screen.fill((245, 245, 245))

        # 2. Vẽ Logo (Đẩy lên trên cùng để tránh đè nút)
        if self.logo_image:
            logo_w = int(sw * 0.5)
            ratio = self.logo_image.get_height() / self.logo_image.get_width()
            logo_h = int(logo_w * ratio)
            logo_scaled = pygame.transform.smoothscale(self.logo_image, (logo_w, logo_h))
            
            # Đặt logo ở vị trí 5% chiều cao màn hình tính từ đỉnh
            self.screen.blit(logo_scaled, logo_scaled.get_rect(centerx=center_x, top=int(sh * 0.05)))

        # 3. Vẽ 4 Nút (Không dùng text render)
        self.draw_custom_button(self.screen, self.rects["single"], self.img_single)
        self.draw_custom_button(self.screen, self.rects["multi"], self.img_multi)
        self.draw_custom_button(self.screen, self.rects["setting"], self.img_setting)
        self.draw_custom_button(self.screen, self.rects["exit"], self.img_exit)