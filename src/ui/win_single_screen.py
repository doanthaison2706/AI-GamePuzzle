import pygame
from configs import game_config as config

class WinSingleScreen:
    def __init__(self, screen, result_data):
        self.screen = screen

        # Nhận dữ liệu kết quả từ ván game vừa kết thúc
        self.time_str = result_data.get("time", "00:00")
        self.moves = result_data.get("moves", 0)
        self.size = result_data.get("size", 4)

        # --- LOAD ASSETS ---
        try:
            self.bg_img = pygame.image.load("assets/images/bg_win.png").convert()
            self.bg_img = pygame.transform.scale(self.bg_img, self.screen.get_size())
        except:
            self.bg_img = None

        try:
            self.title_banner = pygame.image.load("assets/images/title_win_banner.png").convert_alpha()
        except:
            self.title_banner = None

        # --- LOAD FONTS ---
        try:
            self.font_title = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", 36)
            self.font_sub = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", 20)
            self.font_stat_lbl = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", 16)
            self.font_stat_val = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", 38)
            self.font_btn = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", 18)
        except:
            self.font_title = pygame.font.SysFont("arial", 36, bold=True)
            self.font_sub = pygame.font.SysFont("arial", 20, bold=True)
            self.font_stat_lbl = pygame.font.SysFont("arial", 16, bold=True)
            self.font_stat_val = pygame.font.SysFont("arial", 38, bold=True)
            self.font_btn = pygame.font.SysFont("arial", 18, bold=True)

        # --- KHỞI TẠO NÚT BẤM ---
        btn_w, btn_h = 140, 50
        spacing = 20
        total_w = (btn_w * 3) + (spacing * 2)
        start_x = (config.WINDOW_WIDTH - total_w) // 2
        btn_y = config.WINDOW_HEIGHT - 100

        self.rect_replay = pygame.Rect(start_x, btn_y, btn_w, btn_h)
        self.rect_setup = pygame.Rect(start_x + btn_w + spacing, btn_y, btn_w, btn_h)
        self.rect_menu = pygame.Rect(start_x + (btn_w + spacing) * 2, btn_y, btn_w, btn_h)

        # Bảng màu Gradient kẹo ngọt cho 3 nút
        self.colors = {
            "orange": {"top": (255, 210, 130), "bot": (255, 175, 85), "shad": (220, 140, 60)},
            "blue":   {"top": (150, 220, 255), "bot": (100, 190, 240), "shad": (80, 160, 210)},
            "purple": {"top": (220, 180, 255), "bot": (190, 140, 240), "shad": (160, 110, 210)}
        }

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if self.rect_replay.collidepoint(mouse_pos):
                    return "PLAYING", None # Trả về lệnh chơi lại ván y hệt
                elif self.rect_setup.collidepoint(mouse_pos):
                    return "SETUP_SINGLE", None # Quay về màn hình cấu hình trận mới
                elif self.rect_menu.collidepoint(mouse_pos):
                    return "MENU", None # Quay về màn hình chính
        return "WIN_SINGLE", None

    def draw_gradient_rect(self, surface, rect, color_top, color_bottom, radius, shadow_color=None):
        """Hàm vẽ nút xịn xò với bóng đổ"""
        if shadow_color:
            shadow_rect = pygame.Rect(rect.x, rect.y + 6, rect.width, rect.height)
            pygame.draw.rect(surface, shadow_color, shadow_rect, border_radius=radius)

        grad_surf = pygame.Surface((1, 2), pygame.SRCALPHA)
        grad_surf.set_at((0, 0), color_top)
        grad_surf.set_at((0, 1), color_bottom)
        grad_surf = pygame.transform.smoothscale(grad_surf, (rect.width, rect.height))

        mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)
        grad_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(grad_surf, rect.topleft)

    def draw_pill_button(self, surface, rect, text, color_theme):
        self.draw_gradient_rect(surface, rect, color_theme["top"], color_theme["bot"], rect.height//2, color_theme["shad"])
        # Viền trắng nổi bật
        pygame.draw.rect(surface, (255, 255, 255), rect, border_radius=rect.height//2, width=2)

        # Chữ có bóng mờ
        txt_shad = self.font_btn.render(text, True, color_theme["shad"])
        txt_surf = self.font_btn.render(text, True, (255, 255, 255))
        txt_rect = txt_surf.get_rect(center=rect.center)

        surface.blit(txt_shad, (txt_rect.x, txt_rect.y + 1))
        surface.blit(txt_surf, txt_rect)

    def draw_stat_box(self, center_x, y, label, value):
        """Vẽ từng ô vuông bo tròn chứa thông số bên trong Panel"""
        box_w, box_h = 130, 100
        box_rect = pygame.Rect(center_x - box_w//2, y, box_w, box_h)

        # Nền ô thông số (trắng kem) + Viền hồng nhạt
        pygame.draw.rect(self.screen, (255, 252, 248), box_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 210, 210), box_rect, border_radius=15, width=2)

        # Tiêu đề (THỜI GIAN, DI CHUYỂN, CẤP ĐỘ)
        lbl_surf = self.font_stat_lbl.render(label, True, (160, 110, 130))
        self.screen.blit(lbl_surf, lbl_surf.get_rect(centerx=center_x, top=box_rect.y + 15))

        # Giá trị thông số (màu đỏ gạch nổi bật)
        val_surf = self.font_stat_val.render(str(value), True, (230, 100, 100))
        self.screen.blit(val_surf, val_surf.get_rect(centerx=center_x, bottom=box_rect.bottom - 10))

    def render(self):
        screen_w, screen_h = self.screen.get_size()
        center_x = screen_w // 2

        # 1. NỀN & TITLE
        if self.bg_img: self.screen.blit(self.bg_img, (0, 0))
        else: self.screen.fill((255, 240, 235))

        if self.title_banner:
            self.screen.blit(self.title_banner, (center_x - self.title_banner.get_width()//2, 40))
        else:
            title_txt = self.font_title.render("CHÚC MỪNG!", True, (240, 100, 120))
            sub_txt = self.font_sub.render("BẠN ĐÃ HOÀN THÀNH BÀN CỜ!", True, (80, 160, 140))
            self.screen.blit(title_txt, title_txt.get_rect(centerx=center_x, top=50))
            self.screen.blit(sub_txt, sub_txt.get_rect(centerx=center_x, top=100))

        # 2. PANEL THÔNG SỐ (Bảng to bo tròn ở giữa)
        panel_w, panel_h = 460, 140
        panel_rect = pygame.Rect(center_x - panel_w//2, 160, panel_w, panel_h)

        # Bóng đổ Panel
        pygame.draw.rect(self.screen, (245, 215, 215), (panel_rect.x, panel_rect.y + 8, panel_w, panel_h), border_radius=25)
        # Nền Panel màu kem mờ mờ
        pygame.draw.rect(self.screen, (255, 245, 235), panel_rect, border_radius=25)
        # Viền Panel
        pygame.draw.rect(self.screen, (255, 200, 200), panel_rect, border_radius=25, width=3)

        # 3 Ô con bên trong Panel
        box_spacing = 150
        self.draw_stat_box(center_x - box_spacing, panel_rect.y + 20, "THỜI GIAN", self.time_str)
        self.draw_stat_box(center_x, panel_rect.y + 20, "DI CHUYỂN", self.moves)
        self.draw_stat_box(center_x + box_spacing, panel_rect.y + 20, "CẤP ĐỘ", f"{self.size}x{self.size}")

        # 3. 3 NÚT BẤM DƯỚI ĐÁY
        self.draw_pill_button(self.screen, self.rect_replay, "TRẬN MỚI", self.colors["orange"])
        self.draw_pill_button(self.screen, self.rect_setup, "CHỌN MÀN", self.colors["blue"])
        self.draw_pill_button(self.screen, self.rect_menu, "THOÁT", self.colors["purple"])