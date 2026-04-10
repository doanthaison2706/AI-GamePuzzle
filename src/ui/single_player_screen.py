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
        
        # --- THIẾT LẬP MÀN HÌNH ẢO (LANDSCAPE 1280x720) ---
        self.base_w = 1280
        self.base_h = 720
        self.v_surf = pygame.Surface((self.base_w, self.base_h))
        
        # --- TỌA ĐỘ BỐ CỤC CHÍNH ---
        self.board_size = 540    # Kích thước bàn cờ
        self.board_x = 80        # Cách lề trái 80px
        self.board_y = 130       # Cách đỉnh 130px (Chừa chỗ cho Stats)

        self.right_panel_x = 720 # Panel bên phải bắt đầu từ X=720
        self.right_panel_w = 460 # Chiều rộng panel bên phải
        
        self.size = setup_data["size"]
        self.full_image = setup_data.get("image", None)
        self.image_slices = None
        
        if self.full_image:
            _, self.image_slices = slice_image(self.full_image, self.board_size, self.size)
            
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

        try: self.move_sound = pygame.mixer.Sound("assets/sounds/move.wav")
        except: self.move_sound = None

        # --- LOAD ASSETS ---
        try:
            self.bg_img = pygame.image.load("assets/images/background_gameplay.png").convert()
            self.bg_img = pygame.transform.smoothscale(self.bg_img, (self.base_w, self.base_h))
        except: self.bg_img = None

        try: self.title_img = pygame.image.load("assets/images/title_single.png").convert_alpha()
        except: self.title_img = None

        try: self.font_stat = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", 22)
        except: self.font_stat = pygame.font.SysFont("arial", 22, bold=True)

        # --- LƯỚI NÚT BẤM (3x2) ---
        btn_w, btn_h = 130, 100
        # Tính toán khoảng cách đều nhau cho 3 nút
        spacing_x = (self.right_panel_w - (btn_w * 3)) // 2  
        spacing_y = 20
        
        r1_y = 480 # Vị trí Y hàng nút trên
        r2_y = r1_y + btn_h + spacing_y # Vị trí Y hàng nút dưới

        self.btn_names = ["btn_hint1.png", "btn_solve.png", "btn_undo.png", "btn_restart.png", "btn_pause.png", "btn_exit_2.png"]
        self.btn_images = {}
        
        for name in self.btn_names:
            try:
                img = pygame.image.load(f"assets/images/{name}").convert_alpha()
                self.btn_images[name] = pygame.transform.smoothscale(img, (btn_w, btn_h))
            except:
                fallback = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
                pygame.draw.rect(fallback, (180, 180, 180), fallback.get_rect(), border_radius=15)
                self.btn_images[name] = fallback

        # Gán tọa độ theo Layout Ngang
        self.buttons = [
            {"id": "hint",    "name": "btn_hint1.png",    "rect": pygame.Rect(self.right_panel_x, r1_y, btn_w, btn_h)},
            {"id": "ai",      "name": "btn_solve.png",      "rect": pygame.Rect(self.right_panel_x + btn_w + spacing_x, r1_y, btn_w, btn_h)},
            {"id": "undo",    "name": "btn_undo.png",    "rect": pygame.Rect(self.right_panel_x + (btn_w*2) + (spacing_x*2), r1_y, btn_w, btn_h)},
            {"id": "restart", "name": "btn_restart.png", "rect": pygame.Rect(self.right_panel_x, r2_y, btn_w, btn_h)},
            {"id": "pause",   "name": "btn_pause.png",   "rect": pygame.Rect(self.right_panel_x + btn_w + spacing_x, r2_y, btn_w, btn_h)},
            {"id": "exit",    "name": "btn_exit_2.png",    "rect": pygame.Rect(self.right_panel_x + (btn_w*2) + (spacing_x*2), r2_y, btn_w, btn_h)}
        ]

    def save_history(self):
        matrix_copy = [row[:] for row in self.gm.board.matrix]
        self.history.append((matrix_copy, self.gm.move_count))

    def handle_events(self, events):
        # 1. KIỂM TRA TRẠNG THÁI CHIẾN THẮNG
        if self.is_winning:
            # Đợi 1.5s để người chơi nhìn thấy hình hoàn thiện rồi mới chuyển màn
            if pygame.time.get_ticks() - self.win_start_time >= 1500:
                return "WIN_SINGLE", {"time": self.gm.get_formatted_time(), "moves": self.gm.move_count, "size": self.size}
            return "PLAYING", None

        # 2. TÍNH TOÁN TỌA ĐỘ CHUỘT DỰA TRÊN SCALE
        actual_w, actual_h = self.screen.get_size()
        scale = min(actual_w / self.base_w, actual_h / self.base_h)
        offset_x = (actual_w - int(self.base_w * scale)) // 2
        offset_y = (actual_h - int(self.base_h * scale)) // 2

        for event in events:
            # Bấm Space để xem trước ảnh
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: self.show_full_image = True
            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE: self.show_full_image = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Ép tọa độ chuột thật về tọa độ chuột ảo
                vx = (event.pos[0] - offset_x) / scale
                vy = (event.pos[1] - offset_y) / scale
                v_pos = (vx, vy)
                
                # --- XỬ LÝ NÚT BẤM ---
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
                            return "MENU", None

                # --- XỬ LÝ CLICK BÀN CỜ ---
                if self.gm.is_playing and not self.show_full_image and not self.is_paused and not self.is_auto_solving:
                    if self.board_x <= vx <= self.board_x + self.board_size and \
                       self.board_y <= vy <= self.board_y + self.board_size:
                        t_size = self.board_size // self.gm.size
                        r, c = int((vy - self.board_y) // t_size), int((vx - self.board_x) // t_size)
                        
                        if (r, c) in self.gm.board.get_valid_moves():
                            self.save_history()
                            if self.gm.process_move(r, c) and self.move_sound: self.move_sound.play()
                            # Kiểm tra thắng ngay sau khi click
                            if not self.gm.is_playing:
                                self.is_winning, self.show_full_image = True, True
                                self.win_start_time = pygame.time.get_ticks()

            # --- XỬ LÝ BÀN PHÍM ---
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
                    # Kiểm tra thắng ngay sau khi bấm phím
                    if not self.gm.is_playing:
                        self.is_winning, self.show_full_image = True, True
                        self.win_start_time = pygame.time.get_ticks()

        return "PLAYING", None

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
        self.v_surf.fill((255, 246, 233))
        if self.bg_img: self.v_surf.blit(self.bg_img, (0, 0))

        # --- STATS PILLS (Bên Trái) ---
        # Chỉ giữ lại 3 chỉ số và căn đều phía trên bàn cờ
        self.draw_top_stat_pill(self.board_x, 50, 150, self.gm.get_formatted_time(), (50, 100, 150)) 
        self.draw_top_stat_pill(self.board_x + 170, 50, 150, f"CẤP ĐỘ: {self.size}x{self.size}", (50, 100, 150))
        self.draw_top_stat_pill(self.board_x + 340, 50, 150, f"BƯỚC: {self.gm.move_count}", (200, 80, 100))

        # --- TITLE (Bên Phải - Thay thế cho Kỷ Lục) ---
        # Tính toán điểm chính giữa của khu vực bên phải để đặt Title cho cân đối
        right_center_x = self.right_panel_x + (self.right_panel_w // 2)
        
        if self.title_img:
            # Ép size an toàn nếu ảnh title tải vào hơi bự (giới hạn width khoảng 380px)
            t_w, t_h = self.title_img.get_size()
            if t_w > 380:
                scale_ratio = 380 / t_w
                scaled_title = pygame.transform.smoothscale(self.title_img, (380, int(t_h * scale_ratio)))
                title_rect = scaled_title.get_rect(centerx=right_center_x, centery=70)
                self.v_surf.blit(scaled_title, title_rect)
            else:
                title_rect = self.title_img.get_rect(centerx=right_center_x, centery=70)
                self.v_surf.blit(self.title_img, title_rect)
        else:
            # Chữ dự phòng nếu không có ảnh
            title_txt = self.font_stat.render("CHƠI ĐƠN", True, (200, 80, 100))
            self.v_surf.blit(title_txt, title_txt.get_rect(centerx=right_center_x, centery=70))


        # --- KHUNG PREVIEW (Ảnh góc phải) ---
        preview_y = 130
        preview_h = 320
        self.draw_wood_frame(self.v_surf, self.right_panel_x, preview_y, self.right_panel_w, preview_h)
        if self.full_image:
            # Thu nhỏ ảnh cho vừa rãnh trong của khung gỗ
            thumb_w, thumb_h = self.right_panel_w - 40, preview_h - 40
            thumb = pygame.transform.smoothscale(self.full_image, (thumb_w, thumb_h))
            self.v_surf.blit(thumb, (self.right_panel_x + 20, preview_y + 20))
        else:
            txt = self.font_stat.render("MẶC ĐỊNH", True, (150, 100, 100))
            self.v_surf.blit(txt, txt.get_rect(center=(self.right_panel_x + self.right_panel_w//2, preview_y + preview_h//2)))

        # --- VẼ BÀN CỜ ---
        frame_pad = 20
        self.draw_wood_frame(self.v_surf, self.board_x - frame_pad, self.board_y - frame_pad, 
                             self.board_size + frame_pad*2, self.board_size + frame_pad*2)

        # Gán đè Config động để Renderer vẽ đúng vị trí mới mà không cần sửa code bên Renderer
        config.MARGIN_LEFT = self.board_x
        config.MARGIN_TOP = self.board_y
        config.BOARD_SIZE = self.board_size
        
        self.renderer.screen = self.v_surf 
        self.renderer.draw_board(self.gm.board.matrix, self.gm.size, self.image_slices, self.full_image, self.show_full_image)
        self.renderer.screen = self.screen

        if self.is_paused:
            overlay = pygame.Surface((self.base_w, self.base_h), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 150))
            self.v_surf.blit(overlay, (0, 0))

        # --- VẼ NÚT ---
        for btn in self.buttons:
            img = self.btn_images[btn["name"]].copy()
            if btn["id"] == "ai":
                if self.is_auto_solving: img.fill((150, 255, 150), special_flags=pygame.BLEND_RGB_MULT)
                elif self.gm.move_count < 50: img.fill((120, 120, 120), special_flags=pygame.BLEND_RGB_MULT)
            elif btn["id"] == "pause" and self.is_paused:
                img.fill((255, 180, 180), special_flags=pygame.BLEND_RGB_MULT)
            self.v_surf.blit(img, btn["rect"].topleft)

        # --- SCALE RESPONSIVE ---
        actual_w, actual_h = self.screen.get_size()
        scale = min(actual_w / self.base_w, actual_h / self.base_h)
        new_w, new_h = int(self.base_w * scale), int(self.base_h * scale)
        offset_x, offset_y = (actual_w - new_w) // 2, (actual_h - new_h) // 2

        scaled_surf = pygame.transform.smoothscale(self.v_surf, (new_w, new_h))
        self.screen.fill((40, 35, 30)) 
        self.screen.blit(scaled_surf, (offset_x, offset_y))