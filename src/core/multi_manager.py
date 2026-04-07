import pygame
from src.core.game_manager import GameManager
from src.ai.bot import AIBot # <--- IMPORT BỘ NÃO AI TỪ THƯ MỤC MỚI

class MultiplayerManager:
    def __init__(self, size, target_score, mode, ai_difficulty = 'medium'):
        self.size = size
        self.target_score = target_score
        self.mode = mode # 'PvP', 'PvE', 'EvE'
        self.ai_difficulty = ai_difficulty
        
        self.gm1 = GameManager(size)
        self.gm2 = GameManager(size)
        
        # Khởi tạo AI Bot nếu chế độ có máy chơi
        self.bot1 = AIBot(size, "hard") if self.mode == "EvE" else None
        self.bot2 = AIBot(size, self.ai_difficulty) if self.mode in ["PvE", "EvE"] else None
        
        # 2. Khởi tạo "Bot Sư phụ" (Master Bot) - Luôn là Hard để phục vụ Gợi ý cho P1 và P2
        self.master_bot = AIBot(size, "hard")
        
        self.score_p1 = 0
        self.score_p2 = 0
        self.round_winner = 0 
        self.match_winner = 0 
        
        self.ai_move_delay = 400 
        self.last_ai1_move = pygame.time.get_ticks()
        self.last_ai2_move = pygame.time.get_ticks()

        self.init_new_round()
        
    def trigger_hint(self, player_num):
        """
        Hàm phục vụ nút 'Gợi ý' trong màn hình đối kháng.
        Luôn dùng Master Bot (Hard) để tìm nước đi xịn nhất.
        """
        gm = self.gm1 if player_num == 1 else self.gm2
        if not gm.is_playing: return False
        
        # Ép Master Bot tính toán nước đi cho bàn cờ tương ứng
        er, ec = gm.board.get_empty_pos()
        dr, dc = self.master_bot.get_next_move(gm.board.matrix, er, ec)
        
        if dr != 0 or dc != 0:
            return gm.process_move(er + dr, ec + dc)
        return False

    def init_new_round(self):
        """Khởi tạo và đồng bộ 2 bàn cờ cho hiệp mới"""
        self.gm1.new_game()
        self.gm2.new_game()
        
        # Đồng bộ ma trận P2 giống hệt P1 để công bằng
        self.gm2.board.matrix = [row[:] for row in self.gm1.board.matrix]
        
        # QUAN TRỌNG: Đảm bảo cả 2 đều đang ở trạng thái chơi
        self.gm1.is_playing = True
        self.gm2.is_playing = True
        self.round_winner = 0
        
    def update_time(self):
        """Cập nhật thời gian cho cả 2 GameManager"""
        self.gm1.update_time()
        self.gm2.update_time()
        
    @property
    def formatted_time(self):
        """Lấy thời gian định dạng từ gm1 để hiển thị lên UI"""
        return self.gm1.get_formatted_time()
        
    @property
    def done(self):
        """Kiểm tra xem trận đấu đã kết thúc hoàn toàn chưa (có người thắng chung cuộc)"""
        return self.match_winner != 0

    def process_player_move(self, player, dr, dc):
        """Xử lý bước đi của người thật"""
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
        """Điều phối nhịp độ đánh của các Bot"""
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
        """Lấy nước đi từ Bot và áp dụng vào bàn cờ"""
        if not gm.is_playing or not bot: return False
        
        # Cung cấp dữ liệu hiện tại cho AI suy nghĩ
        er, ec = gm.board.get_empty_pos()
        dr, dc = bot.get_next_move(gm.board.matrix, er, ec)
        
        # Áp dụng nước đi
        return gm.process_move(er + dr, ec + dc)

    def _check_win_condition(self):
        """Kiểm tra xem có ai xếp xong chưa"""
        if not self.gm1.is_playing and self.round_winner == 0:
            self.trigger_round_win(1)
        if not self.gm2.is_playing and self.round_winner == 0:
            self.trigger_round_win(2)

    def get_progress(self, player_num):
        """Tính % ô đúng vị trí (không tính ô trống)"""
        gm = self.gm1 if player_num == 1 else self.gm2
        matrix = gm.board.matrix
        correct_tiles = 0
        total_tiles = self.size * self.size - 1

        for r in range(self.size):
            for c in range(self.size):
                val = matrix[r][c]
                if val == 0: continue
                
                # Vị trí đúng của số val: hàng = (val-1)//size, cột = (val-1)%size
                target_r = (val - 1) // self.size
                target_c = (val - 1) % self.size
                
                if r == target_r and c == target_c:
                    correct_tiles += 1
        
        return correct_tiles / total_tiles if total_tiles > 0 else 0

    def update_countdown(self, dt_ms, limit_minutes):
        """
        Quản lý thời gian: 
        - Nếu limit_minutes > 0: Đếm ngược.
        - Nếu limit_minutes == 0: Đếm tiến (vô hạn).
        """
        if limit_minutes == 0:
            # Đếm tiến từ 0
            return dt_ms # Trả về tổng thời gian đã trôi qua
        else:
            # Đếm ngược từ số phút đã chọn
            total_limit_ms = limit_minutes * 60 * 1000
            remaining = total_limit_ms - dt_ms
            if remaining <= 0:
                self.handle_time_out()
                return 0
            return remaining

    def handle_time_out(self):
        """Xử lý khi hết giờ: Ai nhiều ô đúng hơn người đó thắng hiệp"""
        if self.round_winner != 0: return
        p1_prog = self.get_progress(1)
        p2_prog = self.get_progress(2)
        
        if p1_prog >= p2_prog: self.trigger_round_win(1)
        else: self.trigger_round_win(2)

    def trigger_round_win(self, player):
        """Xử lý cộng điểm khi thắng hiệp"""
        self.round_winner = player
        self.gm1.is_playing = False
        self.gm2.is_playing = False
        
        if player == 1: self.score_p1 += 1
        elif player == 2: self.score_p2 += 1
        
        if self.score_p1 >= self.target_score: self.match_winner = 1
        elif self.score_p2 >= self.target_score: self.match_winner = 2