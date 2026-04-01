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

def slice_image(cropped_surface, board_size: int, grid_size: int):
    """Băm cái ảnh vuông vừa cắt thành các mảnh puzzle."""
    if cropped_surface is None: 
        return None, None
        
    tile_size = board_size // grid_size
    slices = {}
    count = 1
    
    for r in range(grid_size):
        for c in range(grid_size):
            # Bỏ qua ô góc phải dưới cùng làm ô trống
            if r == grid_size - 1 and c == grid_size - 1:
                break 
                
            rect = pygame.Rect(c * tile_size, r * tile_size, tile_size, tile_size)
            slices[count] = cropped_surface.subsurface(rect).copy()
            count += 1
            
    return cropped_surface, slices