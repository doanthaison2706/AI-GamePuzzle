import pygame
from configs import game_config as config

class Button:
    def __init__(self, x, y, w, h, text, color, hover_color, text_color=(255, 255, 255), font_size=28, icon_path=None, radius=20):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.SysFont("arial", font_size, bold=True)
        self.radius = radius # Độ bo góc
        
        # Xử lý Icon (nếu có)
        self.icon = None
        if icon_path:
            try:
                # Tải icon gốc
                orig_icon = pygame.image.load(icon_path).convert_alpha()
                # Tự động scale icon cho vừa 60% chiều cao của nút
                icon_h = int(h * 0.6)
                ratio = orig_icon.get_width() / orig_icon.get_height()
                icon_w = int(icon_h * ratio)
                self.icon = pygame.transform.smoothscale(orig_icon, (icon_w, icon_h))
            except:
                print(f"⚠️ Không load được icon: {icon_path}")

    def draw(self, screen):
        # 1. Vẽ nền nút bo tròn (Dùng border_radius xịn xò)
        mouse_pos = pygame.mouse.get_pos()
        draw_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, draw_color, self.rect, border_radius=self.radius)

        # 2. Chuẩn bị Text surface
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect()

        # 3. Thuật toán canh chỉnh Icon + Text vào CHÍNH GIỮA (Crucial Logic)
        if self.icon:
            gap = 10 # Khoảng cách giữa icon và chữ
            icon_w = self.icon.get_width()
            text_w = text_rect.width
            total_content_w = icon_w + gap + text_w
            
            # Tính tọa độ X bắt đầu để cả cụm content nằm giữa nút
            start_x = self.rect.x + (self.rect.width - total_content_w) // 2
            
            # Vẽ icon
            icon_y = self.rect.y + (self.rect.height - self.icon.get_height()) // 2
            screen.blit(self.icon, (start_x, icon_y))
            
            # Vẽ text ngay sau icon
            text_x = start_x + icon_w + gap
            text_y = self.rect.y + (self.rect.height - text_rect.height) // 2
            screen.blit(text_surf, (text_x, text_y))
        else:
            # Nếu không có icon, vẽ text ở giữa như bình thường
            text_rect.center = self.rect.center
            screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False