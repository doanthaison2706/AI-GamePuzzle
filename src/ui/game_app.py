import pygame
import sys
from configs import game_config as config
from src.ui.menu_screen import MenuScreen
from src.ui.single_player_screen import SinglePlayerScreen

class GameApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption("N-Puzzle Arena")
        self.clock = pygame.time.Clock()
        
        self.state = "MENU"
        self.current_screen = MenuScreen(self.screen) # Khởi tạo màn hình đầu tiên

    def run(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # 1. Chuyển trạng thái (State Machine)
            if self.state == "MENU":
                next_state, setup_data = self.current_screen.handle_events(events)
                if next_state == "PLAYING":
                    self.state = "PLAYING"
                    # Nạp đạn: Khởi tạo SinglePlayerScreen với dữ liệu từ Menu
                    self.current_screen = SinglePlayerScreen(self.screen, setup_data)
                    
            elif self.state == "PLAYING":
                next_state = self.current_screen.handle_events(events)
                self.current_screen.update()
                if next_state == "MENU":
                    self.state = "MENU"
                    # Xóa game cũ, nạp lại Menu
                    self.current_screen = MenuScreen(self.screen)

            # 2. Render màn hình hiện tại
            self.screen.fill(config.BG_COLOR)
            self.current_screen.render()
            
            pygame.display.flip()
            self.clock.tick(config.FPS)