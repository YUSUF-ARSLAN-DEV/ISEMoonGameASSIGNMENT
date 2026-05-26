import os
import pygame
from data.gameSetting import (
    PLAYER_MAX_HEALTH, PLAYER_MAX_OXYGEN,
    WINDOW_WIDTH,
    WHITE, RED, CYAN, YELLOW, DARK_GRAY, BLACK,
)

_FONT_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', 'assests', 'sprites',
                 'SimplePixelArtUIpack', 'SimplePixelArtUIpack',
                 'fonts', 'font 1', 'pixelfont.ttf')
)

# Font cache — created lazily after pygame.init()
_fonts = {}


def _font(size, bold=False):
    """Return a pixel font at the given size (TTF if available, else Arial)."""
    key = (size, bold)
    if key not in _fonts:
        if os.path.exists(_FONT_PATH):
            try:
                _fonts[key] = pygame.font.Font(_FONT_PATH, size)
                return _fonts[key]
            except Exception:
                pass
        _fonts[key] = pygame.font.SysFont("Arial", size, bold=bold)
    return _fonts[key]


def draw_hud(surface, player, level_num):
    """
    Draw health hearts, oxygen bar, and level number.
    Call this last so the HUD is always on top of the scene.
    """
    # ── Health hearts ──────────────────────────────────────────────────────────
    for i in range(PLAYER_MAX_HEALTH):
        cx = 22 + i * 32
        cy = 22
        color = RED if i < player.health else DARK_GRAY
        # Heart shape — two arcs on top, V-point at bottom
        pygame.draw.polygon(surface, color, [
            (cx,      cy + 9),
            (cx - 11, cy + 1),
            (cx - 8,  cy - 7),
            (cx,      cy - 3),
            (cx + 8,  cy - 7),
            (cx + 11, cy + 1),
        ])

    # ── Oxygen bar ────────────────────────────────────────────────────────────
    bx, by = 22, 50
    bw, bh = 150, 13

    pygame.draw.rect(surface, DARK_GRAY, (bx - 1, by - 1, bw + 2, bh + 2))

    ratio    = player.oxygen / PLAYER_MAX_OXYGEN
    fill_w   = int(bw * ratio)
    bar_color = CYAN if ratio > 0.5 else (YELLOW if ratio > 0.25 else RED)
    if fill_w > 0:
        pygame.draw.rect(surface, bar_color, (bx, by, fill_w, bh))

    surface.blit(_font(12).render("O2", True, WHITE), (bx + bw + 6, by))

    # ── Level indicator ───────────────────────────────────────────────────────
    txt = _font(16, bold=True).render(f"LEVEL  {level_num}", True, WHITE)
    surface.blit(txt, (WINDOW_WIDTH - txt.get_width() - 12, 14))
