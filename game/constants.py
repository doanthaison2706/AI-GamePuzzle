# ─── Window ──────────────────────────────────────────────────────────────────
WINDOW_WIDTH  = 1300
WINDOW_HEIGHT = 900
FPS           = 60

# ─── Colors — Bright & Minimalist ─────────────────────────────────────────────
BG_COLOR    = (240, 235, 230)   # Warm soft cream
PANEL_BG    = (250, 245, 240)   # Slightly whiter for panels
BTN_COLOR   = (80,  150, 140)   # Calm muted teal
BTN_HOVER   = (60,  130, 120)   # Darker teal for hover
BTN_ACTIVE  = (40,  110, 100)   # Even darker teal
BTN_TEXT    = (255, 255, 255)   # White text on buttons
ACCENT      = (220, 180, 110)   # Muted classic gold
TEXT_COLOR  = (60,  50,  50)    # Deep warm brown/charcoal
MUTED_TEXT  = (130, 115, 110)   # Warm grey
P1_COLOR    = (120, 180, 150)   # Soft sage green
P2_COLOR    = (210, 130, 120)   # Soft dusty rose
WIN_COLOR   = (100, 160, 210)   # Soft steel blue
EMPTY_CELL  = (225, 215, 210)   # Darker cream
DRAG_BORDER = (80,  150, 140)   # Teal drag border
TILE_BORDER = (200, 190, 185)   # Warm grey border

# ─── Puzzle board ─────────────────────────────────────────────────────────────
# Both boards use the same pixel width; tile_size is derived at runtime as
# BOARD_SIZE // n  (so the board pixel width = tile_size * n ≤ BOARD_SIZE).
BOARD_SIZE = 500

DIFFICULTY_GRID = {
    "Easy":   3,
    "Medium": 4,
    "Hard":   5,
}

# ─── Layout (pixel positions for the two boards) ──────────────────────────────
LEFT_BOARD_X  = 40
RIGHT_BOARD_X = 760
BOARD_Y       = 110
CENTER_X      = WINDOW_WIDTH // 2   # 650

# ─── Default game options ─────────────────────────────────────────────────────
DEFAULT_DIFFICULTY    = "Medium"
DEFAULT_SCORE_LIMIT   = 3      # first player to solve N puzzles wins the match
DEFAULT_TIMER_ENABLED = True
DEFAULT_TIMER_SECS    = 180    # seconds per puzzle round
DEFAULT_MULTIPLAYER   = True   # True = 2-player, False = 1-player
