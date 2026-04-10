import pygame

pygame.display.init()
screen_info = pygame.display.Info()

MONITOR_WIDTH = screen_info.current_w
MONITOR_HEIGHT = screen_info.current_h

# --- Giao diện Fixed Size dựa trên Dual Player ---
WINDOW_HEIGHT = int(MONITOR_HEIGHT * 0.9)

# Kích thước khung cửa sổ là cố định và lấy theo tỷ lệ của Dual Player
WINDOW_WIDTH = int(WINDOW_HEIGHT * 1.6)
DUAL_WINDOW_WIDTH = WINDOW_WIDTH # Tương thích ngược với các file UI cũ

# Board Size cho Single Player
BOARD_SIZE = int(WINDOW_HEIGHT * 0.8 * 0.8) # (old WINDOW_WIDTH = HEIGHT*0.8) * 0.8
if BOARD_SIZE > WINDOW_HEIGHT * 0.7:
    BOARD_SIZE = int(WINDOW_HEIGHT * 0.7)
MARGIN_TOP = int(WINDOW_HEIGHT * 0.22)
MARGIN_LEFT = (WINDOW_WIDTH - BOARD_SIZE) // 2

# Board Size cho Dual Player
DUAL_BOARD_SIZE = int(WINDOW_WIDTH * 0.42)
if DUAL_BOARD_SIZE > WINDOW_HEIGHT * 0.6:
    DUAL_BOARD_SIZE = int(WINDOW_HEIGHT * 0.6)
DUAL_MARGIN_TOP = MARGIN_TOP
DUAL_P1_LEFT = int(WINDOW_WIDTH * 0.04)
DUAL_P2_LEFT = WINDOW_WIDTH - DUAL_BOARD_SIZE - DUAL_P1_LEFT

def update_configs():
    pass

# Bảng màu
FPS = 60
BG_COLOR        = (245, 242, 235)   # cream-white background
TEXT_COLOR      = (40,  40,  55)    # near-black text
MUTED_TEXT      = (140, 135, 125)   # secondary / label text
WHITE           = (255, 255, 255)

# Accent & button palette
ACCENT          = (100, 180, 240)   # sky-blue accent
BTN_COLOR       = ( 70,  80, 150)   # default button
BTN_HOVER       = ( 90, 105, 190)   # hovered button
BTN_ACTIVE      = ( 50,  60, 120)   # pressed button
BTN_TEXT        = (255, 255, 255)   # button label

# Player accent colours
P1_COLOR        = ( 80, 160, 220)   # player 1 blue
P2_COLOR        = (220,  90,  90)   # player 2 red
WIN_COLOR       = ( 60, 200, 120)   # win / success green
PANEL_BG        = (220, 215, 205)   # panel background