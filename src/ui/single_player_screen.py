import pygame
import os
from configs import game_config as config
from src.core.single_game_manager import SingleGameManager as GameManager
from src.ui.renderer import Renderer
from src.utils.image_crop import slice_image

class SinglePlayerScreen:
    def __init__(self, screen, setup_data):
        self.screen = screen
        self.renderer = Renderer(screen)

        self.size = setup_data["size"]
        self.full_image = setup_data.get("image", None)
        self.image_slices = None

        if self.full_image:
            _, self.image_slices = slice_image(self.full_image, config.BOARD_SIZE, self.size)

        self.gm = GameManager(size=self.size)
        self.gm.new_game()
        self.player = self.gm.players[0]
        self.board = self.gm.board
        self.show_full_image = False

        # Biến Kỷ lục (Giả lập tạm, bạn có thể lưu file sau)
        self.best_score = 35
        self.is_paused = False

        # --- CHỈ CẦN THÊM ĐÚNG 2 DÒNG NÀY VÀO ĐÂY LÀ HẾT CRASH ---
        self.is_winning = False   # Cờ đánh dấu đã xếp xong/bấm W
        self.win_start_time = 0   # Lưu thời điểm bắt đầu thắng

        try:
            self.move_sound = pygame.mixer.Sound("assets/sounds/move.wav")
        except:
            self.move_sound = None

        # --- 1. LOAD ẢNH (BG, TITLE, KHUNG GỖ) ---
        try:
            self.bg_img = pygame.image.load("assets/images/bg_play.png").convert()
            self.bg_img = pygame.transform.scale(self.bg_img, self.screen.get_size())
        except:
            self.bg_img = None

        try:
            self.title_img = pygame.image.load("assets/images/title_single.png").convert_alpha()
        except:
            self.title_img = None

        try:
            self.wood_frame_img = pygame.image.load("assets/images/wood_frame.png").convert_alpha()
            # Giả sử khung gỗ to hơn bàn cờ một chút (padding 20px mỗi cạnh)
            frame_size = config.BOARD_SIZE + 40
            self.wood_frame_img = pygame.transform.smoothscale(self.wood_frame_img, (frame_size, frame_size))
        except:
            self.wood_frame_img = None

        # --- 2. LOAD FONTS ---
        try:
            self.font_stat = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", 20)
            self.font_btn = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", 16)
        except:
            self.font_stat = pygame.font.SysFont("arial", 20, bold=True)
            self.font_btn = pygame.font.SysFont("arial", 14, bold=True)

        # --- 3. KHỞI TẠO 6 NÚT BẤM (Theo màu ảnh gốc) ---
        btn_w, btn_h = 90, 85
        spacing = 15
        total_w = (btn_w * 6) + (spacing * 5)
        start_x = (config.WINDOW_WIDTH - total_w) // 2
        btn_y = config.WINDOW_HEIGHT - 110 # Cách đáy 110px

        # Cấu trúc: [Tên biến Rect, Text, Màu Top, Màu Bot, Màu Shadow]
        self.buttons = [
            {"rect": pygame.Rect(start_x, btn_y, btn_w, btn_h), "text": "GỢI Ý",
             "c_top": (255, 230, 190), "c_bot": (255, 204, 150), "c_shad": (230, 180, 120)},

            {"rect": pygame.Rect(start_x + (btn_w+spacing)*1, btn_y, btn_w, btn_h), "text": "AI GIẢI",
             "c_top": (190, 240, 255), "c_bot": (135, 215, 245), "c_shad": (110, 190, 220)},

            {"rect": pygame.Rect(start_x + (btn_w+spacing)*2, btn_y, btn_w, btn_h), "text": "HOÀN TÁC",
             "c_top": (210, 250, 200), "c_bot": (160, 230, 150), "c_shad": (130, 200, 120)},

            {"rect": pygame.Rect(start_x + (btn_w+spacing)*3, btn_y, btn_w, btn_h), "text": "CHƠI LẠI",
             "c_top": (255, 200, 230), "c_bot": (255, 150, 200), "c_shad": (220, 120, 170)},

            {"rect": pygame.Rect(start_x + (btn_w+spacing)*4, btn_y, btn_w, btn_h), "text": "TẠM DỪNG",
             "c_top": (200, 210, 255), "c_bot": (150, 170, 255), "c_shad": (120, 140, 220)},

            {"rect": pygame.Rect(start_x + (btn_w+spacing)*5, btn_y, btn_w, btn_h), "text": "THOÁT",
             "c_top": (255, 190, 190), "c_bot": (255, 140, 140), "c_shad": (220, 110, 110)}
        ]

    def handle_events(self, events):
        # --- 1. KIỂM TRA DELAY KHI THẮNG GAME (Chạy mỗi frame) ---
        if self.is_winning:
            # Đợi đủ 1500 mili-giây (1.5 giây) thì mới chuyển cảnh
            if pygame.time.get_ticks() - self.win_start_time >= 1500:
                result_data = {
                    "time": self.gm.get_formatted_time(),
                    "moves": self.player.move_count,
                    "size": self.size
                }
                return "WIN_SINGLE", result_data

            # Trong lúc đang delay chờ chuyển cảnh -> KHÓA thao tác, không cho bấm gì nữa
            return "PLAYING"

        # --- 2. XỬ LÝ SỰ KIỆN CHUỘT/PHÍM BÌNH THƯỜNG ---
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.show_full_image = True
            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                self.show_full_image = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if self.buttons[0]["rect"].collidepoint(mouse_pos): pass # Gợi ý
                if self.buttons[1]["rect"].collidepoint(mouse_pos): pass # AI Giải
                if self.buttons[2]["rect"].collidepoint(mouse_pos): pass # Hoàn tác
                if self.buttons[3]["rect"].collidepoint(mouse_pos): self.gm.new_game() # Chơi lại
                if self.buttons[4]["rect"].collidepoint(mouse_pos): self.is_paused = not self.is_paused # Tạm dừng
                if self.buttons[5]["rect"].collidepoint(mouse_pos): return "MENU" # Thoát

            # ---- [CHEAT KEY] Bấm phím 'W' để kích hoạt THẮNG ----
            if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                self.is_winning = True
                self.win_start_time = pygame.time.get_ticks() # Bắt đầu bấm giờ
                self.show_full_image = True # Bật full ảnh lên cho người chơi ngắm
                self.gm.is_playing = False  # Dừng đồng hồ đếm giờ ngay lập tức
                continue # Bỏ qua các sự kiện khác

            # Trượt gạch
            if self.gm.is_playing and not self.show_full_image and not self.is_paused:
                move_success = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    if config.MARGIN_LEFT <= mx <= config.MARGIN_LEFT + config.BOARD_SIZE and \
                       config.MARGIN_TOP <= my <= config.MARGIN_TOP + config.BOARD_SIZE:
                        t_size = config.BOARD_SIZE // self.board.size
                        move_success = self.gm.process_move((my - config.MARGIN_TOP) // t_size, (mx - config.MARGIN_LEFT) // t_size)

                if event.type == pygame.KEYDOWN:
                    er, ec = self.board.get_empty_pos()
                    tr, tc = er, ec
                    if event.key in (pygame.K_w, pygame.K_UP): tr -= 1
                    elif event.key in (pygame.K_s, pygame.K_DOWN): tr += 1
                    elif event.key in (pygame.K_a, pygame.K_LEFT): tc -= 1
                    elif event.key in (pygame.K_d, pygame.K_RIGHT): tc += 1
                    if (tr, tc) != (er, ec): move_success = self.gm.process_move(tr, tc)

                if move_success:
                    if self.move_sound: self.move_sound.play()

                    # --- XỬ LÝ THẮNG THẬT (Tự chơi xếp xong) ---
                    # Giả sử GameManager của bạn set is_playing = False khi bảng đã được xếp đúng
                    if not self.gm.is_playing:
                        self.is_winning = True
                        self.win_start_time = pygame.time.get_ticks()
                        self.show_full_image = True

        return "PLAYING"

    def update(self):
        if self.gm and not self.is_paused:
            self.gm.update_time()

    def draw_gradient_rect(self, surface, rect, color_top, color_bottom, radius, shadow_color=None, shadow_offset=6, border_color=None):
        """Hàm vẽ nút xịn xò"""
        if shadow_color:
            shadow_rect = pygame.Rect(rect.x, rect.y + shadow_offset, rect.width, rect.height)
            pygame.draw.rect(surface, shadow_color, shadow_rect, border_radius=radius)

        grad_surf = pygame.Surface((1, 2), pygame.SRCALPHA)
        grad_surf.set_at((0, 0), color_top)
        grad_surf.set_at((0, 1), color_bottom)
        grad_surf = pygame.transform.smoothscale(grad_surf, (rect.width, rect.height))

        mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)
        grad_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(grad_surf, rect.topleft)

        if border_color:
            pygame.draw.rect(surface, border_color, rect, border_radius=radius, width=2)

    def draw_top_stat_pill(self, x, y, width, text, icon_color, text_color, is_record=False):
        """Vẽ viên thuốc chứa thông số ở góc trên"""
        rect = pygame.Rect(x, y, width, 40)
        # Nếu là kỷ lục thì vẽ màu hồng, còn lại vẽ màu xanh nhạt/trắng
        bg_color = (255, 220, 230) if is_record else (235, 245, 255)
        border_color = (255, 180, 200) if is_record else (200, 225, 255)

        pygame.draw.rect(self.screen, bg_color, rect, border_radius=20)
        pygame.draw.rect(self.screen, border_color, rect, border_radius=20, width=2)

        surf = self.font_stat.render(text, True, text_color)
        self.screen.blit(surf, surf.get_rect(center=rect.center))

    def render(self):
        screen_w, screen_h = self.screen.get_size()

        # 1. VẼ NỀN
        if self.bg_img: self.screen.blit(self.bg_img, (0, 0))
        else: self.screen.fill((255, 246, 233))

        # 2. VẼ TITLE
        if self.title_img:
            self.screen.blit(self.title_img, (screen_w//2 - self.title_img.get_width()//2, 10))
        else:
            title_txt = self.font_stat.render("CHƠI ĐƠN", True, (0, 120, 120))
            self.screen.blit(title_txt, (screen_w//2 - title_txt.get_width()//2, 25))

        # 3. VẼ TOP STATS (Thời gian, Cấp độ, Bước, Kỷ lục)
        stat_y = 80
        color_text_blue = (50, 100, 150)
        color_text_red = (200, 80, 100)

        self.draw_top_stat_pill(80, stat_y, 140, f"00:00", color_text_blue, color_text_blue) # Thay bằng biến time sau
        self.draw_top_stat_pill(240, stat_y, 140, f"CẤP ĐỘ: {self.size}x{self.size}", color_text_blue, color_text_blue)
        self.draw_top_stat_pill(400, stat_y, 160, f"DI CHUYỂN: {self.player.move_count}", color_text_red, color_text_red)
        self.draw_top_stat_pill(580, stat_y, 140, f"KỶ LỤC: {self.best_score}", color_text_red, color_text_red, is_record=True)

        # 4. VẼ KHUNG GỖ & BÀN CỜ
        # Canh giữa khung gỗ theo lề trái/trên của config
        if self.wood_frame_img:
            frame_x = config.MARGIN_LEFT - 20
            frame_y = config.MARGIN_TOP - 20
            self.screen.blit(self.wood_frame_img, (frame_x, frame_y))
        else:
            # Vẽ nền giả lập khung gỗ nếu chưa có ảnh
            pygame.draw.rect(self.screen, (220, 180, 140),
                             (config.MARGIN_LEFT-20, config.MARGIN_TOP-20, config.BOARD_SIZE+40, config.BOARD_SIZE+40), border_radius=20)
            pygame.draw.rect(self.screen, (180, 130, 90),
                             (config.MARGIN_LEFT-20, config.MARGIN_TOP-20, config.BOARD_SIZE+40, config.BOARD_SIZE+40), border_radius=20, width=4)

        # Gọi Renderer vẽ các mảnh gạch (Tiles) đè lên Khung Gỗ
        # LƯU Ý: Phải xóa các hàm vẽ UI cũ trong Renderer đi, chỉ giữ lại hàm vẽ Tiles thôi nhé!
        self.renderer.draw_board(self.board.matrix, self.gm.size, self.image_slices, self.full_image, self.show_full_image)

        # Nền mờ nếu đang Tạm dừng
        if self.is_paused:
            overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 150))
            self.screen.blit(overlay, (0, 0))
            pause_txt = self.font_stat.render("ĐÃ TẠM DỪNG", True, (200, 80, 100))
            self.screen.blit(pause_txt, pause_txt.get_rect(center=(screen_w//2, screen_h//2)))

        # 5. VẼ 6 NÚT CÔNG CỤ Ở DƯỚI ĐÁY
        for btn in self.buttons:
            # Vẽ hình dạng nút
            self.draw_gradient_rect(self.screen, btn["rect"], btn["c_top"], btn["c_bot"], 20,
                                    shadow_color=btn["c_shad"], shadow_offset=5, border_color=(255, 255, 255))

            # Vẽ Text ở mép dưới của nút
            txt_surf = self.font_btn.render(btn["text"], True, (255, 255, 255))
            txt_rect = txt_surf.get_rect(centerx=btn["rect"].centerx, bottom=btn["rect"].bottom - 10)

            # Đổ bóng chữ để dễ đọc
            txt_shadow = self.font_btn.render(btn["text"], True, btn["c_shad"])
            self.screen.blit(txt_shadow, (txt_rect.x, txt_rect.y + 1))
            self.screen.blit(txt_surf, txt_rect)

            # (Tương lai) Dành chỗ trống ở nửa trên của nút để vẽ Icon