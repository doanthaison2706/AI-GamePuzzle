import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np
from collections import deque

# 1. KIẾN TRÚC MẠNG THẦN KINH (Thay cho HashMap Q-Table cũ)
class DQN(nn.Module):
    def __init__(self, state_size, action_size):
        super(DQN, self).__init__()
        # Mạng 3 lớp ẩn đơn giản gọn nhẹ, tính toán siêu tốc
        self.fc1 = nn.Linear(state_size, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, action_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

# 2. BỘ NÃO ĐIỀU KHIỂN (Thay cho RLAgent.java)
class DQNAgent:
    def __init__(self, state_size=9, action_size=4):
        self.state_size = state_size
        self.action_size = action_size
        
        # Siêu tham số (Hyperparameters)
        self.gamma = 0.99    # Hệ số chiết khấu (Nhìn xa trông rộng)
        self.epsilon = 1.0   # Tỉ lệ đi ngẫu nhiên ban đầu để khám phá
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.batch_size = 64
        
        # Bộ nhớ Experience Replay - Điểm mấu chốt để AI không bị "học vẹt"
        self.memory = deque(maxlen=10000)
        
        # Khởi tạo Mạng chính (Hành động) và Mạng mục tiêu (Đánh giá)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = DQN(state_size, action_size).to(self.device)
        self.target_model = DQN(state_size, action_size).to(self.device)
        self.update_target_model()
        
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.criterion = nn.MSELoss()

    def update_target_model(self):
        """Đồng bộ nếp nhăn từ mạng chính sang mạng mục tiêu"""
        self.target_model.load_state_dict(self.model.state_dict())

    def remember(self, state, action, reward, next_state, done):
        """Lưu lại 1 bước đi vào bộ nhớ"""
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        """Quyết định nước đi tiếp theo"""
        # Khám phá ngẫu nhiên
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
            
        # Tận dụng kiến thức đã học
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            act_values = self.model(state_tensor)
        return torch.argmax(act_values[0]).item() # Trả về hướng có điểm Q cao nhất

    def replay(self):
        """Hồi tưởng bộ nhớ và cập nhật Mạng thần kinh"""
        if len(self.memory) < self.batch_size:
            return # Chưa tích đủ kinh nghiệm thì chưa học
            
        # Bốc ngẫu nhiên một nắm kinh nghiệm từ quá khứ
        minibatch = random.sample(self.memory, self.batch_size)
        
        # Chuyển đổi dữ liệu sang Tensor để PyTorch xử lý
        states = torch.FloatTensor(np.array([t[0] for t in minibatch])).to(self.device)
        actions = torch.LongTensor([t[1] for t in minibatch]).unsqueeze(1).to(self.device)
        rewards = torch.FloatTensor([t[2] for t in minibatch]).unsqueeze(1).to(self.device)
        next_states = torch.FloatTensor(np.array([t[3] for t in minibatch])).to(self.device)
        dones = torch.FloatTensor([t[4] for t in minibatch]).unsqueeze(1).to(self.device)

        # 1. AI tự đánh giá nước đi hiện tại
        current_q_values = self.model(states).gather(1, actions)
        
        # 2. Tính toán mục tiêu lý tưởng bằng phương trình Bellman
        with torch.no_grad():
            max_next_q_values = self.target_model(next_states).max(1)[0].unsqueeze(1)
            target_q_values = rewards + (self.gamma * max_next_q_values * (1 - dones))

        # 3. Phạt AI nếu đoán sai và ép nó sửa sai (Backpropagation)
        loss = self.criterion(current_q_values, target_q_values)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Giảm dần tỉ lệ đi ngẫu nhiên khi AI đã bắt đầu "khôn" lên
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay