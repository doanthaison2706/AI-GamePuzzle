import pygame
from configs.game_config import TEXT_COLOR, MUTED_TEXT, P2_COLOR, ACCENT
from src.ui.components import RoundedButton
from src.ui.background import ModernBackground

class InfoScreen:
    def __init__(self, screen):
        self.screen = screen
        W, H = screen.get_size()
        
        self._bg = ModernBackground(W, H)
        self.font_title = pygame.font.SysFont("Georgia", 42, bold=True)
        self.font_h2 = pygame.font.SysFont("Georgia", 24, bold=True)
        self.font_text = pygame.font.SysFont("Georgia", 18)
        self.font_btn = pygame.font.SysFont("Georgia", 19, bold=True)

        # Nút Quay Lại
        self.btn_back = RoundedButton(
            (W//2 - 90, H - 90, 180, 52), "◀  B A C K", self.font_btn,
            color=(max(0, P2_COLOR[0]-30), max(0, P2_COLOR[1]-30), max(0, P2_COLOR[2]-30)),
            hover_color=P2_COLOR
        )

    def handle_events(self, events):
        for event in events:
            if self.btn_back.handle_event(event):
                return "MENU", None
        return "INFO", None

    def render(self):
        self._bg.draw(self.screen)
        W, H = self.screen.get_size()
        cx = W // 2

        # Tiêu đề
        title = self.font_title.render("H O W   T O   P L A Y", True, TEXT_COLOR)
        self.screen.blit(title, title.get_rect(center=(cx, 80)))

        # Panel chứa nội dung
        panel_rect = pygame.Rect(cx - 360, 140, 720, 480)
        pygame.draw.rect(self.screen, (255, 255, 255, 190), panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, (200, 200, 220), panel_rect, border_radius=15, width=2)
        
        # --- HÀM VẼ CÁC ĐOẠN TEXT ---
        start_y = 160
        pad_x = cx - 330

        def draw_section(icon, title_text, lines, current_y):
            # Vẽ tiêu đề mục
            t_surf = self.font_h2.render(f"{icon} {title_text}", True, (80, 100, 140))
            self.screen.blit(t_surf, (pad_x, current_y))
            current_y += 35
            # Vẽ từng dòng text
            for line in lines:
                l_surf = self.font_text.render(line, True, (60, 60, 60))
                self.screen.blit(l_surf, (pad_x + 20, current_y))
                current_y += 28
            return current_y + 15

        # 1. GOAL
        start_y = draw_section("🎯", "GOAL", [
            "Slide the tiles to form the complete picture or arrange them",
            "in numerical order from 1 to N."
        ], start_y)

        # 2. CONTROLS
        start_y = draw_section("🕹️", "CONTROLS", [
            "• Single Player: Use [W A S D] or [Arrow Keys] to move.",
            "  Hold [SPACE] to peek at the original image.",
            "• Dual Player (Versus):",
            "  - Player 1 (Left): Use [W A S D] | Hold [L-SHIFT] to peek.",
            "  - Player 2 (Right): Use [Arrow Keys] | Hold [R-SHIFT] to peek."
        ], start_y)

        # 3. ITEMS
        start_y = draw_section("💡", "ITEMS & FEATURES", [
            "• HINT: Automatically plays 1 correct move for you.",
            "  (In Versus mode, each player only has 5 hints per match!)",
            "• UNDO: Revert your last move.",
            "• AI SOLVE / AUTO: Watch the bot solve the puzzle perfectly."
        ], start_y)

        # Nút bấm
        mouse = pygame.mouse.get_pos()
        self.btn_back.draw(self.screen, mouse)