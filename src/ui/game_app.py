import pygame
import sys
from configs import game_config as config
from src.ui.menu_screen import MainMenuScreen
from src.ui.setup_screen import SetupSingleScreen
from src.ui.single_player_screen import SinglePlayerScreen
from src.ui.dual_player_screen import DualPlayerScreen
from src.ui.win_single_screen import WinSingleScreen
from src.ui.win_dual_screen import WinDualScreen


class GameApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.RESIZABLE
        )
        pygame.display.set_caption("N-Puzzle Arena")
        self.clock = pygame.time.Clock()

        self.state = "MAIN_MENU"
        self.current_screen = MainMenuScreen(self.screen)
        self.last_setup_data = None

    # ── helpers ───────────────────────────────────────────────────────────────

    def _go_menu(self):
        """Return to main menu, resetting window size."""
        pygame.display.set_mode(
            (config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.RESIZABLE
        )
        self.state = "MAIN_MENU"
        self.current_screen = MainMenuScreen(self.screen)

    def _go_setup(self, start_as_multi: bool = False):
        self.state = "SETUP"
        self.current_screen = SetupSingleScreen(self.screen, start_as_multi)

    def _go_play(self, setup_data: dict):
        """Launch the correct game screen based on data['multiplayer']."""
        self.last_setup_data = setup_data
        if setup_data and setup_data.get("multiplayer"):
            self.state = "PLAYING"
            self.current_screen = DualPlayerScreen(self.screen, setup_data)
        else:
            self.state = "PLAYING"
            self.current_screen = SinglePlayerScreen(self.screen, setup_data)

    def _go_win(self, result_data):
        """Go to the appropriate win screen."""
        is_multi = (self.last_setup_data or {}).get("multiplayer", False)
        self.state = "WIN"
        if is_multi:
            self.current_screen = WinDualScreen(self.screen, result_data)
        else:
            self.current_screen = WinSingleScreen(self.screen, result_data)

    # ── main loop ─────────────────────────────────────────────────────────────

    def run(self):
        dt = 0.0
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # ── MAIN_MENU ────────────────────────────────────────────────────
            if self.state == "MAIN_MENU":
                next_state, _ = self.current_screen.handle_events(events)
                if next_state == "SETUP":
                    self._go_setup()

            # ── SETUP (unified 1P + 2P) ──────────────────────────────────────
            elif self.state == "SETUP":
                next_state, setup_data = self.current_screen.handle_events(events)
                if next_state == "PLAYING":
                    self._go_play(setup_data)
                elif next_state == "MENU":
                    self._go_menu()

            # ── PLAYING (single or dual — determined by setup_data) ───────────
            elif self.state == "PLAYING":
                result = self.current_screen.handle_events(events)
                if isinstance(result, tuple):
                    next_state, result_data = result
                else:
                    next_state, result_data = result, None

                self.current_screen.update(dt)

                if next_state == "MENU":
                    self._go_menu()
                elif next_state in ("WIN_SINGLE", "WIN_DUAL"):
                    self._go_win(result_data)

            # ── WIN ───────────────────────────────────────────────────────────
            elif self.state == "WIN":
                next_state, _ = self.current_screen.handle_events(events)

                if next_state == "PLAYING":
                    self._go_play(self.last_setup_data)
                elif next_state in ("SETUP_SINGLE", "SETUP", "SETUP_MULTI"):
                    self._go_setup()
                elif next_state == "MENU":
                    self._go_menu()
                # PLAYING_DUAL from WinDualScreen — re-play dual
                elif next_state == "PLAYING_DUAL":
                    self._go_play(self.last_setup_data)

            # ── RENDER ───────────────────────────────────────────────────────
            self.current_screen.render()
            pygame.display.flip()
            dt = self.clock.tick(config.FPS) / 1000.0