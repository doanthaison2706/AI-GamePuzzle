import pygame
import os
from configs import game_config as config
from src.utils.image_crop import open_file_dialog
from src.ui.crop_menu import CropImageMenu

class SetupSingleScreen:
    def __init__(self, screen):
        self.screen = screen
        self.selected_size = 4
        self.selected_time = 0
        self.image_mode = "DEFAULT"
        self.full_image = None

        # --- BẢNG MÀU GRADIENT & SHADOW ---
        # Panel
        self.color_panel_top = (255, 252, 246)
        self.color_panel_bot = (255, 240, 225)
        self.color_panel_border = (248, 186, 186)

        # Chữ
        self.color_text_title = (205, 92, 92)
        self.color_text_inactive = (196, 120, 120)
        self.color_text_active = (255, 255, 255)

        # Nút Inactive (Chưa chọn) - Vàng kem
        self.color_btn_in_top = (255, 248, 238)
        self.color_btn_in_bot = (248, 233, 213)
        self.color_btn_in_shadow = (235, 215, 190)

        # Nút Active (Đã chọn) - Xanh mint
        self.color_btn_ac_top = (165, 240, 210)
        self.color_btn_ac_bot = (132, 220, 187)
        self.color_btn_ac_shadow = (110, 200, 165)

        # Nút Bắt đầu - Hồng kẹo ngọt
        self.color_btn_st_top = (255, 175, 198)
        self.color_btn_st_bot = (246, 143, 168)
        self.color_btn_st_shadow = (220, 120, 145)

        # --- LOAD ASSETS & FONTS ---
        try:
            self.bg_img = pygame.image.load("assets/images/bg_setup_new.png").convert()
            self.bg_img = pygame.transform.scale(self.bg_img, self.screen.get_size())
        except:
            self.bg_img = None

        try:
            self.font_label = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", 22)
            self.font_btn = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", 20)
            self.font_start = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", 35)
        except:
            self.font_label = pygame.font.SysFont("arial", 22, bold=True)
            self.font_btn = pygame.font.SysFont("arial", 18, bold=True)
            self.font_start = pygame.font.SysFont("arial", 30, bold=True)

        self.rects_size = {3: None, 4: None, 5: None, 6: None}
        self.rects_time = {0: None, 120: None, 300: None, 600: None}
        self.rects_img = {"DEFAULT": None, "CUSTOM": None}
        self.rect_start = None
        self.rect_back = None

    def handle_events(self, events):
        # ... (Phần logic handle_events giữ nguyên 100% như code cũ bạn nhé) ...
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                for size, rect in self.rects_size.items():
                    if rect and rect.collidepoint(mouse_pos): self.selected_size = size
                for time_val, rect in self.rects_time.items():
                    if rect and rect.collidepoint(mouse_pos): self.selected_time = time_val
                if self.rects_img["DEFAULT"] and self.rects_img["DEFAULT"].collidepoint(mouse_pos):
                    self.image_mode = "DEFAULT"
                    self.full_image = None
                if self.rects_img["CUSTOM"] and self.rects_img["CUSTOM"].collidepoint(mouse_pos):
                    file_path = open_file_dialog()
                    if file_path:

                        crop_ui = CropImageMenu(self.screen, file_path, config.BOARD_SIZE)
                        cropped = crop_ui.run()

                        if cropped:
                            self.full_image = cropped
                            self.image_mode = "CUSTOM"
                if self.rect_start and self.rect_start.collidepoint(mouse_pos):
                    setup_data = {
                        "size": self.selected_size,
                        "time": self.selected_time,
                        "image": self.full_image if self.image_mode == "CUSTOM" else None
                    }
                    return "PLAYING", setup_data
                if self.rect_back and self.rect_back.collidepoint(mouse_pos):
                    return "MENU", None
        return "SETUP_SINGLE", None

    def draw_gradient_rect(self, surface, rect, color_top, color_bottom, radius, shadow_color=None, shadow_offset=6, border_color=None, border_width=0):
        """Hàm siêu xịn: Vẽ hình chữ nhật bo tròn có gradient và bóng đổ"""
        # 1. Vẽ bóng (Shadow)
        if shadow_color:
            shadow_rect = pygame.Rect(rect.x, rect.y + shadow_offset, rect.width, rect.height)
            pygame.draw.rect(surface, shadow_color, shadow_rect, border_radius=radius)

        # 2. Tạo Gradient Surface
        grad_surf = pygame.Surface((1, 2), pygame.SRCALPHA)
        grad_surf.set_at((0, 0), color_top)
        grad_surf.set_at((0, 1), color_bottom)
        grad_surf = pygame.transform.smoothscale(grad_surf, (rect.width, rect.height))

        # 3. Tạo Mask bo tròn
        mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)

        # 4. Ép Mask vào Gradient
        grad_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # 5. In lên màn hình
        surface.blit(grad_surf, rect.topleft)

        # 6. Vẽ viền (Nếu có)
        if border_color and border_width > 0:
            pygame.draw.rect(surface, border_color, rect, border_radius=radius, width=border_width)

    def draw_pill_button(self, surface, rect, text, is_active, font, btn_type="normal"):
        """Sử dụng hàm draw_gradient_rect để tạo nút"""
        if btn_type == "start":
            c_top, c_bot = self.color_btn_st_top, self.color_btn_st_bot
            c_shadow = self.color_btn_st_shadow
            txt_color = self.color_text_active
            border_color, border_width = None, 0
        else:
            if is_active:
                c_top, c_bot = self.color_btn_ac_top, self.color_btn_ac_bot
                c_shadow = self.color_btn_ac_shadow
                txt_color = self.color_text_active
                border_color, border_width = None, 0
            else:
                c_top, c_bot = self.color_btn_in_top, self.color_btn_in_bot
                c_shadow = self.color_btn_in_shadow
                txt_color = self.color_text_inactive
                border_color, border_width = (235, 205, 185), 3 # Viền mỏng cho nút chưa chọn

        radius = rect.height // 2
        self.draw_gradient_rect(surface, rect, c_top, c_bot, radius, c_shadow, 6, border_color, border_width)

        text_surf = font.render(text, True, txt_color)
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)

    def render(self):
        screen_w, screen_h = self.screen.get_size()
        center_x = screen_w // 2

        if self.bg_img: self.screen.blit(self.bg_img, (0, 0))
        else: self.screen.fill((255, 230, 235))

        # 1. BẢNG ĐIỀU KHIỂN (Cũng dùng Gradient cho xịn)
        panel_w, panel_h = int(screen_w * 0.85), int(screen_h * 0.78)
        panel_rect = pygame.Rect(center_x - panel_w//2, int(screen_h * 0.12), panel_w, panel_h)
        self.draw_gradient_rect(self.screen, panel_rect, self.color_panel_top, self.color_panel_bot, 25,
                                shadow_color=(240, 210, 210), shadow_offset=8, border_color=self.color_panel_border, border_width=4)

        # 2. BOX TIÊU ĐỀ
        title_surf = self.font_start.render("TÙY CHỈNH TRẬN ĐẤU", True, self.color_text_active)
        box_w, box_h = title_surf.get_width() + 80, title_surf.get_height() + 20
        box_rect = pygame.Rect(center_x - box_w//2, panel_rect.y - box_h//2, box_w, box_h)
        self.draw_gradient_rect(self.screen, box_rect, self.color_btn_st_top, self.color_btn_st_bot, 20,
                                shadow_color=self.color_btn_st_shadow, shadow_offset=6, border_color=(255, 200, 210), border_width=4)
        self.screen.blit(title_surf, (center_x - title_surf.get_width()//2, box_rect.y + 8))

        def draw_section_label(text, y_pos):
            lbl_surf = self.font_label.render(text, True, self.color_text_title)
            self.screen.blit(lbl_surf, (panel_rect.x + 40, y_pos))

        current_y = panel_rect.y + 60

        # 3. KÍCH THƯỚC BÀN CỜ
        draw_section_label("KÍCH THƯỚC BÀN CỜ", current_y)
        current_y += 45
        btn_w, btn_h, spacing, start_x = 90, 50, 25, panel_rect.x + 40
        for i, size in enumerate([3, 4, 5, 6]):
            rect = pygame.Rect(start_x + i * (btn_w + spacing), current_y, btn_w, btn_h)
            self.rects_size[size] = rect
            self.draw_pill_button(self.screen, rect, f"{size}x{size}", self.selected_size == size, self.font_btn)

        current_y += 85

        # 4. THỜI GIAN
        draw_section_label("THỜI GIAN / VÁN", current_y)
        current_y += 45
        time_options = [(0, "KHÔNG GIỚI HẠN"), (120, "2:00"), (300, "5:00"), (600, "10:00")]
        t_start_x = panel_rect.x + 40
        for i, (val, text) in enumerate(time_options):
            t_w = 200 if val == 0 else 85
            rect = pygame.Rect(t_start_x, current_y, t_w, btn_h)
            self.rects_time[val] = rect
            self.draw_pill_button(self.screen, rect, text, self.selected_time == val, self.font_btn)
            t_start_x += t_w + spacing

        current_y += 85

        # 5. HÌNH ẢNH SỬ DỤNG
        draw_section_label("HÌNH ẢNH SỬ DỤNG", current_y)
        current_y += 45
        rect_default = pygame.Rect(panel_rect.x + 40, current_y, 140, btn_h)
        self.rects_img["DEFAULT"] = rect_default
        self.draw_pill_button(self.screen, rect_default, "MẶC ĐỊNH", self.image_mode == "DEFAULT", self.font_btn)

        rect_custom = pygame.Rect(panel_rect.x + 200, current_y, 200, btn_h)
        self.rects_img["CUSTOM"] = rect_custom
        self.draw_pill_button(self.screen, rect_custom, "CHỌN ẢNH CROP", self.image_mode == "CUSTOM", self.font_btn)

        if self.full_image and self.image_mode == "CUSTOM":
            thumb_size = 220
            thumb = pygame.transform.smoothscale(self.full_image, (thumb_size, thumb_size))
            thumb_x, thumb_y = rect_custom.centerx - (thumb_size // 2), current_y + btn_h + 15
            pygame.draw.rect(self.screen, (220, 190, 190), (thumb_x - 6, thumb_y - 2, thumb_size + 12, thumb_size + 12), border_radius=12)
            pygame.draw.rect(self.screen, (255, 255, 255), (thumb_x - 6, thumb_y - 6, thumb_size + 12, thumb_size + 12), border_radius=12)
            self.screen.blit(thumb, (thumb_x, thumb_y - 3))

        # 6. NÚT QUAY LẠI VÀ BẮT ĐẦU
        btn_bottom_y = panel_rect.bottom - 85
        self.rect_back = pygame.Rect(panel_rect.x + 40, btn_bottom_y, 150, 60)
        self.draw_pill_button(self.screen, self.rect_back, "QUAY LẠI", False, self.font_btn)

        self.rect_start = pygame.Rect(panel_rect.right - 240, btn_bottom_y, 200, 65)
        self.draw_pill_button(self.screen, self.rect_start, "BẮT ĐẦU", True, self.font_start, btn_type="start")

class SetupMultiScreen:
    def __init__(self, screen):
        self.screen = screen

        # --- TRẠNG THÁI LỰA CHỌN (MULTI) ---
        self.selected_size = 4
        self.selected_time = 0
        self.selected_score = 3          # Mặc định chạm mốc 3 điểm sẽ thắng [cite: 57]
        self.image_mode = "DEFAULT"
        self.full_image = None

        # --- BẢNG MÀU GRADIENT XUYÊN TÂM (Đậm viền -> Nhạt giữa) ---
        self.color_panel_bg = (255, 246, 233)
        self.color_panel_border = (248, 186, 186)
        self.color_text_title = (205, 92, 92)
        self.color_text_inactive = (196, 120, 120)
        self.color_text_active = (255, 255, 255)

        # Nút Inactive (Chưa chọn)
        self.color_btn_in_edge = (235, 215, 190)
        self.color_btn_in_center = (255, 252, 246)
        self.color_btn_in_shadow = (225, 205, 180)

        # Nút Active (Đã chọn)
        self.color_btn_ac_edge = (110, 200, 165)
        self.color_btn_ac_center = (180, 245, 220)
        self.color_btn_ac_shadow = (95, 185, 150)

        # Nút Bắt đầu
        self.color_btn_st_edge = (230, 110, 140)
        self.color_btn_st_center = (255, 185, 205)
        self.color_btn_st_shadow = (210, 95, 125)

        # --- LOAD ASSETS & FONTS ---
        try:
            self.bg_img = pygame.image.load("assets/images/bg_setup_new.png").convert()
            self.bg_img = pygame.transform.scale(self.bg_img, self.screen.get_size())
        except:
            self.bg_img = None

        try:
            self.font_label = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", 20) # Giảm font xíu để nhét vừa 4 mục
            self.font_btn = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", 18)
            self.font_start = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", 32)
        except:
            self.font_label = pygame.font.SysFont("arial", 20, bold=True)
            self.font_btn = pygame.font.SysFont("arial", 18, bold=True)
            self.font_start = pygame.font.SysFont("arial", 30, bold=True)

        self.rects_size = {3: None, 4: None, 5: None, 6: None}
        self.rects_time = {0: None, 120: None, 300: None, 600: None}
        self.rects_score = {1: None, 3: None, 5: None} # Thêm rect cho Điểm số
        self.rects_img = {"DEFAULT": None, "CUSTOM": None}
        self.rect_start = None
        self.rect_back = None

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                for size, rect in self.rects_size.items():
                    if rect and rect.collidepoint(mouse_pos): self.selected_size = size

                for time_val, rect in self.rects_time.items():
                    if rect and rect.collidepoint(mouse_pos): self.selected_time = time_val

                # Bắt sự kiện chọn điểm thắng
                for score_val, rect in self.rects_score.items():
                    if rect and rect.collidepoint(mouse_pos): self.selected_score = score_val

                if self.rects_img["DEFAULT"] and self.rects_img["DEFAULT"].collidepoint(mouse_pos):
                    self.image_mode = "DEFAULT"
                    self.full_image = None

                if self.rects_img["CUSTOM"] and self.rects_img["CUSTOM"].collidepoint(mouse_pos):
                    file_path = open_file_dialog()
                    if file_path:
                        # Thay vì gọi hàm cũ, ta gọi Class UI Cắt ảnh mới
                        crop_ui = CropImageMenu(self.screen, file_path, config.BOARD_SIZE)
                        cropped = crop_ui.run() # Chạy vòng lặp của màn hình cắt ảnh

                        if cropped:
                            self.full_image = cropped
                            self.image_mode = "CUSTOM"

                if self.rect_start and self.rect_start.collidepoint(mouse_pos):
                    setup_data = {
                        "size": self.selected_size,
                        "time": self.selected_time,
                        "score": self.selected_score, # Gửi thêm dữ liệu điểm
                        "image": self.full_image if self.image_mode == "CUSTOM" else None
                    }
                    return "PLAYING_MULTI", setup_data

                if self.rect_back and self.rect_back.collidepoint(mouse_pos):
                    return "MENU", None
        return "SETUP_MULTI", None

    def draw_radial_pill_button(self, surface, rect, text, is_active, font, btn_type="normal"):
        """Vẽ nút với hiệu ứng Gradient từ Đậm ở viền -> Nhạt ở trung tâm"""
        if btn_type == "start":
            c_edge, c_center = self.color_btn_st_edge, self.color_btn_st_center
            c_shadow = self.color_btn_st_shadow
            txt_color = self.color_text_active
        else:
            if is_active:
                c_edge, c_center = self.color_btn_ac_edge, self.color_btn_ac_center
                c_shadow = self.color_btn_ac_shadow
                txt_color = self.color_text_active
            else:
                c_edge, c_center = self.color_btn_in_edge, self.color_btn_in_center
                c_shadow = self.color_btn_in_shadow
                txt_color = self.color_text_inactive

        radius = rect.height // 2

        # 1. Vẽ bóng đổ (Shadow) tạo độ dày
        shadow_rect = pygame.Rect(rect.x, rect.y + 6, rect.width, rect.height)
        pygame.draw.rect(surface, c_shadow, shadow_rect, border_radius=radius)

        # 2. Vẽ viền (Chỉ dành cho nút chưa được chọn)
        if not is_active and btn_type == "normal":
            pygame.draw.rect(surface, (230, 205, 185), rect, border_radius=radius)
            inner_rect = rect.inflate(-4, -4)
            inner_radius = max(2, radius - 2)
        else:
            inner_rect = rect
            inner_radius = radius

        # 3. Vẽ Gradient xuyên tâm bằng cách lồng các khối nhỏ dần
        steps = 8
        for i in range(steps):
            t = i / (steps - 1)
            # Tính toán nội suy màu
            r = int(c_edge[0] + (c_center[0] - c_edge[0]) * t)
            g = int(c_edge[1] + (c_center[1] - c_edge[1]) * t)
            b = int(c_edge[2] + (c_center[2] - c_edge[2]) * t)

            # Thu nhỏ kích thước dần vào giữa
            shrink_x = int((inner_rect.width * 0.1) * t)
            shrink_y = int((inner_rect.height * 0.3) * t)

            current_rect = inner_rect.inflate(-shrink_x * 2, -shrink_y * 2)
            current_radius = max(2, inner_radius - int(max(shrink_x, shrink_y)))

            pygame.draw.rect(surface, (r, g, b), current_rect, border_radius=current_radius)

        # 4. Vẽ Text
        text_surf = font.render(text, True, txt_color)
        text_rect = text_surf.get_rect(center=rect.center)
        # Tạo hiệu ứng chữ in sâu nhẹ cho nút active
        if is_active or btn_type == "start":
            shadow_txt = font.render(text, True, c_edge)
            surface.blit(shadow_txt, (text_rect.x, text_rect.y + 1))
        surface.blit(text_surf, text_rect)

    def render(self):
        screen_w, screen_h = self.screen.get_size()
        center_x = screen_w // 2

        if self.bg_img: self.screen.blit(self.bg_img, (0, 0))
        else: self.screen.fill((255, 230, 235))

        # Bảng điều khiển (Làm cao hơn chút để chứa Điểm Thắng)
        panel_w, panel_h = int(screen_w * 0.85), int(screen_h * 0.82)
        panel_rect = pygame.Rect(center_x - panel_w//2, int(screen_h * 0.10), panel_w, panel_h)

        pygame.draw.rect(self.screen, (240, 210, 210), (panel_rect.x+5, panel_rect.y+8, panel_w, panel_h), border_radius=25)
        pygame.draw.rect(self.screen, self.color_panel_bg, panel_rect, border_radius=25)
        pygame.draw.rect(self.screen, self.color_panel_border, panel_rect, border_radius=25, width=4)

        # BOX TIÊU ĐỀ
        title_surf = self.font_start.render("TÙY CHỈNH ĐỐI KHÁNG", True, self.color_text_active)
        box_w, box_h = title_surf.get_width() + 80, title_surf.get_height() + 20
        box_rect = pygame.Rect(center_x - box_w//2, panel_rect.y - box_h//2, box_w, box_h)

        pygame.draw.rect(self.screen, self.color_btn_st_shadow, (box_rect.x, box_rect.y + 6, box_w, box_h), border_radius=20)
        pygame.draw.rect(self.screen, self.color_btn_st_edge, box_rect, border_radius=20)
        pygame.draw.rect(self.screen, (255, 200, 210), box_rect, border_radius=20, width=4)
        self.screen.blit(title_surf, (center_x - title_surf.get_width()//2, box_rect.y + 8))

        def draw_section_label(text, y_pos):
            lbl_surf = self.font_label.render(text, True, self.color_text_title)
            self.screen.blit(lbl_surf, (panel_rect.x + 40, y_pos))

        current_y = panel_rect.y + 50
        spacing_y = 75 # Giảm khoảng cách giữa các hàng để nhét vừa 4 mục

        # 1. KÍCH THƯỚC BÀN CỜ
        draw_section_label("KÍCH THƯỚC BÀN CỜ", current_y)
        current_y += 35
        btn_w, btn_h, spacing_x, start_x = 85, 45, 20, panel_rect.x + 40
        for i, size in enumerate([3, 4, 5, 6]):
            rect = pygame.Rect(start_x + i * (btn_w + spacing_x), current_y, btn_w, btn_h)
            self.rects_size[size] = rect
            self.draw_radial_pill_button(self.screen, rect, f"{size}x{size}", self.selected_size == size, self.font_btn)

        current_y += spacing_y

        # 2. ĐIỂM THẮNG (Mục mới cho đối kháng)
        draw_section_label("ĐIỂM THẮNG (BEST OF)", current_y)
        current_y += 35
        for i, score in enumerate([1, 3, 5]):
            rect = pygame.Rect(start_x + i * (btn_w + spacing_x), current_y, btn_w, btn_h)
            self.rects_score[score] = rect
            self.draw_radial_pill_button(self.screen, rect, str(score), self.selected_score == score, self.font_btn)

        current_y += spacing_y

        # 3. THỜI GIAN
        draw_section_label("THỜI GIAN / VÁN", current_y)
        current_y += 35
        time_options = [(0, "KHÔNG GIỚI HẠN"), (120, "2:00"), (300, "5:00"), (600, "10:00")]
        t_start_x = panel_rect.x + 40
        for i, (val, text) in enumerate(time_options):
            t_w = 190 if val == 0 else 85
            rect = pygame.Rect(t_start_x, current_y, t_w, btn_h)
            self.rects_time[val] = rect
            self.draw_radial_pill_button(self.screen, rect, text, self.selected_time == val, self.font_btn)
            t_start_x += t_w + spacing_x

        current_y += spacing_y

        # 4. HÌNH ẢNH SỬ DỤNG
        draw_section_label("HÌNH ẢNH SỬ DỤNG CHUNG", current_y)
        current_y += 35
        rect_default = pygame.Rect(panel_rect.x + 40, current_y, 140, btn_h)
        self.rects_img["DEFAULT"] = rect_default
        self.draw_radial_pill_button(self.screen, rect_default, "MẶC ĐỊNH", self.image_mode == "DEFAULT", self.font_btn)

        rect_custom = pygame.Rect(panel_rect.x + 200, current_y, 180, btn_h)
        self.rects_img["CUSTOM"] = rect_custom
        self.draw_radial_pill_button(self.screen, rect_custom, "CHỌN ẢNH", self.image_mode == "CUSTOM", self.font_btn)

        if self.full_image and self.image_mode == "CUSTOM":
            thumb_size = 90 # Giảm size ảnh xuống một xíu để khỏi đè lên nút dưới
            thumb = pygame.transform.smoothscale(self.full_image, (thumb_size, thumb_size))
            thumb_x, thumb_y = rect_custom.centerx - (thumb_size // 2), current_y + btn_h + 10
            pygame.draw.rect(self.screen, (220, 190, 190), (thumb_x - 4, thumb_y - 2, thumb_size + 8, thumb_size + 8), border_radius=10)
            pygame.draw.rect(self.screen, (255, 255, 255), (thumb_x - 4, thumb_y - 4, thumb_size + 8, thumb_size + 8), border_radius=10)
            self.screen.blit(thumb, (thumb_x, thumb_y - 2))

        # NÚT ĐIỀU HƯỚNG BÊN DƯỚI
        btn_bottom_y = panel_rect.bottom - 80
        self.rect_back = pygame.Rect(panel_rect.x + 40, btn_bottom_y, 140, 55)
        self.draw_radial_pill_button(self.screen, self.rect_back, "QUAY LẠI", False, self.font_btn)

        self.rect_start = pygame.Rect(panel_rect.right - 220, btn_bottom_y, 180, 60)
        self.draw_radial_pill_button(self.screen, self.rect_start, "BẮT ĐẦU", True, self.font_start, btn_type="start")