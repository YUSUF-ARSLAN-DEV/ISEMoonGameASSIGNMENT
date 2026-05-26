import pygame
from data.gameSetting import (
    PLAYER_MAX_HEALTH, PLAYER_MAX_OXYGEN,
    WINDOW_WIDTH,
    WHITE, RED, CYAN, YELLOW, DARK_GRAY, BLACK,
)

# Font cache — created lazily after pygame.init()
_fonts = {}

def _font(size, bold=False):
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont("Arial", size, bold=bold)
    return _fonts[key]


def draw_hud(surface, player, level_num):
    """
    Draw health hearts, oxygen bar, and level number.
    Call this last so the HUD is always on top.
    """
    # ── Health hearts ──────────────────────────────────────────────────────────
    for i in range(PLAYER_MAX_HEALTH):
        cx = 22 + i * 32
        cy = 22
        color = RED if i < player.health else DARK_GRAY
        # Simple heart shape using two triangles
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

    # Background track
    pygame.draw.rect(surface, DARK_GRAY, (bx - 1, by - 1, bw + 2, bh + 2))

    # Filled portion
    ratio    = player.oxygen / PLAYER_MAX_OXYGEN
    fill_w   = int(bw * ratio)
    bar_color = CYAN if ratio > 0.5 else (YELLOW if ratio > 0.25 else RED)
    if fill_w > 0:
        pygame.draw.rect(surface, bar_color, (bx, by, fill_w, bh))

    # "O2" label next to bar
    surface.blit(_font(12).render("O2", True, WHITE), (bx + bw + 6, by))

    # ── Level indicator ───────────────────────────────────────────────────────
    txt = _font(16, bold=True).render(f"LEVEL  {level_num}", True, WHITE)
    surface.blit(txt, (WINDOW_WIDTH - txt.get_width() - 12, 14))
