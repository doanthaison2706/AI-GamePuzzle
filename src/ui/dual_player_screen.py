import pygame
from configs import game_config as config
from src.core.base_game_manager import BaseGameManager
from src.core.dual_game_manager import DualGameManager
from src.core.player import PlayerSlot, PlayerType
from src.core.settings_manager import SettingsManager
from src.ui.renderer import Renderer
from src.ui.components import PillButton
from src.ai.bot import AIBot

class DualPlayerScreen:
    """Màn hình chế độ 2 người chơi (split-screen)."""

    P1_KEYS = {
        pygame.K_w: (-1, 0),
        pygame.K_s: (1, 0),
        pygame.K_a: (0, -1),
        pygame.K_d: (0, 1),
    }
    P2_KEYS = {
        pygame.K_UP: (-1, 0),
        pygame.K_DOWN: (1, 0),
        pygame.K_LEFT: (0, -1),
        pygame.K_RIGHT: (0, 1),
    }

    def __init__(self, screen, setup_data: dict):
        self.screen = screen
        self.size = setup_data.get("size", 3)

        pygame.display.set_caption("N-Puzzle Arena — Đối Kháng")

        # --- XÁC ĐỊNH LOẠI NGƯỜI CHƠI ---
        p1_type_enum = PlayerType.BOT if setup_data.get("p1_type") == "BOT" else PlayerType.HUMAN
        p2_type_enum = PlayerType.BOT if setup_data.get("p2_type") == "BOT" else PlayerType.HUMAN
        diff_p1 = setup_data.get("p1_diff", "hard")
        diff_p2 = setup_data.get("p2_diff", "hard")

        # Lưu lại cờ xem ai là BOT "cứng" từ đầu
        self.is_p1_bot = (p1_type_enum == PlayerType.BOT)
        self.is_p2_bot = (p2_type_enum == PlayerType.BOT)

        # --- GAME MANAGER ---
        p1 = PlayerSlot(player_id=1, player_type=p1_type_enum)
        p2 = PlayerSlot(player_id=2, player_type=p2_type_enum)
        score_limit = setup_data.get("score", 3)
        time_limit = setup_data.get("time", 0)
        self.gm = DualGameManager(size=self.size, p1=p1, p2=p2, score_limit=score_limit, time_limit=time_limit)
        self.gm.new_game()

        self.p1 = self.gm.p1
        self.p2 = self.gm.p2
        self.board1 = self.gm.board1
        self.board2 = self.gm.board2

        # --- KHỞI TẠO 2 BOT ---
        self.bots = {
            1: AIBot(size=self.size, difficulty=diff_p1),
            2: AIBot(size=self.size, difficulty=diff_p2)
        }

        # Bật AI mặc định nếu là BOT
        self.ai_active = {
            1: self.is_p1_bot,
            2: self.is_p2_bot
        }

        self.last_bot_move = {1: 0, 2: 0}
        self.bot_speed = 300

        self.renderer = Renderer(screen)

        W = config.DUAL_WINDOW_WIDTH
        H = config.WINDOW_HEIGHT

        available_b_h = H - int(H * 0.15) - 170
        available_b_w = int(W * 0.42)
        B = min(available_b_h, available_b_w)

        GAP = int(W * 0.05)

        total_boards_w = B * 2 + GAP
        self._p1_board_x = (W - total_boards_w) // 2
        self._p2_board_x = self._p1_board_x + B + GAP
        self._board_y    = int(H * 0.15)

        self._p1_offset_x = self._p1_board_x - config.MARGIN_LEFT
        self._p2_offset_x = self._p2_board_x - config.MARGIN_LEFT
        self._board_top   = self._board_y - config.MARGIN_TOP

        self._stat_box_h = 70

        self._stat_box_y = self._board_y + B + 35
        self._B = B

        self.win_start_time = 0
        self.is_round_over_state = False
        # Âm thanh
        try:
            self.move_sound = pygame.mixer.Sound("assets/sounds/move.wav")
            mgr = SettingsManager()
            vol = mgr.get("move_volume")
            if vol is not None:
                self.move_sound.set_volume(vol / 100.0)
        except Exception:
            self.move_sound = None

        # Fonts
        try:
            self.font_stat  = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", 20)
            self.font_title = pygame.font.Font("assets/fonts/Baloo-Regular.ttf", 32)
            self.font_btn   = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", 15)
            self.font_small = pygame.font.Font("assets/fonts/Quicksand-Bold.ttf", 16)
        except Exception:
            self.font_stat  = pygame.font.SysFont("arial", 20, bold=True)
            self.font_title = pygame.font.SysFont("arial", 28, bold=True)
            self.font_btn   = pygame.font.SysFont("arial", 14, bold=True)
            self.font_small = pygame.font.SysFont("arial", 15, bold=True)

        try:
            self.bg_img = pygame.image.load("assets/images/bg_play.png").convert()
            self.bg_img = pygame.transform.scale(self.bg_img, (W, H))
        except Exception:
            self.bg_img = None

        try:
            self.wood_frame_img = pygame.image.load("assets/images/wood_frame.png").convert_alpha()
            # Ở chế độ Dual, bàn cờ là self._B nên khung sẽ là self._B + 40
            frame_size = self._B + 40
            self.wood_frame_img = pygame.transform.smoothscale(self.wood_frame_img, (frame_size, frame_size))
        except Exception:
            self.wood_frame_img = None

        self._init_buttons()

    def _init_buttons(self):
        H   = config.WINDOW_HEIGHT
        W   = config.DUAL_WINDOW_WIDTH
        cx  = W // 2

        btn_h    = 42
        btn_y    = H - 65
        bw_act   = int(W * 0.08)
        bw_ctr   = int(W * 0.09)
        pad      = int(W * 0.01)

        def _pb(rect, text, c_top, c_bot, c_shad):
            return PillButton(rect, text, self.font_btn,
                              color_top=c_top, color_bot=c_bot, shadow_color=c_shad)

        total_ctr = bw_ctr * 3 + pad * 2
        start_ctr = cx - total_ctr // 2
        self.btn_new_game = _pb((start_ctr, btn_y, bw_ctr, btn_h),
                                "TRẬN MỚI", (160,230,150), (120,200,110), (90,160,80))
        self.btn_pause    = _pb((start_ctr + bw_ctr + pad, btn_y, bw_ctr, btn_h),
                                "TẠM DỪNG", (255,230,150), (230,200,100), (200,170,70))
        self.btn_quit     = _pb((start_ctr + (bw_ctr + pad) * 2, btn_y, bw_ctr, btn_h),
                                "THOÁT", (255,160,160), (230,120,120), (200,90,90))

        p1_cx = self._p1_board_x + self._B // 2
        self.btn_p1_undo = _pb((p1_cx - pad // 2 - bw_act, btn_y, bw_act, btn_h),
                               "HOÀN TÁC", (200,210,255), (150,170,255), (120,140,220))
        self.btn_p1_ai   = _pb((p1_cx + pad // 2, btn_y, bw_act, btn_h),
                               "AI GIẢI", (190,240,255), (135,215,245), (110,190,220))

        p2_cx = self._p2_board_x + self._B // 2
        self.btn_p2_ai   = _pb((p2_cx - pad // 2 - bw_act, btn_y, bw_act, btn_h),
                               "AI GIẢI", (190,240,255), (135,215,245), (110,190,220))
        self.btn_p2_undo = _pb((p2_cx + pad // 2, btn_y, bw_act, btn_h),
                               "HOÀN TÁC", (200,210,255), (150,170,255), (120,140,220))

        self.btn_next_round = _pb((W // 2 - bw_ctr // 2, self._board_y + self._B // 2 + 30, bw_ctr, btn_h),
                                "TIẾP TỤC", (160,230,150), (120,200,110), (90,160,80))

        # --- LÀM MỜ NÚT AI NẾU ĐÃ CHỌN LÀ BOT TỪ SETUP ---
        if self.is_p1_bot:
            self.btn_p1_ai.text = "🤖 TỰ ĐỘNG"
            self.btn_p1_ai.color_top = (180, 180, 180)
            self.btn_p1_ai.color_bot = (140, 140, 140)
            self.btn_p1_ai.shadow_color = (100, 100, 100)

        if self.is_p2_bot:
            self.btn_p2_ai.text = "🤖 TỰ ĐỘNG"
            self.btn_p2_ai.color_top = (180, 180, 180)
            self.btn_p2_ai.color_bot = (140, 140, 140)
            self.btn_p2_ai.shadow_color = (100, 100, 100)

    def handle_events(self, events):
        for event in events:
            if self.btn_quit.handle_event(event):     return "MENU"
            if self.btn_pause.handle_event(event):    self.gm.is_paused = not self.gm.is_paused

            if self.is_round_over_state:
                if self.btn_next_round.handle_event(event):
                    self.is_round_over_state = False
                    if self.gm.is_game_over():
                        winner = self.gm.get_winner()
                        result_data = {
                            "winner_id": winner.player_id if winner else 0,
                            "time":      self.gm.get_formatted_time(),
                            "p1_moves":  self.p1.move_count,
                            "p2_moves":  self.p2.move_count,
                            "score":     self.gm.get_score_text(),
                            "size":      self.size,
                        }
                        return "WIN_DUAL", result_data
                    else:
                        self.gm.new_game()
                        self.ai_active[1] = self.is_p1_bot
                        self.ai_active[2] = self.is_p2_bot
                return "PLAYING_DUAL"

            # --- CẬP NHẬT TRẬN MỚI: Tự động chạy lại AI cho các BOT ---
            if self.btn_new_game.handle_event(event):
                self.gm.new_game()
                self.ai_active[1] = self.is_p1_bot
                self.ai_active[2] = self.is_p2_bot

            if self.btn_p1_undo.handle_event(event) and not self.gm.is_paused:
                if self.gm.undo(1):
                    self.bots[1].clear_memory()
                    if self.move_sound: self.move_sound.play()

            if self.btn_p2_undo.handle_event(event) and not self.gm.is_paused:
                if self.gm.undo(2):
                    self.bots[2].clear_memory()
                    if self.move_sound: self.move_sound.play()

            # --- NÚT BẬT/TẮT AI (Khóa lại nếu đã là BOT từ đầu) ---
            if not self.is_p1_bot and self.btn_p1_ai.handle_event(event) and not self.gm.is_paused:
                self.ai_active[1] = not self.ai_active[1]
                if self.ai_active[1]: self.bots[1].clear_memory()
                self.btn_p1_ai.text = "DỪNG AI" if self.ai_active[1] else "AI GIẢI"

            if not self.is_p2_bot and self.btn_p2_ai.handle_event(event) and not self.gm.is_paused:
                self.ai_active[2] = not self.ai_active[2]
                if self.ai_active[2]: self.bots[2].clear_memory()
                self.btn_p2_ai.text = "DỪNG AI" if self.ai_active[2] else "AI GIẢI"

            #  KHÓA BÀN PHÍM NẾU AI ĐANG CHẠY ---
            moved_p1 = False
            moved_p2 = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.gm.is_paused:
                mx, my = event.pos
                if self._board_y <= my <= self._board_y + self._B:
                    t_size = self._B // self.size
                    if not self.ai_active[1] and self._p1_board_x <= mx <= self._p1_board_x + self._B:
                        r = (my - self._board_y) // t_size
                        c = (mx - self._p1_board_x) // t_size
                        moved_p1 = self.gm.process_move(1, r, c)
                    elif not self.ai_active[2] and self._p2_board_x <= mx <= self._p2_board_x + self._B:
                        r = (my - self._board_y) // t_size
                        c = (mx - self._p2_board_x) // t_size
                        moved_p2 = self.gm.process_move(2, r, c)

            if event.type == pygame.KEYDOWN and not self.gm.is_paused:
                if event.key in self.P1_KEYS and not self.ai_active[1]:
                    dr, dc = self.P1_KEYS[event.key]
                    er, ec = self.board1.get_empty_pos()
                    moved_p1 = self.gm.process_move(1, er + dr, ec + dc)

                elif event.key in self.P2_KEYS and not self.ai_active[2]:
                    dr, dc = self.P2_KEYS[event.key]
                    er, ec = self.board2.get_empty_pos()
                    moved_p2 = self.gm.process_move(2, er + dr, ec + dc)

            if moved_p1 or moved_p2:
                if self.move_sound: self.move_sound.play()

                if self.gm.is_round_over() and not self.is_round_over_state:
                    self.is_round_over_state = True
                    self.ai_active = {1: False, 2: False}
                    if not self.is_p1_bot: self.btn_p1_ai.text = "AI GIẢI"
                    if not self.is_p2_bot: self.btn_p2_ai.text = "AI GIẢI"
                    if self.gm.is_game_over():
                        self.btn_next_round.text = "KẾT QUẢ"
                    else:
                        self.btn_next_round.text = "TIẾP TỤC"

        return "PLAYING_DUAL"

    def update(self, dt: float = 0.0):
        if not self.gm.is_paused:
            self.gm.update_time(dt)

            if not self.gm.is_playing and self.gm.is_round_over() and not self.is_round_over_state:
                self.is_round_over_state = True
                self.ai_active = {1: False, 2: False}
                if not self.is_p1_bot: self.btn_p1_ai.text = "AI GIẢI"
                if not self.is_p2_bot: self.btn_p2_ai.text = "AI GIẢI"
                if self.gm.is_game_over():
                    self.btn_next_round.text = "KẾT QUẢ"
                else:
                    self.btn_next_round.text = "TIẾP TỤC"

        # --- LOGIC 2 BOT CHẠY ĐUA ---
        if self.gm.is_playing and not self.gm.is_paused and not self.is_round_over_state:
            current_time = pygame.time.get_ticks()

            for p_id in [1, 2]:
                if self.ai_active[p_id]:
                    if current_time - self.last_bot_move[p_id] >= self.bot_speed:
                        board = self.board1 if p_id == 1 else self.board2
                        empty_r, empty_c = board.get_empty_pos()

                        dx, dy = self.bots[p_id].get_next_move(board.matrix, empty_r, empty_c)

                        if (dx, dy) != (0, 0):
                            target_r, target_c = empty_r + dx, empty_c + dy

                            if self.gm.process_move(p_id, target_r, target_c):
                                if self.move_sound: self.move_sound.play()
                                self.last_bot_move[p_id] = current_time

                                if self.gm.is_round_over() and not self.is_round_over_state:
                                    self.is_round_over_state = True
                                    self.ai_active = {1: False, 2: False}
                                    if not self.is_p1_bot: self.btn_p1_ai.text = "AI GIẢI"
                                    if not self.is_p2_bot: self.btn_p2_ai.text = "AI GIẢI"
                                    if self.gm.is_game_over():
                                        self.btn_next_round.text = "KẾT QUẢ"
                                    else:
                                        self.btn_next_round.text = "TIẾP TỤC"

    def _draw_info_pill(self, rect, label, value, lbl_color, val_color):
        pygame.draw.rect(self.screen, (235, 245, 255), rect, border_radius=12)
        pygame.draw.rect(self.screen, (200, 220, 255), rect, border_radius=12, width=2)
        lbl_s = self.font_small.render(label, True, lbl_color)
        val_s = self.font_stat.render(value,  True, val_color)
        self.screen.blit(lbl_s, lbl_s.get_rect(centerx=rect.centerx, top=rect.y + 5))
        self.screen.blit(val_s, val_s.get_rect(centerx=rect.centerx, bottom=rect.bottom - 7))

    def _draw_stat_box(self, player: PlayerSlot, board, board_x: int):
        box = pygame.Rect(board_x, self._stat_box_y, self._B, self._stat_box_h)
        pygame.draw.rect(self.screen, (255, 252, 245), box, border_radius=12)
        pygame.draw.rect(self.screen, (230, 210, 200), box, border_radius=12, width=2)

        pad = 12
        text_x = box.x + pad
        c_lbl = (160, 110, 90)
        c_val = (60, 60, 60)

        correct_tiles = board.count_correct_tiles()
        total_tiles = board.total_tiles

        line1 = self.font_small.render(
            f"Số bước:  {player.move_count}",
            True, c_val)
        line2 = self.font_small.render(
            f"Ô đúng:  {correct_tiles}/{total_tiles}",
            True, c_val)

        self.screen.blit(line1, (text_x, box.y + 10))
        self.screen.blit(line2, (text_x, box.y + 36))

    def render(self):
        screen_w = self.screen.get_width()
        cx_top   = screen_w // 2
        W        = config.DUAL_WINDOW_WIDTH

        if self.bg_img:
            self.screen.blit(self.bg_img, (0, 0))
        else:
            self.screen.fill((255, 246, 233))

        title = self.font_title.render("ĐỐI KHÁNG", True, (50, 100, 150))
        self.screen.blit(title, title.get_rect(centerx=cx_top, top=12))

        pill_h = 50
        pill_w = 170
        pill_y = 52
        gap_pill = 20

        rect_time  = pygame.Rect(cx_top - pill_w - gap_pill - pill_w // 2, pill_y, pill_w, pill_h)
        rect_score = pygame.Rect(cx_top - pill_w // 2,                     pill_y, pill_w, pill_h)
        rect_level = pygame.Rect(cx_top + gap_pill + pill_w // 2,          pill_y, pill_w, pill_h)

        self._draw_info_pill(rect_time,  "Thời gian",   self.gm.get_formatted_time(), (100, 130, 180), (50, 100, 150))
        self._draw_info_pill(rect_score, "Tỉ số",        self.gm.get_score_text(),     (180, 80, 80),   (200, 80, 100))
        self._draw_info_pill(rect_level, "Cấp độ",       f"{self.size}×{self.size}",   (100, 120, 100), (60, 120, 80))

        p1_lbl = self.font_stat.render("NGƯỜI CHƠI 1  (WASD)", True, (80, 160, 120))
        p2_lbl = self.font_stat.render("NGƯỜI CHƠI 2  (↑↓←→)", True, (200, 100, 80))
        self.screen.blit(p1_lbl, (self._p1_board_x, self._board_y - 45))
        self.screen.blit(p2_lbl, (self._p2_board_x, self._board_y - 45))

        # --- Vẽ khung gỗ cho 2 bàn cờ ---
        def draw_frame(actual_x, actual_y):
            # Lùi ra 20px so với tọa độ thật để tạo viền
            frame_x = actual_x - 20
            frame_y = actual_y - 20
            if self.wood_frame_img:
                self.screen.blit(self.wood_frame_img, (frame_x, frame_y))
            else:
                rect = (frame_x, frame_y, self._B + 40, self._B + 40)
                pygame.draw.rect(self.screen, (220, 180, 140), rect, border_radius=20)
                pygame.draw.rect(self.screen, (180, 130, 90), rect, border_radius=20, width=4)

        # SỬ DỤNG TỌA ĐỘ THỰC TẾ (board_x, board_y) THAY VÌ OFFSET
        draw_frame(self._p1_board_x, self._board_y)
        draw_frame(self._p2_board_x, self._board_y)

        self.renderer.draw_board(
            self.board1.matrix, self.size,
            offset_x=self._p1_offset_x, offset_y=self._board_top,
            board_size=self._B
        )
        self.renderer.draw_board(
            self.board2.matrix, self.size,
            offset_x=self._p2_offset_x, offset_y=self._board_top,
            board_size=self._B
        )

        self._draw_stat_box(self.p1, self.board1, self._p1_board_x)
        self._draw_stat_box(self.p2, self.board2, self._p2_board_x)

        if self.gm.is_paused:
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 150))
            self.screen.blit(overlay, (0, 0))
            pause_txt = self.font_stat.render("ĐÃ TẠM DỪNG", True, (200, 80, 100))
            self.screen.blit(pause_txt, pause_txt.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2)))

        mouse = pygame.mouse.get_pos()
        self.btn_pause.text = "TIẾP TỤC" if self.gm.is_paused else "TẠM DỪNG"
        self.btn_new_game.draw(self.screen, mouse)
        self.btn_pause.draw(self.screen, mouse)
        self.btn_quit.draw(self.screen, mouse)
        self.btn_p1_undo.draw(self.screen, mouse)
        self.btn_p1_ai.draw(self.screen, mouse)
        self.btn_p2_ai.draw(self.screen, mouse)
        self.btn_p2_undo.draw(self.screen, mouse)

        if self.is_round_over_state:
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 160))
            self.screen.blit(overlay, (0, 0))

            rw = self.gm.round_winner
            if rw == "TIE":
                msg = "HÒA VÁN NÀY (HẾT GIỜ)"
            elif rw:
                msg = f"NGƯỜI CHƠI {rw.player_id} THẮNG VÁN"
            else:
                msg = "VÁN KẾT THÚC"

            if self.gm.is_game_over():
                winner = self.gm.get_winner()
                msg = f"NGƯỜI CHƠI {winner.player_id} THẮNG CẢ TRẬN!" if winner else "HÒA CẢ TRẬN!"

            win_surf = self.font_title.render(msg, True, (230, 80, 100))
            self.screen.blit(win_surf, win_surf.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 - 40)))
            self.btn_next_round.draw(self.screen, mouse)
            self.btn_next_round.draw(self.screen, mouse)