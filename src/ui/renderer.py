import pygame
from configs import game_config as config

class Renderer:
    """
    Class chuyên lo việc vẽ vời lên màn hình: vẽ bảng, vẽ số, tô màu.
    """
    def __init__(self, screen):
        self.screen = screen
        # Khởi tạo font chữ (Thay cho việc set Font trong Java)
        self.font_large = pygame.font.SysFont("comicsansms", 40, bold=True)
        self.font_medium = pygame.font.SysFont("arial", 24, bold=True)

    def get_gradient_color(self, value: int, size: int) -> tuple[int, int, int]:
        """Thuật toán đổi màu Gradient chuẩn 100% từ code Java cũ của bạn."""
        if value == 0:
            return config.WHITE

        ratio = value / (size * size - 1)

        base = (255, 182, 193)   # Hồng nhạt
        middle = (255, 223, 100) # Vàng
        end = (173, 216, 230)    # Xanh dương nhạt

        if ratio < 0.5:
            t = ratio * 2
            r = int(base[0] - (base[0] - middle[0]) * t)
            g = int(base[1] - (base[1] - middle[1]) * t)
            b = int(base[2] - (base[2] - middle[2]) * t)
        else:
            t = (ratio - 0.5) * 2
            r = int(middle[0] - (middle[0] - end[0]) * t)
            g = int(middle[1] - (middle[1] - end[1]) * t)
            b = int(middle[2] - (middle[2] - end[2]) * t)

        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

    def draw_text_with_shadow(self, text: str, rect: pygame.Rect):
        """Hàm phụ trợ để vẽ số có viền đen, chống chìm màu khi đè lên ảnh."""
        shadow_surf = self.font_large.render(text, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(rect.centerx + 2, rect.centery + 2))
        self.screen.blit(shadow_surf, shadow_rect)

        text_surf = self.font_large.render(text, True, config.WHITE)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def draw_board(self, matrix, size: int, image_slices: dict = None, full_image=None, show_full: bool = False):
        """Vẽ bàn cờ. Đã nâng cấp để nhận cả ảnh cắt và tính năng giữ phím Space."""
        if show_full and full_image:
            self.screen.blit(full_image, (config.MARGIN_LEFT, config.MARGIN_TOP))
            pygame.draw.rect(self.screen, config.TEXT_COLOR,
                             (config.MARGIN_LEFT, config.MARGIN_TOP, config.BOARD_SIZE, config.BOARD_SIZE), 3)
            return

        tile_size = config.BOARD_SIZE // size

        for r in range(size):
            for c in range(size):
                value = matrix[r][c]
                x = config.MARGIN_LEFT + c * tile_size
                y = config.MARGIN_TOP + r * tile_size
                rect = pygame.Rect(x, y, tile_size, tile_size)

                if value != 0:
                    # Nếu có ảnh cắt -> Vẽ ảnh
                    if image_slices and value in image_slices:
                        self.screen.blit(image_slices[value], (x, y))
                    # Nếu không có ảnh -> Vẽ Gradient như cũ
                    else:
                        color = self.get_gradient_color(value, size)
                        pygame.draw.rect(self.screen, color, rect)

                    pygame.draw.rect(self.screen, config.WHITE, rect, 2)
                    self.draw_text_with_shadow(str(value), rect)
                else:
                    # Ô trống
                    pygame.draw.rect(self.screen, (220, 220, 220), rect)
                    pygame.draw.rect(self.screen, (200, 200, 200), rect, 2)

    def draw_ui(self, move_count: int, time_str: str, is_playing: bool):
        """Vẽ thông tin game (Số bước, Thời gian, Thông báo Thắng)."""
        time_text = self.font_medium.render(f"Time: {time_str}", True, config.TEXT_COLOR)
        move_text = self.font_medium.render(f"Moves: {move_count}", True, config.TEXT_COLOR)

        # Đẩy Time và Moves lên cao (Y = 20)
        self.screen.blit(time_text, (30, 20))
        self.screen.blit(move_text, (config.WINDOW_WIDTH - 150, 20))

        # Nếu thắng (không còn chơi nữa) thì hiện thông báo
        if not is_playing:
            win_text = self.font_large.render("YOU WON!", True, (255, 105, 180))
            self.screen.blit(win_text, (config.WINDOW_WIDTH//2 - 100, 100))