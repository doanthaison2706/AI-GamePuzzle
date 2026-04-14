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

        self.config = {
            "easy":   {"mistake_rate": 0.30, "forget_rate": 0.40},
            "medium": {"mistake_rate": 0.10, "forget_rate": 0.15},
            "hard":   {"mistake_rate": 0.00, "forget_rate": 0.00} 
        }

    def get_next_move(self, matrix, empty_r, empty_c):
        return self._get_search_move(matrix)

    def _get_search_move(self, matrix):
        board_1d = tuple(val for row in matrix for val in row)
        settings = self.config.get(self.difficulty, self.config["hard"])

        if random.random() < settings["mistake_rate"]:
            neighbors = self.solver.get_neighbors(board_1d)
            self.path_cache.clear()
            random_move = random.choice(neighbors)[1]
            return self.moves_map_search.get(random_move, (0, 0))

        if random.random() < settings["forget_rate"]:
            self.path_cache.clear()

        # NẾU CHƯA CÓ ĐƯỜNG ĐI -> TÍNH TOÁN CHIẾN THUẬT MỚI
        if not self.path_cache:
            if self.size >= 5:
                # Kích hoạt chế độ Đại Kiện Tướng cho bàn cờ lớn
                self.path_cache = self._solve_divide_and_conquer(board_1d)
            else:
                # Bàn cờ nhỏ (3x3, 4x4) cứ dùng A* đấm thẳng mặt
                self.path_cache = self.solver.solve_smart_hybrid(matrix)

        if self.path_cache:
            best_move = self.path_cache.pop(0)
            return self.moves_map_search.get(best_move, (0, 0))

        return (0, 0)

    def _solve_divide_and_conquer(self, start_board):
        """
        Nhạc trưởng điều khiển chiến thuật "Lột hành tây".
        Giải quyết vòng ngoài, thu hẹp dần bàn cờ cho đến khi còn 3x3.
        """
        full_path = []
        current_board = start_board
        locked_indices = set()
        N = self.size

        # Kích thước lõi cuối cùng chừa lại cho A* (3x3 là tối ưu nhất, giải trong 0.01s)
        target_sub_size = 3 
        
        # Vòng lặp bóc tách (Với 6x6, k sẽ chạy 0, 1, 2)
        for k in range(N - target_sub_size):
            
            # ==========================================
            # BƯỚC 1: GIẢI HÀNG k (Từ trái qua phải)
            # ==========================================
            for col in range(k, N - 2): # Trừ 2 ô cuối cùng ra
                target_val = k * N + col + 1
                target_idx = k * N + col
                path, current_board = self.solver.solve_single_tile(current_board, target_val, target_idx, locked_indices)
                full_path.extend(path)
                locked_indices.add(target_idx) # Xếp xong thì khóa lại

            # Macro-move xử lý 2 ô cuối của Hàng k (Ô A và Ô B)
            tile_a = k * N + (N - 2) + 1  
            tile_b = k * N + (N - 1) + 1  
            idx_a = k * N + (N - 2)              # Vị trí đích của A
            idx_b = k * N + (N - 1)              # Vị trí góc (đích của B)
            idx_b_below = (k + 1) * N + (N - 1)  # Vị trí ngay dưới góc

            # ==========================================
            # MACRO-MOVE HÀNG (SỬA Ở ĐÂY)
            # ==========================================
            # Đưa A vào góc, B vào dưới góc
            path, current_board = self.solver.solve_single_tile(current_board, tile_a, idx_b, locked_indices)
            full_path.extend(path)
            locked_indices.add(idx_b)

            path, current_board = self.solver.solve_single_tile(current_board, tile_b, idx_b_below, locked_indices)
            full_path.extend(path)
            locked_indices.add(idx_b_below)

            # --- ĐÃ SỬA: Lùa ô trống (0) VÀO TRƯỚC khi mở khóa ---
            # GIỮ KHÓA: Lùa ô trống (0) vào idx_a
            path, current_board = self.solver.solve_single_tile(current_board, 0, idx_a, locked_indices)
            full_path.extend(path)

            # BÂY GIỜ MỚI MỞ KHÓA
            locked_indices.remove(idx_b)
            locked_indices.remove(idx_b_below)
            # -----------------------------------------------------

            # Đẩy A và B vào đúng vị trí cuối cùng
            path, current_board = self.solver.solve_single_tile(current_board, tile_a, idx_a, locked_indices)
            full_path.extend(path)
            path, current_board = self.solver.solve_single_tile(current_board, tile_b, idx_b, locked_indices)
            full_path.extend(path)

            locked_indices.add(idx_a)
            locked_indices.add(idx_b)

            # ==========================================
            # BƯỚC 2: GIẢI CỘT k (Từ trên xuống dưới)
            # ==========================================
            for row in range(k + 1, N - 2): # Bỏ qua ô đầu tiên vì nó thuộc Hàng k đã giải
                target_val = row * N + k + 1
                target_idx = row * N + k
                path, current_board = self.solver.solve_single_tile(current_board, target_val, target_idx, locked_indices)
                full_path.extend(path)
                locked_indices.add(target_idx)

            # ==========================================
            # MACRO-MOVE CỘT (SỬA Ở ĐÂY)
            # ==========================================
            tile_a = (N - 2) * N + k + 1
            tile_b = (N - 1) * N + k + 1
            idx_a = (N - 2) * N + k              # Vị trí đích của A
            idx_b = (N - 1) * N + k              # Vị trí góc đáy (đích của B)
            idx_b_right = (N - 1) * N + k + 1    # Vị trí ngay bên phải góc

            # Đưa A vào góc đáy, B vào bên phải góc
            path, current_board = self.solver.solve_single_tile(current_board, tile_a, idx_b, locked_indices)
            full_path.extend(path)
            locked_indices.add(idx_b)

            path, current_board = self.solver.solve_single_tile(current_board, tile_b, idx_b_right, locked_indices)
            full_path.extend(path)
            locked_indices.add(idx_b_right)

            # --- ĐÃ SỬA: Lùa ô trống (0) VÀO TRƯỚC khi mở khóa ---
            # GIỮ KHÓA: Lùa ô trống (0) vào idx_a
            path, current_board = self.solver.solve_single_tile(current_board, 0, idx_a, locked_indices)
            full_path.extend(path)

            # BÂY GIỜ MỚI MỞ KHÓA
            locked_indices.remove(idx_b)
            locked_indices.remove(idx_b_right)
            # -----------------------------------------------------

            # Kéo A và B vào vị trí
            path, current_board = self.solver.solve_single_tile(current_board, tile_a, idx_a, locked_indices)
            full_path.extend(path)
            path, current_board = self.solver.solve_single_tile(current_board, tile_b, idx_b, locked_indices)
            full_path.extend(path)

            locked_indices.add(idx_a)
            locked_indices.add(idx_b)


        # ==========================================
        # GIAI ĐOẠN CUỐI: Dọn dẹp lõi 3x3 bằng Weighted A*
        # ==========================================
        # Chuyển state 1D hiện tại thành ma trận 2D để đưa vào hàm cũ
        matrix_2d = [list(current_board[i:i+N]) for i in range(0, len(current_board), N)]
        
        # Bật A* thần thánh quét sạch tàn cuộc (nhớ truyền locked_indices)
        final_path = self.solver.solve_smart_hybrid(matrix_2d, locked_indices)
        full_path.extend(final_path)

        return full_path

    def clear_memory(self):
        self.path_cache.clear()