import pygame
import math
from configs import game_config as config

class SettingScreen:
    def __init__(self, screen):
        self.screen = screen
        self.last_size = (0, 0)
        
        # --- LƯU TRỮ TRẠNG THÁI CÀI ĐẶT ---
        # Value chạy từ 0 đến 100
        self.settings = {
            "music": {"val": 80,  "label": "NHẠC NỀN", "color": (186, 115, 104)}, # Đỏ nâu
            "sound": {"val": 70,  "label": "HIỆU ỨNG ÂM THANH", "color": (98, 153, 196)}, # Xanh dương
            "bright": {"val": 100, "label": "ĐỘ SÁNG", "color": (92, 172, 157)} # Xanh ngọc
        }
        
        self.color_panel_top = (255, 252, 246)
        self.color_panel_bot = (255, 240, 225)
        self.color_panel_border = (248, 186, 186)
        
        # Lưu các Rect/Tâm đường tròn để bắt click
        self.hitboxes = {
            "music": {"minus": None, "plus": None, "radius": 0},
            "sound": {"minus": None, "plus": None, "radius": 0},
            "bright": {"minus": None, "plus": None, "radius": 0}
        }
        self.rect_back = None

        # --- LOAD ASSETS ---
        try:
            self.bg_img = pygame.image.load("assets/images/background_setup.png").convert()
            self.bg_img = pygame.transform.scale(self.bg_img, self.screen.get_size())
        except: self.bg_img = None

        try:
            self.img_leaf = pygame.image.load("assets/images/btn_oval.png").convert_alpha()
            self.img_banner_title = pygame.image.load("assets/images/title_setup.png").convert_alpha()
        except: 
            self.img_leaf = None
            self.img_banner_title = None

    def _update_layout(self):
        sw, sh = self.screen.get_size()
        if self.last_size == (sw, sh): return
        
        self.last_size = (sw, sh)
        self.scale = max(0.85, min(sw / 1200.0, sh / 800.0))

        # Fonts
        try:
            self.font_label = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", int(24 * self.scale))
            self.font_val = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", int(36 * self.scale))
            self.font_btn = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", int(20 * self.scale))
            self.font_title = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", int(36 * self.scale))
        except:
            self.font_label = pygame.font.SysFont("arial", int(24 * self.scale), bold=True)
            self.font_val = pygame.font.SysFont("arial", int(36 * self.scale), bold=True)
            self.font_btn = pygame.font.SysFont("arial", int(20 * self.scale), bold=True)
            self.font_title = pygame.font.SysFont("arial", int(36 * self.scale), bold=True)

    def handle_events(self, events):
        self._update_layout()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                
                # Check click nút Back
                if self.rect_back and self.rect_back.collidepoint((mx, my)):
                    return "MENU", self.settings # Trả về menu kèm data setting để áp dụng
                
                # Check click nút Tròn (+ / -)
                for key, boxes in self.hitboxes.items():
                    r = boxes["radius"]
                    
                    # Tính khoảng cách từ chuột đến tâm hình tròn
                    if boxes["minus"]:
                        cx, cy = boxes["minus"]
                        if math.hypot(mx - cx, my - cy) <= r:
                            self.settings[key]["val"] = max(0, self.settings[key]["val"] - 5)
                            
                    if boxes["plus"]:
                        cx, cy = boxes["plus"]
                        if math.hypot(mx - cx, my - cy) <= r:
                            self.settings[key]["val"] = min(100, self.settings[key]["val"] + 5)

        return "SETTING", None

    def draw_gradient_rect(self, surface, rect, color_top, color_bottom, radius):
        pygame.draw.rect(surface, (240, 210, 210), pygame.Rect(rect.x, rect.y + 8, rect.width, rect.height), border_radius=radius)
        grad_surf = pygame.Surface((1, 2), pygame.SRCALPHA)
        grad_surf.set_at((0, 0), color_top); grad_surf.set_at((0, 1), color_bottom)
        grad_surf = pygame.transform.smoothscale(grad_surf, (rect.width, rect.height))
        mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)
        grad_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(grad_surf, rect.topleft)
        pygame.draw.rect(surface, self.color_panel_border, rect, border_radius=radius, width=4)

    def draw_circle_btn(self, surface, center_x, center_y, radius, text, color):
        """Vẽ nút tròn xịn xò cho dấu + và -"""
        # Viền ngoài mờ mờ
        pygame.draw.circle(surface, (color[0], color[1], color[2], 100), (center_x, center_y), radius + 4)
        # Khung chính
        pygame.draw.circle(surface, color, (center_x, center_y), radius)
        # Viền trắng
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), radius, width=2)
        
        # Dấu + hoặc -
        txt_surf = self.font_val.render(text, True, (255, 255, 255))
        # Điều chỉnh Y lên một chút xíu để dấu +- nằm chuẩn giữa
        txt_rect = txt_surf.get_rect(center=(center_x, center_y - 3))
        surface.blit(txt_surf, txt_rect)

    def draw_setting_row(self, key, center_x, y_pos):
        data = self.settings[key]
        scale = self.scale
        
        # 1. Tiêu đề
        lbl_surf = self.font_label.render(data["label"], True, (130, 120, 120))
        self.screen.blit(lbl_surf, lbl_surf.get_rect(centerx=center_x, top=y_pos))
        
        # 2. Hàng Control (Nút -, Text %, Nút +)
        ctrl_y = y_pos + int(50 * scale)
        radius = int(25 * scale)
        self.hitboxes[key]["radius"] = radius
        
        spacing = int(70 * scale)
        
        # Nút Trừ
        minus_x = center_x - spacing
        self.draw_circle_btn(self.screen, minus_x, ctrl_y, radius, "-", data["color"])
        self.hitboxes[key]["minus"] = (minus_x, ctrl_y)
        
        # Text Giá trị
        val_surf = self.font_val.render(f"{data['val']}%", True, (60, 50, 50))
        self.screen.blit(val_surf, val_surf.get_rect(center=(center_x, ctrl_y)))
        
        # Nút Cộng
        plus_x = center_x + spacing
        self.draw_circle_btn(self.screen, plus_x, ctrl_y, radius, "+", data["color"])
        self.hitboxes[key]["plus"] = (plus_x, ctrl_y)
        
        # 3. Thanh Progress Bar
        bar_w = int(280 * scale)
        bar_h = int(12 * scale)
        bar_x = center_x - bar_w // 2
        bar_y = ctrl_y + int(45 * scale)
        
        # Nền thanh (Xám nhạt)
        pygame.draw.rect(self.screen, (230, 225, 220), (bar_x, bar_y, bar_w, bar_h), border_radius=bar_h//2)
        
        # Thanh màu lấp đầy
        fill_w = int(bar_w * (data["val"] / 100))
        if fill_w > 0:
            pygame.draw.rect(self.screen, data["color"], (bar_x, bar_y, fill_w, bar_h), border_radius=bar_h//2)

    def draw_image_button(self, surface, rect, text, image):
        if image:
            scaled_img = pygame.transform.smoothscale(image, (rect.width, rect.height))
            surface.blit(scaled_img, rect.topleft)
            text_surf = self.font_btn.render(text, True, (180, 50, 50))
            text_rect = text_surf.get_rect(center=(rect.centerx, rect.centery - 2)) 
            shadow_surf = self.font_btn.render(text, True, (255, 240, 240))
            surface.blit(shadow_surf, (text_rect.x, text_rect.y + 1))
            surface.blit(text_surf, text_rect)
        else:
            pygame.draw.rect(surface, (235, 205, 185), rect, border_radius=15)
            text_surf = self.font_btn.render(text, True, (150, 100, 100))
            surface.blit(text_surf, text_surf.get_rect(center=rect.center))

    def render(self):
        self._update_layout()
        sw, sh = self.screen.get_size()
        center_x = sw // 2

        if self.bg_img: 
            bg_scaled = pygame.transform.smoothscale(self.bg_img, (sw, sh))
            self.screen.blit(bg_scaled, (0, 0))
        else: 
            self.screen.fill((255, 230, 235)) 

        # PANEL CÀI ĐẶT (Gọn gàng ở giữa màn hình)
        panel_w = int(sw * 0.45)
        panel_h = int(sh * 0.8)
        panel_w = max(panel_w, int(450 * self.scale)) # Đảm bảo không quá bé
        panel_rect = pygame.Rect(center_x - panel_w//2, int(sh * 0.1), panel_w, panel_h)

        self.draw_gradient_rect(self.screen, panel_rect, self.color_panel_top, self.color_panel_bot, 25)

        # TITLE BANNER
        if self.img_banner_title:
            banner_w, banner_h = int(400 * self.scale), int(90 * self.scale)
            scaled_banner = pygame.transform.smoothscale(self.img_banner_title, (banner_w, banner_h))
            banner_rect = scaled_banner.get_rect(centerx=center_x, top=panel_rect.y - banner_h // 2)
            self.screen.blit(scaled_banner, banner_rect)
        else:
            title_surf = self.font_title.render("TÙY CHỈNH", True, (205, 92, 92))
            self.screen.blit(title_surf, title_surf.get_rect(centerx=center_x, top=panel_rect.y + 20))

        # --- VẼ 3 HÀNG CÀI ĐẶT ---
        start_y = panel_rect.y + int(60 * self.scale)
        gap_y = int(140 * self.scale)

        self.draw_setting_row("music", center_x, start_y)
        self.draw_setting_row("sound", center_x, start_y + gap_y)
        self.draw_setting_row("bright", center_x, start_y + gap_y * 2)

        # --- NÚT QUAY LẠI ---
        btn_w = int(180 * self.scale)
        btn_h = int(60 * self.scale)
        self.rect_back = pygame.Rect(center_x - btn_w // 2, panel_rect.bottom - btn_h - int(30 * self.scale), btn_w, btn_h)
        self.draw_image_button(self.screen, self.rect_back, "XONG", self.img_leaf)