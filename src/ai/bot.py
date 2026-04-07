import torch
import random
import numpy as np
from src.ai.agent import DQN 
from src.ai.solver import PuzzleSolver

class AIBot:
    def __init__(self, size, difficulty="hard"):
        self.size = size
        self.difficulty = difficulty.lower()
        
        # Output chuẩn cho Game Manager: (dr, dc)
        self.actions_rl = [(-1, 0), (1, 0), (0, -1), (0, 1)] # Index 0, 1, 2, 3
        self.moves_map_search = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}

        # ==========================================================
        # LUỒNG 1: XỬ LÝ 3x3 BẰNG DEEP LEARNING (MẠNG THẦN KINH)
        # ==========================================================
        if self.size == 3:
            self.ai_type = "RL"
            state_size = size * size
            action_size = 4
            self.device = torch.device("cpu")
            self.model = DQN(state_size, action_size).to(self.device)
            
            model_paths = {
                "easy": "assets/models/puzzle_easy.pth",
                "medium": "assets/models/puzzle_medium.pth",
                "hard": "assets/models/puzzle_hard.pth"
            }
            path = model_paths.get(self.difficulty, model_paths["hard"])
            
            try:
                self.model.load_state_dict(torch.load(path, map_location=self.device))
                self.model.eval() 
            except Exception as e:
                print(f"Lỗi: Không tìm thấy file model {path}. Vui lòng train trên Colab!")

        # ==========================================================
        # LUỒNG 2: XỬ LÝ 4x4 ĐẾN 6x6 BẰNG THUẬT TOÁN TÌM KIẾM
        # ==========================================================
        else:
            self.ai_type = "SEARCH"
            self.solver = PuzzleSolver(size)
            self.path_cache = [] # Bộ nhớ tạm cho đường đi
            
            # Cấu hình "Nhân tính" theo độ khó
            self.config = {
                "easy":   {"mistake_rate": 0.30, "forget_rate": 0.40},
                "medium": {"mistake_rate": 0.10, "forget_rate": 0.15},
                "hard":   {"mistake_rate": 0.00, "forget_rate": 0.00} # Đại kiện tướng
            }

    def get_next_move(self, matrix, empty_r, empty_c):
        """Hàm duy nhất mà Game Manager gọi đến"""
        if self.ai_type == "RL":
            return self._get_rl_move(matrix)
        else:
            return self._get_search_move(matrix)

    def _get_rl_move(self, matrix):
        """Bật não Deep Learning (Dành cho 3x3)"""
        board_1d = [val for row in matrix for val in row]
        state_tensor = torch.FloatTensor(board_1d).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            q_values = self.model(state_tensor)
            
        best_action_index = torch.argmax(q_values[0]).item()
        return self.actions_rl[best_action_index]

    def _get_search_move(self, matrix):
        """Bật thuật toán tìm kiếm có Nhân tính (Dành cho >= 4x4)"""
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
            # Gọi hàm Weighted A* siêu tốc bạn đã chép vào solver.py
            self.path_cache = self.solver.solve_smart_hybrid(matrix)

        # 4. Trả về bước đi tiếp theo
        if self.path_cache:
            best_move = self.path_cache.pop(0)
            return self.moves_map_search.get(best_move, (0, 0))
            
        return (0, 0) # Fallback an toàn