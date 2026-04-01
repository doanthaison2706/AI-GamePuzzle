import pygame
from configs import game_config as config

class CropImageMenu:
    def __init__(self, screen, image_path, board_size):
        self.screen = screen
        self.board_size = board_size
        self.original_img = None
        self.result_image = None
        
        try:
            self.original_img = pygame.image.load(image_path).convert_alpha()
        except Exception as e:
            print("Lỗi load ảnh:", e)

        if self.original_img:
            self._setup_ui()

    def _setup_ui(self):
        """Khởi tạo các thông số UI"""
        img_w, img_h = self.original_img.get_size()
        self.screen_w, self.screen_h = self.screen.get_size()
        
        # Căn chỉnh tỷ lệ
        self.scale = min((self.screen_w - 60) / img_w, (self.screen_h - 220) / img_h)
        self.scaled_w, self.scaled_h = int(img_w * self.scale), int(img_h * self.scale)
        self.scaled_img = pygame.transform.smoothscale(self.original_img, (self.scaled_w, self.scaled_h))
        
        self.crop_size = min(self.scaled_w, self.scaled_h)
        self.crop_rect = pygame.Rect(0, 0, self.crop_size, self.crop_size)
        
        self.offset_x = (self.screen_w - self.scaled_w) // 2
        self.offset_y = (self.screen_h - self.scaled_h) // 2 + 10 
        
        # Nút bấm
        btn_w, btn_h = 160, 55
        self.btn_cancel_rect = pygame.Rect(self.screen_w // 2 - 180, self.screen_h - 85, btn_w, btn_h)
        self.btn_confirm_rect = pygame.Rect(self.screen_w // 2 + 20, self.screen_h - 85, btn_w, btn_h)

        # Fonts
        try:
            self.font_title = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", 28)
            self.font_btn = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", 20)
        except:
            self.font_title = pygame.font.SysFont("arial", 24, bold=True)
            self.font_btn = pygame.font.SysFont("arial", 18, bold=True)

    def run(self):
        """Vòng lặp chính của menu cắt ảnh (Giống như hàm tương tác cũ)"""
        if not self.original_img:
            return None

        dragging = False
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                    
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_x, mouse_y = event.pos
                    
                    if self.btn_confirm_rect.collidepoint(mouse_x, mouse_y):
                        running = False
                        self._process_crop() # Chốt ảnh
                        
                    elif self.btn_cancel_rect.collidepoint(mouse_x, mouse_y):
                        return None
                        
                    elif self.crop_rect.collidepoint(mouse_x - self.offset_x, mouse_y - self.offset_y):
                        dragging = True
                        offset_x_drag = self.crop_rect.x - (mouse_x - self.offset_x)
                        offset_y_drag = self.crop_rect.y - (mouse_y - self.offset_y)
                        
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    dragging = False
                    
                elif event.type == pygame.MOUSEMOTION:
                    if dragging:
                        mouse_x, mouse_y = event.pos
                        new_x = (mouse_x - self.offset_x) + offset_x_drag
                        new_y = (mouse_y - self.offset_y) + offset_y_drag
                        self.crop_rect.x = max(0, min(new_x, self.scaled_w - self.crop_size))
                        self.crop_rect.y = max(0, min(new_y, self.scaled_h - self.crop_size))
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        running = False
                        self._process_crop()
                    elif event.key == pygame.K_ESCAPE:
                        return None
            
            self._render()
            clock.tick(60)
            
        return self.result_image

    def _process_crop(self):
        """Toán học xử lý cắt ảnh sau khi xác nhận"""
        real_x = int(self.crop_rect.x / self.scale)
        real_y = int(self.crop_rect.y / self.scale)
        real_size = int(self.crop_size / self.scale)
        
        cropped_original = self.original_img.subsurface((real_x, real_y, real_size, real_size)).copy()
        self.result_image = pygame.transform.smoothscale(cropped_original, (self.board_size, self.board_size))

    def _render(self):
        """Vẽ toàn bộ giao diện"""
        self.screen.fill((255, 246, 233)) 
        
        # Header
        pygame.draw.rect(self.screen, (255, 230, 235), (0, 0, self.screen_w, 80))
        pygame.draw.line(self.screen, (248, 186, 186), (0, 80), (self.screen_w, 80), 3)
        
        title_surf = self.font_title.render("CẮT ẢNH CHO BÀN CỜ", True, (205, 92, 92))
        sub_surf = self.font_btn.render("Kéo thả vùng sáng để chọn mảnh ghép vuông", True, (150, 100, 100))
        self.screen.blit(title_surf, (self.screen_w // 2 - title_surf.get_width() // 2, 10))
        self.screen.blit(sub_surf, (self.screen_w // 2 - sub_surf.get_width() // 2, 45))
        
        # Ảnh & Lớp phủ
        self.screen.blit(self.scaled_img, (self.offset_x, self.offset_y))
        
        overlay = pygame.Surface((self.scaled_w, self.scaled_h), pygame.SRCALPHA)
        overlay.fill((60, 40, 40, 160)) 
        pygame.draw.rect(overlay, (0, 0, 0, 0), self.crop_rect) 
        self.screen.blit(overlay, (self.offset_x, self.offset_y))
        
        # Khung viền và Handle
        crop_draw_x = self.offset_x + self.crop_rect.x
        crop_draw_y = self.offset_y + self.crop_rect.y
        
        pygame.draw.rect(self.screen, (255, 255, 255, 100), (crop_draw_x-2, crop_draw_y-2, self.crop_size+4, self.crop_size+4), 2)
        pygame.draw.rect(self.screen, (255, 255, 255), (crop_draw_x, crop_draw_y, self.crop_size, self.crop_size), 3)
        
        corners = [
            (crop_draw_x, crop_draw_y), (crop_draw_x + self.crop_size, crop_draw_y),
            (crop_draw_x, crop_draw_y + self.crop_size), (crop_draw_x + self.crop_size, crop_draw_y + self.crop_size)
        ]
        for cx, cy in corners:
            h_rect = pygame.Rect(0, 0, 12, 12)
            h_rect.center = (cx, cy)
            pygame.draw.rect(self.screen, (246, 143, 168), h_rect, border_radius=3)
            pygame.draw.rect(self.screen, (255, 255, 255), h_rect, border_radius=3, width=2)
        
        # Nút bấm Hủy & Xác nhận
        pygame.draw.rect(self.screen, (220, 200, 200), (self.btn_cancel_rect.x, self.btn_cancel_rect.y + 4, 160, 55), border_radius=25)
        pygame.draw.rect(self.screen, (245, 230, 230), self.btn_cancel_rect, border_radius=25)
        cancel_txt = self.font_btn.render("HỦY", True, (150, 100, 100))
        self.screen.blit(cancel_txt, cancel_txt.get_rect(center=self.btn_cancel_rect.center))
        
        pygame.draw.rect(self.screen, (110, 200, 165), (self.btn_confirm_rect.x, self.btn_confirm_rect.y + 4, 160, 55), border_radius=25)
        pygame.draw.rect(self.screen, (132, 220, 187), self.btn_confirm_rect, border_radius=25)
        confirm_txt = self.font_btn.render("XÁC NHẬN", True, (255, 255, 255))
        self.screen.blit(confirm_txt, confirm_txt.get_rect(center=self.btn_confirm_rect.center))
        
        pygame.display.flip()