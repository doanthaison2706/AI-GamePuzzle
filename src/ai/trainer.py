import torch
import numpy as np
from puzzle_env import PuzzleEnv
from agent import DQNAgent

def train():
    # 1. KHỞI TẠO ĐẤU TRƯỜNG VÀ VÕ SĨ
    # Bắt đầu với size 3x3 trước để test tốc độ hội tụ
    env = PuzzleEnv(size=3) 
    state_size = env.num_tiles
    action_size = len(env.action_space)

    agent = DQNAgent(state_size, action_size)

    # 2. THIẾT LẬP CHIẾN DỊCH HUẤN LUYỆN
    EPISODES = 8000     # Số ván chơi.
    MAX_STEPS = 200      # Giới hạn số bước mỗi ván

    print("🚀 Bắt đầu khóa huấn luyện AI (Deep Q-Network)...")

    for e in range(EPISODES):
        scramble_difficulty = min(100, 10 + (e // 500) * 5) 
        state = env.reset(scramble_steps=scramble_difficulty)
        total_reward = 0

        for time in range(MAX_STEPS):
            action = agent.act(state)
            next_state, reward, done = env.step(action)
            total_reward += reward
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            agent.replay()

            if done:
                # CHỈ IN LOG MỖI 100 VÁN 1 LẦN (Cho đỡ lag Colab)
                if e % 100 == 0:
                    print(f"✅ Ván {e}/{EPISODES} | Giải sau {time} bước | Epsilon: {agent.epsilon:.3f} | Xáo trộn: {scramble_difficulty} bước")
                break
        else:
            # Hết giờ cũng chỉ in mỗi 100 ván 1 lần
            if e % 100 == 0:
                print(f"❌ Ván {e}/{EPISODES} | Bị kẹt (Hết 200 bước) | Epsilon: {agent.epsilon:.3f}")

        # Đồng bộ mạng mục tiêu
        if e % 10 == 0:
            agent.update_target_model()

        # --- TRÍCH XUẤT 3 CẤP ĐỘ MODEL ---
        if e == 1000:
            torch.save(agent.model.state_dict(), "puzzle_easy.pth")
            print("\n💾 ĐÃ LƯU: Model Dễ (puzzle_easy.pth)\n")

        if e == 4000:
            torch.save(agent.model.state_dict(), "puzzle_medium.pth")
            print("\n💾 ĐÃ LƯU: Model Trung Bình (puzzle_medium.pth)\n")

    # Lưu lúc kết thúc
    torch.save(agent.model.state_dict(), "puzzle_hard.pth")
    print("\n💾 ĐÃ LƯU: Model Khó (puzzle_hard.pth)")
    
    # --- TỰ ĐỘNG TẢI VỀ TỪ COLAB ---
    try:
        from google.colab import files
        print("Đang chuẩn bị tải 3 file về máy...")
        files.download("puzzle_easy.pth")
        files.download("puzzle_medium.pth")
        files.download("puzzle_hard.pth")
    except ImportError:
        pass # Bỏ qua nếu đang chạy thẳng trên máy Mac

if __name__ == "__main__":
    train()