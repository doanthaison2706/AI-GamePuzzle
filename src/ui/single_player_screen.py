import pygame
import random
import os
from configs import game_config as config
from src.core.game_manager import GameManager
from src.ui.renderer import Renderer
from src.utils.image_crop import slice_image

class SinglePlayerScreen:
    def __init__(self, screen, setup_data):
        self.screen = screen
        self.renderer = Renderer(screen)
        
        # --- THIẾT LẬP MÀN HÌNH ẢO (VIRTUAL SURFACE) CHO RESPONSIVE ---
        self.base_w = config.WINDOW_WIDTH
        self.base_h = config.WINDOW_HEIGHT
        self.v_surf = pygame.Surface((self.base_w, self.base_h))
        
        self.size = setup_data["size"]
        self.full_image = setup_data.get("image", None)
        self.image_slices = None
        
        if self.full_image:
            _, self.image_slices = slice_image(self.full_image, config.BOARD_SIZE, self.size)
            
        self.gm = GameManager(size=self.size)
        self.gm.new_game()
        self.show_full_image = False
        
        self.best_score = 35 
        self.is_paused = False
        
        self.is_auto_solving = False
        self.last_auto_move = 0
        self.is_winning = False   
        self.win_start_time = 0   
        self.history = []

        try:
            self.move_sound = pygame.mixer.Sound("assets/sounds/move.wav")
        except:
            self.move_sound = None

        # --- 1. LOAD ẢNH NỀN & TITLE ---
        try:
            self.bg_img = pygame.image.load("assets/images/bg_play.png").convert()
            self.bg_img = pygame.transform.scale(self.bg_img, (self.base_w, self.base_h))
        except:
            self.bg_img = None

        try:
            self.title_img = pygame.image.load("assets/images/title_single.png").convert_alpha()
        except:
            self.title_img = None

        try:
            self.font_stat = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", 20)
        except:
            self.font_stat = pygame.font.SysFont("arial", 20, bold=True)

        # --- 2. LOAD ẢNH CUSTOM CHO 6 NÚT BẤM ---
        btn_w, btn_h = 95, 90
        spacing = 15
        total_w = (btn_w * 6) + (spacing * 5)
        start_x = (self.base_w - total_w) // 2
        btn_y = self.base_h - 120 

        # Tên file ảnh tương ứng mà bạn cần bỏ vào thư mục: assets/images/
        self.btn_names = ["btn_hint.png", "btn_ai.png", "btn_undo.png", "btn_restart.png", "btn_pause.png", "btn_exit.png"]
        self.btn_images = {}
        
        for name in self.btn_names:
            try:
                img = pygame.image.load(f"assets/images/{name}").convert_alpha()
                self.btn_images[name] = pygame.transform.smoothscale(img, (btn_w, btn_h))
            except:
                # Nếu bạn chưa kịp bỏ ảnh vào, nó sẽ vẽ một ô xám giữ chỗ
                fallback = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
                pygame.draw.rect(fallback, (180, 180, 180), fallback.get_rect(), border_radius=15)
                self.btn_images[name] = fallback

        # Khởi tạo Hitbox (Rect) cho các nút
        self.buttons = [
            {"id": "hint",    "name": "btn_hint.png",    "rect": pygame.Rect(start_x, btn_y, btn_w, btn_h)},
            {"id": "ai",      "name": "btn_ai.png",      "rect": pygame.Rect(start_x + (btn_w+spacing)*1, btn_y, btn_w, btn_h)},
            {"id": "undo",    "name": "btn_undo.png",    "rect": pygame.Rect(start_x + (btn_w+spacing)*2, btn_y, btn_w, btn_h)},
            {"id": "restart", "name": "btn_restart.png", "rect": pygame.Rect(start_x + (btn_w+spacing)*3, btn_y, btn_w, btn_h)},
            {"id": "pause",   "name": "btn_pause.png",   "rect": pygame.Rect(start_x + (btn_w+spacing)*4, btn_y, btn_w, btn_h)},
            {"id": "exit",    "name": "btn_exit.png",    "rect": pygame.Rect(start_x + (btn_w+spacing)*5, btn_y, btn_w, btn_h)}
        ]

    def save_history(self):
        matrix_copy = [row[:] for row in self.gm.board.matrix]
        self.history.append((matrix_copy, self.gm.move_count))

    def handle_events(self, events):
        if self.is_winning:
            if pygame.time.get_ticks() - self.win_start_time >= 1500:
                result_data = {"time": self.gm.get_formatted_time(), "moves": self.gm.move_count, "size": self.size}
                return "WIN_SINGLE", result_data
            return "PLAYING"

        # --- LOGIC TÍNH TỌA ĐỘ CHUỘT RESPONSIVE ---
        actual_w, actual_h = self.screen.get_size()
        scale = min(actual_w / self.base_w, actual_h / self.base_h)
        offset_x = (actual_w - int(self.base_w * scale)) // 2
        offset_y = (actual_h - int(self.base_h * scale)) // 2

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: self.show_full_image = True
            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE: self.show_full_image = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Ép tọa độ chuột thật về tọa độ chuột ảo
                vx = (event.pos[0] - offset_x) / scale
                vy = (event.pos[1] - offset_y) / scale
                v_pos = (vx, vy)
                
                # --- XỬ LÝ CLICK NÚT ---
                for btn in self.buttons:
                    if btn["rect"].collidepoint(v_pos):
                        if btn["id"] == "hint" and not self.is_auto_solving and self.gm.is_playing:
                            self.save_history()
                            if self.gm.get_ai_hint() and self.move_sound: self.move_sound.play()
                        
                        elif btn["id"] == "ai" and self.gm.is_playing and not self.is_auto_solving:
                            if self.gm.move_count >= 50: self.is_auto_solving = True
                                
                        elif btn["id"] == "undo" and not self.is_auto_solving and self.gm.is_playing:
                            if len(self.history) > 0:
                                prev_matrix, prev_moves = self.history.pop()
                                self.gm.board.matrix = [row[:] for row in prev_matrix]
                                self.gm.move_count = prev_moves

                        elif btn["id"] == "restart":
                            self.gm.new_game()
                            self.is_auto_solving = False
                            self.is_paused = False
                            self.history.clear()

                        elif btn["id"] == "pause" and not self.is_auto_solving:
                            self.is_paused = not self.is_paused
                            self.gm.is_playing = not self.is_paused 

                        elif btn["id"] == "exit":
                            return "MENU"

                # --- XỬ LÝ CLICK TRƯỢT GẠCH ---
                if self.gm.is_playing and not self.show_full_image and not self.is_paused and not self.is_auto_solving:
                    if config.MARGIN_LEFT <= vx <= config.MARGIN_LEFT + config.BOARD_SIZE and \
                       config.MARGIN_TOP <= vy <= config.MARGIN_TOP + config.BOARD_SIZE:
                        t_size = config.BOARD_SIZE // self.gm.size
                        r, c = int((vy - config.MARGIN_TOP) // t_size), int((vx - config.MARGIN_LEFT) // t_size)
                        
                        if (r, c) in self.gm.board.get_valid_moves():
                            self.save_history()
                            if self.gm.process_move(r, c) and self.move_sound: self.move_sound.play()
                            if not self.gm.is_playing:
                                self.is_winning, self.show_full_image = True, True
                                self.win_start_time = pygame.time.get_ticks()

            # Bàn phím (Giữ nguyên)
            if event.type == pygame.KEYDOWN and self.gm.is_playing and not self.is_auto_solving and not self.is_paused:
                er, ec = self.gm.board.get_empty_pos()
                tr, tc = er, ec
                if event.key in (pygame.K_w, pygame.K_UP): tr -= 1
                elif event.key in (pygame.K_s, pygame.K_DOWN): tr += 1
                elif event.key in (pygame.K_a, pygame.K_LEFT): tc -= 1
                elif event.key in (pygame.K_d, pygame.K_RIGHT): tc += 1
                if (tr, tc) != (er, ec) and (tr, tc) in self.gm.board.get_valid_moves():
                    self.save_history()
                    if self.gm.process_move(tr, tc) and self.move_sound: self.move_sound.play()
                    if not self.gm.is_playing:
                        self.is_winning, self.show_full_image = True, True
                        self.win_start_time = pygame.time.get_ticks()

        return "PLAYING"

    def update(self):
        if self.gm and not self.is_paused: 
            self.gm.update_time()

            if self.is_auto_solving and self.gm.is_playing:
                current_time = pygame.time.get_ticks()
                if current_time - self.last_auto_move > 200:
                    if self.gm.get_ai_hint() and self.move_sound: self.move_sound.play()
                    self.last_auto_move = current_time
                    if not self.gm.is_playing: 
                        self.is_auto_solving = False
                        self.is_winning, self.show_full_image = True, True
                        self.win_start_time = pygame.time.get_ticks()

    def draw_wood_frame(self, surface, x, y, width, height):
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (222, 184, 135), rect, border_radius=15)
        
        # Vân gỗ
        texture = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        random.seed(42)
        for _ in range(60):
            gx, gy1 = random.randint(0, rect.width), random.randint(0, rect.height)
            gy2 = gy1 + random.randint(50, 150)
            thickness = random.randint(1, 4)
            pygame.draw.line(texture, (205, 170, 125, 120), (gx, gy1), (gx, gy2), thickness)
        surface.blit(texture, (rect.x, rect.y))
        
        # Rãnh trong
        border_thickness = 15
        inner_rect = pygame.Rect(rect.x + border_thickness, rect.y + border_thickness,
                                 rect.width - border_thickness * 2, rect.height - border_thickness * 2)
        pygame.draw.rect(surface, (130, 85, 60), inner_rect, border_radius=8)

    def draw_top_stat_pill(self, x, y, width, text, text_color, is_record=False):
        rect = pygame.Rect(x, y, width, 40)
        bg_color, border_color = ((255, 220, 230), (255, 180, 200)) if is_record else ((235, 245, 255), (200, 225, 255))
        pygame.draw.rect(self.v_surf, bg_color, rect, border_radius=20)
        pygame.draw.rect(self.v_surf, border_color, rect, border_radius=20, width=2)
        surf = self.font_stat.render(text, True, text_color)
        self.v_surf.blit(surf, surf.get_rect(center=rect.center))

    def render(self):
        # 1. XÓA SẠCH VIRTUAL SURFACE VÀ VẼ LÊN ĐÓ
        self.v_surf.fill((255, 246, 233))
        if self.bg_img: self.v_surf.blit(self.bg_img, (0, 0))

        if self.title_img:
            self.v_surf.blit(self.title_img, (self.base_w//2 - self.title_img.get_width()//2, 10))
        else:
            title_txt = self.font_stat.render("CHƠI ĐƠN", True, (0, 120, 120))
            self.v_surf.blit(title_txt, (self.base_w//2 - title_txt.get_width()//2, 25))

        self.draw_top_stat_pill(80, 80, 140, self.gm.get_formatted_time(), (50, 100, 150)) 
        self.draw_top_stat_pill(240, 80, 140, f"CẤP ĐỘ: {self.size}x{self.size}", (50, 100, 150))
        self.draw_top_stat_pill(400, 80, 160, f"DI CHUYỂN: {self.gm.move_count}", (200, 80, 100))
        self.draw_top_stat_pill(580, 80, 140, f"KỶ LỤC: {self.best_score}", (200, 80, 100), is_record=True)

        frame_pad = 20
        self.draw_wood_frame(self.v_surf, config.MARGIN_LEFT - frame_pad, config.MARGIN_TOP - frame_pad, 
                             config.BOARD_SIZE + frame_pad*2, config.BOARD_SIZE + frame_pad*2)

        # Chuyển hướng vẽ của Renderer sang virtual surface
        self.renderer.screen = self.v_surf 
        self.renderer.draw_board(self.gm.board.matrix, self.gm.size, self.image_slices, self.full_image, self.show_full_image)
        self.renderer.screen = self.screen # Trả lại như cũ

        # Nền mờ nếu Tạm dừng
        if self.is_paused:
            overlay = pygame.Surface((self.base_w, self.base_h), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 150))
            self.v_surf.blit(overlay, (0, 0))

        # 2. VẼ ẢNH CUSTOM CHO CÁC NÚT
        for btn in self.buttons:
            img = self.btn_images[btn["name"]].copy()
            
            # --- Logic thay đổi trạng thái cho Nút AI GIẢI ---
            if btn["id"] == "ai":
                if self.is_auto_solving:
                    # Đang giải -> Phủ màu xanh lá nhạt
                    img.fill((150, 255, 150), special_flags=pygame.BLEND_RGB_MULT)
                elif self.gm.move_count < 50:
                    # Chưa đủ 50 bước -> Phủ màu xám
                    img.fill((120, 120, 120), special_flags=pygame.BLEND_RGB_MULT)
                    
            # --- Logic thay đổi trạng thái cho Nút TẠM DỪNG ---
            elif btn["id"] == "pause" and self.is_paused:
                # Đang dừng -> Phủ màu đỏ nhạt (hoặc bạn có thể tải ảnh btn_play.png)
                img.fill((255, 180, 180), special_flags=pygame.BLEND_RGB_MULT)

            self.v_surf.blit(img, btn["rect"].topleft)

        # 3. KỸ THUẬT SCALING RESPONSIVE: Ép Màn Hình Ảo ra Cửa Sổ Thật
        actual_w, actual_h = self.screen.get_size()
        scale = min(actual_w / self.base_w, actual_h / self.base_h)
        new_w, new_h = int(self.base_w * scale), int(self.base_h * scale)
        offset_x, offset_y = (actual_w - new_w) // 2, (actual_h - new_h) // 2

        scaled_surf = pygame.transform.smoothscale(self.v_surf, (new_w, new_h))
        self.screen.fill((40, 35, 30)) # Vẽ 2 viền đen chống móp méo hình (Letterboxing)
        self.screen.blit(scaled_surf, (offset_x, offset_y))