import pygame
import random
import math


class Particle:
    """
    A single particle: position, velocity, color, radius, lifetime.
    Alpha fades as lifetime shrinks toward zero.
    """
    def __init__(self, x, y, vx, vy, color, radius, lifetime):
        self.x        = x
        self.y        = y
        self.vx       = vx
        self.vy       = vy
        self.color    = color
        self.radius   = radius
        self.lifetime = lifetime
        self.max_life = lifetime

    @property
    def alive(self):
        return self.lifetime > 0

    def update(self, dt):
        self.x  += self.vx * dt
        self.y  += self.vy * dt
        self.vy += 180 * dt      # light gravity
        self.lifetime -= dt

    def draw(self, surface, offset_x):
        if not self.alive:
            return
        alpha = max(0, int(255 * (self.lifetime / self.max_life)))
        size  = max(1, int(self.radius))
        surf  = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        r, g, b = self.color
        pygame.draw.circle(surf, (r, g, b, alpha), (size, size), size)
        surface.blit(surf, (int(self.x - size - offset_x), int(self.y - size)))


class ParticleSystem:
    """
    Manages all particles.  Call emit_* methods to trigger effects.
    Call update() each frame, then draw() after the background is rendered.
    """

    def __init__(self):
        self.particles = []

    # ── Emission helpers ───────────────────────────────────────────────────────

    def emit_dust(self, x, y, count=8):
        """Gray dust cloud on player landing."""
        for _ in range(count):
            vx    = random.uniform(-70, 70)
            vy    = random.uniform(-50, -15)
            color = random.choice([
                (185, 180, 195), (155, 150, 165), (210, 205, 220),
            ])
            self.particles.append(
                Particle(x, y, vx, vy, color,
                         random.uniform(3, 7), random.uniform(0.35, 0.75))
            )

    def emit_sparks(self, x, y, count=12):
        """Yellow/orange sparks on damage or pickup."""
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(60, 180)
            color = random.choice([
                (255, 210, 50), (255, 155, 30), (255, 255, 100),
            ])
            self.particles.append(
                Particle(x, y,
                         math.cos(angle) * speed,
                         math.sin(angle) * speed - 60,
                         color, random.uniform(2, 5), random.uniform(0.25, 0.55))
            )

    def emit_death_burst(self, x, y, count=22):
        """Red/orange burst when an enemy is stomped."""
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(60, 220)
            base  = random.choice([
                (220, 55, 55), (255, 120, 30), (255, 200, 50),
            ])
            r = max(0, min(255, base[0] + random.randint(-25, 25)))
            g = max(0, min(255, base[1] + random.randint(-15, 15)))
            b = max(0, min(255, base[2] + random.randint(-15, 15)))
            self.particles.append(
                Particle(x, y,
                         math.cos(angle) * speed,
                         math.sin(angle) * speed - 100,
                         (r, g, b),
                         random.uniform(3, 9), random.uniform(0.4, 1.0))
            )

    def emit_oxygen_leak(self, x, y):
        """Cyan bubbles floating upward when O2 is critically low."""
        vx = random.uniform(-18, 18)
        vy = random.uniform(-90, -45)
        self.particles.append(
            Particle(x + random.uniform(-12, 12), y,
                     vx, vy, (0, 210, 255),
                     random.uniform(2, 4), random.uniform(0.5, 1.1))
        )

    def emit_comet_trail(self, x, y, count=4):
        """
        Fiery sparks shed by a comet in flight.
        Called every ~25 ms while the comet moves.
        """
        for _ in range(count):
            vx    = random.uniform(-35, 35)
            vy    = random.uniform(-25, 25)
            color = random.choice([
                (255, 200, 50), (255, 120, 20),
                (255, 255, 120), (255, 80, 20),
            ])
            self.particles.append(
                Particle(x + random.uniform(-6, 6),
                         y + random.uniform(-6, 6),
                         vx, vy, color,
                         random.uniform(3, 8), random.uniform(0.15, 0.4))
            )

    def emit_comet_explosion(self, x, y):
        """
        Massive burst when a comet impacts a tile (the floor-fracture event).
        Three layers: bright core flash, main fire debris, slow rock chunks.
        """
        # Layer 1 — bright core flash
        for _ in range(30):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(120, 400)
            color = random.choice([(255, 240, 150), (255, 200, 80), (255, 255, 255)])
            self.particles.append(
                Particle(x, y,
                         math.cos(angle) * speed,
                         math.sin(angle) * speed - 80,
                         color, random.uniform(3, 7), random.uniform(0.2, 0.5))
            )
        # Layer 2 — main fire debris
        for _ in range(35):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(60, 280)
            color = random.choice([
                (255, 140, 30), (220, 70, 20),
                (255, 180, 50), (200, 50, 10),
            ])
            self.particles.append(
                Particle(x, y,
                         math.cos(angle) * speed,
                         math.sin(angle) * speed - 100,
                         color, random.uniform(4, 10), random.uniform(0.5, 1.2))
            )
        # Layer 3 — slow rock/dust chunks (linger longest)
        for _ in range(20):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(20, 110)
            gray  = random.randint(120, 190)
            self.particles.append(
                Particle(x, y,
                         math.cos(angle) * speed,
                         math.sin(angle) * speed - 40,
                         (gray, gray - 20, gray - 40),
                         random.uniform(5, 13), random.uniform(0.8, 2.0))
            )

    def emit_level_complete(self, x, y, count=45):
        """Multicolour confetti burst on reaching the exit portal."""
        colors = [
            (255, 225, 50), (50, 220, 80), (0, 210, 255),
            (255, 80, 180), (180, 100, 255),
        ]
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(100, 320)
            self.particles.append(
                Particle(x, y,
                         math.cos(angle) * speed,
                         math.sin(angle) * speed - 160,
                         random.choice(colors),
                         random.uniform(3, 9), random.uniform(0.6, 1.3))
            )

    # ── Per-frame ─────────────────────────────────────────────────────────────

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, surface, offset_x=0):
        for p in self.particles:
            p.draw(surface, offset_x)
