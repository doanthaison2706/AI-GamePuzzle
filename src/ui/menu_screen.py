import pygame
from configs import game_config as config
from src.ui.components import Button
from src.utils.image_crop import open_file_dialog, interactive_crop

class MenuScreen:
    def __init__(self, screen):
        self.screen = screen
        self.selected_size = 3
        self.full_image = None
        
        center_x = config.WINDOW_WIDTH // 2
        
        # Setup UI Menu
        self.level_buttons = []
        for i, size in enumerate([3, 4, 5, 6]):
            btn = Button(center_x - 130 + i * 65, 250, 50, 40, f"{size}x{size}", (200, 200, 200), (150, 150, 150), (0,0,0))
            self.level_buttons.append((size, btn))
            
        self.btn_select_img = Button(center_x - 100, 350, 200, 45, "Chọn Ảnh Bàn Cờ", (100, 149, 237), (65, 105, 225))
        self.btn_play = Button(center_x - 100, 600, 200, 60, "BẮT ĐẦU CHƠI", (46, 204, 113), (39, 174, 96))

    def handle_events(self, events):
        """Trả về tuple: (Trạng thái tiếp, Dữ liệu setup)"""
        for event in events:
            # Chọn Level
            for size, btn in self.level_buttons:
                if btn.handle_event(event):
                    self.selected_size = size

            # Bật hộp thoại cắt ảnh
            if self.btn_select_img.handle_event(event):
                file_path = open_file_dialog()
                if file_path:
                    cropped = interactive_crop(self.screen, file_path, config.BOARD_SIZE)
                    if cropped:
                        self.full_image = cropped

            # Bấm Play -> Gói ghém dữ liệu gửi đi
            if self.btn_play.handle_event(event):
                setup_data = {
                    "size": self.selected_size,
                    "image": self.full_image
                }
                return "PLAYING", setup_data
                
        return "MENU", None

    def render(self):
        font_title = pygame.font.SysFont("comicsansms", 45, bold=True)
        font_label = pygame.font.SysFont("arial", 22, bold=True)
        center_x = config.WINDOW_WIDTH // 2
        
        title = font_title.render("N-PUZZLE ARENA", True, (50, 50, 50))
        lbl_lvl = font_label.render("1. CHỌN ĐỘ KHÓ", True, (100, 100, 100))
        lbl_img = font_label.render("2. CHỌN ẢNH BÀN CỜ (Tùy chọn)", True, (100, 100, 100))
        
        self.screen.blit(title, (center_x - title.get_width()//2, 80))
        self.screen.blit(lbl_lvl, (center_x - lbl_lvl.get_width()//2, 210))
        self.screen.blit(lbl_img, (center_x - lbl_img.get_width()//2, 315))
        
        for size, btn in self.level_buttons:
            if size == self.selected_size: # Đóng khung nút đang chọn
                pygame.draw.rect(self.screen, (255, 105, 180), (btn.rect.x - 4, btn.rect.y - 4, btn.rect.w + 8, btn.rect.h + 8), border_radius=10)
            btn.draw(self.screen)
            
        self.btn_select_img.draw(self.screen)
        self.btn_play.draw(self.screen)
        
        # Vẽ Thumbnail ảnh đã cắt
        if self.full_image:
            thumb = pygame.transform.smoothscale(self.full_image, (150, 150))
            thumb_rect = thumb.get_rect(center=(center_x, 485))
            self.screen.blit(thumb, thumb_rect)
            pygame.draw.rect(self.screen, (50, 50, 50), thumb_rect, 2)