import pygame
import sys
from configs import game_config as config
from src.ui.menu_screen import MainMenuScreen
from src.ui.setup_single_screen import SetupSingleScreen  
from src.ui.single_player_screen import SinglePlayerScreen
from src.ui.setup_multi_screen import SetupMultiScreen
from src.ui.multi_player_screen import MultiPlayerScreen
from src.ui.win_single_screen import WinSingleScreen 
# Bạn có thể import WinMultiScreen sau khi chúng ta code xong nó
# from src.ui.win_multi_screen import WinMultiScreen 

class GameApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("N-Puzzle Arena")
        self.clock = pygame.time.Clock()
        
        self.state = "MAIN_MENU" 
        self.current_screen = MainMenuScreen(self.screen) 
        
        self.last_setup_data = None 

    def run(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # --- MÁY TRẠNG THÁI (STATE MACHINE) ---
            if self.state == "MAIN_MENU":
                next_state, _ = self.current_screen.handle_events(events)
                
                if next_state == "SETUP_SINGLE":
                    self.state = "SETUP_SINGLE"
                    self.current_screen = SetupSingleScreen(self.screen)
                # FIX 1: THÊM LỐI VÀO CHO SETUP MULTI TỪ MAIN MENU
                elif next_state == "SETUP_MULTI":
                    self.state = "SETUP_MULTI"
                    self.current_screen = SetupMultiScreen(self.screen)
                    
            elif self.state == "SETUP_SINGLE":
                next_state, setup_data = self.current_screen.handle_events(events)
                if next_state == "PLAYING":
                    self.state = "PLAYING"
                    self.last_setup_data = setup_data 
                    self.current_screen = SinglePlayerScreen(self.screen, setup_data)
                elif next_state == "MENU":
                    self.state = "MAIN_MENU"
                    self.current_screen = MainMenuScreen(self.screen)
                    
            elif self.state == "PLAYING":
                result = self.current_screen.handle_events(events)
                if isinstance(result, tuple):
                    next_state, result_data = result
                else:
                    next_state = result
                    result_data = None

                self.current_screen.update()
                
                if next_state == "MENU": 
                    self.state = "MAIN_MENU"
                    self.current_screen = MainMenuScreen(self.screen)
                elif next_state == "WIN_SINGLE": 
                    self.state = "WIN_SINGLE"
                    self.current_screen = WinSingleScreen(self.screen, result_data)

            elif self.state == "WIN_SINGLE":
                next_state, _ = self.current_screen.handle_events(events)
                
                if next_state == "PLAYING":
                    self.state = "PLAYING"
                    self.current_screen = SinglePlayerScreen(self.screen, self.last_setup_data)
                elif next_state == "SETUP_SINGLE":
                    self.state = "SETUP_SINGLE"
                    self.current_screen = SetupSingleScreen(self.screen)
                elif next_state == "MENU":
                    self.state = "MAIN_MENU"
                    self.current_screen = MainMenuScreen(self.screen)

            # --- NHÁNH CHƠI ĐỐI KHÁNG ---
            elif self.state == "SETUP_MULTI":
                next_state, setup_data = self.current_screen.handle_events(events)
                if next_state == "PLAYING_MULTI":
                    self.state = "PLAYING_MULTI"
                    self.last_setup_data = setup_data
                    
                    self.screen = self.resize_window("LANDSCAPE")
                    self.current_screen = MultiPlayerScreen(self.screen, setup_data)
                    
                elif next_state == "MENU":
                    self.state = "MAIN_MENU"
                    self.screen = self.resize_window("PORTRAIT") 
                    self.current_screen = MainMenuScreen(self.screen)

            elif self.state == "PLAYING_MULTI":
                # FIX 2: BỔ SUNG ĐẦY ĐỦ LOGIC ĐÓN KẾT QUẢ TRẢ VỀ
                result = self.current_screen.handle_events(events)
                if isinstance(result, tuple):
                    next_state, result_data = result
                else:
                    next_state = result
                    result_data = None
                
                # RẤT QUAN TRỌNG: Gọi update để Game chạy AI và delay lúc thắng
                self.current_screen.update()
                
                if next_state == "MENU":
                    self.state = "MAIN_MENU"
                    self.screen = self.resize_window("PORTRAIT")
                    self.current_screen = MainMenuScreen(self.screen)
                    
                elif next_state == "WIN_MULTI":
                    pass # Chờ code WinMultiScreen xong sẽ nhét vào đây
                    print(f"Bên chiến thắng chung cuộc là: P{result_data['winner']}")
                    # Tạm thời quay về Menu khi thắng
                    self.state = "MAIN_MENU"
                    self.screen = self.resize_window("PORTRAIT")
                    self.current_screen = MainMenuScreen(self.screen)

            # --- VẼ GIAO DIỆN ---
            self.screen.fill(config.BG_COLOR)
            self.current_screen.render()
            
            pygame.display.flip()
            self.clock.tick(config.FPS)

    def resize_window(self, mode):
        """Hàm hô biến cửa sổ Dọc <-> Ngang"""
        if mode == "LANDSCAPE":
            new_size = (1200, 800) 
        else:
            new_size = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
            
        self.screen = pygame.display.set_mode(new_size, pygame.RESIZABLE)
        return self.screen