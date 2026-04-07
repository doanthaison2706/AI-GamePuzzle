import time
from src.core.board import Board
from src.ai.bot import AIBot

class GameManager:
    """
    Quản lý luồng chính của trò chơi: Trạng thái, số bước đi, thời gian.
    Giao diện (UI) sẽ chỉ cần giao tiếp với class này.
    """
    def __init__(self, size: int = 3):
        self.size = size
        self.board = Board(size)
        
        self.is_playing = False 
        self.move_count = 0
        self.start_time = 0.0
        self.elapsed_time = 0.0
        
        # Thêm biến lưu trữ bộ não AI (Khởi tạo rỗng để tiết kiệm RAM)
        self.hint_bot = None
        self.ai_helper = None

    def execute_hint_move(self) -> bool:
        """
        Kích hoạt AI để đi hộ 1 bước.
        Giao diện (UI) chỉ cần gọi hàm này khi người chơi bấm nút "Gợi ý".
        Trả về True nếu đi thành công.
        """
        if not self.is_playing:
            return False
            
        # Lazy Loading: Chỉ khởi tạo Bot ở lần bấm Gợi ý đầu tiên
        if self.hint_bot is None:
            from src.ai.bot import AIBot # Import trễ để chống lỗi vòng lặp (circular import)
            print("Đang khởi động bộ não AI...")
            self.hint_bot = AIBot(self.size, difficulty="hard") # Gợi ý thì luôn dùng đường đi tối ưu nhất
            
        # Lấy tọa độ ô trống
        er, ec = self.board.get_empty_pos()
        
        # Hỏi AI xem nên đi hướng nào (dr, dc)
        dr, dc = self.hint_bot.get_next_move(self.board.matrix, er, ec)
        
        # Nếu AI trả về hướng đi hợp lệ (không phải fallback 0,0)
        if dr != 0 or dc != 0:
            target_r = er + dr
            target_c = ec + dc
            return self.process_move(target_r, target_c) # Gọi thẳng hàm di chuyển sẵn có của bạn
            
        return False
    
    def get_ai_hint(self):
        """Phục vụ nút Gợi ý hoặc Auto-solve trong chơi đơn. Luôn là Hard."""
        if not self.is_playing: return False
        
        if not hasattr(self, 'ai_helper') or self.ai_helper is None:
            from src.ai.bot import AIBot
            print("Đang nạp bộ não AI...")
            self.ai_helper = AIBot(self.size, "hard")
            
        er, ec = self.board.get_empty_pos()
        dr, dc = self.ai_helper.get_next_move(self.board.matrix, er, ec)
        
        if dr != 0 or dc != 0:
            return self.process_move(er + dr, ec + dc)
        return False

    def start_game(self):
        """Tiếp tục trò chơi (tương đương nút Resume/Start)."""
        if not self.is_playing and not self.board.is_solved():
            self.is_playing = True
            self.start_time = time.time() - self.elapsed_time 

    def reset_game(self):
        """Đưa bàn cờ về đích, reset đếm bước và thời gian (tương đương Reset)."""
        self.board = Board(self.size)
        self.is_playing = False
        self.move_count = 0
        self.start_time = 0.0
        self.elapsed_time = 0.0

    def new_game(self):
        """Tạo ván mới: xáo trộn bàn cờ và bắt đầu tính giờ."""
        self.board = Board(self.size)
        self.board.shuffle() 
        
        self.is_playing = True
        self.move_count = 0
        self.start_time = time.time()
        self.elapsed_time = 0.0

    def process_move(self, r: int, c: int) -> bool:
        """
        Nhận tọa độ click chuột từ UI, thực hiện di chuyển và check Win.
        Trả về True nếu di chuyển thành công.
        """
        if not self.is_playing:
            return False
        if self.board.move(r, c):
            self.move_count += 1
            
            if self.board.is_solved():
                self.is_playing = False
                self.update_time() 
                # Giao diện sẽ tự động check hàm is_solved() để hiện JDialog báo Win
            return True
            
        return False

    def get_formatted_time(self) -> str:
        """Trả về chuỗi thời gian định dạng MM:SS để UI in lên màn hình."""
        self.update_time()
        minutes = int(self.elapsed_time // 60)
        seconds = int(self.elapsed_time % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def update_time(self):
        """Cập nhật thời gian đã trôi qua."""
        if self.is_playing:
            self.elapsed_time = time.time() - self.start_time