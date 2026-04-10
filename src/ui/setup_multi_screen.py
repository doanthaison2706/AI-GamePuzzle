import pygame
from configs import game_config as config
from src.utils.image_crop import open_file_dialog
from src.ui.crop_menu import CropImageMenu

class SetupMultiScreen:
    def __init__(self, screen):
        self.screen = screen
        
        # --- TRẠNG THÁI LỰA CHỌN ---
        self.selected_mode = "PvP"       
        self.selected_difficulty = "medium" 
        self.selected_size = 4           
        self.selected_score = 3          
        self.selected_time = 0           
        self.image_mode = "DEFAULT"      
        self.full_image = None
        
        self.color_panel_top = (255, 252, 246)
        self.color_panel_bot = (255, 240, 225)
        self.color_panel_border = (248, 186, 186)
        self.color_text_title = (205, 92, 92)    
        self.color_text_active = (255, 255, 255)
        self.color_text_inactive = (150, 100, 100) 

        # --- LOAD ASSETS ---
        try:
            self.bg_img = pygame.image.load("assets/images/background_setup.png").convert()
            self.bg_img = pygame.transform.scale(self.bg_img, self.screen.get_size())
        except: self.bg_img = None

        try:
            self.img_banner_title = pygame.image.load("assets/images/title_setup.png").convert_alpha()
            self.img_ribbon_long = pygame.image.load("assets/images/btn_long.png").convert_alpha()
            self.img_ribbon_short = pygame.image.load("assets/images/btn_rect.png").convert_alpha()
            self.img_leaf = pygame.image.load("assets/images/btn_oval.png").convert_alpha()
        except:
            self.img_banner_title = self.img_ribbon_long = self.img_ribbon_short = self.img_leaf = None

        # KHỞI TẠO RECT RỖNG ĐỂ BẮT HITBOX
        self.rects_mode = {"PvP": None, "PvE": None, "EvE": None}
        self.rects_diff = {"easy": None, "medium": None, "hard": None}
        self.rects_size = {3: None, 4: None, 5: None, 6: None}
        self.rects_score = {1: None, 3: None, 5: None}
        self.rects_time = {0: None, 120: None, 300: None, 600: None}
        self.rects_img = {"DEFAULT": None, "CUSTOM": None}
        self.rect_start = None
        self.rect_back = None

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                
                for mode_val, rect in self.rects_mode.items():
                    if rect and rect.collidepoint(mouse_pos): self.selected_mode = mode_val
                
                if self.selected_mode in ["PvE", "EvE"]:
                    for diff_val, rect in self.rects_diff.items():
                        if rect and rect.collidepoint(mouse_pos): self.selected_difficulty = diff_val

                for size, rect in self.rects_size.items():
                    if rect and rect.collidepoint(mouse_pos): self.selected_size = size
                
                for score_val, rect in self.rects_score.items():
                    if rect and rect.collidepoint(mouse_pos): self.selected_score = score_val

                for time_val, rect in self.rects_time.items():
                    if rect and rect.collidepoint(mouse_pos): self.selected_time = time_val
                    
                if self.rects_img["DEFAULT"] and self.rects_img["DEFAULT"].collidepoint(mouse_pos):
                    self.image_mode = "DEFAULT"; self.full_image = None
                    
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
                        "mode": self.selected_mode,
                        "difficulty": self.selected_difficulty if self.selected_mode in ["PvE", "EvE"] else None,
                        "size": self.selected_size,
                        "time": self.selected_time,
                        "score": self.selected_score,
                        "image": self.full_image if self.image_mode == "CUSTOM" else None
                    }
                    return "PLAYING_MULTI", setup_data
                    
                if self.rect_back and self.rect_back.collidepoint(mouse_pos):
                    return "MENU", None
        return "SETUP_MULTI", None

    def draw_gradient_rect(self, surface, rect, color_top, color_bottom, radius, shadow_color=None, shadow_offset=6, border_color=None, border_width=0):
        if shadow_color:
            pygame.draw.rect(surface, shadow_color, pygame.Rect(rect.x, rect.y + shadow_offset, rect.width, rect.height), border_radius=radius)
        grad_surf = pygame.Surface((1, 2), pygame.SRCALPHA)
        grad_surf.set_at((0, 0), color_top); grad_surf.set_at((0, 1), color_bottom)
        grad_surf = pygame.transform.smoothscale(grad_surf, (rect.width, rect.height))
        mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)
        grad_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(grad_surf, rect.topleft)
        if border_color and border_width > 0:
            pygame.draw.rect(surface, border_color, rect, border_radius=radius, width=border_width)

    def draw_image_button(self, surface, x, y, width, height, text, is_active, font, base_image):
        rect = pygame.Rect(x, y, width, height)
        if base_image:
            scaled_img = pygame.transform.smoothscale(base_image, (width, height))
            if is_active:
                surface.blit(scaled_img, rect.topleft)
                txt_color = (180, 50, 50)
            else:
                alpha_img = scaled_img.copy()
                alpha_img.set_alpha(150) 
                surface.blit(alpha_img, rect.topleft)
                txt_color = self.color_text_inactive

            text_surf = font.render(text, True, txt_color)
            text_rect = text_surf.get_rect(center=(rect.centerx, rect.centery - 2)) 
            
            if is_active:
                shadow_surf = font.render(text, True, (255, 240, 240))
                surface.blit(shadow_surf, (text_rect.x, text_rect.y + 1))
            surface.blit(text_surf, text_rect)
            return rect
        else:
            color = (165, 240, 210) if is_active else (235, 205, 185)
            pygame.draw.rect(surface, color, rect, border_radius=15)
            txt_c = (180, 50, 50) if is_active else self.color_text_inactive
            text_surf = font.render(text, True, txt_c)
            surface.blit(text_surf, text_surf.get_rect(center=rect.center))
            return rect

    def render(self):
        sw, sh = self.screen.get_size()
        center_x = sw // 2

        if self.bg_img: 
            bg_scaled = pygame.transform.smoothscale(self.bg_img, (sw, sh))
            self.screen.blit(bg_scaled, (0, 0))
        else: 
            self.screen.fill((255, 230, 235)) 

        # BẢNG PANEL LỚN
        panel_w = int(sw * 0.92)
        panel_h = int(sh * 0.88)
        panel_rect = pygame.Rect(center_x - panel_w//2, int(sh * 0.08), panel_w, panel_h)

        self.draw_gradient_rect(self.screen, panel_rect, self.color_panel_top, self.color_panel_bot, 25, 
                                shadow_color=(240, 210, 210), shadow_offset=8, border_color=self.color_panel_border, border_width=4)

        # SCALE 
        scale = max(0.85, min(sw / 1200.0, sh / 800.0))
        
        try:
            self.font_label = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", int(22 * scale))
            self.font_btn = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", int(18 * scale))
            self.font_start = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", int(32 * scale))
        except:
            self.font_label = pygame.font.SysFont("arial", int(22 * scale), bold=True)
            self.font_btn = pygame.font.SysFont("arial", int(18 * scale), bold=True)
            self.font_start = pygame.font.SysFont("arial", int(30 * scale), bold=True)

        # KÍCH THƯỚC NÚT
        btn_h = int(60 * scale)
        btn_short = int(105 * scale) 
        btn_mid = int(150 * scale)   
        btn_long = int(220 * scale)
        spacing = int(12 * scale)    

        # TITLE BANNER
        if self.img_banner_title:
            banner_w, banner_h = int(550 * scale), int(110 * scale)
            scaled_banner = pygame.transform.smoothscale(self.img_banner_title, (banner_w, banner_h))
            banner_rect = scaled_banner.get_rect(centerx=center_x, top=panel_rect.y - banner_h // 2)
            self.screen.blit(scaled_banner, banner_rect)

        def draw_section_label(text, x_pos, y_pos):
            txt_surf = self.font_label.render(text, True, (255, 255, 255))
            txt_shadow = self.font_label.render(text, True, (180, 90, 90)) 
            
            rb_w = int(txt_surf.get_width() + 60 * scale)
            rb_h = int(48 * scale) 
            
            rb_x = x_pos - int(15 * scale)
            rb_y = y_pos - int(12 * scale)
            
            if self.img_ribbon_long:
                scaled_rb = pygame.transform.smoothscale(self.img_ribbon_long, (rb_w, rb_h))
                self.screen.blit(scaled_rb, (rb_x, rb_y))
            else:
                lbl_surf = self.font_label.render(text, True, self.color_text_title)
                self.screen.blit(lbl_surf, (x_pos, y_pos))
                return
                
            self.screen.blit(txt_shadow, (x_pos + 1, y_pos + 1))
            self.screen.blit(txt_surf, (x_pos, y_pos))

        # ==========================================
        # 2 CỘT
        # ==========================================
        col1_x = panel_rect.x + int(panel_w * 0.04)
        col2_x = panel_rect.centerx + int(panel_w * 0.02)

        row_step = int(160 * scale)
        row1_y = panel_rect.y + int(60 * scale)
        row2_y = row1_y + row_step
        row3_y = row2_y + row_step
        label_margin = int(55 * scale) 

        # --- CỘT TRÁI ---
        # 1. KÍCH THƯỚC BÀN CỜ
        draw_section_label("KÍCH THƯỚC BÀN CỜ", col1_x, row1_y)
        curr_x = col1_x
        for size in [3, 4, 5, 6]:
            self.rects_size[size] = self.draw_image_button(
                self.screen, curr_x, row1_y + label_margin, btn_short, btn_h, f"{size}x{size}", 
                self.selected_size == size, self.font_btn, self.img_ribbon_short
            )
            curr_x += btn_short + spacing

        # 2. ĐIỂM THẮNG
        draw_section_label("ĐIỂM THẮNG (BEST OF)", col1_x, row2_y)
        curr_x = col1_x
        for score in [1, 3, 5]:
            self.rects_score[score] = self.draw_image_button(
                self.screen, curr_x, row2_y + label_margin, btn_short, btn_h, str(score), 
                self.selected_score == score, self.font_btn, self.img_ribbon_short
            )
            curr_x += btn_short + spacing

        # 3. HÌNH ẢNH SỬ DỤNG
        draw_section_label("HÌNH ẢNH SỬ DỤNG", col1_x, row3_y)
        self.rects_img["DEFAULT"] = self.draw_image_button(
            self.screen, col1_x, row3_y + label_margin, btn_mid, btn_h, "MẶC ĐỊNH", 
            self.image_mode == "DEFAULT", self.font_btn, self.img_ribbon_short
        )
        
        self.rects_img["CUSTOM"] = self.draw_image_button(
            self.screen, self.rects_img["DEFAULT"].right + spacing, row3_y + label_margin, btn_long, btn_h, "CHỌN ẢNH CROP", 
            self.image_mode == "CUSTOM", self.font_btn, self.img_ribbon_short
        )

        # FIX: DỜI ẢNH THUMBNAIL SANG BÊN PHẢI NÚT "CHỌN ẢNH CROP"
        if self.full_image and self.image_mode == "CUSTOM":
            thumb_size = int(200 * scale) 
            thumb = pygame.transform.smoothscale(self.full_image, (thumb_size, thumb_size))
            
            # Neo tọa độ X sang bên phải nút
            thumb_x = self.rects_img["CUSTOM"].right + spacing
            # Căn giữa theo trục Y của nút "CHỌN ẢNH CROP"
            thumb_y = self.rects_img["CUSTOM"].centery - (thumb_size // 2)
            
            pygame.draw.rect(self.screen, (220, 190, 190), (thumb_x - 3, thumb_y - 1, thumb_size + 6, thumb_size + 6), border_radius=8)
            pygame.draw.rect(self.screen, (255, 255, 255), (thumb_x - 3, thumb_y - 3, thumb_size + 6, thumb_size + 6), border_radius=8)
            self.screen.blit(thumb, (thumb_x, thumb_y - 1))

        # --- CỘT PHẢI ---
        # 4. CHẾ ĐỘ CHƠI
        draw_section_label("CHẾ ĐỘ CHƠI", col2_x, row1_y)
        curr_x = col2_x
        mode_options = [("PvP", "NGƯỜI-NGƯỜI"), ("PvE", "NGƯỜI-MÁY"), ("EvE", "MÁY-MÁY")]
        for mode_val, text in mode_options:
            self.rects_mode[mode_val] = self.draw_image_button(
                self.screen, curr_x, row1_y + label_margin, btn_mid, btn_h, text, 
                self.selected_mode == mode_val, self.font_btn, self.img_ribbon_short
            )
            curr_x += btn_mid + spacing

        # 5. THỜI GIAN
        draw_section_label("THỜI GIAN / VÁN", col2_x, row2_y)
        curr_x = col2_x
        time_options = [(0, "VÔ HẠN"), (120, "2:00"), (300, "5:00"), (600, "10:00")]
        for val, text in time_options:
            w = btn_mid if val == 0 else btn_short
            self.rects_time[val] = self.draw_image_button(
                self.screen, curr_x, row2_y + label_margin, w, btn_h, text, 
                self.selected_time == val, self.font_btn, self.img_ribbon_short
            )
            curr_x += w + spacing

        # 6. ĐỘ KHÓ AI
        if self.selected_mode in ["PvE", "EvE"]:
            draw_section_label("ĐỘ KHÓ AI", col2_x, row3_y)
            curr_x = col2_x
            diff_options = [("easy", "DỄ"), ("medium", "TRUNG BÌNH"), ("hard", "KHÓ")]
            for diff_val, text in diff_options:
                w = btn_long if diff_val == "medium" else btn_short
                self.rects_diff[diff_val] = self.draw_image_button(
                    self.screen, curr_x, row3_y + label_margin, w, btn_h, text, 
                    self.selected_difficulty == diff_val, self.font_btn, self.img_ribbon_short
                )
                curr_x += w + spacing

        # --- FOOTER: NÚT ĐIỀU HƯỚNG ---
        btn_bottom_y = panel_rect.bottom - int(80 * scale) 
        
        self.rect_back = self.draw_image_button(
            self.screen, col1_x, btn_bottom_y, int(180 * scale), int(65 * scale), "QUAY LẠI", 
            False, self.font_btn, self.img_leaf
        )
        
        start_btn_w = int(240 * scale)
        start_btn_x = panel_rect.right - int(panel_w * 0.04) - start_btn_w
        self.rect_start = self.draw_image_button(
            self.screen, start_btn_x, btn_bottom_y, start_btn_w, int(75 * scale), "BẮT ĐẦU", 
            True, self.font_start, self.img_leaf
        )