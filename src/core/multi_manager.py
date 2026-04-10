import pygame
from src.core.game_manager import GameManager
from src.ai.bot import AIBot 

class MultiplayerManager:
    # FIX 1: Bổ sung tham số time_limit vào để hứng dữ liệu từ Setup
    def __init__(self, size, target_score, mode, ai_difficulty='medium', time_limit=0):
        self.size = size
        if target_score in [3, 5]:
            self.target_score = (target_score // 2) + 1
        else:
            self.target_score = target_score 
            
        self.mode = mode 
        self.ai_difficulty = ai_difficulty
        self.time_limit = time_limit # Đã nhận mốc thời gian (Tính bằng Giây)
        
        self.gm1 = GameManager(size)
        self.gm2 = GameManager(size)
        
        self.bot1 = AIBot(size, "hard") if self.mode == "EvE" else None
        self.bot2 = AIBot(size, self.ai_difficulty) if self.mode in ["PvE", "EvE"] else None
        
        self.master_bot = AIBot(size, "hard")
        
        self.score_p1 = 0
        self.score_p2 = 0
        self.round_winner = 0 
        self.match_winner = 0 
        
        self.ai_move_delay = 400 
        self.last_ai1_move = pygame.time.get_ticks()
        self.last_ai2_move = pygame.time.get_ticks()
        
        self.round_start_time = 0 # Lưu mốc thời gian bắt đầu hiệp

        self.init_new_round()
        
    def trigger_hint(self, player_num):
        gm = self.gm1 if player_num == 1 else self.gm2
        if not gm.is_playing: return False
        
        er, ec = gm.board.get_empty_pos()
        dr, dc = self.master_bot.get_next_move(gm.board.matrix, er, ec)
        
        if dr != 0 or dc != 0:
            return gm.process_move(er + dr, ec + dc)
        return False

    def init_new_round(self):
        self.gm1.new_game()
        self.gm2.new_game()
        
        self.gm2.board.matrix = [row[:] for row in self.gm1.board.matrix]
        
        self.gm1.is_playing = True
        self.gm2.is_playing = True
        self.round_winner = 0
        self.round_start_time = pygame.time.get_ticks() # Reset đồng hồ
        
    def update_time(self):
        if self.round_winner != 0: return

        self.gm1.update_time()
        self.gm2.update_time()
        
        # FIX 2: Tự động khóa bảng nếu quá thời gian quy định
        if self.time_limit > 0:
            elapsed_sec = (pygame.time.get_ticks() - self.round_start_time) // 1000
            if elapsed_sec >= self.time_limit:
                self.handle_time_out()
        
    @property
    def formatted_time(self):
        return self.gm1.get_formatted_time()
        
    @property
    def done(self):
        return self.match_winner != 0

    def process_player_move(self, player, dr, dc):
        if self.round_winner != 0: return False
        
        if player == 1 and self.mode in ["PvP", "PvE"] and self.gm1.is_playing:
            er, ec = self.gm1.board.get_empty_pos()
            success = self.gm1.process_move(er + dr, ec + dc)
            self._check_win_condition()
            return success
            
        elif player == 2 and self.mode == "PvP" and self.gm2.is_playing:
            er, ec = self.gm2.board.get_empty_pos()
            success = self.gm2.process_move(er + dr, ec + dc)
            self._check_win_condition()
            return success
            
        return False

    def update_ai(self):
        if self.round_winner != 0: return False
        current_time = pygame.time.get_ticks()
        ai_moved = False

        if self.mode == "EvE":
            if current_time - self.last_ai1_move > self.ai_move_delay:
                if self._execute_bot_move(self.gm1, self.bot1): ai_moved = True
                self.last_ai1_move = current_time
            if current_time - self.last_ai2_move > self.ai_move_delay:
                if self._execute_bot_move(self.gm2, self.bot2): ai_moved = True
                self.last_ai2_move = current_time
                
        elif self.mode == "PvE":
            if current_time - self.last_ai2_move > self.ai_move_delay:
                if self._execute_bot_move(self.gm2, self.bot2): ai_moved = True
                self.last_ai2_move = current_time

        if ai_moved: self._check_win_condition()
        return ai_moved

    def _execute_bot_move(self, gm, bot):
        if not gm.is_playing or not bot: return False
        
        er, ec = gm.board.get_empty_pos()
        dr, dc = bot.get_next_move(gm.board.matrix, er, ec)
        
        return gm.process_move(er + dr, ec + dc)

    def _check_win_condition(self):
        if not self.gm1.is_playing and self.round_winner == 0:
            self.trigger_round_win(1)
        if not self.gm2.is_playing and self.round_winner == 0:
            self.trigger_round_win(2)

    def get_progress(self, player_num):
        gm = self.gm1 if player_num == 1 else self.gm2
        matrix = gm.board.matrix
        correct_tiles = 0
        total_tiles = self.size * self.size - 1

        for r in range(self.size):
            for c in range(self.size):
                val = matrix[r][c]
                if val == 0: continue
                
                target_r = (val - 1) // self.size
                target_c = (val - 1) % self.size
                
                if r == target_r and c == target_c:
                    correct_tiles += 1
        
        return correct_tiles / total_tiles if total_tiles > 0 else 0

    def handle_time_out(self):
        """FIX 3: Xử lý công bằng khi hết giờ"""
        if self.round_winner != 0: return
        p1_prog = self.get_progress(1)
        p2_prog = self.get_progress(2)
        
        if p1_prog > p2_prog: 
            self.trigger_round_win(1)
        elif p2_prog > p1_prog: 
            self.trigger_round_win(2)
        else:
            # Hai bên bằng % nhau -> Hòa -> Khóa bàn cờ lại để sang hiệp mới, không ai cộng điểm
            self.round_winner = 3 
            self.gm1.is_playing = False
            self.gm2.is_playing = False

    def trigger_round_win(self, player):
        self.round_winner = player
        self.gm1.is_playing = False
        self.gm2.is_playing = False
        
        if player == 1: self.score_p1 += 1
        elif player == 2: self.score_p2 += 1
        
        if self.score_p1 >= self.target_score: self.match_winner = 1
        elif self.score_p2 >= self.target_score: self.match_winner = 2