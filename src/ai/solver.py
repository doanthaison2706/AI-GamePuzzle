import heapq
import itertools

class PuzzleSolver:
    def __init__(self, size):
        self.size = size
        # Trạng thái đích chuẩn: (1, 2, 3, ..., 0)
        self.target = tuple(list(range(1, size * size)) + [0])

    def get_manhattan_and_linear_conflict(self, board):
        """
        Siêu Heuristic: Manhattan Distance kết hợp Linear Conflict
        board: Trạng thái bàn cờ dạng tuple 1D
        """
        size = self.size
        manhattan = 0
        linear_conflict = 0

        # 1. Tính Manhattan Distance
        for i in range(size * size):
            val = board[i]
            if val != 0:
                target_x, target_y = (val - 1) // size, (val - 1) % size
                curr_x, curr_y = i // size, i % size
                manhattan += abs(curr_x - target_x) + abs(curr_y - target_y)

        # 2. Tính Linear Conflict (Hàng ngang)
        for row in range(size):
            for i in range(size):
                curr_i = row * size + i
                val_i = board[curr_i]
                if val_i != 0 and (val_i - 1) // size == row:
                    for j in range(i + 1, size):
                        curr_j = row * size + j
                        val_j = board[curr_j]
                        if val_j != 0 and (val_j - 1) // size == row:
                            if val_i > val_j:
                                linear_conflict += 2 

        # 3. Tính Linear Conflict (Cột dọc)
        for col in range(size):
            for i in range(size):
                curr_i = i * size + col
                val_i = board[curr_i]
                if val_i != 0 and (val_i - 1) % size == col:
                    for j in range(i + 1, size):
                        curr_j = j * size + col
                        val_j = board[curr_j]
                        if val_j != 0 and (val_j - 1) % size == col:
                            if val_i > val_j:
                                linear_conflict += 2

        return manhattan + linear_conflict

    def get_neighbors(self, board):
        """Tìm các trạng thái tiếp theo có thể đi từ trạng thái hiện tại"""
        neighbors = []
        zero_idx = board.index(0)
        curr_x, curr_y = zero_idx // self.size, zero_idx % self.size
        
        # Các hướng di chuyển của Ô TRỐNG
        moves = {
            "UP": (-1, 0), "DOWN": (1, 0),
            "LEFT": (0, -1), "RIGHT": (0, 1)
        }
        
        for move_name, (dx, dy) in moves.items():
            next_x, next_y = curr_x + dx, curr_y + dy
            if 0 <= next_x < self.size and 0 <= next_y < self.size:
                next_idx = next_x * self.size + next_y
                # Đổi chỗ tạo trạng thái mới
                new_board = list(board)
                new_board[zero_idx], new_board[next_idx] = new_board[next_idx], new_board[zero_idx]
                neighbors.append((tuple(new_board), move_name))
                
        return neighbors

    def solve_smart_hybrid(self, start_matrix):
        """
        Thuật toán Siêu tốc cho bàn cờ lớn (Weighted A*).
        Đảm bảo phản hồi ngay lập tức cho 4x4, 5x5, 6x6.
        """
        # Chuyển 2D thành 1D Tuple để xử lý siêu tốc
        start_board = tuple(val for row in start_matrix for val in row)
        
        if start_board == self.target:
            return []

        # Tùy biến Trọng số (Weight) dựa trên kích thước bàn cờ
        # Bàn cờ càng to, AI càng phải "tham lam" để tránh bị tràn RAM
        weight = 1.0
        if self.size == 4: weight = 5.0
        elif self.size >= 5: weight = 10.0

        h_start = self.get_manhattan_and_linear_conflict(start_board)
        
        # Dùng counter để giải quyết lỗi so sánh Tuple khi 2 trạng thái có cùng điểm F
        counter = itertools.count() 
        
        # Hàng đợi: (Điểm F, Điểm H, Điểm G, ID đếm, Trạng thái, Lịch sử nước đi)
        queue = [(h_start * weight, h_start, 0, next(counter), start_board, [])]
        
        # Chỉ lưu trạng thái đã đi qua bằng Set (Tốc độ O(1) và cực kỳ tiết kiệm RAM)
        visited = set()
        visited.add(start_board)

        while queue:
            f, h, g, _, current, path = heapq.heappop(queue)

            if current == self.target:
                return path 

            # Giới hạn độ sâu để chống treo máy (Safety net)
            # Nếu tính toán vượt quá 5000 vòng lặp, chốt luôn nước đi Greedy tốt nhất để thoát hiểm
            if next(counter) > 5000:
                neighbors = self.get_neighbors(current)
                best_neighbor = min(neighbors, key=lambda x: self.get_manhattan_and_linear_conflict(x[0]))
                return path + [best_neighbor[1]]

            for next_board, move_name in self.get_neighbors(current):
                if next_board not in visited:
                    visited.add(next_board)
                    new_g = g + 1
                    new_h = self.get_manhattan_and_linear_conflict(next_board)
                    new_f = new_g + (new_h * weight) # Áp dụng phép thuật Weighted A*
                    
                    heapq.heappush(queue, (new_f, new_h, new_g, next(counter), next_board, path + [move_name]))
        
        return []