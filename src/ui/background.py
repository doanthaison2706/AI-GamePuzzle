"""
background.py
-------------
ModernBackground — animated floating-shape background used by all screens.
Draws a soft cream-to-white gradient and gently drifting translucent shapes
to create a bright, minimalist, and creative aesthetic.
"""

import math
import random
import pygame

from configs.game_config import BG_COLOR


class _FloatingShape:
    """A single translucent shape that drifts slowly across the background."""

    KINDS = ("circle", "rect", "triangle")

    def __init__(self, W: int, H: int):
        self.W, self.H = W, H
        self.kind = random.choice(self.KINDS)
        self.size = random.randint(30, 120)
        self.x = random.uniform(-self.size, W + self.size)
        self.y = random.uniform(-self.size, H + self.size)
        self.vx = random.uniform(-0.25, 0.25)
        self.vy = random.uniform(-0.15, 0.15)
        self.angle_speed = random.uniform(-0.3, 0.3)
        self.angle = random.uniform(0, 360)
        # Pastel palette — warm tones matching the design
        palettes = [
            (200, 220, 210),  # sage mist
            (220, 200, 180),  # warm sand
            (190, 210, 230),  # soft sky
            (230, 200, 195),  # blush
            (210, 220, 190),  # lime mist
            (220, 210, 230),  # lavender
        ]
        self.color = random.choice(palettes)
        self.alpha = random.randint(25, 55)
        self._phase = random.uniform(0, math.tau)

    def update(self) -> None:
        self.x += self.vx
        self.y += self.vy
        self.angle += self.angle_speed
        # Wrap around so shapes never disappear
        margin = self.size + 20
        if self.x < -margin:
            self.x = self.W + margin
        elif self.x > self.W + margin:
            self.x = -margin
        if self.y < -margin:
            self.y = self.H + margin
        elif self.y > self.H + margin:
            self.y = -margin

    def draw(self, target: pygame.Surface) -> None:
        s = self.size
        surf = pygame.Surface((s * 2, s * 2), pygame.SRCALPHA)

        if self.kind == "circle":
            pygame.draw.circle(surf, (*self.color, self.alpha), (s, s), s)
        elif self.kind == "rect":
            rect = pygame.Rect(s // 4, s // 4, int(s * 1.5), int(s * 1.5))
            pygame.draw.rect(surf, (*self.color, self.alpha), rect, border_radius=s // 5)
        elif self.kind == "triangle":
            cx, cy = s, s
            pts = []
            for i in range(3):
                a = math.radians(self.angle + i * 120)
                pts.append((cx + s * math.cos(a), cy + s * math.sin(a)))
            pygame.draw.polygon(surf, (*self.color, self.alpha), pts)

        target.blit(surf, (int(self.x) - s, int(self.y) - s))


class ModernBackground:
    """Animated background with a soft gradient and floating shapes."""

    NUM_SHAPES = 18

    def __init__(self, W: int, H: int):
        self.W, self.H = W, H
        self._shapes = [_FloatingShape(W, H) for _ in range(self.NUM_SHAPES)]
        self._gradient = self._build_gradient(W, H)

    # ------------------------------------------------------------------
    @staticmethod
    def _build_gradient(W: int, H: int) -> pygame.Surface:
        """Vertical gradient from BG_COLOR (top) to a slightly lighter shade (bottom)."""
        surf = pygame.Surface((W, H))
        top = BG_COLOR
        bot = (
            min(255, top[0] + 12),
            min(255, top[1] + 10),
            min(255, top[2] + 8),
        )
        for y in range(H):
            t = y / max(1, H - 1)
            r = int(top[0] + (bot[0] - top[0]) * t)
            g = int(top[1] + (bot[1] - top[1]) * t)
            b = int(top[2] + (bot[2] - top[2]) * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (W, y))
        return surf

    # ------------------------------------------------------------------
    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self._gradient, (0, 0))
        for shape in self._shapes:
            shape.update()
            shape.draw(screen)
