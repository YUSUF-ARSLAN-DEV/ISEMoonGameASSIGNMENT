import pygame
from data.gameSetting import (
    ENEMY_SPEED, ENEMY_PATROL,
    GRAVITY, TERMINAL_VEL,
    WHITE, BLACK, RED,
)


class Enemy(pygame.sprite.Sprite):
    """
    Moon alien that patrols left/right and chases the player when nearby.

    Behaviour
    ---------
    - Patrols within ENEMY_PATROL pixels of its spawn point.
    - Switches to chase mode when the player comes within SIGHT_RANGE pixels.
    - Falls with gravity so it lands naturally on any tile.
    - Reverses direction on hitting a wall tile.
    - Dies when the player stomps it from above (handled in Main.py).
    - Damages the player on lateral contact (handled in Main.py).
    """

    WIDTH       = 30
    HEIGHT      = 34
    SIGHT_RANGE = 200   # px: distance at which the enemy notices the player

    def __init__(self, x, y, groups):
        super().__init__(groups)
        self.image = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        self.rect  = self.image.get_rect(topleft=(x, y))

        self.spawn_x    = x
        self.vx         = ENEMY_SPEED   # current horizontal speed
        self.vy         = 0.0           # vertical speed (gravity)
        self.on_ground  = False
        self.alive_flag = True

        # Animation
        self.anim_timer = 0.0
        self.anim_frame = 0

        self._draw()

    # ── Drawing ───────────────────────────────────────────────────────────────

    def _draw(self):
        """Draw a simple alien: oval body, round head, glowing eyes."""
        self.image.fill((0, 0, 0, 0))

        # Body — wobbles slightly on alt frames
        body_color  = (200, 45, 45) if self.anim_frame % 2 == 0 else (180, 35, 35)
        head_color  = (225, 75, 75)
        cx = self.WIDTH // 2

        # Body
        pygame.draw.ellipse(self.image, body_color,
                            (3, 12, self.WIDTH - 6, self.HEIGHT - 12))
        # Head
        pygame.draw.circle(self.image, head_color, (cx, 10), 10)

        # Eyes (white sclera + dark pupil + cyan glow)
        for ex in (cx - 4, cx + 4):
            pygame.draw.circle(self.image, WHITE,        (ex, 9), 3)
            pygame.draw.circle(self.image, (0, 210, 230),(ex, 9), 2)
            pygame.draw.circle(self.image, BLACK,        (ex, 9), 1)

        # Antennae
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
            self.vx = ENEMY_SPEED if dx_to_player > 0 else -ENEMY_SPEED
        else:
            # Patrol: reverse when we've walked far enough from spawn
            if abs(self.rect.x - self.spawn_x) > ENEMY_PATROL:
                self.vx = -self.vx

        # ── Gravity ───────────────────────────────────────────────────────────
        self.vy += GRAVITY * dt
        self.vy  = min(self.vy, TERMINAL_VEL)

        # ── Horizontal movement + collision ───────────────────────────────────
        self.rect.x += int(self.vx * dt)
        for tile in tiles:
            if self.rect.colliderect(tile):
                if self.vx > 0:
                    self.rect.right = tile.left
                    self.vx = -self.vx    # bounce back
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
        if self.anim_timer >= 0.28:
            self.anim_frame += 1
            self.anim_timer  = 0.0
            self._draw()
