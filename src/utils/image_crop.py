import platform
import subprocess
import pygame

def open_file_dialog():
    """Mở hộp thoại chọn ảnh. Tự động tương thích an toàn cho cả Mac và Windows."""
    # Nếu đang chạy trên macOS (Tránh lỗi crash giữa Pygame và Tkinter)
    if platform.system() == "Darwin":
        script = '''
        try
            set theFile to choose file with prompt "Chọn một bức ảnh để chơi:" of type {"public.image"}
            POSIX path of theFile
        on error
            return ""
        end try
        '''
        try:
            # Gọi AppleScript native của Mac
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            path = result.stdout.strip()
            return path if path else None
        except Exception as e:
            print("⚠️ Lỗi khi mở hộp thoại trên Mac:", e)
            return None

    # Nếu chạy trên Windows / Linux (Dùng Tkinter bình thường)
    else:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True) # Ép hộp thoại nổi lên trên cùng cửa sổ game
        file_path = filedialog.askopenfilename(
            title="Chọn một bức ảnh để chơi (JPG/PNG)",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        root.destroy()
        return file_path

def slice_image(image, board_size, size):
    """Cắt ảnh thành các miếng nhỏ một cách an toàn."""
    if image is None:
        return None, None

    # BƯỚC QUAN TRỌNG NHẤT: Ép ảnh về đúng kích thước bàn cờ
    # Điều này đảm bảo ảnh không bao giờ nhỏ hơn vùng định cắt
    target_img = pygame.transform.smoothscale(image, (board_size, board_size))
    
    # Tính kích thước mỗi ô (dùng số nguyên)
    tile_size = board_size // size
    slices = {}
    count = 1

    for r in range(size):
        for c in range(size):
            # Không cắt ô cuối cùng (để làm ô trống)
            if count == size * size:
                break
            
            # Tính toán tọa độ x, y
            x = c * tile_size
            y = r * tile_size
            
            # Tạo Rect bảo vệ: đảm bảo không bao giờ vượt quá board_size
            rect = pygame.Rect(x, y, tile_size, tile_size)
            
            # Cắt ảnh từ tấm target_img đã được scale chuẩn
            try:
                slices[count] = target_img.subsurface(rect).copy()
            except ValueError:
                # Nếu vẫn lỗi (do làm tròn số lẻ), ta thu nhỏ rect lại 1 pixel
                safe_rect = pygame.Rect(x, y, min(tile_size, board_size - x), min(tile_size, board_size - y))
                slices[count] = target_img.subsurface(safe_rect).copy()
                
            count += 1

    return target_img, slices