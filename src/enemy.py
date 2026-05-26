import os
import pygame
from data.gameSetting import (
    ENEMY_SPEED, ENEMY_PATROL,
    GRAVITY, TERMINAL_VEL,
    WHITE, BLACK, RED,
)

_SPRITE_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', 'assests', 'sprites',
                 'Pixel_crab_byBrysia', 'Animation sprites')
)

_SCALE = 2   # 32 × 32 raw → 64 × 64 on screen


def _load_crab_sheet(filename):
    """
    Load a crab sprite sheet (32 px tall, N×32 wide) and return scaled frames.
    Returns None if the file is missing or fails to load.
    """
    path = os.path.join(_SPRITE_DIR, filename)
    if not os.path.exists(path):
        return None
    try:
        sheet  = pygame.image.load(path).convert_alpha()
        sw, sh = sheet.get_size()
        frame_h = sh                    # always 32
        frame_w = frame_h               # frames are square
        cols    = sw // frame_w
        frames  = []
        for col in range(cols):
            raw    = sheet.subsurface(pygame.Rect(col * frame_w, 0, frame_w, frame_h))
            scaled = pygame.transform.scale(raw, (frame_w * _SCALE, frame_h * _SCALE))
            frames.append(scaled)
        return frames
    except Exception:
        return None


class Enemy(pygame.sprite.Sprite):
    """
    Moon crab that patrols left/right and chases the player when nearby.

    Behaviour
    ---------
    - Patrols within ENEMY_PATROL pixels of its spawn point.
    - Switches to chase mode when the player comes within SIGHT_RANGE pixels.
    - Falls with gravity so it lands naturally on any tile.
    - Reverses direction on hitting a wall tile.
    - Dies when the player stomps it from above (handled in Main.py).
    - Damages the player on lateral contact (handled in Main.py).

    Animation
    ---------
    Uses real crab sprite sheets when available; falls back to procedural drawing.
    Sheet layout: each sheet is N×32 pixels; each frame is 32×32, scaled ×2 to 64×64.
        crab_idle.png    128×32 → 4 frames
        crab_walk1.png   128×32 → 4 frames
        crab_damage.png   96×32 → 3 frames
        crab_death.png   128×32 → 4 frames
    """

    SIGHT_RANGE = 200   # px: distance at which the enemy notices the player

    def __init__(self, x, y, groups):
        super().__init__(groups)

        self._frames = {
            'idle':  _load_crab_sheet('crab_idle.png'),
            'walk':  _load_crab_sheet('crab_walk1.png'),
            'hurt':  _load_crab_sheet('crab_damage.png'),
            'dead':  _load_crab_sheet('crab_death.png'),
        }
        self._use_sprites = any(v is not None for v in self._frames.values())

        if self._use_sprites:
            self.WIDTH  = 32 * _SCALE   # 64
            self.HEIGHT = 32 * _SCALE   # 64
        else:
            self.WIDTH  = 30
            self.HEIGHT = 34

        self.image = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        self.rect  = self.image.get_rect(topleft=(x, y))

        self.spawn_x      = x
        self.vx           = float(ENEMY_SPEED)
        self.vy           = 0.0
        self.on_ground    = False
        self.alive_flag   = True

        self.anim_timer   = 0.0
        self.anim_frame   = 0
        self._state       = 'idle'
        self._facing_right = True

        self._draw()

    # ── Drawing ───────────────────────────────────────────────────────────────

    def _draw(self):
        self.image.fill((0, 0, 0, 0))

        if self._use_sprites:
            frames = self._frames.get(self._state) or self._frames.get('idle')
            if frames:
                idx   = self.anim_frame % len(frames)
                frame = frames[idx]
                if not self._facing_right:
                    frame = pygame.transform.flip(frame, True, False)
                self.image.blit(frame, (0, 0))
            return

        # ── Fallback: procedural alien ────────────────────────────────────────
        body_color = (200, 45, 45) if self.anim_frame % 2 == 0 else (180, 35, 35)
        cx = self.WIDTH // 2

        pygame.draw.ellipse(self.image, body_color,
                            (3, 12, self.WIDTH - 6, self.HEIGHT - 12))
        pygame.draw.circle(self.image, (225, 75, 75), (cx, 10), 10)

        for ex in (cx - 4, cx + 4):
            pygame.draw.circle(self.image, WHITE,        (ex, 9), 3)
            pygame.draw.circle(self.image, (0, 210, 230),(ex, 9), 2)
            pygame.draw.circle(self.image, BLACK,        (ex, 9), 1)

        pygame.draw.line(self.image, (230, 100, 100), (cx - 4, 1), (cx - 8, -5), 2)
        pygame.draw.line(self.image, (230, 100, 100), (cx + 4, 1), (cx + 8, -5), 2)

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt, tiles, player_rect):
        """
        dt          — seconds since last frame
        tiles       — list of solid tile Rects for collision
        player_rect — player's world-space Rect (used for chase AI)
        """
        if not self.alive_flag:
            return

        # ── AI ────────────────────────────────────────────────────────────────
        dx_to_player = player_rect.centerx - self.rect.centerx
        if abs(dx_to_player) < self.SIGHT_RANGE:
            # Chase: run toward player
            self.vx    = ENEMY_SPEED if dx_to_player > 0 else -ENEMY_SPEED
            self._state = 'walk'
        else:
            # Patrol: reverse when strayed too far from spawn
            if abs(self.rect.x - self.spawn_x) > ENEMY_PATROL:
                self.vx = -self.vx
            self._state = 'walk'

        self._facing_right = self.vx > 0

        # ── Gravity ───────────────────────────────────────────────────────────
        self.vy += GRAVITY * dt
        self.vy  = min(self.vy, TERMINAL_VEL)

        # ── Horizontal movement + collision ───────────────────────────────────
        self.rect.x += int(self.vx * dt)
        for tile in tiles:
            if self.rect.colliderect(tile):
                if self.vx > 0:
                    self.rect.right = tile.left
                    self.vx = -self.vx
                elif self.vx < 0:
                    self.rect.left  = tile.right
                    self.vx = -self.vx

        # ── Vertical movement + collision ─────────────────────────────────────
        self.on_ground = False
        self.rect.y   += int(self.vy * dt)
        for tile in tiles:
            if self.rect.colliderect(tile):
                if self.vy > 0:
                    self.rect.bottom = tile.top
                    self.on_ground   = True
                    self.vy          = 0.0
                elif self.vy < 0:
                    self.rect.top = tile.bottom
                    self.vy       = 0.0

        # ── Animation tick ────────────────────────────────────────────────────
        self.anim_timer += dt
        if self.anim_timer >= 0.15:
            self.anim_frame += 1
            self.anim_timer  = 0.0
            self._draw()
