import random
from src.ai.solver import PuzzleSolver

class AIBot:
    def __init__(self, size, difficulty="hard"):
        self.size = size
        self.difficulty = difficulty.lower()
        self.ai_type = "SEARCH"

        self.moves_map_search = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}
        self.solver = PuzzleSolver(size)
        self.path_cache = []

        # Cấu hình "Nhân tính" theo độ khó
        self.config = {
            "easy":   {"mistake_rate": 0.30, "forget_rate": 0.40},
            "medium": {"mistake_rate": 0.10, "forget_rate": 0.15},
            "hard":   {"mistake_rate": 0.00, "forget_rate": 0.00} # Đại kiện tướng
        }

    def get_next_move(self, matrix, empty_r, empty_c):
        """Hàm duy nhất mà Game Manager gọi đến"""
        return self._get_search_move(matrix)

    def _get_search_move(self, matrix):
        """Bật thuật toán tìm kiếm có Nhân tính"""
        board_1d = tuple(val for row in matrix for val in row)
        settings = self.config.get(self.difficulty, self.config["hard"])

        # 1. Tật "Bấm nhầm": Có tỉ lệ đi bừa 1 bước
        if random.random() < settings["mistake_rate"]:
            neighbors = self.solver.get_neighbors(board_1d)
            self.path_cache.clear() # Đi bừa xong phải xóa trí nhớ để tính lại
            random_move = random.choice(neighbors)[1]
            return self.moves_map_search.get(random_move, (0, 0))

        # 2. Tật "Não cá vàng": Đang đi thì quên đường
        if random.random() < settings["forget_rate"]:
            self.path_cache.clear()

        # 3. Bật Weighted A* tính đường (nếu chưa có hoặc vừa bị xóa)
        if not self.path_cache:
            # Gọi hàm Weighted A* siêu tốc (3x3 chạy chớp mắt)
            self.path_cache = self.solver.solve_smart_hybrid(matrix)

        # 4. Trả về bước đi tiếp theo
        if self.path_cache:
            best_move = self.path_cache.pop(0)
            return self.moves_map_search.get(best_move, (0, 0))

        return (0, 0) # Fallback an toàn

    def clear_memory(self):
        """Xóa bộ nhớ đệm để tính lại đường đi từ đầu"""
        self.path_cache.clear()
