import pygame

# Khởi tạo module hiển thị để Pygame có thể "đọc" được phần cứng
pygame.display.init()
screen_info = pygame.display.Info()

# Kích thước thật của màn hình máy tính (Ví dụ: 1920x1080 hoặc 2560x1600 trên Mac)
MONITOR_WIDTH = screen_info.current_w
MONITOR_HEIGHT = screen_info.current_h

# --- THIẾT LẬP KÍCH THƯỚC ĐỘNG ---
# Chiều cao cửa sổ = 90% chiều cao màn hình (Chừa chỗ cho Taskbar / Mac Dock)
WINDOW_HEIGHT = int(MONITOR_HEIGHT * 0.9)

# Chiều rộng cửa sổ chơi đơn = 80% chiều cao (Tạo ra tỷ lệ hình chữ nhật đứng chuẩn Mobile)
# (Sau này làm màn Chơi Đôi, ta chỉ cần nhân đôi chiều rộng này lên)
WINDOW_WIDTH = int(WINDOW_HEIGHT * 0.8)

# --- TÍNH TOÁN TỌA ĐỘ BÀN CỜ THEO TỶ LỆ ---
# Bàn cờ luôn chiếm 80% chiều rộng cửa sổ
BOARD_SIZE = int(WINDOW_WIDTH * 0.8)

# Đẩy bàn cờ xuống vị trí 22% tính từ đỉnh màn hình
MARGIN_TOP = int(WINDOW_HEIGHT * 0.22)
MARGIN_LEFT = (WINDOW_WIDTH - BOARD_SIZE) // 2

# Bảng màu
FPS = 60
BG_COLOR = (245, 245, 245)
TEXT_COLOR = (50, 50, 50)
WHITE = (255, 255, 255)