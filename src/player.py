import os
import pygame
from data.gameSetting import (
    PLAYER_WIDTH, PLAYER_HEIGHT,
    PLAYER_MAX_HEALTH, PLAYER_MAX_OXYGEN,
    OXYGEN_DRAIN_RATE, OXYGEN_REFILL_AMT,
    PLAYER_SPEED, JUMP_VELOCITY, GRAVITY, TERMINAL_VEL,
    INVINCIBLE_DURATION,
    WHITE, BLACK, RED, CYAN,
)

_SPRITE_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', 'assests', 'sprites', 'astronaut_v1.2')
)

FRAME_SIZE = 64  # every frame in the sprite sheets is 64 × 64 px


def _load_sheet(filename, cols, rows):
    """
    Slice a sprite sheet into a list of 64×64 surfaces.
    Returns None if the file is missing or fails to load.
    """
    path = os.path.join(_SPRITE_DIR, filename)
    if not os.path.exists(path):
        return None
    try:
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        for row in range(rows):
            for col in range(cols):
                frame = sheet.subsurface(
                    pygame.Rect(col * FRAME_SIZE, row * FRAME_SIZE,
                                FRAME_SIZE, FRAME_SIZE)
                )
                frames.append(frame)
        return frames
    except Exception:
        return None


class Player(pygame.sprite.Sprite):
    """
    Moon astronaut controlled by arrow keys / WASD.

    Physics
    -------
    All movement uses delta time (dt) so behaviour is frame-rate independent.
    Horizontal and vertical axes are resolved separately for clean corners.

    Oxygen system
    -------------
    Oxygen depletes at OXYGEN_DRAIN_RATE units/s.  Pickups refill it.

    Animation
    ---------
    Loads real sprite sheets when available; falls back to procedural drawing.
    Sheet dimensions (64 px per frame):
        idle_breath(64,64).png  4 cols × 3 rows = 12 frames
        idle_walk(64,64).png    4 cols × 4 rows = 16 frames
        idle_jump(64,64).png    3 cols × 3 rows =  9 frames
        idle_hurt(64,64).png    3 cols × 2 rows =  6 frames
        idle_dead(64,64).png    4 cols × 3 rows = 12 frames
    """

    def __init__(self, pos, groups):
        super().__init__(groups)

        # Load sprite sheets
        self._frames = {
            'idle': _load_sheet('idle_breath(64,64).png', 4, 3),
            'walk': _load_sheet('idle_walk(64,64).png',   4, 4),
            'jump': _load_sheet('idle_jump(64,64).png',   3, 3),
            'hurt': _load_sheet('idle_hurt(64,64).png',   3, 2),
            'dead': _load_sheet('idle_dead(64,64).png',   4, 3),
        }
        self._use_sprites = any(v is not None for v in self._frames.values())

        # Use 64×64 when sprites are available; fall back to original hitbox
        w = FRAME_SIZE   if self._use_sprites else PLAYER_WIDTH
        h = FRAME_SIZE   if self._use_sprites else PLAYER_HEIGHT

        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self.rect  = self.image.get_rect(topleft=pos)

        # Physics state
        self.vx              = 0.0
        self.vy              = 0.0
        self.on_ground       = False
        self._prev_on_ground = False
        self._just_jumped    = False

        # Game stats
        self.health = PLAYER_MAX_HEALTH
        self.oxygen = PLAYER_MAX_OXYGEN
        self.alive  = True

        # Invincibility frames after taking damage
        self.invincible       = False
        self.invincible_timer = 0.0

        # Animation
        self.state        = 'idle'
        self.anim_frame   = 0
        self.anim_timer   = 0.0
        self.facing_right = True

        self._draw()

    # ── Drawing ───────────────────────────────────────────────────────────────

    def _draw(self):
        """Refresh self.image from the current animation frame."""
        self.image.fill((0, 0, 0, 0))

        # Flicker rapidly during invincibility frames
        if self.invincible and int(self.invincible_timer * 10) % 2 == 0:
            return

        if self._use_sprites:
            state  = 'dead' if not self.alive else self.state
            frames = self._frames.get(state) or self._frames.get('idle')
            if frames:
                idx   = self.anim_frame % len(frames)
                frame = frames[idx]
                if not self.facing_right:
                    frame = pygame.transform.flip(frame, True, False)
                self.image.blit(frame, (0, 0))
            return

        # ── Fallback: procedural astronaut ────────────────────────────────────
        cx     = PLAYER_WIDTH // 2
        suit   = (175, 178, 198)
        helmet = (215, 230, 255)
        visor  = (70,  155, 225)
        pack   = (95,  98,  118)

        leg_bob = (3 if self.anim_frame % 2 == 0 else -3) if self.state == 'walk' else 0
        pygame.draw.rect(self.image, suit, (cx - 10, PLAYER_HEIGHT - 14,      8, 13))
        pygame.draw.rect(self.image, suit, (cx + 2,  PLAYER_HEIGHT - 14 + leg_bob, 8, 13))
        pygame.draw.rect(self.image, suit, (cx - 12, 14, 24, 18), border_radius=3)
        pygame.draw.rect(self.image, pack, (cx + 10, 15,  5, 13), border_radius=2)
        pygame.draw.circle(self.image, helmet, (cx, 10), 11)
        pygame.draw.ellipse(self.image, visor, (cx - 6, 5, 13, 8))

        if self.state == 'hurt':
            tint = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
            tint.fill((255, 0, 0, 90))
            self.image.blit(tint, (0, 0))

    # ── Public API ────────────────────────────────────────────────────────────

    def update(self, dt, tiles):
        """
        Called every frame.
        dt    — seconds since the last frame
        tiles — list of pygame.Rect for solid platforms/walls
        """
        self._prev_on_ground = self.on_ground
        self._just_jumped    = False

        # Input
        keys = pygame.key.get_pressed()
        self.vx = 0.0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
            self.vx = -PLAYER_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx =  PLAYER_SPEED
            self.facing_right = True
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) \
                and self.on_ground:
            self.vy            = JUMP_VELOCITY
            self.on_ground     = False
            self._just_jumped  = True

        # Gravity
        self.vy += GRAVITY * dt
        self.vy  = min(self.vy, TERMINAL_VEL)

        # Horizontal move → resolve X collisions
        self.rect.x += int(self.vx * dt)
        self._collide_x(tiles)

        # Vertical move → resolve Y collisions
        self.on_ground = False
        self.rect.y   += int(self.vy * dt)
        self._collide_y(tiles)

        # Oxygen drains continuously
        self.oxygen -= OXYGEN_DRAIN_RATE * dt
        self.oxygen  = max(0.0, self.oxygen)
        if self.oxygen == 0:
            self.take_damage()

        # Count down invincibility
        if self.invincible:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.invincible = False

        # Advance animation
        self._update_state()
        self.anim_timer += dt
        if self.anim_timer >= 0.10:
            self.anim_frame += 1
            self.anim_timer  = 0.0
        self._draw()

    @property
    def just_landed(self):
        """True only on the exact frame the player touches ground."""
        return self.on_ground and not self._prev_on_ground

    @property
    def just_jumped(self):
        """True only on the exact frame the player leaves the ground by jumping."""
        return self._just_jumped

    def take_damage(self):
        """
        Subtract one health point.
        Returns True if damage was applied (not blocked by iframes).
        """
        if self.invincible:
            return False
        self.health -= 1
        self.state   = 'hurt'
        if self.health <= 0:
            self.alive = False
        else:
            self.invincible       = True
            self.invincible_timer = INVINCIBLE_DURATION
        return True

    def refill_oxygen(self):
        """Restore oxygen from a canister pickup."""
        self.oxygen = min(PLAYER_MAX_OXYGEN, self.oxygen + OXYGEN_REFILL_AMT)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _update_state(self):
        if not self.alive:
            self.state = 'dead'
            return
        if not self.on_ground:
            self.state = 'jump'
        elif abs(self.vx) > 0:
            self.state = 'walk'
        elif self.state == 'hurt' and self.invincible_timer < 0.8:
            self.state = 'idle'
        elif self.state not in ('hurt', 'idle'):
            self.state = 'idle'

    def _collide_x(self, tiles):
        for tile in tiles:
            if self.rect.colliderect(tile):
                if self.vx > 0:
                    self.rect.right = tile.left
                elif self.vx < 0:
                    self.rect.left  = tile.right

    def _collide_y(self, tiles):
        for tile in tiles:
            if self.rect.colliderect(tile):
                if self.vy > 0:
                    self.rect.bottom = tile.top
                    self.on_ground   = True
                    self.vy          = 0.0
                elif self.vy < 0:
                    self.rect.top = tile.bottom
                    self.vy       = 0.0
