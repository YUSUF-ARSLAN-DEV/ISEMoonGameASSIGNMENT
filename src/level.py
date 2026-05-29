import os
import pygame
import random
import math
from data.gameSetting import (
    TILE_SIZE, LEVEL_COLS, WINDOW_WIDTH, WINDOW_HEIGHT,
    LVL1_BG_COLOR, LVL1_TILE_COLOR, LVL1_TILE_ACCENT,
    LVL2_BG_COLOR, LVL2_TILE_COLOR, LVL2_TILE_ACCENT,
    WHITE, BLACK, CYAN, GREEN,
)

# Tile sprite cache — loaded on first use
_tile_img_cache = {}


def _get_tile_img(level_num):
    return None


class Level:
    """
    Loads a level from a string-grid tilemap and handles all rendering.

    After __init__:
        self.tiles        — list of solid pygame.Rect
        self.oxygen_rects — list of pygame.Rect for oxygen pickups
        self.exit_rect    — pygame.Rect for the exit portal (or None)
        self.player_spawn — (x, y) tuple
        self.enemy_spawns — list of (x, y) tuples
    """

    def __init__(self, tilemap, level_num):
        self.level_num = level_num
        self.tiles         = []
        self.oxygen_rects  = []
        self.exit_rect     = None
        self.player_spawn  = (TILE_SIZE, TILE_SIZE)
        self.enemy_spawns  = []

        if level_num == 1:
            self.bg_color    = LVL1_BG_COLOR
            self.tile_color  = LVL1_TILE_COLOR
            self.tile_accent = LVL1_TILE_ACCENT
        else:
            self.bg_color    = LVL2_BG_COLOR
            self.tile_color  = LVL2_TILE_COLOR
            self.tile_accent = LVL2_TILE_ACCENT

        # Deterministic star field
        rng = random.Random(level_num * 137)
        self.stars = [
            (rng.randint(0, LEVEL_COLS * TILE_SIZE), rng.randint(0, WINDOW_HEIGHT - 80))
            for _ in range(140)
        ]

        # Pre-load tile texture for this level
        self._tile_img = _get_tile_img(level_num)

        self._parse(tilemap)

    # ── Parsing ───────────────────────────────────────────────────────────────

    def _parse(self, tilemap):
        for row_idx, row in enumerate(tilemap):
            row = row.ljust(LEVEL_COLS)
            for col_idx, cell in enumerate(row):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE

                if cell == 'X':
                    self.tiles.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                elif cell == 'P':
                    self.player_spawn = (x, y)
                elif cell == 'E':
                    self.enemy_spawns.append((x, y))
                elif cell == 'O':
                    margin = 8
                    self.oxygen_rects.append(
                        pygame.Rect(x + margin, y + margin,
                                    TILE_SIZE - margin * 2, TILE_SIZE - margin * 2)
                    )
                elif cell == '>':
                    self.exit_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

    # ── Rendering ─────────────────────────────────────────────────────────────

    def draw_background(self, surface, offset_x):
        """
        Fill background with moon-themed scenery.
        Stars use parallax scrolling (30 % of camera speed).
        """
        surface.fill(self.bg_color)

        for sx, sy in self.stars:
            screen_x = int(sx - offset_x * 0.3) % WINDOW_WIDTH
            pygame.draw.circle(surface, WHITE, (screen_x, sy), 1)

        if self.level_num == 1:
            # Earth in the sky with atmosphere ring
            earth_x = int(660 - offset_x * 0.05)
            pygame.draw.circle(surface, (28, 68, 180), (earth_x, 95), 68)
            pygame.draw.circle(surface, (38, 115, 55), (earth_x - 22, 75), 28)
            pygame.draw.circle(surface, (38, 115, 55), (earth_x + 28, 105), 18)
            pygame.draw.circle(surface, (60, 100, 200), (earth_x, 95), 70, 3)
        else:
            # Lunar cavern: subtle purple glow
            glow = pygame.Surface((WINDOW_WIDTH, 90), pygame.SRCALPHA)
            glow.fill((80, 35, 130, 18))
            surface.blit(glow, (0, WINDOW_HEIGHT - 90))

    def draw_tiles(self, surface, offset_x):
        """
        Render only tiles currently on screen (culled for performance).
        Uses the maze wall texture when available; falls back to flat color.
        """
        for tile in self.tiles:
            sx = tile.x - offset_x
            if not (-TILE_SIZE < sx < WINDOW_WIDTH + TILE_SIZE):
                continue
            sr = pygame.Rect(int(sx), tile.y, tile.width, tile.height)

            if self._tile_img is not None:
                surface.blit(self._tile_img, sr.topleft)
                pygame.draw.line(surface, self.tile_accent, sr.topleft, sr.topright, 2)
            else:
                pygame.draw.rect(surface, self.tile_color, sr)
                pygame.draw.line(surface, self.tile_accent, sr.topleft, sr.topright, 2)
                # Small crack detail
                cx = sr.x + 10
                pygame.draw.line(surface, self.tile_accent,
                                 (cx, sr.y + 8), (cx + 12, sr.y + 20), 1)

    def draw_darkness(self, surface, light_x, light_y):
        """
        Lunar cavern darkness overlay — Level 2 only.

        Creates a torch-light special effect: the screen is mostly dark except
        for a radial gradient centred on the player.  Built by layering an
        SRCALPHA surface (filled solid dark) and using BLEND_RGBA_MIN to carve
        out a transparent "light cone" — pixels closest to the player become
        fully transparent, letting the scene show through.
        """
        if self.level_num != 2:
            return

        # Pitch-black overlay — fully opaque so nothing leaks through
        dark = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        dark.fill((0, 0, 0, 255))

        # Glow surface: filled fully opaque outside, circles carve alpha toward
        # zero at the centre.  BLEND_RGBA_MIN keeps the minimum alpha at each
        # pixel, so only the carved-out light cone becomes transparent on 'dark'.
        glow = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        glow.fill((0, 0, 0, 255))   # fully opaque everywhere by default
        for radius, alpha in [(280, 255), (220, 210), (160, 150), (100, 70), (50, 0)]:
            pygame.draw.circle(glow, (0, 0, 0, alpha), (light_x, light_y), radius)

        # After BLEND_RGBA_MIN:
        #   outside 280 px → min(255,255)=255 → black (fully dark)
        #   at 160 px      → min(255,150)=150 → partially transparent (dim)
        #   within 50 px   → min(255,0)=0     → fully transparent (lit)
        dark.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surface.blit(dark, (0, 0))

    def draw_items(self, surface, offset_x, elapsed):
        """
        Draw oxygen canisters and the exit portal with glowing effects.
        elapsed — total seconds since game start (drives pulse animations).
        """
        # ── Oxygen canisters ──────────────────────────────────────────────────
        for oxy in self.oxygen_rects:
            sx = oxy.x - offset_x
            if not (-60 < sx < WINDOW_WIDTH + 60):
                continue

            # Pulsing glow ring (glowing canister special effect)
            pulse  = int(10 * abs(math.sin(elapsed * 3.0)))
            radius = 22 + pulse
            glow   = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (0, 200, 255, 45), (radius, radius), radius)
            surface.blit(glow, (int(sx + oxy.width // 2 - radius),
                                oxy.y + oxy.height // 2 - radius))

            body = pygame.Rect(int(sx), oxy.y, oxy.width, oxy.height)
            pygame.draw.rect(surface, CYAN,  body, border_radius=5)
            pygame.draw.rect(surface, WHITE, body, 1, border_radius=5)

        # ── Exit portal ───────────────────────────────────────────────────────
        if self.exit_rect:
            sx = self.exit_rect.x - offset_x
            if not (-80 < sx < WINDOW_WIDTH + 80):
                return

            # Expanding glow ring (portal activation special effect)
            pulse  = int(18 * abs(math.sin(elapsed * 2.0)))
            radius = 28 + pulse
            glow   = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (50, 255, 100, 55), (radius, radius), radius)
            surface.blit(glow, (int(sx + self.exit_rect.width  // 2 - radius),
                                self.exit_rect.y + self.exit_rect.height // 2 - radius))

            pr = pygame.Rect(int(sx), self.exit_rect.y,
                             self.exit_rect.width, self.exit_rect.height)
            pygame.draw.rect(surface, GREEN, pr, border_radius=5)
            pygame.draw.rect(surface, WHITE, pr, 2, border_radius=5)

            font = pygame.font.SysFont("Arial", 11, bold=True)
            txt  = font.render("EXIT", True, BLACK)
            surface.blit(txt, (pr.x + (pr.width - txt.get_width()) // 2,
                               pr.y + (pr.height - txt.get_height()) // 2))
