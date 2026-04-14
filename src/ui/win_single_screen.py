import pygame
from configs import game_config as config
from src.ui.components import PillButton

class WinSingleScreen:
    def __init__(self, screen, result_data):
        self.screen = screen

        # Nhận dữ liệu kết quả từ ván game vừa kết thúc
        self.time_str = result_data.get("time", "00:00")
        self.moves = result_data.get("moves", 0)
        self.size = result_data.get("size", 4)
        self.is_solved = result_data.get("is_solved", True)

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

        self.btn_replay = PillButton(
            (start_x, btn_y, btn_w, btn_h), "TRẬN MỚI", self.font_btn,
            color_top=(255, 210, 130), color_bot=(255, 175, 85), shadow_color=(220, 140, 60),
        )
        self.btn_setup = PillButton(
            (start_x + btn_w + spacing, btn_y, btn_w, btn_h), "CHỌ N MÀN", self.font_btn,
            color_top=(150, 220, 255), color_bot=(100, 190, 240), shadow_color=(80, 160, 210),
        )
        self.btn_menu = PillButton(
            (start_x + (btn_w + spacing) * 2, btn_y, btn_w, btn_h), "THOÁT", self.font_btn,
            color_top=(220, 180, 255), color_bot=(190, 140, 240), shadow_color=(160, 110, 210),
        )

    def handle_events(self, events):
        for event in events:
            if self.btn_replay.handle_event(event): return "PLAYING", None
            if self.btn_setup.handle_event(event):  return "SETUP_SINGLE", None
            if self.btn_menu.handle_event(event):   return "MENU", None
        return "WIN_SINGLE", None

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

        if self.title_banner and self.is_solved:
            self.screen.blit(self.title_banner, (center_x - self.title_banner.get_width()//2, 40))
        else:
            title_text = "CHÚC MỪNG!" if self.is_solved else "RẤT TIẾC!"
            sub_text = "BẠN ĐÃ HOÀN THÀNH BÀN CỜ!" if self.is_solved else "BẠN CHƯA GIẢI ĐƯỢC BÀN CỜ NÀY!"
            title_color = (240, 100, 120) if self.is_solved else (100, 120, 240)
            sub_color = (80, 160, 140) if self.is_solved else (160, 80, 80)

            title_txt = self.font_title.render(title_text, True, title_color)
            sub_txt = self.font_sub.render(sub_text, True, sub_color)
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
        mouse = pygame.mouse.get_pos()
        self.btn_replay.draw(self.screen, mouse)
        self.btn_setup.draw(self.screen, mouse)
        self.btn_menu.draw(self.screen, mouse)