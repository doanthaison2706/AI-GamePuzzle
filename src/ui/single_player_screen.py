import pygame
from configs import game_config as config
from src.core.single_game_manager import SingleGameManager
from src.ui.renderer import Renderer
from src.ui.components import Button
from src.utils.image_crop import slice_image

class SinglePlayerScreen:
    def __init__(self, screen, setup_data):
        raise RuntimeError("Currently this UI is not compatible with the new Core Logic. This must be refactored later.")
        self.screen = screen
        self.renderer = Renderer(screen)

        self.size = setup_data["size"]
        self.full_image = setup_data["image"]
        self.image_slices = None

        # Băm ảnh nếu người dùng có up ảnh
        if self.full_image:
            _, self.image_slices = slice_image(self.full_image, config.BOARD_SIZE, self.size)

        self.gm = SingleGameManager(size=self.size)
        self.gm.new_game()
        self.show_full_image = False

        try:
            self.move_sound = pygame.mixer.Sound("assets/sounds/move.wav")
        except:
            self.move_sound = None

        # Setup Nút Gameplay
        btn_y = config.WINDOW_HEIGHT - 80
        btn_color, btn_hover = (100, 149, 237), (65, 105, 225)
        self.btn_new = Button(50, btn_y, 150, 40, "Xáo Trộn Lại", btn_color, btn_hover)
        self.btn_solve = Button(225, btn_y, 150, 40, "AI Giải", btn_color, btn_hover)
        self.btn_menu = Button(400, btn_y, 150, 40, "Về Menu", (231, 76, 60), (192, 57, 43))

    def handle_events(self, events):
        for event in events:
            # Xem ảnh gốc
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.show_full_image = True
            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                self.show_full_image = False

            if self.btn_new.handle_event(event): self.gm.new_game()
            if self.btn_solve.handle_event(event): pass # Giai đoạn 3 làm AI
            if self.btn_menu.handle_event(event): return "MENU"

            # Trượt gạch
            if self.gm.is_playing and not self.show_full_image:
                move_success = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    if config.MARGIN_LEFT <= mx <= config.MARGIN_LEFT + config.BOARD_SIZE and \
                       config.MARGIN_TOP <= my <= config.MARGIN_TOP + config.BOARD_SIZE:
                        t_size = config.BOARD_SIZE // self.gm.size
                        move_success = self.gm.process_move((my - config.MARGIN_TOP) // t_size, (mx - config.MARGIN_LEFT) // t_size)

                if event.type == pygame.KEYDOWN:
                    er, ec = self.gm.board.get_empty_pos()
                    tr, tc = er, ec
                    if event.key in (pygame.K_w, pygame.K_UP): tr -= 1
                    elif event.key in (pygame.K_s, pygame.K_DOWN): tr += 1
                    elif event.key in (pygame.K_a, pygame.K_LEFT): tc -= 1
                    elif event.key in (pygame.K_d, pygame.K_RIGHT): tc += 1
                    if (tr, tc) != (er, ec): move_success = self.gm.process_move(tr, tc)

                if move_success and self.move_sound: self.move_sound.play()

        return "PLAYING"

    def update(self):
        if self.gm: self.gm.update_time()

    def render(self):
        # Chữ hướng dẫn xem ảnh gốc
        hint = pygame.font.SysFont("arial", 16, italic=True).render("Giữ phím SPACE để xem ảnh gốc", True, (150, 150, 150))
        self.screen.blit(hint, (config.WINDOW_WIDTH//2 - hint.get_width()//2, 10))

        self.renderer.draw_ui(self.gm.move_count, self.gm.get_formatted_time(), self.gm.is_playing)
        self.renderer.draw_board(self.gm.board.matrix, self.gm.size, self.image_slices, self.full_image, self.show_full_image)

        self.btn_new.draw(self.screen)
        self.btn_solve.draw(self.screen)
        self.btn_menu.draw(self.screen)