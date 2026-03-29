import os

# Đảm bảo thư mục tồn tại (không bị lỗi đường dẫn như Java)
os.makedirs("experiments", exist_ok=True)
FILE_OUTPUT_PATH = "experiments/KetQua.txt"

def write_result(time_str: str, move_count: int):
    """Ghi kết quả chơi giống hệt format wFile.writeFile của bạn."""
    try:
        with open(FILE_OUTPUT_PATH, "a", encoding="utf-8") as f:
            f.write(f"{time_str}(s) - {move_count} Clicks\n")
    except Exception as e:
        print(f"Lỗi khi ghi kết quả: {e}")

# Hàm đọc file đầu vào nếu sau này Dev 3 cần load mảng cố định
def read_custom_board(filepath: str) -> list[int]:
    # Logic nạp file DuLieu.txt sẽ nằm ở đây
    pass