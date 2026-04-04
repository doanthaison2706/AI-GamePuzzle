import pygame
import sys
from configs import game_config as config
from src.ui.menu_screen import MainMenuScreen
from src.ui.setup_screen import SetupSingleScreen
from src.ui.single_player_screen import SinglePlayerScreen
# Đừng quên import màn hình Win nhé!
from src.ui.win_single_screen import WinSingleScreen

class GameApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("N-Puzzle Arena")
        self.clock = pygame.time.Clock()

        self.state = "MAIN_MENU"
        self.current_screen = MainMenuScreen(self.screen)

        # Thêm biến này để "nhớ" cấu hình ảnh/level, dùng cho nút CHƠI LẠI
        self.last_setup_data = None

    def run(self):
        dt = 0.0
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

            elif self.state == "SETUP_SINGLE":
                next_state, setup_data = self.current_screen.handle_events(events)
                if next_state == "PLAYING":
                    self.state = "PLAYING"
                    self.last_setup_data = setup_data # Lưu lại cấu hình ngay khi bắt đầu
                    self.current_screen = SinglePlayerScreen(self.screen, setup_data)
                elif next_state == "MENU":
                    self.state = "MAIN_MENU"
                    self.current_screen = MainMenuScreen(self.screen)

            elif self.state == "PLAYING":
                # Dùng mẹo kiểm tra xem kết quả trả về là Tuple (có result_data) hay chỉ là String
                result = self.current_screen.handle_events(events)
                if isinstance(result, tuple):
                    next_state, result_data = result
                else:
                    next_state = result
                    result_data = None

                self.current_screen.update(dt)

                if next_state == "MENU":
                    self.state = "MAIN_MENU"
                    self.current_screen = MainMenuScreen(self.screen)
                elif next_state == "WIN_SINGLE": # Nếu nhận được cờ chiến thắng
                    self.state = "WIN_SINGLE"
                    self.current_screen = WinSingleScreen(self.screen, result_data)

            # --- TRẠNG THÁI MỚI: MÀN HÌNH CHIẾN THẮNG ---
            elif self.state == "WIN_SINGLE":
                next_state, _ = self.current_screen.handle_events(events)

                if next_state == "PLAYING":
                    # Bấm nút Trận Mới -> Lấy cấu hình cũ ra xài lại
                    self.state = "PLAYING"
                    self.current_screen = SinglePlayerScreen(self.screen, self.last_setup_data)
                elif next_state == "SETUP_SINGLE":
                    # Bấm Chọn Màn
                    self.state = "SETUP_SINGLE"
                    self.current_screen = SetupSingleScreen(self.screen)
                elif next_state == "MENU":
                    # Bấm Thoát
                    self.state = "MAIN_MENU"
                    self.current_screen = MainMenuScreen(self.screen)

            # --- VẼ GIAO DIỆN ---
            self.screen.fill(config.BG_COLOR)
            self.current_screen.render()

            pygame.display.flip()
            dt = self.clock.tick(config.FPS) / 1000.0