"""
pill_button.py
--------------
Candy-gradient style button with drop shadow and white border.

Shape: always full pill — border_radius = rect.height // 2 (fixed, not configurable).
Used in: win screens, single/dual player game screens.
"""

import pygame
from src.ui.components.base_button import Button


class PillButton(Button):
    """
    Candy-gradient pill button with drop shadow.

    Shape is always a true pill (border_radius = height // 2).
    The class enforces the shape; callers configure only colour and shadow.

    Args:
        color_top:    Top gradient colour.
        color_bot:    Bottom gradient colour.
        shadow_color: Drop shadow and text-shadow colour.
        shadow_offset: Vertical pixel offset for the drop shadow.
    """

    def __init__(
        self,
        rect,
        text: str,
        font,
        color_top=(255, 210, 130),
        color_bot=(255, 175, 85),
        shadow_color=(220, 140, 60),
        text_color=(255, 255, 255),
        shadow_offset: int = 5,
    ):
        super().__init__(rect, text, font, text_color=text_color)
        self.color_top    = color_top
        self.color_bot    = color_bot
        self.shadow_color = shadow_color
        self.shadow_offset = shadow_offset

    @property
    def border_radius(self) -> int:
        """Always full pill — derived from rect height, not a constructor param."""
        return self.rect.height // 2

    def draw(self, surface, mouse_pos=None) -> None:
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()

        rect   = self.rect
        radius = self.border_radius

        # ── Drop shadow ───────────────────────────────────────────────────────
        shad_rect = pygame.Rect(
            rect.x, rect.y + self.shadow_offset, rect.width, rect.height
        )
        shadow_color = self.shadow_color if self.enabled else (105, 105, 105)
        pygame.draw.rect(surface, shadow_color, shad_rect, border_radius=radius)

        # ── Vertical gradient fill ─────────────────────────────────────────────
        c_top = self.color_top
        c_bot = self.color_bot
        if not self.enabled:
            c_top = (185, 185, 185)
            c_bot = (145, 145, 145)
        elif rect.collidepoint(mouse_pos):          # lighten on hover
            c_top = tuple(min(255, c + 20) for c in c_top)
            c_bot = tuple(min(255, c + 20) for c in c_bot)

        grad = pygame.Surface((1, 2), pygame.SRCALPHA)
        grad.set_at((0, 0), c_top)
        grad.set_at((0, 1), c_bot)
        grad = pygame.transform.smoothscale(grad, (rect.width, rect.height))

        # Clip gradient to pill shape
        mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)
        grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(grad, rect.topleft)

        # ── White border ──────────────────────────────────────────────────────
        pygame.draw.rect(surface, (255, 255, 255), rect, border_radius=radius, width=2)

        # ── Label + text shadow ───────────────────────────────────────────────
        text_color = self.text_color if self.enabled else (235, 235, 235)
        label = self.font.render(self.text, True, text_color)
        shad  = self.font.render(self.text, True, shadow_color)
        label_rect = label.get_rect(center=rect.center)
        surface.blit(shad,  (label_rect.x, label_rect.y + 1))
        surface.blit(label, label_rect)
