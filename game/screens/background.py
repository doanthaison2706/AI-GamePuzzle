"""
Shared background renderer used by all pygame screens.
"""

from pathlib import Path

import pygame

from game.constants import BG_COLOR


_ASSET_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_BG_IMAGE = _ASSET_ROOT / "Gemini_Generated_Image_7aqi1n7aqi1n7aqi.png"


class ModernBackground:
    """Static shared background with image-first rendering."""

    def __init__(self, W: int, H: int, image_name: str | None = None):
        self.W, self.H = W, H
        self._fallback = self._build_fallback(W, H)
        self._background = self._load_background(W, H, image_name)

    @staticmethod
    def _build_fallback(W: int, H: int) -> pygame.Surface:
        surf = pygame.Surface((W, H))
        surf.fill(BG_COLOR)
        return surf

    @staticmethod
    def _load_background(W: int, H: int, image_name: str | None) -> pygame.Surface:
        if image_name:
            raw_path = Path(image_name)
            image_path = raw_path if raw_path.is_absolute() else _ASSET_ROOT / image_name
        else:
            image_path = _DEFAULT_BG_IMAGE
        if not image_path.exists():
            return ModernBackground._build_fallback(W, H)

        try:
            image = pygame.image.load(str(image_path)).convert()
        except pygame.error:
            return ModernBackground._build_fallback(W, H)

        return pygame.transform.smoothscale(image, (W, H))

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self._background, (0, 0))
