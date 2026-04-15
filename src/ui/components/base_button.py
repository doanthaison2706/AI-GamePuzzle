"""
base_button.py
--------------
Abstract base for all interactive buttons in the game.

Handles state (hover / held) and event detection only.
Rendering is fully delegated to concrete subclasses.
"""

import pygame


class Button:
    """
    Base clickable button.

    Subclasses must implement ``draw()``.
    Common state managed here:
      - rect, text, font, text_color
      - _held flag for press-and-release click detection
    """

    def __init__(self, rect, text: str, font, text_color=(255, 255, 255)):
        self.rect       = pygame.Rect(rect)
        self.text       = text
        self.font       = font
        self.text_color = text_color
        self._held      = False
        self.enabled    = True

    # ── Public API ────────────────────────────────────────────────────────────

    def handle_event(self, event) -> bool:
        """
        Feed a single pygame event.
        Returns True on the frame the button is released (clicked).
        """
        if not self.enabled:
            self._held = False
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._held = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._held and self.rect.collidepoint(event.pos):
                self._held = False
                return True
            self._held = False
        return False

    def draw(self, surface, mouse_pos=None) -> None:
        raise NotImplementedError(f"{type(self).__name__} must implement draw()")
