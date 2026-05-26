import pygame
from data.gameSetting import (
    PLAYER_WIDTH, PLAYER_HEIGHT,
    PLAYER_MAX_HEALTH, PLAYER_MAX_OXYGEN,
    OXYGEN_DRAIN_RATE, OXYGEN_REFILL_AMT,
    PLAYER_SPEED, JUMP_VELOCITY, GRAVITY, TERMINAL_VEL,
    INVINCIBLE_DURATION,
    WHITE, BLACK, RED, CYAN,
)


class Player(pygame.sprite.Sprite):
    """
    Moon astronaut controlled by arrow keys / WASD.

    Physics
    -------
    All movement uses delta time (dt) so the game behaves the same at any
    frame rate.  Horizontal and vertical movement are resolved separately
    so corner collisions are handled cleanly.

    Oxygen system
    -------------
    Oxygen depletes at OXYGEN_DRAIN_RATE units/s.  At zero the player
    loses health.  Oxygen canisters refill it.

    Animation states: 'idle', 'walk', 'jump', 'hurt'
    The astronaut is drawn entirely with pygame.draw calls — no image files
    needed.
    """

    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
        self.rect  = self.image.get_rect(topleft=pos)

        # Physics state
        self.vx            = 0.0
        self.vy            = 0.0
        self.on_ground     = False
        self._prev_on_ground = False   # used to detect landing frame

        # Game stats
        self.health  = PLAYER_MAX_HEALTH
        self.oxygen  = PLAYER_MAX_OXYGEN
        self.alive   = True

        # Invincibility frames after taking damage
        self.invincible        = False
        self.invincible_timer  = 0.0

        # Animation
        self.state        = 'idle'
        self.anim_frame   = 0
        self.anim_timer   = 0.0
        self.facing_right = True

        self._draw()

    # ── Drawing ───────────────────────────────────────────────────────────────

    def _draw(self):
        """Redraw the astronaut sprite based on current state."""
        self.image.fill((0, 0, 0, 0))

        # Flicker rapidly during invincibility frames
        if self.invincible and int(self.invincible_timer * 10) % 2 == 0:
            return

        cx = PLAYER_WIDTH // 2
        suit   = (175, 178, 198)   # light gray spacesuit
        helmet = (215, 230, 255)   # slightly blue-white helmet glass
        visor  = (70,  155, 225)   # blue visor
        pack   = (95,  98,  118)   # life-support backpack

        # Animated legs — bob up and down while walking
        leg_bob = 3 if (self.anim_frame % 2 == 0) else -3
        if self.state != 'walk':
            leg_bob = 0
        left_foot_y  = PLAYER_HEIGHT - 14
        right_foot_y = PLAYER_HEIGHT - 14 + leg_bob

        pygame.draw.rect(self.image, suit, (cx - 10, left_foot_y,  8, 13))   # left leg
        pygame.draw.rect(self.image, suit, (cx + 2,  right_foot_y, 8, 13))   # right leg

        # Body / torso
        pygame.draw.rect(self.image, suit, (cx - 12, 14, 24, 18), border_radius=3)

        # Backpack (visible on the right side)
        pygame.draw.rect(self.image, pack, (cx + 10, 15, 5, 13), border_radius=2)

        # Helmet
        pygame.draw.circle(self.image, helmet, (cx, 10), 11)

        # Visor
        pygame.draw.ellipse(self.image, visor, (cx - 6, 5, 13, 8))

        # Red tint overlay while in 'hurt' state
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
            self.vy        = JUMP_VELOCITY
            self.on_ground = False

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
            self.take_damage()   # suffocating

        # Count down invincibility
        if self.invincible:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.invincible = False

        # Advance animation
        self._update_state()
        self.anim_timer += dt
        if self.anim_timer >= 0.12:
            self.anim_frame += 1
            self.anim_timer  = 0.0
        self._draw()

    @property
    def just_landed(self):
        """True only on the exact frame the player touches ground."""
        return self.on_ground and not self._prev_on_ground

    def take_damage(self):
        """
        Subtract one health point.
        Returns True if damage was actually applied (not during iframes).
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
        if not self.on_ground:
            self.state = 'jump'
        elif abs(self.vx) > 0:
            self.state = 'walk'
        else:
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
                if self.vy > 0:                    # falling → land on top
                    self.rect.bottom = tile.top
                    self.on_ground   = True
                    self.vy          = 0.0
                elif self.vy < 0:                  # jumping → hit ceiling
                    self.rect.top = tile.bottom
                    self.vy       = 0.0
