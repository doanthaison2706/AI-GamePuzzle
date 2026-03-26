import pygame

class Button:
    """
    Class tạo nút bấm UI tái sử dụng được ở mọi nơi trong game.
    Thay thế cho JButton của Java.
    """
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 color: tuple, hover_color: tuple, text_color: tuple = (255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        
        # Font chữ mặc định cho nút
        self.font = pygame.font.SysFont("arial", 20, bold=True)
        self.is_hovered = False

    def draw(self, screen):
        """Vẽ nút lên màn hình."""
        # Đổi màu nếu chuột đang trỏ vào 
        current_color = self.hover_color if self.is_hovered else self.color
        
        # Vẽ hình chữ nhật bo góc 
        pygame.draw.rect(screen, current_color, self.rect, border_radius=8)
        
        # Vẽ chữ căn giữa nút
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event) -> bool:
        """
        Nhận sự kiện từ chuột. 
        Trả về True nếu nút bị click.
        """
        # Kiểm tra xem chuột có đang nằm trong khu vực của nút không
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            
        # Kiểm tra xem người dùng có click chuột trái vào nút không
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
                
        return False