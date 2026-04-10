import pygame

# Khởi tạo module hiển thị để Pygame có thể "đọc" được phần cứng
pygame.display.init()
screen_info = pygame.display.Info()

# Kích thước thật của màn hình máy tính
MONITOR_WIDTH = screen_info.current_w
MONITOR_HEIGHT = screen_info.current_h

# --- THIẾT LẬP KÍCH THƯỚC CỬA SỔ (NGANG - TỶ LỆ 16:9) ---
# Lấy chiều rộng bằng 80% màn hình thật
WINDOW_WIDTH = int(MONITOR_WIDTH * 0.8)
# Chiều cao tính theo chuẩn 16:9 (như màn hình PC/Youtube)
WINDOW_HEIGHT = int(WINDOW_WIDTH * (9 / 16))

# Đảm bảo an toàn: Nếu tính ra chiều cao mà vượt quá 90% màn hình thật (bị lẹm Taskbar)
# Thì ta tính ngược lại từ chiều cao
if WINDOW_HEIGHT > MONITOR_HEIGHT * 0.9:
    WINDOW_HEIGHT = int(MONITOR_HEIGHT * 0.9)
    WINDOW_WIDTH = int(WINDOW_HEIGHT * (16 / 9))

# --- TỌA ĐỘ BÀN CỜ (Giá trị khởi tạo) ---
# Các giá trị này giờ chỉ là Placeholder (giữ chỗ). 
# Trong các Class màn chơi (như SinglePlayerScreen) sẽ tự động ghi đè lại 
# để đảm bảo tính Responsive.
BOARD_SIZE = 540
MARGIN_LEFT = 80
MARGIN_TOP = 130

# --- CẤU HÌNH CHUNG ---
FPS = 60
BG_COLOR = (245, 245, 245)      
TEXT_COLOR = (50, 50, 50)       
WHITE = (255, 255, 255)