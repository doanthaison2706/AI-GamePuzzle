import numpy as np
import random

class PuzzleEnv:
    """
    Môi trường N-Puzzle chuẩn mực cho Deep Reinforcement Learning.
    Sử dụng numpy array 1D để tối ưu tốc độ và dễ dàng đưa vào Neural Network.
    """
    def __init__(self, size=3):
        self.size = size
        self.num_tiles = size * size
        
        # Trạng thái đích: [1, 2, 3, ..., 0] (0 là ô trống)
        self.target_state = np.append(np.arange(1, self.num_tiles), 0)
        self.state = np.copy(self.target_state)
        
        # RL thường dùng số nguyên cho Action thay vì String
        # 0: UP, 1: DOWN, 2: LEFT, 3: RIGHT
        self.action_space = [0, 1, 2, 3]

    def reset(self, scramble_steps=100):
        """
        Khởi tạo lại bàn cờ bằng cách đi ngược từ đích.
        Đảm bảo 100% bàn cờ sinh ra luôn giải được (khắc phục lỗi xáo trộn ngẫu nhiên).
        scramble_steps: Số bước xáo trộn. Càng cao thì bàn cờ càng khó.
        """
        self.state = np.copy(self.target_state)
        
        # Xáo trộn bàn cờ
        for _ in range(scramble_steps):
            valid_actions = self._get_valid_actions()
            action = random.choice(valid_actions)
            self._move(action)
            
        return np.copy(self.state)

    def _get_valid_actions(self):
        """Trả về danh sách các action hợp lệ (không bị đụng tường)"""
        zero_idx = np.where(self.state == 0)[0][0]
        row, col = zero_idx // self.size, zero_idx % self.size
        
        valid_actions = []
        if row > 0: valid_actions.append(0) # UP
        if row < self.size - 1: valid_actions.append(1) # DOWN
        if col > 0: valid_actions.append(2) # LEFT
        if col < self.size - 1: valid_actions.append(3) # RIGHT
        
        return valid_actions

    def _move(self, action):
        """Thực hiện di chuyển ô trống. Trả về True nếu hợp lệ, False nếu chạm tường."""
        zero_idx = np.where(self.state == 0)[0][0]
        row, col = zero_idx // self.size, zero_idx % self.size
        
        # Xác định vị trí mới của ô trống
        new_row, new_col = row, col
        if action == 0 and row > 0: new_row -= 1            # UP
        elif action == 1 and row < self.size - 1: new_row += 1  # DOWN
        elif action == 2 and col > 0: new_col -= 1            # LEFT
        elif action == 3 and col < self.size - 1: new_col += 1  # RIGHT
        else:
            return False # Nước đi không hợp lệ

        new_idx = new_row * self.size + new_col
        # Hoán đổi giá trị
        self.state[zero_idx], self.state[new_idx] = self.state[new_idx], self.state[zero_idx]
        return True

    def step(self, action):
        """
        Thực hiện một bước đi trong quá trình huấn luyện RL.
        Trả về: next_state, reward, done
        """
        valid = self._move(action)
        
        # Kiểm tra xem đã giải xong chưa
        done = np.array_equal(self.state, self.target_state)
        
        # Hệ thống tính phần thưởng (Reward Shaping)
        if done:
            reward = 100  # Thưởng lớn khi giải xong (giống bản Java cũ)
        elif not valid:
            reward = -5   # Phạt nặng nếu cố tình đi đâm vào tường (giống bản Java cũ)
        else:
            reward = -1   # Phạt nhẹ mỗi bước đi để AI tìm đường ngắn nhất (giống bản Java cũ)
            
        return np.copy(self.state), reward, done

    def get_state(self):
        """Trả về state hiện tại"""
        return np.copy(self.state)

    def render(self):
        """In bàn cờ ra console để dễ debug"""
        board_2d = self.state.reshape((self.size, self.size))
        print(board_2d)
        print("-" * 15)