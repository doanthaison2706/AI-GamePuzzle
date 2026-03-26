import random

class Board:
    """
    Quản lý logic ma trận của bàn cờ N-Puzzle.
    Không chứa bất kỳ code giao diện (Pygame/UI) nào ở đây.
    0 đại diện cho ô trống (Empty Tile).
    """
    def __init__(self, size: int):
        self.size = size
        self.matrix = self._generate_solved_board()

    def _generate_solved_board(self) -> list[list[int]]:
        # Tạo ma trận trạng thái đích cho bàn cờ N-Puzzle.
        board = []
        count = 1
        for i in range(self.size):
            row = []
            for j in range(self.size):
                if i == self.size - 1 and j == self.size - 1:
                    row.append(0)  # 0 là ô trống ở góc dưới cùng bên phải
                else:
                    row.append(count)
                    count += 1
            board.append(row)
        return board

    def get_empty_pos(self) -> tuple[int, int]:
        """Tìm tọa độ (row, col) của ô trống."""
        for r in range(self.size):
            for c in range(self.size):
                if self.matrix[r][c] == 0:
                    return r, c
        return -1, -1

    def get_valid_moves(self) -> list[tuple[int, int]]:
        """Trả về danh sách các tọa độ có thể trượt vào ô trống."""
        r, c = self.get_empty_pos()
        moves = []
        if r > 0: moves.append((r - 1, c))             
        if r < self.size - 1: moves.append((r + 1, c)) 
        if c > 0: moves.append((r, c - 1))             
        if c < self.size - 1: moves.append((r, c + 1))
        return moves

    def move(self, r: int, c: int) -> bool:
        """
        Thực hiện hoán đổi ô trống với ô ở tọa độ (r, c).
        Trả về True nếu di chuyển hợp lệ, False nếu sai luật.
        """
        er, ec = self.get_empty_pos()
        if (r, c) in self.get_valid_moves():
            # Cú pháp swap thần thánh của Python
            self.matrix[er][ec], self.matrix[r][c] = self.matrix[r][c], self.matrix[er][ec]
            return True
        return False

    def _get_inversion_count(self, flat_board: list[int]) -> int:
        """Đếm số nghịch thế I trong mảng 1D."""
        inversions = 0
        for i in range(len(flat_board)):
            for j in range(i + 1, len(flat_board)):
                if flat_board[i] != 0 and flat_board[j] != 0 and flat_board[i] > flat_board[j]:
                    inversions += 1
        return inversions

    def shuffle(self):
        """Sinh bàn cờ ngẫu nhiên và kiểm tra bằng toán học."""
        flat_board = [i for i in range(self.size * self.size)]
        
        while True:
            random.shuffle(flat_board)
            inversions = self._get_inversion_count(flat_board)
            
            is_solvable = False
            if self.size % 2 != 0:
                is_solvable = (inversions % 2 == 0)
            else:
                empty_idx = flat_board.index(0)
                empty_row_from_bottom = self.size - (empty_idx // self.size)
                is_solvable = ((inversions + empty_row_from_bottom) % 2 != 0)
                
            if is_solvable:
                # Đổ mảng 1D về lại 2D
                self.matrix = [flat_board[i*self.size : (i+1)*self.size] for i in range(self.size)]
                # Đảm bảo không trùng ngay trạng thái đích
                if not self.is_solved():
                    break

    def is_solved(self) -> bool:
        """Kiểm tra xem người chơi đã thắng chưa."""
        return self.matrix == self._generate_solved_board()

    def print_board(self):
        """Hàm phụ trợ để in ra Terminal test thử."""
        for row in self.matrix:
            print("\t".join(str(x) if x != 0 else " " for x in row))
        print("-" * 20)