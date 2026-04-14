import heapq
import itertools
import random

class PuzzleSolver:
    def __init__(self, size):
        self.size = size
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

    def get_neighbors(self, board, locked_indices=None):
        """
        Đã nâng cấp: Thêm tham số locked_indices.
        AI sẽ KHÔNG BAO GIỜ tráo đổi ô trống với các vị trí đã bị khóa.
        """
        if locked_indices is None:
            locked_indices = set()

        neighbors = []
        zero_idx = board.index(0)
        curr_x, curr_y = zero_idx // self.size, zero_idx % self.size

        moves = {
            "UP": (-1, 0), "DOWN": (1, 0),
            "LEFT": (0, -1), "RIGHT": (0, 1)
        }

        for move_name, (dx, dy) in moves.items():
            next_x, next_y = curr_x + dx, curr_y + dy
            if 0 <= next_x < self.size and 0 <= next_y < self.size:
                next_idx = next_x * self.size + next_y
                
                # CHỐT CHẶN QUAN TRỌNG: Nếu ô định đi tới đang bị khóa -> Bỏ qua
                if next_idx in locked_indices:
                    continue

                new_board = list(board)
                new_board[zero_idx], new_board[next_idx] = new_board[next_idx], new_board[zero_idx]
                neighbors.append((tuple(new_board), move_name))

        random.shuffle(neighbors)
        return neighbors

    def solve_single_tile(self, start_board, tile_val, target_idx, locked_indices):
        """
        HÀM MỚI: Chỉ tập trung tìm đường đưa ĐÚNG 1 VIÊN GẠCH (tile_val) về ĐÚNG 1 VỊ TRÍ (target_idx).
        Bỏ qua điểm số của các viên gạch khác.
        """
        def single_tile_heuristic(board):
            # Khoảng cách từ viên gạch mục tiêu đến đích
            tile_curr_idx = board.index(tile_val)
            t_x, t_y = tile_curr_idx // self.size, tile_curr_idx % self.size
            dest_x, dest_y = target_idx // self.size, target_idx % self.size
            dist_tile_to_dest = abs(t_x - dest_x) + abs(t_y - dest_y)

            # Khoảng cách từ ô trống (0) đến viên gạch mục tiêu (để có thể đẩy nó đi)
            zero_idx = board.index(0)
            z_x, z_y = zero_idx // self.size, zero_idx % self.size
            dist_zero_to_tile = abs(z_x - t_x) + abs(z_y - t_y)

            return dist_tile_to_dest * 10 + dist_zero_to_tile

        counter = itertools.count()
        h_start = single_tile_heuristic(start_board)
        queue = [(h_start, 0, next(counter), start_board, [])]
        visited = set()
        visited.add(start_board)

        while queue:
            f, g, _, current, path = heapq.heappop(queue)

            # Điểm dừng: Viên gạch đã nằm đúng vị trí đích
            if current.index(tile_val) == target_idx:
                return path, current

            # Dùng get_neighbors có hệ thống khóa
            for next_board, move_name in self.get_neighbors(current, locked_indices):
                if next_board not in visited:
                    visited.add(next_board)
                    new_g = g + 1
                    new_f = new_g + single_tile_heuristic(next_board)
                    heapq.heappush(queue, (new_f, new_g, next(counter), next_board, path + [move_name]))

        return [], start_board

    def solve_smart_hybrid(self, start_matrix, locked_indices=None):
        if locked_indices is None:
            locked_indices = set()
            
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

            if next(counter) > 5000:
                # Sửa dòng này: truyền locked_indices vào get_neighbors
                neighbors = self.get_neighbors(current, locked_indices)
                best_neighbor = min(neighbors, key=lambda x: self.get_manhattan_and_linear_conflict(x[0]))
                return path + [best_neighbor[1]]

            # Sửa dòng này: truyền locked_indices vào get_neighbors
            for next_board, move_name in self.get_neighbors(current, locked_indices):
                if next_board not in visited:
                    visited.add(next_board)
                    new_g = g + 1
                    new_h = self.get_manhattan_and_linear_conflict(next_board)
                    new_f = new_g + (new_h * weight) # Áp dụng phép thuật Weighted A*

                    heapq.heappush(queue, (new_f, new_h, new_g, next(counter), next_board, path + [move_name]))

        return []