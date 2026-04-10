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
            self.img_banner_title = None; self.img_ribbon_long = None
            self.img_ribbon_short = None; self.img_leaf = None

        self.rects_size = {3: pygame.Rect(0,0,0,0), 4: pygame.Rect(0,0,0,0), 5: pygame.Rect(0,0,0,0), 6: pygame.Rect(0,0,0,0)}
        self.rects_time = {0: pygame.Rect(0,0,0,0), 120: pygame.Rect(0,0,0,0), 300: pygame.Rect(0,0,0,0), 600: pygame.Rect(0,0,0,0)}
        self.rects_img = {"DEFAULT": pygame.Rect(0,0,0,0), "CUSTOM": pygame.Rect(0,0,0,0)}
        self.rect_start = pygame.Rect(0,0,0,0)
        self.rect_back = pygame.Rect(0,0,0,0)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                for size, rect in self.rects_size.items():
                    if rect and rect.collidepoint(mouse_pos): self.selected_size = size
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
                    return "PLAYING", {"size": self.selected_size, "time": self.selected_time, "image": self.full_image if self.image_mode == "CUSTOM" else None}
                if self.rect_back and self.rect_back.collidepoint(mouse_pos):
                    return "MENU", None
        return "SETUP_SINGLE", None

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

        scale = max(0.85, min(sw / 1200.0, sh / 800.0)) 

        try:
            self.font_label = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", int(22 * scale))
            self.font_btn = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", int(18 * scale))
            self.font_start = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", int(32 * scale))
        except:
            self.font_label = pygame.font.SysFont("arial", int(22 * scale), bold=True)
            self.font_btn = pygame.font.SysFont("arial", int(18 * scale), bold=True)
            self.font_start = pygame.font.SysFont("arial", int(30 * scale), bold=True)

        btn_h = int(75 * scale)
        btn_short_w = int(140 * scale)
        btn_mid_w = int(190 * scale)
        btn_long_w = int(260 * scale)
        spacing_x = int(25 * scale)

        # Vẽ Banner
        if self.img_banner_title:
            banner_w, banner_h = int(600 * scale), int(120 * scale)
            scaled_banner = pygame.transform.smoothscale(self.img_banner_title, (banner_w, banner_h))
            banner_rect = scaled_banner.get_rect(centerx=center_x, top=panel_rect.y - banner_h // 2)
            self.screen.blit(scaled_banner, banner_rect)
        else:
            title_text = "TÙY CHỈNH TRẬN ĐẤU"
            title_surf = self.font_start.render(title_text, True, self.color_text_active)
            box_rect = pygame.Rect(center_x - 150, panel_rect.y - 30, 300, 60)
            pygame.draw.rect(self.screen, (255, 175, 198), box_rect, border_radius=20)
            self.screen.blit(title_surf, title_surf.get_rect(center=box_rect.center))

        def draw_section_label(text, x_pos, y_pos):
            txt_surf = self.font_label.render(text, True, (255, 255, 255))
            txt_shadow = self.font_label.render(text, True, (180, 90, 90)) 
            
            rb_w = int((txt_surf.get_width() + int(60 * scale)) * 1.2)
            rb_h = int(55 * 1.5 * scale) 
            
            rb_x = x_pos - (rb_w - txt_surf.get_width()) // 2
            rb_y = y_pos - (rb_h - txt_surf.get_height()) // 2
            
            if self.img_ribbon_long:
                scaled_rb = pygame.transform.smoothscale(self.img_ribbon_long, (rb_w, rb_h))
                self.screen.blit(scaled_rb, (rb_x, rb_y))
            else:
                lbl_surf = self.font_label.render(text, True, self.color_text_title)
                self.screen.blit(lbl_surf, (x_pos, y_pos))
                return
                
            self.screen.blit(txt_shadow, (x_pos + 2, y_pos + 2))
            self.screen.blit(txt_surf, (x_pos, y_pos))

        start_x = panel_rect.x + int(panel_w * 0.08) 
        row_step = int(170 * scale)
        row1_y = panel_rect.y + int(80 * scale)
        row2_y = row1_y + row_step
        row3_y = row2_y + row_step
        label_margin = int(70 * scale)

        # --- HÀNG 1: KÍCH THƯỚC BÀN CỜ ---
        draw_section_label("KÍCH THƯỚC BÀN CỜ", start_x, row1_y)
        btn_y = row1_y + label_margin
        curr_x = start_x
        for size in [3, 4, 5, 6]:
            self.rects_size[size] = self.draw_image_button(
                self.screen, curr_x, btn_y, btn_short_w, btn_h, f"{size}x{size}", 
                self.selected_size == size, self.font_btn, self.img_ribbon_short
            )
            curr_x += btn_short_w + spacing_x

        # --- HÀNG 2: THỜI GIAN ---
        draw_section_label("THỜI GIAN / VÁN", start_x, row2_y)
        btn_y = row2_y + label_margin
        curr_x = start_x
        time_options = [(0, "KHÔNG GIỚI HẠN"), (120, "2:00"), (300, "5:00"), (600, "10:00")]
        for val, text in time_options:
            btn_w = btn_long_w if val == 0 else btn_short_w
            # LUÔN SỬ DỤNG NÚT TÍM (img_ribbon_short) DÙ CHO TEXT DÀI HAY NGẮN
            self.rects_time[val] = self.draw_image_button(
                self.screen, curr_x, btn_y, btn_w, btn_h, text, 
                self.selected_time == val, self.font_btn, self.img_ribbon_short
            )
            curr_x += btn_w + spacing_x

        # --- HÀNG 3: HÌNH ẢNH SỬ DỤNG ---
        draw_section_label("HÌNH ẢNH SỬ DỤNG", start_x, row3_y)
        btn_y = row3_y + label_margin
        
        self.rects_img["DEFAULT"] = self.draw_image_button(
            self.screen, start_x, btn_y, btn_mid_w, btn_h, "MẶC ĐỊNH", 
            self.image_mode == "DEFAULT", self.font_btn, self.img_ribbon_short
        )
        
        custom_x = self.rects_img["DEFAULT"].right + spacing_x
        self.rects_img["CUSTOM"] = self.draw_image_button(
            self.screen, custom_x, btn_y, btn_long_w, btn_h, "CHỌN ẢNH CROP", 
            self.image_mode == "CUSTOM", self.font_btn, self.img_ribbon_short
        )

        if self.full_image and self.image_mode == "CUSTOM":
            thumb_size = int(110 * scale) 
            thumb = pygame.transform.smoothscale(self.full_image, (thumb_size, thumb_size))
            
            thumb_x = self.rects_img["CUSTOM"].right + spacing_x
            thumb_y = self.rects_img["CUSTOM"].centery - (thumb_size // 2)
            
            pygame.draw.rect(self.screen, (220, 190, 190), (thumb_x - 4, thumb_y - 2, thumb_size + 8, thumb_size + 8), border_radius=10)
            pygame.draw.rect(self.screen, (255, 255, 255), (thumb_x - 4, thumb_y - 4, thumb_size + 8, thumb_size + 8), border_radius=10)
            self.screen.blit(thumb, (thumb_x, thumb_y - 2))

        # --- FOOTER: NÚT ĐIỀU HƯỚNG ---
        btn_bottom_y = panel_rect.bottom - int(100 * scale) 
        
        self.rect_back = self.draw_image_button(
            self.screen, start_x, btn_bottom_y, int(200 * scale), int(80 * scale), "QUAY LẠI", 
            False, self.font_btn, self.img_leaf
        )
        
        start_btn_w = int(280 * scale)
        start_btn_x = panel_rect.right - int(panel_w * 0.08) - start_btn_w
        self.rect_start = self.draw_image_button(
            self.screen, start_btn_x, btn_bottom_y, start_btn_w, int(90 * scale), "BẮT ĐẦU", 
            True, self.font_start, self.img_leaf
        )