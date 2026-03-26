import pygame
from configs import game_config as config

import platform
import subprocess

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

def interactive_crop(screen, image_path: str, board_size: int):
    """
    Tạo màn hình giao diện để người dùng dùng chuột kéo thả khung vuông cắt ảnh.
    """
    try:
        original_img = pygame.image.load(image_path).convert_alpha()
    except Exception:
        return None

    # Lấy kích thước ảnh gốc
    img_w, img_h = original_img.get_size()
    screen_w, screen_h = config.WINDOW_WIDTH, config.WINDOW_HEIGHT
    
    # Tính tỷ lệ thu nhỏ sao cho bức ảnh hiển thị vừa vặn trên màn hình để cắt
    scale = min((screen_w - 40) / img_w, (screen_h - 150) / img_h)
    scaled_w, scaled_h = int(img_w * scale), int(img_h * scale)
    scaled_img = pygame.transform.smoothscale(original_img, (scaled_w, scaled_h))
    
    # Khung cắt (Crop Box) LUÔN LUÔN LÀ HÌNH VUÔNG
    crop_size = min(scaled_w, scaled_h)
    crop_rect = pygame.Rect(0, 0, crop_size, crop_size)
    
    # Tọa độ để vẽ ảnh ra giữa màn hình
    offset_x = (screen_w - scaled_w) // 2
    offset_y = (screen_h - scaled_h) // 2
    
    font = pygame.font.SysFont("arial", 20, bold=True)
    dragging = False
    running = True
    clock = pygame.time.Clock()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
                
            # Xử lý KÉO THẢ CHUỘT
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Kiểm tra xem chuột có click trúng vào trong Khung Cắt không
                if crop_rect.collidepoint(event.pos[0] - offset_x, event.pos[1] - offset_y):
                    dragging = True
                    mouse_x, mouse_y = event.pos
                    # Lưu lại độ lệch (offset) để kéo thả mượt hơn
                    offset_x_drag = crop_rect.x - mouse_x
                    offset_y_drag = crop_rect.y - mouse_y
                    
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = False
                
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    mouse_x, mouse_y = event.pos
                    crop_rect.x = mouse_x + offset_x_drag
                    crop_rect.y = mouse_y + offset_y_drag
                    
                    # Chặn không cho người dùng kéo khung cắt chạy ra ngoài viền ảnh
                    crop_rect.x = max(0, min(crop_rect.x, scaled_w - crop_size))
                    crop_rect.y = max(0, min(crop_rect.y, scaled_h - crop_size))
            
            # Xử lý PHÍM ENTER để chốt
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    running = False # Chốt vùng cắt và thoát vòng lặp
        
        # --- VẼ GIAO DIỆN CẮT ẢNH ---
        screen.fill((40, 40, 40)) # Nền màu xám đen chuyên nghiệp kiểu Photoshop
        
        # Vẽ bức ảnh đã thu nhỏ
        screen.blit(scaled_img, (offset_x, offset_y))
        
        # Vẽ một lớp sương mù đen mờ mờ đè lên toàn bộ ảnh...
        overlay = pygame.Surface((scaled_w, scaled_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        # ...sau đó đục một lỗ trong suốt đúng bằng cái khung vuông để làm nổi bật vùng được chọn
        pygame.draw.rect(overlay, (0, 0, 0, 0), crop_rect)
        screen.blit(overlay, (offset_x, offset_y))
        
        # Vẽ viền xanh lá cây (Khung Cắt)
        pygame.draw.rect(screen, (0, 255, 0), 
                         (offset_x + crop_rect.x, offset_y + crop_rect.y, crop_size, crop_size), 3)
        
        # Vẽ chữ hướng dẫn
        text1 = font.render("Kéo thả khung Xanh Lá để chọn vùng ảnh.", True, (255, 255, 255))
        text2 = font.render("Nhấn phím ENTER để xác nhận!", True, (255, 215, 0)) # Màu vàng
        screen.blit(text1, (screen_w // 2 - text1.get_width() // 2, 30))
        screen.blit(text2, (screen_w // 2 - text2.get_width() // 2, 60))
        
        pygame.display.flip()
        clock.tick(60)
        
    # --- XỬ LÝ TOÁN HỌC SAU KHI CẮT ---
    # Người ta vừa kéo khung trên ảnh thu nhỏ, mình phải quy đổi tỷ lệ về bức ảnh Gốc siêu to khổng lồ
    real_x = int(crop_rect.x / scale)
    real_y = int(crop_rect.y / scale)
    real_size = int(crop_size / scale)
    
    # Cắt lấy miếng vuông hoàn hảo từ ảnh gốc
    cropped_original = original_img.subsurface((real_x, real_y, real_size, real_size)).copy()
    
    # Cuối cùng, resize miếng vuông đó về đúng kích thước bàn cờ (ví dụ 500x500)
    final_image = pygame.transform.smoothscale(cropped_original, (board_size, board_size))
    return final_image

def slice_image(cropped_surface, board_size: int, grid_size: int):
    """Băm cái ảnh vuông vừa cắt thành các mảnh puzzle."""
    if cropped_surface is None: 
        return None, None
        
    tile_size = board_size // grid_size
    slices = {}
    count = 1
    
    for r in range(grid_size):
        for c in range(grid_size):
            if r == grid_size - 1 and c == grid_size - 1:
                break # Bỏ qua ô góc phải dưới cùng
                
            rect = pygame.Rect(c * tile_size, r * tile_size, tile_size, tile_size)
            slices[count] = cropped_surface.subsurface(rect).copy()
            count += 1
            
    return cropped_surface, slices