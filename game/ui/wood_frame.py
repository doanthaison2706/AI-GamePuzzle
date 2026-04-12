import pygame


WOOD_DARK = (92, 58, 28)
WOOD_MID = (136, 88, 44)
WOOD_LIGHT = (184, 133, 78)
WOOD_SHADOW = (58, 34, 14)
PARCHMENT = (243, 232, 205)
PARCHMENT_SHADE = (222, 205, 171)
PARCHMENT_LINE = (166, 134, 92)


def draw_wood_frame(
    surface: pygame.Surface,
    content_rect: pygame.Rect,
    *,
    padding: int = 6,
    frame_width: int = 12,
    radius: int = 14,
) -> pygame.Rect:
    frame_rect = content_rect.inflate(
        (padding + frame_width) * 2,
        (padding + frame_width) * 2,
    )
    inner_rect = content_rect.inflate(padding * 2, padding * 2)

    pygame.draw.rect(
        surface,
        WOOD_SHADOW,
        frame_rect,
        border_radius=radius + frame_width + padding,
    )
    pygame.draw.rect(
        surface,
        WOOD_DARK,
        frame_rect.inflate(-4, -4),
        border_radius=radius + frame_width + padding - 2,
    )
    pygame.draw.rect(
        surface,
        WOOD_MID,
        frame_rect.inflate(-10, -10),
        border_radius=radius + frame_width + padding - 5,
    )
    pygame.draw.rect(
        surface,
        WOOD_LIGHT,
        inner_rect.inflate(frame_width * 2, frame_width * 2),
        width=3,
        border_radius=radius + frame_width,
    )
    pygame.draw.rect(
        surface,
        WOOD_SHADOW,
        inner_rect.inflate(frame_width, frame_width),
        width=2,
        border_radius=radius + frame_width - 2,
    )
    return frame_rect


def draw_wood_panel(
    surface: pygame.Surface,
    panel_rect: pygame.Rect,
    *,
    radius: int = 24,
    inset: int = 16,
) -> pygame.Rect:
    pygame.draw.rect(
        surface,
        WOOD_SHADOW,
        panel_rect.move(0, 4),
        border_radius=radius + 2,
    )
    pygame.draw.rect(surface, WOOD_DARK, panel_rect, border_radius=radius + 2)
    pygame.draw.rect(
        surface,
        WOOD_MID,
        panel_rect.inflate(-8, -8),
        border_radius=radius,
    )

    inner = panel_rect.inflate(-inset * 2, -inset * 2)
    pygame.draw.rect(surface, PARCHMENT_SHADE, inner, border_radius=max(10, radius - 10))
    pygame.draw.rect(
        surface,
        PARCHMENT,
        inner.inflate(-6, -6),
        border_radius=max(8, radius - 14),
    )
    pygame.draw.rect(
        surface,
        WOOD_LIGHT,
        panel_rect.inflate(-12, -12),
        width=2,
        border_radius=radius - 2,
    )
    pygame.draw.rect(
        surface,
        PARCHMENT_LINE,
        inner.inflate(-6, -6),
        width=1,
        border_radius=max(8, radius - 14),
    )
    return inner.inflate(-6, -6)


def draw_wood_plaque(
    surface: pygame.Surface,
    rect: pygame.Rect,
    *,
    radius: int = 18,
) -> None:
    pygame.draw.rect(surface, WOOD_SHADOW, rect.move(0, 3), border_radius=radius + 1)
    pygame.draw.rect(surface, WOOD_DARK, rect, border_radius=radius + 1)
    pygame.draw.rect(surface, WOOD_MID, rect.inflate(-6, -6), border_radius=radius)
    pygame.draw.rect(surface, WOOD_LIGHT, rect.inflate(-10, -10), width=2, border_radius=radius - 2)


def draw_status_badge(
    surface: pygame.Surface,
    rect: pygame.Rect,
    *,
    fill: tuple[int, int, int],
    border: tuple[int, int, int],
) -> None:
    pygame.draw.rect(surface, border, rect.move(0, 2), border_radius=rect.height // 2)
    pygame.draw.rect(surface, fill, rect, border_radius=rect.height // 2)
    pygame.draw.rect(surface, (255, 255, 255), rect.inflate(-8, -8), 1, border_radius=max(8, rect.height // 2 - 4))
