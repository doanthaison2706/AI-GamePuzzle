import pygame
import os
from configs import game_config as config
from src.core.single_game_manager import SingleGameManager
from src.ui.renderer import Renderer
from src.utils.image_crop import slice_image
from src.ui.components import PillButton
from src.core.settings_manager import SettingsManager
from src.ai.bot import AIBot

class SinglePlayerScreen:
    def __init__(self, screen, setup_data):
        self.screen = screen
        self.renderer = Renderer(screen)

        self.size = setup_data["size"]
        self.full_image = setup_data.get("image", None)
        self.image_slices = None

        if self.full_image:
            _, self.image_slices = slice_image(self.full_image, config.BOARD_SIZE, self.size)

        self.gm = SingleGameManager(size=self.size, time_limit=setup_data.get("time", 0))
        self.gm.new_game()
        self.player = self.gm.players[0]
        self.board = self.gm.board
        self.show_full_image = False

        # --- LẤY DỮ LIỆU TỪ SETUP ---
        p1_type = setup_data.get("p1_type", "HUMAN")
        difficulty = setup_data.get("difficulty", "hard")

        self.is_bot = (p1_type == "BOT") # Lưu cờ xác nhận là BOT từ đầu

        # --- KHỞI TẠO AI ---
        self.bot = AIBot(size=self.size, difficulty=difficulty)
        self.is_ai_playing = self.is_bot # Nếu là BOT thì tự bật True luôn
        self.last_bot_move_time = 0
        self.bot_speed = 300

        self.settings_mgr = SettingsManager()
        self.best_score = self.settings_mgr.get(f"high_score_{self.size}x{self.size}")
        if self.best_score is None:
            self.best_score = "--"

        self.is_paused = False
        self.is_winning = False
        self.win_start_time = 0

        try:
            self.move_sound = pygame.mixer.Sound("assets/sounds/move.wav")
            mgr = SettingsManager()
            vol = mgr.get("move_volume")
            if vol is not None:
                self.move_sound.set_volume(vol / 100.0)
        except:
            self.move_sound = None

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
            frame_size = config.BOARD_SIZE + 40
            self.wood_frame_img = pygame.transform.smoothscale(self.wood_frame_img, (frame_size, frame_size))
        except:
            self.wood_frame_img = None

        try:
            self.font_stat = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", 20)
            self.font_btn = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", 16)
        except:
            self.font_stat = pygame.font.SysFont("arial", 20, bold=True)
            self.font_btn = pygame.font.SysFont("arial", 14, bold=True)

        btn_w, btn_h = 90, 85
        spacing = 15
        total_w = btn_w * 6 + spacing * 5
        start_x = (config.WINDOW_WIDTH - total_w) // 2
        btn_y = config.WINDOW_HEIGHT - 110

        def _pb(i, text, c_top, c_bot, c_shad):
            x = start_x + (btn_w + spacing) * i
            return PillButton((x, btn_y, btn_w, btn_h), text, self.font_btn,
                              color_top=c_top, color_bot=c_bot, shadow_color=c_shad)

        self.btn_hint   = _pb(0, "HINT",   (255,230,190), (255,204,150), (230,180,120))
        self.btn_ai     = _pb(1, "AI SOLVE",  (190,240,255), (135,215,245), (110,190,220))
        self.btn_undo   = _pb(2, "UNDO", (210,250,200), (160,230,150), (130,200,120))
        self.btn_replay = _pb(3, "REPLAY", (255,200,230), (255,150,200), (220,120,170))
        self.btn_pause  = _pb(4, "PAUSE", (200,210,255), (150,170,255), (120,140,220))
        self.btn_quit   = _pb(5, "EXIT",    (255,190,190), (255,140,140), (220,110,110))

        # --- LÀM MỜ NÚT AI NẾU ĐÃ CHỌN LÀ BOT TỪ SETUP ---
        if self.is_bot:
            self.btn_ai.text = "AUTOMATIC"
            self.btn_ai.color_top = (180, 180, 180)
            self.btn_ai.color_bot = (140, 140, 140)
            self.btn_ai.shadow_color = (100, 100, 100)
            # Khóa nút Gợi ý
            self.btn_hint.color_top = (180, 180, 180)
            self.btn_hint.color_bot = (140, 140, 140)
            self.btn_hint.shadow_color = (100, 100, 100)

            # Khóa nút Hoàn tác
            self.btn_undo.color_top = (180, 180, 180)
            self.btn_undo.color_bot = (140, 140, 140)
            self.btn_undo.shadow_color = (100, 100, 100)

        self._refresh_button_states()

    def _refresh_button_states(self):
        controls_locked = self.is_paused or self.is_winning

        self.btn_hint.enabled = (not self.is_bot) and (not self.is_ai_playing) and (not controls_locked)
        self.btn_ai.enabled = (not self.is_bot) and (not self.is_paused) and (not self.is_winning)
        self.btn_undo.enabled = (not self.is_bot) and (not self.is_ai_playing) and (not controls_locked)
        self.btn_replay.enabled = (not self.is_paused) and (not self.is_winning)
        self.btn_pause.enabled = not self.is_winning
        self.btn_quit.enabled = True

    def handle_events(self, events):
        self._refresh_button_states()

        if self.is_winning:
            if pygame.time.get_ticks() - self.win_start_time >= 1500:
                result_data = {
                    "time": self.gm.get_formatted_time(),
                    "moves": self.player.move_count,
                    "size": self.size,
                    "is_solved": self.gm.board.is_solved()
                }
                return "WIN_SINGLE", result_data
            return "PLAYING"

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.show_full_image = True
            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                self.show_full_image = False

            # --- NÚT AI GIẢI: Bật/tắt AI  ---
            if not self.is_bot and self.btn_ai.handle_event(event):
                self.is_ai_playing = not self.is_ai_playing
                if self.is_ai_playing:
                    self.bot.clear_memory()
                self.btn_ai.text = "STOP AI" if self.is_ai_playing else "AI SOLVE"

            if not self.is_bot and not self.is_ai_playing:
                if self.btn_undo.handle_event(event):
                    if self.gm.undo():
                        self.bot.clear_memory()
                        if self.move_sound: self.move_sound.play()

            # --- GỢI Ý: Khóa thao tác nếu là chế độ BOT hoặc AI đang tự giải ---
            if not self.is_bot and not self.is_ai_playing:
                if self.btn_hint.handle_event(event):
                    if self.gm.is_playing and not self.is_winning and not self.is_paused:
                        empty_r, empty_c = self.board.get_empty_pos()
                        dx, dy = self.bot.get_next_move(self.board.matrix, empty_r, empty_c)
                        if (dx, dy) != (0, 0):
                            tr, tc = empty_r + dx, empty_c + dy
                            if self.gm.process_move(tr, tc):
                                if self.move_sound: self.move_sound.play()
                                if not self.gm.is_playing:
                                    self._on_win()

            # --- CHƠI LẠI: Tự động chạy AI nếu là BOT ---
            if self.btn_replay.handle_event(event):
                self.gm.new_game()
                self.is_winning = False
                self.is_ai_playing = self.is_bot
                if self.is_bot:
                    self.bot.clear_memory()

            if self.btn_pause.handle_event(event):
                self.is_paused = not self.is_paused
                self.btn_pause.text = "CONTINUE" if self.is_paused else "PAUSE"
                self._refresh_button_states()
            if self.btn_quit.handle_event(event):   return "MENU"

            if self.gm.is_playing and not self.show_full_image and not self.is_paused and not self.is_ai_playing:
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

                    if not self.gm.is_playing:
                        self._on_win()

        return "PLAYING"

    def _on_win(self):
        if self.is_winning: return
        self.is_winning = True
        self.win_start_time = pygame.time.get_ticks()
        self.show_full_image = True
        self.is_ai_playing = False
        if not self.is_bot:
            self.btn_ai.text = "AI SOLVE"
            if self.gm.board.is_solved():
                if self.best_score == "--" or self.player.move_count < self.best_score:
                    self.best_score = self.player.move_count
                    self.settings_mgr.update({f"high_score_{self.size}x{self.size}": self.best_score})

    def update(self, dt: float = 0.0):
        if self.gm and not self.is_paused:
            self.gm.update_time(dt)
            if not self.gm.is_playing and not self.is_winning:
                self._on_win()

        if self.is_ai_playing and self.gm.is_playing and not self.is_paused and not self.is_winning:
            current_time = pygame.time.get_ticks()

            if current_time - self.last_bot_move_time >= self.bot_speed:
                empty_r, empty_c = self.board.get_empty_pos()

                dx, dy = self.bot.get_next_move(self.board.matrix, empty_r, empty_c)

                if (dx, dy) != (0, 0):
                    target_r, target_c = empty_r + dx, empty_c + dy

                    if self.gm.process_move(target_r, target_c):
                        if self.move_sound: self.move_sound.play()
                        self.last_bot_move_time = current_time

                        if not self.gm.is_playing:
                            self._on_win()

    def draw_gradient_rect(self, surface, rect, color_top, color_bottom, radius, shadow_color=None, shadow_offset=6, border_color=None):
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
        rect = pygame.Rect(x, y, width, 40)
        bg_color = (255, 220, 230) if is_record else (235, 245, 255)
        border_color = (255, 180, 200) if is_record else (200, 225, 255)

        pygame.draw.rect(self.screen, bg_color, rect, border_radius=20)
        pygame.draw.rect(self.screen, border_color, rect, border_radius=20, width=2)

        surf = self.font_stat.render(text, True, text_color)
        self.screen.blit(surf, surf.get_rect(center=rect.center))

    def render(self):
        screen_w, screen_h = self.screen.get_size()
        self._refresh_button_states()

        if self.bg_img: self.screen.blit(self.bg_img, (0, 0))
        else: self.screen.fill((255, 246, 233))

        if self.title_img:
            self.screen.blit(self.title_img, (screen_w//2 - self.title_img.get_width()//2, 10))
        else:
            title_txt = self.font_stat.render("SINGLE PLAYER", True, (0, 120, 120))
            self.screen.blit(title_txt, (screen_w//2 - title_txt.get_width()//2, 25))

        stat_y = 80
        color_text_blue = (50, 100, 150)
        color_text_red = (200, 80, 100)

        # 1. Kích thước linh hoạt cho 5 ô (ô CORRECT cần rộng hơn một chút)
        w_time = 110
        w_level = 130
        w_move = 130
        w_correct = 170 
        w_best = 130
        gap = 15 # Khoảng cách giữa các ô

        # 2. Tính tổng chiều rộng để căn ra chính giữa màn hình
        total_w = w_time + w_level + w_move + w_correct + w_best + (gap * 4)
        sx = (screen_w - total_w) // 2

        # 3. Tính toán vị trí X cho từng ô
        x_time = sx
        x_level = x_time + w_time + gap
        x_move = x_level + w_level + gap
        x_correct = x_move + w_move + gap
        x_best = x_correct + w_correct + gap

        correct_tiles = self.gm.board.count_correct_tiles()
        total_tiles = self.gm.board.total_tiles

        # 4. Vẽ cả 5 ô lên màn hình
        self.draw_top_stat_pill(x_time, stat_y, w_time, self.gm.get_formatted_time(), color_text_blue, color_text_blue)
        self.draw_top_stat_pill(x_level, stat_y, w_level, f"LEVEL: {self.size}x{self.size}", color_text_blue, color_text_blue)
        self.draw_top_stat_pill(x_move, stat_y, w_move, f"MOVE: {self.player.move_count}", color_text_red, color_text_red)
        self.draw_top_stat_pill(x_correct, stat_y, w_correct, f"CORRECT: {correct_tiles}/{total_tiles}", color_text_red, color_text_red)
        
        # Ô Kỷ lục có màu nền khác biệt (is_record=True)
        self.draw_top_stat_pill(x_best, stat_y, w_best, f"BEST: {self.best_score}", color_text_red, color_text_red, is_record=True)

        if self.wood_frame_img:
            frame_x = config.MARGIN_LEFT - 20
            frame_y = config.MARGIN_TOP - 20
            self.screen.blit(self.wood_frame_img, (frame_x, frame_y))
        else:
            pygame.draw.rect(self.screen, (220, 180, 140),
                             (config.MARGIN_LEFT-20, config.MARGIN_TOP-20, config.BOARD_SIZE+40, config.BOARD_SIZE+40), border_radius=20)
            pygame.draw.rect(self.screen, (180, 130, 90),
                             (config.MARGIN_LEFT-20, config.MARGIN_TOP-20, config.BOARD_SIZE+40, config.BOARD_SIZE+40), border_radius=20, width=4)

        self.renderer.draw_board(self.board.matrix, self.gm.size, self.image_slices, self.full_image, self.show_full_image)

        if self.is_paused:
            overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 150))
            self.screen.blit(overlay, (0, 0))
            pause_txt = self.font_stat.render("PAUSED", True, (200, 80, 100))
            self.screen.blit(pause_txt, pause_txt.get_rect(center=(screen_w//2, screen_h//2)))

        mouse = pygame.mouse.get_pos()
        self.btn_hint.draw(self.screen, mouse)
        self.btn_ai.draw(self.screen, mouse)
        self.btn_undo.draw(self.screen, mouse)
        self.btn_replay.draw(self.screen, mouse)
        self.btn_pause.draw(self.screen, mouse)
        self.btn_quit.draw(self.screen, mouse)