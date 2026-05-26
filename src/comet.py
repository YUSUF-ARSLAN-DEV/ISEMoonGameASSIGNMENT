"""
Comet — motion-tracking hazard
================================
Each comet spawns above the visible screen and, every frame, recalculates the
direction vector toward the player's current position.  It then steers its
velocity toward that direction at COMET_STEER_FORCE px/s².

This continuous per-frame recalculation is the "motion tracking" technique
required by the assignment overview.  It is analogous to a heat-seeking
missile: the projectile always knows where the target is and adjusts course.

On hitting any solid tile the comet explodes:
  • A large particle burst (handled by ParticleSystem.emit_comet_explosion)
  • Nearby tiles are removed from the level  → "floor fracture" mechanic
  • The caller (Main.py) applies screen shake and checks player proximity
    for damage.
"""

import pygame
import math
import random
from data.gameSetting import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    COMET_STEER_FORCE, COMET_MAX_SPEED,
    COMET_RADIUS,
    WHITE,
)


class Comet:
    """
    Attributes set after explosion (read by Main.py):
        self.exploded     — True on the frame the comet hits a tile
        self.impact_x/y   — world-space coordinates of the impact
    """

    def __init__(self, world_x, camera_offset_x):
        """
        world_x        — x spawn position in world space
        camera_offset_x — current camera offset so the comet appears on screen
        """
        # Spawn above the visible screen area
        self.x = float(world_x)
        self.y = float(-60)

        # Initial velocity: straight down with a small random horizontal nudge
        self.vx = float(random.randint(-40, 40))
        self.vy = float(180)           # starts falling at 180 px/s

        self.alive    = True
        self.exploded = False
        self.impact_x = 0.0
        self.impact_y = 0.0

        # Trail particles are emitted on a short timer to avoid flooding
        self._trail_timer = 0.0

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt, player_rect, tiles, particles):
        """
        dt          — seconds since last frame
        player_rect — player's world-space Rect (target for motion tracking)
        tiles       — list of solid tile Rects (collision)
        particles   — ParticleSystem (trail emission)
        """
        if not self.alive:
            return

        # ── MOTION TRACKING ───────────────────────────────────────────────────
        # Step 1: direction vector from comet to player (world space)
        dx = player_rect.centerx - self.x
        dy = player_rect.centery - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 1:
            # Step 2: normalise to unit vector, scale by steering force
            steer_x = (dx / dist) * COMET_STEER_FORCE
            steer_y = (dy / dist) * COMET_STEER_FORCE

            # Step 3: apply steering as acceleration this frame
            self.vx += steer_x * dt
            self.vy += steer_y * dt

        # ── Speed cap ─────────────────────────────────────────────────────────
        speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
        if speed > COMET_MAX_SPEED:
            scale  = COMET_MAX_SPEED / speed
            self.vx *= scale
            self.vy *= scale

        # ── Move ──────────────────────────────────────────────────────────────
        self.x += self.vx * dt
        self.y += self.vy * dt

        # ── Trail particles ───────────────────────────────────────────────────
        self._trail_timer += dt
        if self._trail_timer >= 0.025:          # emit every 25 ms
            self._trail_timer = 0.0
            particles.emit_comet_trail(self.x, self.y)

        # ── Tile collision → explosion ────────────────────────────────────────
        comet_rect = pygame.Rect(
            int(self.x - COMET_RADIUS), int(self.y - COMET_RADIUS),
            COMET_RADIUS * 2, COMET_RADIUS * 2,
        )
        for tile in tiles:
            if comet_rect.colliderect(tile):
                self._explode(particles)
                return

        # ── Off-screen (missed everything) ───────────────────────────────────
        if self.y > WINDOW_HEIGHT + 80:
            self.alive = False

    def _explode(self, particles):
        """Record impact position, emit burst, mark dead."""
        self.impact_x = self.x
        self.impact_y = self.y
        self.alive    = False
        self.exploded = True
        particles.emit_comet_explosion(self.x, self.y)

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface, offset_x):
        """Draw glowing comet body. offset_x converts world → screen X."""
        if not self.alive:
            return

        sx = int(self.x - offset_x)
        sy = int(self.y)

        # Cull if off screen
        if not (-COMET_RADIUS * 4 < sx < WINDOW_WIDTH + COMET_RADIUS * 4):
            return

        # Outer glow layers (largest → smallest, increasing opacity)
        for radius, alpha in [(44, 18), (32, 35), (22, 60)]:
            glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 155, 45, alpha), (radius, radius), radius)
            surface.blit(glow, (sx - radius, sy - radius))

        # Solid core
        pygame.draw.circle(surface, (255, 225, 110), (sx, sy), COMET_RADIUS)
        # Bright hot centre
        pygame.draw.circle(surface, WHITE, (sx, sy), COMET_RADIUS // 2)
