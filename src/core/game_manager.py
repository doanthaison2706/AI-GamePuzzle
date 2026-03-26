import time
from src.core.board import Board

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