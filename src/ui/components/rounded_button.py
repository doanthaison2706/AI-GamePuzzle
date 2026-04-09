"""
rounded_button.py
-----------------
Neon-glow style button with fixed rounded-corner shape.

Shape: always border_radius = BORDER_RADIUS (class constant, not configurable).
Used in: main menu, setup screen.
"""

import pygame
from configs.game_config import BTN_COLOR, BTN_HOVER, BTN_ACTIVE, BTN_TEXT
from src.ui.components.base_button import Button


class RoundedButton(Button):
    """
    Rounded-corner button with neon glow border effect.

    Corner radius is fixed at BORDER_RADIUS — shape is defined by the class,
    not by the caller.
    """

    BORDER_RADIUS: int = 8

    def __init__(
        self,
        rect,
        text: str,
        font,
        color=None,
        hover_color=None,
        active_color=None,
        text_color=None,
    ):
        super().__init__(
            rect, text, font,
            text_color=text_color if text_color is not None else BTN_TEXT,
        )
        self.color        = color        if color        is not None else BTN_COLOR
        self.hover_color  = hover_color  if hover_color  is not None else BTN_HOVER
        self.active_color = active_color if active_color is not None else BTN_ACTIVE

    def draw(self, surface, mouse_pos=None) -> None:
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()

        hovered = self.rect.collidepoint(mouse_pos)
        if self._held and hovered:
            bg = self.active_color
        elif hovered:
            bg = self.hover_color
        else:
            bg = self.color

        r = self.BORDER_RADIUS

        # Outer neon glow ring (2 px, brighter tint)
        glow_color = tuple(min(255, int(c * 1.6)) for c in bg)
        pygame.draw.rect(surface, glow_color, self.rect.inflate(4, 4), 2,
                         border_radius=r + 2)

        # Fill
        pygame.draw.rect(surface, bg, self.rect, border_radius=r)

        # Inner highlight rim
        pygame.draw.rect(surface, (255, 255, 255, 30), self.rect, 1, border_radius=r)

        # Label
        label = self.font.render(self.text, True, self.text_color)
        surface.blit(label, label.get_rect(center=self.rect.center))
