import pygame
import sys
from configs import game_config as config
from src.ui.components import Button

class MainMenuScreen:
    def __init__(self, screen):
        self.screen = screen
        
        # 1. TẢI TÀI NGUYÊN (Chỉ tải ảnh gốc, chưa scale vội)
        try:
            self.original_bg = pygame.image.load("Assets/images/background.png").convert()
            self.cached_bg = None
            self.last_size = (0, 0) # Dùng để check xem cửa sổ có bị kéo to ra không
            
            self.logo_image = pygame.image.load("Assets/images/logo.png").convert_alpha()
        except Exception as e:
            print("⚠️ Lỗi tải ảnh:", e)
            self.original_bg = None
            self.logo_image = None

        # 2. KHỞI TẠO NÚT (Tọa độ tạm thời, lát render sẽ tính lại chuẩn)
        btn_w, btn_h = 320, 65
        color_pink = (247, 168, 196)
        color_mint = (159, 227, 214)
        color_blue = (169, 214, 245)
        color_lavender = (203, 183, 246)
        text_color = (255, 255, 255)

        self.btn_single = Button(0, 0, btn_w, btn_h, "CHƠI ĐƠN", color_pink, (255, 180, 210), text_color)
        self.btn_multi = Button(0, 0, btn_w, btn_h, "ĐỐI KHÁNG", color_mint, (170, 240, 225), text_color)
        self.btn_setting = Button(0, 0, btn_w, btn_h, "TÙY CHỈNH", color_blue, (180, 225, 255), text_color)
        self.btn_exit = Button(0, 0, btn_w, btn_h, "THOÁT", color_lavender, (220, 200, 255), text_color)

    def handle_events(self, events):
        for event in events:
            if self.btn_single.handle_event(event):
                return "SETUP_SINGLE", None 
            if self.btn_multi.handle_event(event):
                return "SETUP_MULTI", None
            if self.btn_setting.handle_event(event):
                pass
            if self.btn_exit.handle_event(event):
                pygame.quit()
                sys.exit()
                
        return "MAIN_MENU", None

    def render(self):
        # Lấy kích thước THỰC TẾ của cửa sổ ngay lúc này
        current_w, current_h = self.screen.get_size()
        center_x = current_w // 2

        # ==========================================
        # 1. VẼ NỀN (Tự động lấp đầy khoảng trắng)
        # ==========================================
        if self.original_bg:
            # Thuật toán Cache: Chỉ scale lại ảnh nếu kích thước cửa sổ bị thay đổi (để chống lag)
            if self.last_size != (current_w, current_h):
                self.cached_bg = pygame.transform.smoothscale(self.original_bg, (current_w, current_h))
                self.last_size = (current_w, current_h)
            
            self.screen.blit(self.cached_bg, (0, 0))
        else:
            self.screen.fill((245, 245, 245))

        # ==========================================
        # 2. VẼ LOGO (Tự động căn giữa trên cùng)
        # ==========================================
        if self.logo_image:
            # Tự co giãn logo chiếm 70% chiều rộng màn hình
            logo_w = int(current_w * 0.7)
            logo_ratio = self.logo_image.get_height() / self.logo_image.get_width()
            scaled_logo = pygame.transform.smoothscale(self.logo_image, (logo_w, int(logo_w * logo_ratio)))
            
            logo_rect = scaled_logo.get_rect(center=(center_x, int(current_h * 0.25)))
            self.screen.blit(scaled_logo, logo_rect)

        # ==========================================
        # 3. VẼ NÚT (Tự động nhảy ra giữa màn hình)
        # ==========================================
        # Tính toán tọa độ Y linh hoạt theo chiều cao màn hình
        start_y = int(current_h * 0.48)
        gap = int(current_h * 0.11)

        # Ép các nút nhảy ra giữa
        self.btn_single.rect.x = center_x - self.btn_single.rect.w // 2
        self.btn_single.rect.y = start_y
        
        self.btn_multi.rect.x = center_x - self.btn_multi.rect.w // 2
        self.btn_multi.rect.y = start_y + gap
        
        self.btn_setting.rect.x = center_x - self.btn_setting.rect.w // 2
        self.btn_setting.rect.y = start_y + gap * 2
        
        self.btn_exit.rect.x = center_x - self.btn_exit.rect.w // 2
        self.btn_exit.rect.y = start_y + gap * 3

        # Vẽ ra
        self.btn_single.draw(self.screen)
        self.btn_multi.draw(self.screen)
        self.btn_setting.draw(self.screen)
        self.btn_exit.draw(self.screen)