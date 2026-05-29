import os
import pygame
import random
import math
from data.gameSetting import (
    TILE_SIZE, LEVEL_COLS, WINDOW_WIDTH, WINDOW_HEIGHT,
    LVL1_BG_COLOR, LVL1_TILE_COLOR, LVL1_TILE_ACCENT,
    LVL2_BG_COLOR, LVL2_TILE_COLOR, LVL2_TILE_ACCENT,
    LVL3_BG_COLOR, LVL3_TILE_COLOR, LVL3_TILE_ACCENT,
    WHITE, BLACK, CYAN, GREEN,
)

_CRATER_COLOR  = (62, 64,  76)
_ROCK_COLOR    = (108, 111, 125)
_SPIKE_COLOR   = (100, 104, 118)
_SPIKE_SHINE   = (160, 165, 180)

_tile_img_cache = {}


def _get_tile_img(level_num):
    return None


class Level:
    def __init__(self, tilemap, level_num):
        self.level_num = level_num
        self.tiles         = []
        self.trap_rects    = []
        self.oxygen_rects  = []
        self.exit_rect     = None
        self.player_spawn  = (TILE_SIZE, TILE_SIZE)
        self.enemy_spawns  = []
        self._surface_tile_details = {}

        if level_num == 1:
            self.bg_color    = LVL1_BG_COLOR
            self.tile_color  = LVL1_TILE_COLOR
            self.tile_accent = LVL1_TILE_ACCENT
        elif level_num == 2:
            self.bg_color    = LVL2_BG_COLOR
            self.tile_color  = LVL2_TILE_COLOR
            self.tile_accent = LVL2_TILE_ACCENT
        else:
            self.bg_color    = LVL3_BG_COLOR
            self.tile_color  = LVL3_TILE_COLOR
            self.tile_accent = LVL3_TILE_ACCENT

        rng = random.Random(level_num * 137)
        self.stars = [
            (rng.randint(0, LEVEL_COLS * TILE_SIZE), rng.randint(0, WINDOW_HEIGHT - 80))
            for _ in range(140)
        ]

        self._tile_img = _get_tile_img(level_num)
        self._parse(tilemap)
        if level_num in (1, 3):
            self._build_surface_details()

    def _parse(self, tilemap):
        for row_idx, row in enumerate(tilemap):
            row = row.ljust(LEVEL_COLS)
            for col_idx, cell in enumerate(row):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE

                if cell == 'X':
                    self.tiles.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                elif cell == 'T':
                    spike_h = int(TILE_SIZE * 0.6)
                    self.trap_rects.append(
                        pygame.Rect(x + 2, y, TILE_SIZE - 4, spike_h)
                    )
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

    def _build_surface_details(self):
        tile_set = {(t.x, t.y) for t in self.tiles}
        for tile in self.tiles:
            above = (tile.x, tile.y - TILE_SIZE)
            if above in tile_set:
                continue
            rng = random.Random(tile.x * 31 + tile.y * 17)
            n_craters = rng.randint(0, 2)
            craters = [
                (rng.randint(5, TILE_SIZE - 5), rng.randint(3, 10), rng.randint(2, 5))
                for _ in range(n_craters)
            ]
            n_rocks = rng.randint(1, 3)
            rocks = [
                (rng.randint(3, TILE_SIZE - 3), rng.randint(1, 3))
                for _ in range(n_rocks)
            ]
            self._surface_tile_details[(tile.x, tile.y)] = {
                'craters': craters,
                'rocks':   rocks,
            }

    def draw_background(self, surface, offset_x):
        surface.fill(self.bg_color)

        for sx, sy in self.stars:
            screen_x = int(sx - offset_x * 0.3) % WINDOW_WIDTH
            pygame.draw.circle(surface, WHITE, (screen_x, sy), 1)

        if self.level_num == 1:
            earth_x = int(660 - offset_x * 0.05)
            pygame.draw.circle(surface, (28, 68, 180), (earth_x, 95), 68)
            pygame.draw.circle(surface, (38, 115, 55), (earth_x - 22, 75), 28)
            pygame.draw.circle(surface, (38, 115, 55), (earth_x + 28, 105), 18)
            pygame.draw.circle(surface, (60, 100, 200), (earth_x, 95), 70, 3)
        else:
            glow = pygame.Surface((WINDOW_WIDTH, 90), pygame.SRCALPHA)
            glow.fill((80, 35, 130, 18))
            surface.blit(glow, (0, WINDOW_HEIGHT - 90))

    def draw_tiles(self, surface, offset_x):
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

                if self.level_num in (1, 3):
                    details = self._surface_tile_details.get((tile.x, tile.y))
                    if details:
                        for (dx, dy, r) in details['craters']:
                            pygame.draw.circle(surface, _CRATER_COLOR,
                                               (sr.x + dx, sr.y + dy), r)
                            pygame.draw.circle(surface, self.tile_accent,
                                               (sr.x + dx, sr.y + dy), r, 1)
                        for (dx, dy) in details['rocks']:
                            pygame.draw.circle(surface, _ROCK_COLOR,
                                               (sr.x + dx, sr.y), dy + 2)
                    rng = random.Random(tile.x * 7 + tile.y * 3)
                    for _ in range(3):
                        gx = sr.x + rng.randint(2, TILE_SIZE - 2)
                        gy = sr.y + rng.randint(6, TILE_SIZE - 4)
                        pygame.draw.circle(surface, self.tile_accent, (gx, gy), 1)
                else:
                    cx = sr.x + 10
                    pygame.draw.line(surface, self.tile_accent,
                                     (cx, sr.y + 8), (cx + 12, sr.y + 20), 1)

    def draw_traps(self, surface, offset_x):
        for trap in self.trap_rects:
            sx = trap.x - offset_x
            if not (-TILE_SIZE < sx < WINDOW_WIDTH + TILE_SIZE):
                continue
            base_y = trap.y + trap.height
            n_spikes = 3
            spike_w  = trap.width // n_spikes
            for i in range(n_spikes):
                x0 = int(sx) + i * spike_w
                x1 = x0 + spike_w
                tip_x = x0 + spike_w // 2
                tip_y = trap.y
                pygame.draw.polygon(surface, _SPIKE_COLOR, [
                    (x0, base_y), (x1, base_y), (tip_x, tip_y)
                ])
                pygame.draw.line(surface, _SPIKE_SHINE,
                                 (tip_x, tip_y), (x0, base_y), 1)

    def draw_darkness(self, surface, light_x, light_y):
        if self.level_num != 2:
            return

        dark = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        dark.fill((0, 0, 0, 255))

        glow = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        glow.fill((0, 0, 0, 255))
        for radius, alpha in [(280, 255), (220, 210), (160, 150), (100, 70), (50, 0)]:
            pygame.draw.circle(glow, (0, 0, 0, alpha), (light_x, light_y), radius)

        dark.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surface.blit(dark, (0, 0))

    def draw_items(self, surface, offset_x, elapsed):
        for oxy in self.oxygen_rects:
            sx = oxy.x - offset_x
            if not (-60 < sx < WINDOW_WIDTH + 60):
                continue

            pulse  = int(10 * abs(math.sin(elapsed * 3.0)))
            radius = 22 + pulse
            glow   = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (0, 200, 255, 45), (radius, radius), radius)
            surface.blit(glow, (int(sx + oxy.width // 2 - radius),
                                oxy.y + oxy.height // 2 - radius))

            body = pygame.Rect(int(sx), oxy.y, oxy.width, oxy.height)
            pygame.draw.rect(surface, CYAN,  body, border_radius=5)
            pygame.draw.rect(surface, WHITE, body, 1, border_radius=5)

        if self.exit_rect:
            sx = self.exit_rect.x - offset_x
            if not (-80 < sx < WINDOW_WIDTH + 80):
                return

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
