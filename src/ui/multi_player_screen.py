import pygame
import random
from configs import game_config as config
from src.core.multi_manager import MultiplayerManager
from src.ui.renderer import Renderer
from src.utils.image_crop import slice_image

class MultiPlayerScreen:
    def __init__(self, screen, setup_data):
        self.screen = screen
        self.renderer = Renderer(screen)
        
        # --- SỬA LỖI CHÍ MẠNG: KÍCH THƯỚC ĐỘNG THEO BOARD_SIZE ---
        b_size = config.BOARD_SIZE
        self.gap = 180 
        self.side_margin = 60 # Khoảng cách lề 2 bên
        
        # Chiều rộng tự động = 2 Lề + 2 Bàn cờ + Khoảng trống giữa
        self.base_w = (self.side_margin * 2) + (b_size * 2) + self.gap
        
        # Tọa độ Y động
        self.board_y = 150
        self.stats_y = self.board_y + b_size + 30
        self.btn_y = self.stats_y + 110 + 40 # 110 là chiều cao cục stats
        
        # Chiều cao tự động = Tọa độ nút + Chiều cao nút + Lề đáy
        self.base_h = self.btn_y + 120
        
        self.v_surf = pygame.Surface((self.base_w, self.base_h))
        
        # --- MANAGER & LOGIC ---
        self.manager = MultiplayerManager(
            size=setup_data["size"],
            target_score=setup_data["score"],
            mode=setup_data.get("mode", "PvP"),
            ai_difficulty=setup_data.get("difficulty", "medium"),
            time_limit=setup_data.get("time", 0)
        )
        self.is_paused = False 

        try:
            self.move_sound = pygame.mixer.Sound("assets/sounds/move.wav")
        except:
            self.move_sound = None

        # --- LOAD ẢNH NỀN & TITLE ---
        try:
            self.bg_img = pygame.image.load("assets/images/background_gameplay.png").convert()
            self.bg_img = pygame.transform.scale(self.bg_img, (self.base_w, self.base_h))
        except: 
            self.bg_img = None
            
        self.title_img = None

        # --- LOAD FONTS ---
        try:
            self.font_title = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", 45)
            self.font_stat = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", int(b_size*0.035)) # Font scale theo bảng
            self.font_btn = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", 18)
        except:
            self.font_title = pygame.font.SysFont("arial", 40, bold=True)
            self.font_stat = pygame.font.SysFont("arial", max(16, int(b_size*0.03)), bold=True)
            self.font_btn = pygame.font.SysFont("arial", 16, bold=True)

        # --- LOAD 5 ẢNH NÚT / HOẶC DÙNG NÚT VẼ DỰ PHÒNG ---
        btn_w, btn_h = 110, 50
        spacing = 30
        total_w = (btn_w * 5) + (spacing * 4)
        start_x = (self.base_w - total_w) // 2

        self.btn_images = {}
        btn_files = ["btn_hint1.png", "btn_restart.png", "btn_exit_2.png", "btn_pause.png", "btn_hint2.png"]
        self.btn_ids = ["hint1", "restart", "exit", "pause", "hint2"]
        self.btn_texts = ["GỢI Ý P1", "CHƠI LẠI", "THOÁT", "TẠM DỪNG", "GỢI Ý P2"] 
        
        for i, name in enumerate(btn_files):
            try:
                img = pygame.image.load(f"assets/images/{name}").convert_alpha()
                self.btn_images[self.btn_ids[i]] = pygame.transform.smoothscale(img, (btn_w, btn_h))
            except:
                self.btn_images[self.btn_ids[i]] = None # Báo Null để vẽ dự phòng

        self.buttons = []
        for i in range(5):
            rect = pygame.Rect(start_x + i * (btn_w + spacing), self.btn_y, btn_w, btn_h)
            self.buttons.append({"id": self.btn_ids[i], "rect": rect, "text": self.btn_texts[i]})
            
        # --- LOAD & SCALE ẢNH REVIEW CHỌN NÚT ---
        self.full_image = setup_data.get("image", None)
        self.review_image = None
        self.image_slices = None # Thêm biến lưu các mảnh ảnh
        
        if self.full_image:
            self.review_image = pygame.transform.smoothscale(self.full_image, (150, 150))
            # Cắt ảnh cho các ô gạch giống y hệt màn chơi đơn
            _, self.image_slices = slice_image(self.full_image, config.BOARD_SIZE, self.manager.size)
            
        try:
            self.icon_p1 = pygame.image.load(
                "assets/images/icon_p1.png"
            ).convert_alpha()

            self.icon_p1 = pygame.transform.smoothscale(
                self.icon_p1,
                (28, 28)
            )
        except:
            self.icon_p1 = None

        try:
            self.icon_p2 = pygame.image.load(
                "assets/images/icon_p2.png"
            ).convert_alpha()

            self.icon_p2 = pygame.transform.smoothscale(
                self.icon_p2,
                (28, 28)
            )
        except:
            self.icon_p2 = None
            
        self.round_end_time = 0

    def handle_events(self, events):
        # Lấy kích thước màn hình thật tại thời điểm hiện tại
        screen_w, screen_h = self.screen.get_size()
        cx = screen_w // 2
        
        # --- ĐỒNG BỘ BỐ CỤC ĐỂ HITBOX CHUẨN 100% ---
        board_y = 160 # Kéo bàn cờ lên cao một chút để nhường chỗ cho nút bấm ở đáy
        gap = 180     # Khoảng cách giữa 2 bàn giống hệt trên __init__
        margin_x1 = cx - (gap // 2) - config.BOARD_SIZE
        margin_x2 = cx + (gap // 2)

        # Cập nhật tọa độ hitbox 5 nút theo kích thước mới
        btn_w, btn_h, spacing = 110, 50, 30
        total_w = (btn_w * 5) + (spacing * 4)
        start_x = (screen_w - total_w) // 2
        btn_y = screen_h - btn_h - 50 # Bám sát đáy màn hình
        
        for i, btn in enumerate(self.buttons):
            btn["rect"].x = start_x + i * (btn_w + spacing)
            btn["rect"].y = btn_y

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                vx, vy = event.pos # Dùng tọa độ chuột thật 100%
                
                for btn in self.buttons:
                    if btn["rect"].collidepoint((vx, vy)):
                        if btn["id"] == "exit": return "MENU"
                        elif btn["id"] == "restart": self.manager.init_new_round()
                        elif btn["id"] == "pause": self.is_paused = not self.is_paused
                        
                        # --- FIX: CHỈ CHO PHÉP CLICK GỢI Ý NẾU LÀ NGƯỜI CHƠI ---
                        elif btn["id"] == "hint1":
                            # P1 là người nếu không phải chế độ Máy vs Máy
                            if self.manager.mode not in ["AIvAI", "EvE", "CvC"]: 
                                self.manager.trigger_hint(1)
                                
                        elif btn["id"] == "hint2":
                            # P2 chỉ là người nếu là chế độ PvP
                            if self.manager.mode == "PvP": 
                                self.manager.trigger_hint(2)
                if not self.is_paused and self.manager.round_winner == 0:
                    # Bàn 1
                    if margin_x1 <= vx <= margin_x1 + config.BOARD_SIZE and board_y <= vy <= board_y + config.BOARD_SIZE:
                        t_size = config.BOARD_SIZE // self.manager.size
                        if self.manager.gm1.process_move(int((vy-board_y)//t_size), int((vx-margin_x1)//t_size)):
                            if self.move_sound: self.move_sound.play()
                    # Bàn 2
                    if margin_x2 <= vx <= margin_x2 + config.BOARD_SIZE and board_y <= vy <= board_y + config.BOARD_SIZE:
                        t_size = config.BOARD_SIZE // self.manager.size
                        if self.manager.gm2.process_move(int((vy-board_y)//t_size), int((vx-margin_x2)//t_size)):
                            if self.move_sound: self.move_sound.play()

            # Phím P1
            if event.type == pygame.KEYDOWN and not self.is_paused and self.manager.round_winner == 0:
                
                # 1. ĐIỀU KHIỂN BÀN 1 (P1) - Bằng phím W, A, S, D
                if self.manager.gm1.is_playing:
                    er, ec = self.manager.gm1.board.get_empty_pos()
                    tr, tc = er, ec
                    if event.key == pygame.K_w: tr -= 1
                    elif event.key == pygame.K_s: tr += 1
                    elif event.key == pygame.K_a: tc -= 1
                    elif event.key == pygame.K_d: tc += 1
                    
                    if (tr, tc) != (er, ec):
                        if self.manager.gm1.process_move(tr, tc):
                            if self.move_sound: self.move_sound.play()
                            self.manager._check_win_condition() # Kích hoạt check thắng luôn

                # 2. ĐIỀU KHIỂN BÀN 2 (P2) - Bằng phím Mũi Tên (Chỉ dành cho chế độ PvP)
                if self.manager.gm2.is_playing and self.manager.mode == "PvP":
                    er, ec = self.manager.gm2.board.get_empty_pos()
                    tr, tc = er, ec
                    if event.key == pygame.K_UP: tr -= 1
                    elif event.key == pygame.K_DOWN: tr += 1
                    elif event.key == pygame.K_LEFT: tc -= 1
                    elif event.key == pygame.K_RIGHT: tc += 1
                    
                    if (tr, tc) != (er, ec):
                        if self.manager.gm2.process_move(tr, tc):
                            if self.move_sound: self.move_sound.play()
                            self.manager._check_win_condition() # Kích hoạt check thắng luôn
                        
        if self.manager.round_winner != 0:
            if self.round_end_time == 0:
                self.round_end_time = pygame.time.get_ticks() 
            elif pygame.time.get_ticks() - self.round_end_time > 2000: # Đợi 2 giây
                if getattr(self.manager, 'done', False):
                    # Trả về tín hiệu WIN_MULTI cho game_app.py xử lý
                    return "WIN_MULTI", {
                        "winner": self.manager.match_winner,
                        "score1": self.manager.score_p1,
                        "score2": self.manager.score_p2
                    }
                else:
                    # Bắt đầu hiệp mới
                    self.manager.init_new_round()
                    self.round_end_time = 0 # Reset đồng hồ

        return "PLAYING_MULTI"

    def update(self):
        if not self.is_paused and not getattr(self.manager, 'done', False):
            if self.manager.round_winner == 0:
                self.manager.update_time()
                self.manager.update_ai()

    def _draw_vietnamese_wood_panel(self, surface, rect, is_board=False):
        """
        Khung gỗ cho bàn cờ:
        - viền ngoài sáng mỏng
        - thân gỗ nâu đỏ
        - lõi trong đậm để chứa gạch
        """
        # Viền ngoài sáng nhẹ
        outer_border = (205, 170, 125)

        # Thân gỗ chính
        wood_base = (105, 55, 35)

        # Lõi trong đậm
        inner_dark = (45, 20, 12)

        # 1. Viền sáng mỏng ngoài cùng
        pygame.draw.rect(
            surface,
            outer_border,
            rect,
            border_radius=12
        )

        # 2. Lớp thân gỗ
        middle_rect = rect.inflate(-4, -4)
        pygame.draw.rect(
            surface,
            wood_base,
            middle_rect,
            border_radius=10
        )

        # 3. Vân gỗ
        grain_surf = pygame.Surface(
            (middle_rect.width, middle_rect.height),
            pygame.SRCALPHA
        )

        rng = random.Random(123)

        for _ in range(30):
            gx = rng.randint(0, middle_rect.width)
            gy = rng.randint(0, middle_rect.height)

            pygame.draw.line(
                grain_surf,
                (130, 75, 50, 90),
                (gx, gy),
                (gx, gy + rng.randint(30, 90)),
                rng.randint(1, 3)
            )

        surface.blit(grain_surf, middle_rect.topleft)

        # 4. Lõi trong chứa gạch
        if is_board:
            inner_rect = middle_rect.inflate(-24, -24)

            pygame.draw.rect(
                surface,
                inner_dark,
                inner_rect,
                border_radius=6
            )
            
    def _draw_dark_wood_frame(self, surface, rect):
        """
        Khung gỗ trầm đậm cho progress / ảnh preview
        """
        dark_wood = (75, 35, 20)
        border_gold = (170, 130, 80)
        deep_shadow = (40, 15, 10)

        # viền ngoài
        pygame.draw.rect(
            surface,
            border_gold,
            rect,
            border_radius=14
        )

        # thân gỗ
        inner = rect.inflate(-4, -4)

        pygame.draw.rect(
            surface,
            dark_wood,
            inner,
            border_radius=12
        )

        # bóng lõm trong
        core = inner.inflate(-8, -8)

        pygame.draw.rect(
            surface,
            deep_shadow,
            core,
            border_radius=10
        )

        # vân gỗ
        grain = pygame.Surface((inner.width, inner.height), pygame.SRCALPHA)
        rng = random.Random(456)

        for _ in range(25):
            x = rng.randint(0, inner.width)
            y = rng.randint(0, inner.height)

            pygame.draw.line(
                grain,
                (110, 60, 35, 80),
                (x, y),
                (x + rng.randint(-5, 5), y + rng.randint(20, 60)),
                2
            )

        surface.blit(grain, inner.topleft)

    def _draw_progress_bar(self, surface, x, y, width, height, progress, player_name, is_p1=True):
        frame_rect = pygame.Rect(x - 8, y - 8, width + 16, height + 16)
        self._draw_dark_wood_frame(surface, frame_rect)

        rect = pygame.Rect(x, y, width, height)

        pygame.draw.rect(surface, (245, 240, 235), rect, border_radius=height//2)
        pygame.draw.rect(surface, (180, 150, 130), rect, border_radius=height//2, width=1)

        if progress > 0:
            fill_width = max(height, int(width * progress))
            color = (255, 182, 193) if is_p1 else (173, 216, 230)

            pygame.draw.rect(
                surface,
                color,
                pygame.Rect(x, y, fill_width, height),
                border_radius=height//2
            )

        txt_surf = self.font_stat.render(
            f"Tiến độ: {int(progress * 100)}%",
            True,
            (80, 50, 35)
        )

        surface.blit(txt_surf, txt_surf.get_rect(center=rect.center))

    def _draw_scoreboard(self, surface, x, y, width, height, score1, score2):
        """
        Scoreboard pastel mang vibe Việt:
        - pastel mềm
        - hoa văn sen / mây
        - viền vàng champagne
        """
        rect = pygame.Rect(x, y, width, height)

        # ===== palette pastel =====
        outer = (248, 240, 225)       # kem ngà
        border = (215, 190, 145)      # vàng champagne
        left_fill = (255, 225, 230)   # hồng pastel
        right_fill = (220, 235, 250)  # xanh pastel
        text_left = (180, 90, 110)
        text_right = (90, 120, 180)
        pattern = (235, 210, 180)

        # ===== 1. khung ngoài =====
        pygame.draw.rect(
            surface,
            outer,
            rect,
            border_radius=18
        )

        pygame.draw.rect(
            surface,
            border,
            rect,
            border_radius=18,
            width=2
        )

        # ===== 2. phần lõi =====
        inner = rect.inflate(-10, -10)

        left_rect = pygame.Rect(
            inner.x,
            inner.y,
            inner.width // 2,
            inner.height
        )

        right_rect = pygame.Rect(
            inner.centerx,
            inner.y,
            inner.width // 2,
            inner.height
        )

        pygame.draw.rect(
            surface,
            left_fill,
            left_rect,
            border_top_left_radius=12,
            border_bottom_left_radius=12
        )

        pygame.draw.rect(
            surface,
            right_fill,
            right_rect,
            border_top_right_radius=12,
            border_bottom_right_radius=12
        )

        # ===== 3. vạch chia =====
        pygame.draw.line(
            surface,
            border,
            (inner.centerx, inner.y + 6),
            (inner.centerx, inner.bottom - 6),
            2
        )

        # ===== 4. hoa văn mây / sen mini =====
        # bên trái
       # ===== DRAW ICON =====
        icon_size = 28

        p1_icon_rect = pygame.Rect(
            left_rect.x + 18,
            left_rect.centery - icon_size // 2,
            icon_size,
            icon_size
        )

        p2_icon_rect = pygame.Rect(
            right_rect.right - 18 - icon_size,
            right_rect.centery - icon_size // 2,
            icon_size,
            icon_size
        )

        if self.icon_p1:
            surface.blit(self.icon_p1, p1_icon_rect.topleft)
        else:
            pygame.draw.rect(surface, (255, 245, 245), p1_icon_rect, border_radius=8)
            pygame.draw.rect(surface, border, p1_icon_rect, width=1, border_radius=8)

        if self.icon_p2:
            surface.blit(self.icon_p2, p2_icon_rect.topleft)
        else:
            pygame.draw.rect(surface, (245, 248, 255), p2_icon_rect, border_radius=8)
            pygame.draw.rect(surface, border, p2_icon_rect, width=1, border_radius=8)

        # ===== 5. huy hiệu giữa =====
        pygame.draw.circle(
            surface,
            border,
            (inner.centerx, inner.centery),
            8
        )

        pygame.draw.circle(
            surface,
            (255, 250, 245),
            (inner.centerx, inner.centery),
            4
        )

        # ===== 6. text =====
        txt1 = self.font_title.render(f"P1: {score1}", True, text_left)
        txt2 = self.font_title.render(f"P2: {score2}", True, text_right)

        surface.blit(txt1, txt1.get_rect(center=left_rect.center))
        surface.blit(txt2, txt2.get_rect(center=right_rect.center))
        
    def _draw_individual_stat_box(self, surface, x, y, width, height, moves, time_str, score):
        """Khung chứa thông số cá nhân chuẩn form"""
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (255, 250, 245), rect, border_radius=10)
        pygame.draw.rect(surface, (200, 180, 170), rect, border_radius=10, width=3)

        move_txt = self.font_stat.render(f"Số bước: {moves}", True, (80, 60, 50))
        time_txt = self.font_stat.render(f"Thời gian: {time_str}", True, (80, 60, 50))
        surface.blit(move_txt, (x + 25, y + 20))
        surface.blit(time_txt, (x + 25, y + 50))

        score_txt = self.font_stat.render(f"Điểm đạt được: {score}", True, (200, 60, 60))
        surface.blit(score_txt, (x + width - score_txt.get_width() - 25, y + 35))

    def _draw_fallback_button(self, surface, rect, text):
        """Nút dự phòng cực đẹp trong trường hợp lỗi load ảnh"""
        pygame.draw.rect(surface, (180, 150, 200), pygame.Rect(rect.x, rect.y+6, rect.width, rect.height), border_radius=15)
        pygame.draw.rect(surface, (220, 190, 240), rect, border_radius=15)
        pygame.draw.rect(surface, (255, 255, 255), rect, border_radius=15, width=2)
        txt_surf = self.font_btn.render(text, True, (80, 50, 100))
        surface.blit(txt_surf, txt_surf.get_rect(center=rect.center))

    def render(self):
        screen_w, screen_h = self.screen.get_size()

        # ===== 1. VẼ TOÀN BỘ UI LÊN VIRTUAL SURFACE =====
        self.v_surf.fill((255, 248, 238))

        if self.bg_img:
            bg_scaled = pygame.transform.scale(
                self.bg_img,
                (self.base_w, self.base_h)
            )
            self.v_surf.blit(bg_scaled, (0, 0))

        cx = self.base_w // 2

        score_w = min(450, int(self.base_w * 0.4))
        self._draw_scoreboard(
            self.v_surf,
            cx - score_w // 2,
            20,
            score_w,
            75,
            self.manager.score_p1,
            self.manager.score_p2
        )

        board_y = 160 
        stats_y = board_y + config.BOARD_SIZE + 20

        gap = 180
        margin_x1 = cx - (gap // 2) - config.BOARD_SIZE
        margin_x2 = cx + (gap // 2)

        prog1 = self.manager.get_progress(1)
        prog2 = self.manager.get_progress(2)

        time1 = self.manager.gm1.get_formatted_time()
        time2 = self.manager.gm2.get_formatted_time()

        # ===== P1 =====
        bar_w = int(config.BOARD_SIZE * 0.5)
        bar_x1 = margin_x1 + (config.BOARD_SIZE - bar_w) // 2

        self._draw_progress_bar(
            self.v_surf,
            bar_x1,
            board_y - 45,
            bar_w,
            18,
            prog1,
            "P1",
            True
        )

        self._draw_vietnamese_wood_panel(
            self.v_surf,
            pygame.Rect(
                margin_x1 - 15,
                board_y - 15,
                config.BOARD_SIZE + 30,
                config.BOARD_SIZE + 30
            ),
            True
        )

        old_mx, old_my = config.MARGIN_LEFT, config.MARGIN_TOP

        config.MARGIN_LEFT = margin_x1
        config.MARGIN_TOP = board_y

        self.renderer.screen = self.v_surf

        self.renderer.draw_board(
            self.manager.gm1.board.matrix,
            self.manager.size,
            self.image_slices,
            self.full_image,
            False
        )

        self._draw_individual_stat_box(
            self.v_surf,
            margin_x1,
            stats_y,
            config.BOARD_SIZE,
            95,
            self.manager.gm1.move_count,
            time1,
            self.manager.score_p1
        )

        # ===== P2 =====
        bar_x2 = margin_x2 + (config.BOARD_SIZE - bar_w) // 2

        self._draw_progress_bar(
            self.v_surf,
            bar_x2,
            board_y - 45,
            bar_w,
            18,
            prog2,
            "P2",
            False
        )

        self._draw_vietnamese_wood_panel(
            self.v_surf,
            pygame.Rect(
                margin_x2 - 15,
                board_y - 15,
                config.BOARD_SIZE + 30,
                config.BOARD_SIZE + 30
            ),
            True
        )

        config.MARGIN_LEFT = margin_x2

        self.renderer.draw_board(
            self.manager.gm2.board.matrix,
            self.manager.size,
            self.image_slices,
            self.full_image,
            False
        )

        self._draw_individual_stat_box(
            self.v_surf,
            margin_x2,
            stats_y,
            config.BOARD_SIZE,
            95,
            self.manager.gm2.move_count,
            time2,
            self.manager.score_p2
        )

        # ===== preview =====
        if self.review_image:
            preview_size = 150 # SỬA Ở ĐÂY: Giờ gap đã rộng, phóng to ảnh lên 150!

            preview_rect = pygame.Rect(
                cx - preview_size // 2,
                105, # Tọa độ Y này kết hợp với size 150 sẽ thò xuống khe giữa 2 bàn cờ rất đẹp
                preview_size,
                preview_size
            )

            frame_rect = preview_rect.inflate(18, 18)

            self._draw_dark_wood_frame(self.v_surf, frame_rect)

            scaled_preview = pygame.transform.smoothscale(
                self.review_image,
                (preview_size, preview_size)
            )

            self.v_surf.blit(scaled_preview, preview_rect.topleft)

        # ===== restore config =====
        config.MARGIN_LEFT, config.MARGIN_TOP = old_mx, old_my

        # ===== 2. SCALE TO SCREEN =====
        # ===== FULL SCREEN SCALE =====
        scaled_ui = pygame.transform.smoothscale(
            self.v_surf,
            (screen_w, screen_h)
        )

        self.screen.blit(scaled_ui, (0, 0))
        for btn in self.buttons:
            img = self.btn_images.get(btn["id"])
            if img:
                img_copy = img.copy()
                
                # Kiểm tra xem có phải là nút Gợi ý của AI không
                is_p1_ai = self.manager.mode in ["AIvAI", "EvE", "CvC"]
                is_p2_ai = self.manager.mode != "PvP"
                
                if (btn["id"] == "hint1" and is_p1_ai) or (btn["id"] == "hint2" and is_p2_ai):
                    # Phủ màu xám mờ để báo hiệu nút bị vô hiệu hóa
                    img_copy.fill((100, 100, 100), special_flags=pygame.BLEND_RGB_MULT)
                elif btn["id"] == "pause" and self.is_paused:
                    # Phủ đỏ nhạt nếu đang Tạm dừng
                    img_copy.fill((255, 180, 180), special_flags=pygame.BLEND_RGB_MULT)
                    
                self.screen.blit(img_copy, btn["rect"].topleft)
            else:
                self._draw_fallback_button(self.screen, btn["rect"], btn["text"])