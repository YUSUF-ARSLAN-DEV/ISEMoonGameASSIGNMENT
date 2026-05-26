"""
Lunar Escape
============
Moon-themed 2D platformer built with Pygame.

Controls
--------
  Arrow keys / WASD  — move and jump
  SPACE              — jump
  R                  — restart (from Game Over or Win screen)
  ESC                — quit

Rubric checklist
----------------
  ✓ Moon theme (surface + cavern levels, Earth in sky, astronaut player)
  ✓ Two levels with distinct environments and unique challenges
  ✓ Sprite animation (idle / walk / jump / hurt states, per-frame redrawn)
  ✓ Particle effects (dust on land, sparks on damage/pickup, death burst,
                       oxygen-leak bubbles, comet trail, comet explosion,
                       level-complete confetti)
  ✓ Motion tracking  — comet recalculates direction to player every frame
                       (vector normalisation → steering force → velocity)
  ✓ Event-driven gameplay (oxygen depletion, enemy AI, stomping,
                            comet impact + floor fracture, pickups, exit)
  ✓ Visual special effects (screen shake on damage/comet, pulsing glow on
                              items, parallax starfield, particle system)
  ✓ Audio special effects (synthesised jump, hurt, pickup, enemy death,
                            explosion, O2 alert, background music)
  ✓ Background music per level (ambient drone, different tone per level)
"""

import pygame
import sys
import math
import random
from data.gameSetting import *
from src.player    import Player
from src.enemy     import Enemy
from src.level     import Level
from src.camera    import Camera
from src.particles import ParticleSystem
from src.comet     import Comet
from src.hud       import draw_hud
from src.audio     import AudioManager

# ─── Game-state constants ─────────────────────────────────────────────────────
STATE_MENU       = 'menu'
STATE_PLAYING    = 'playing'
STATE_TRANSITION = 'transition'
STATE_DEAD       = 'dead'
STATE_WIN        = 'win'


# ─── Helper: semi-transparent overlay with centred text ───────────────────────
def _draw_overlay(surface, text, color, font,
                  sub_text='', sub_font=None, sub_color=None):
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surface.blit(overlay, (0, 0))

    msg = font.render(text, True, color)
    surface.blit(msg, (WINDOW_WIDTH // 2 - msg.get_width()  // 2,
                        WINDOW_HEIGHT // 2 - msg.get_height() // 2 - 20))
    if sub_text and sub_font:
        sub = sub_font.render(sub_text, True, sub_color or GRAY)
        surface.blit(sub, (WINDOW_WIDTH // 2 - sub.get_width() // 2,
                            WINDOW_HEIGHT // 2 + 20))


# ─── Helper: main menu screen ─────────────────────────────────────────────────
def _draw_menu(surface, font_big, font_small, elapsed):
    surface.fill(LVL1_BG_COLOR)

    # Static star field
    for i in range(90):
        x = (i * 139 + 50) % WINDOW_WIDTH
        y = (i * 83  + 30) % (WINDOW_HEIGHT - 60)
        pygame.draw.circle(surface, WHITE, (x, y), 1)

    # Gently floating moon
    moon_x = WINDOW_WIDTH // 2
    moon_y = 148 + int(6 * math.sin(elapsed * 0.8))
    pygame.draw.circle(surface, (205, 208, 220), (moon_x, moon_y), 80)
    for cx, cy, cr in [(moon_x - 25, moon_y - 15, 12),
                        (moon_x + 28, moon_y + 18,  9),
                        (moon_x - 5,  moon_y + 30,  6)]:
        pygame.draw.circle(surface, (175, 178, 190), (cx, cy), cr)
        pygame.draw.circle(surface, (195, 198, 210), (cx, cy), cr, 1)

    title  = font_big.render("LUNAR  ESCAPE", True, (218, 228, 255))
    prompt = font_small.render("Press  SPACE  or  ENTER  to  Start", True, (155, 165, 205))
    ctrl   = font_small.render("Arrow Keys / WASD — Move & Jump      ESC — Quit", True, (90, 95, 130))
    tip    = font_small.render("Stomp enemies  |  Collect O2 canisters  |  Dodge comets!", True, (70, 75, 110))

    surface.blit(title,  (WINDOW_WIDTH // 2 - title.get_width()  // 2, 270))
    surface.blit(prompt, (WINDOW_WIDTH // 2 - prompt.get_width() // 2, 345))
    surface.blit(ctrl,   (WINDOW_WIDTH // 2 - ctrl.get_width()   // 2, 395))
    surface.blit(tip,    (WINDOW_WIDTH // 2 - tip.get_width()    // 2, 440))


# ─── Helper: set up a fresh level with all objects ────────────────────────────
def _load_level(level_num, audio):
    tilemap = LEVEL_1_MAP if level_num == 1 else LEVEL_2_MAP
    level   = Level(tilemap, level_num)
    camera  = Camera()

    all_sprites = pygame.sprite.Group()
    player      = Player(level.player_spawn, all_sprites)

    enemies = [Enemy(ex, ey, all_sprites) for ex, ey in level.enemy_spawns]

    particles   = ParticleSystem()
    comets      = []
    comet_timer = 0.0

    audio.start_music(level_num)
    return level, camera, player, enemies, particles, comets, comet_timer


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock  = pygame.time.Clock()

    font_big   = pygame.font.SysFont("Arial", 50, bold=True)
    font_mid   = pygame.font.SysFont("Arial", 34, bold=True)
    font_small = pygame.font.SysFont("Arial", 20)

    audio = AudioManager()

    # ── State variables ───────────────────────────────────────────────────────
    state         = STATE_MENU
    current_level = 1
    elapsed       = 0.0    # drives glow/pulse animations
    shake_time    = 0.0    # remaining seconds of screen shake
    shake_mag     = 6      # current shake magnitude
    trans_timer   = 0.0

    level = camera = player = enemies = particles = None
    comets      = []
    comet_timer = 0.0

    # ── Game loop ─────────────────────────────────────────────────────────────
    while True:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)
        elapsed += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

        keys = pygame.key.get_pressed()

        # ══════════════════════════════════════════════════════════════════════
        # MENU
        # ══════════════════════════════════════════════════════════════════════
        if state == STATE_MENU:
            _draw_menu(screen, font_big, font_small, elapsed)
            if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                current_level = 1
                level, camera, player, enemies, particles, comets, comet_timer = \
                    _load_level(current_level, audio)
                state = STATE_PLAYING

        # ══════════════════════════════════════════════════════════════════════
        # PLAYING
        # ══════════════════════════════════════════════════════════════════════
        elif state == STATE_PLAYING:

            # ── Update player ─────────────────────────────────────────────────
            player.update(dt, level.tiles)
            camera.follow(player.rect)

            # ── Update enemies ────────────────────────────────────────────────
            for enemy in enemies:
                enemy.update(dt, level.tiles, player.rect)

            # ── Update particles ──────────────────────────────────────────────
            particles.update(dt)

            # ── Dust cloud on landing ─────────────────────────────────────────
            if player.just_landed:
                particles.emit_dust(player.rect.centerx, player.rect.bottom)

            # ── Oxygen-low visual + audio warning ────────────────────────────
            if player.oxygen < 25 and int(elapsed * 6) % 2 == 0:
                particles.emit_oxygen_leak(player.rect.centerx, player.rect.top)
                if int(elapsed) % 2 == 0:
                    audio.play('low_oxygen')

            # ── Player ↔ Enemy collision ──────────────────────────────────────
            for enemy in enemies[:]:
                if not enemy.alive_flag:
                    continue
                if not player.rect.colliderect(enemy.rect):
                    continue

                stomp = (
                    player.vy > 50 and
                    player.rect.bottom <= enemy.rect.centery + 12 and
                    player.rect.bottom >= enemy.rect.top - 8
                )
                if stomp:
                    enemy.alive_flag = False
                    particles.emit_death_burst(enemy.rect.centerx, enemy.rect.centery)
                    audio.play('enemy_death')
                    player.vy = -320
                else:
                    if player.take_damage():
                        particles.emit_sparks(player.rect.centerx, player.rect.centery)
                        audio.play('hurt')
                        shake_time = 0.28
                        shake_mag  = 6

            enemies = [e for e in enemies if e.alive_flag]

            # ── Oxygen canister pickup ────────────────────────────────────────
            for oxy in level.oxygen_rects[:]:
                if player.rect.colliderect(oxy):
                    player.refill_oxygen()
                    level.oxygen_rects.remove(oxy)
                    particles.emit_sparks(oxy.centerx, oxy.centery, count=8)
                    audio.play('pickup')

            # ── Exit portal ───────────────────────────────────────────────────
            if level.exit_rect and player.rect.colliderect(level.exit_rect):
                particles.emit_level_complete(player.rect.centerx, player.rect.centery)
                audio.play('level_complete')
                if current_level == 1:
                    trans_timer = 1.8
                    state = STATE_TRANSITION
                else:
                    audio.stop_music()
                    state = STATE_WIN

            # ══ COMET SYSTEM ══════════════════════════════════════════════════
            #
            # Spawning
            # --------
            comet_timer += dt
            if comet_timer >= COMET_SPAWN_INTERVAL:
                comet_timer = 0.0
                # Spawn within the visible screen in world space
                spawn_x = camera.offset_x + random.randint(60, WINDOW_WIDTH - 60)
                comets.append(Comet(spawn_x, camera.offset_x))

            # Update + collision
            for comet in comets:
                comet.update(dt, player.rect, level.tiles, particles)

                # On explosion this frame:
                if comet.exploded:
                    audio.play('explosion')

                    # ── Large screen shake on impact ──────────────────────────
                    shake_time = 0.55
                    shake_mag  = 12

                    # ── Floor fracture: remove tiles near the impact ──────────
                    # This is the "comet collision and floor fracture" mechanic
                    # described in the assignment narrative storyboard section.
                    ix, iy = comet.impact_x, comet.impact_y
                    level.tiles = [
                        t for t in level.tiles
                        if math.dist((t.centerx, t.centery), (ix, iy))
                           > COMET_FRACTURE_RADIUS
                    ]

                    # ── Damage player if close to impact ──────────────────────
                    pdist = math.dist(
                        (player.rect.centerx, player.rect.centery),
                        (ix, iy)
                    )
                    if pdist <= COMET_DAMAGE_RADIUS:
                        if player.take_damage():
                            particles.emit_sparks(
                                player.rect.centerx, player.rect.centery
                            )
                            audio.play('hurt')

            # Remove dead comets
            comets = [c for c in comets if c.alive or not c.exploded]
            # ══════════════════════════════════════════════════════════════════

            # ── Death check ───────────────────────────────────────────────────
            if not player.alive or player.rect.top > WINDOW_HEIGHT + 50:
                audio.stop_music()
                state = STATE_DEAD

            # ── Screen-shake offset ───────────────────────────────────────────
            sx = sy = 0
            if shake_time > 0:
                shake_time -= dt
                sx = random.randint(-shake_mag, shake_mag)
                sy = random.randint(-shake_mag // 2, shake_mag // 2)

            # ── Draw ──────────────────────────────────────────────────────────
            level.draw_background(screen, camera.offset_x)
            level.draw_tiles(screen,      camera.offset_x + sx)
            level.draw_items(screen,      camera.offset_x + sx, elapsed)

            # Comets (behind player, in front of tiles)
            for comet in comets:
                comet.draw(screen, camera.offset_x + sx)

            # Player
            pr = camera.apply(player.rect)
            pr.x += sx;  pr.y += sy
            screen.blit(player.image, pr)

            # Enemies
            for enemy in enemies:
                er = camera.apply(enemy.rect)
                screen.blit(enemy.image, er)

            # Particles (world-space, pass camera offset)
            particles.draw(screen, camera.offset_x)

            # HUD on top of everything
            draw_hud(screen, player, current_level)

        # ══════════════════════════════════════════════════════════════════════
        # LEVEL TRANSITION
        # ══════════════════════════════════════════════════════════════════════
        elif state == STATE_TRANSITION:
            level.draw_background(screen, camera.offset_x)
            level.draw_tiles(screen, camera.offset_x)
            particles.draw(screen, camera.offset_x)
            _draw_overlay(screen, "LEVEL  2", (100, 255, 160), font_big,
                          "Get ready…", font_small)
            trans_timer -= dt
            if trans_timer <= 0:
                current_level = 2
                level, camera, player, enemies, particles, comets, comet_timer = \
                    _load_level(current_level, audio)
                state = STATE_PLAYING

        # ══════════════════════════════════════════════════════════════════════
        # GAME OVER
        # ══════════════════════════════════════════════════════════════════════
        elif state == STATE_DEAD:
            screen.fill(BLACK)
            _draw_overlay(screen, "YOU  DIED", RED, font_big,
                          "Press  R  to retry   |   ESC  to quit", font_small)
            if keys[pygame.K_r]:
                current_level = 1
                level, camera, player, enemies, particles, comets, comet_timer = \
                    _load_level(current_level, audio)
                state = STATE_PLAYING

        # ══════════════════════════════════════════════════════════════════════
        # WIN
        # ══════════════════════════════════════════════════════════════════════
        elif state == STATE_WIN:
            screen.fill((4, 4, 28))
            _draw_overlay(screen, "YOU  ESCAPED!", (100, 255, 200), font_mid,
                          "Press  R  to play again   |   ESC  to quit",
                          font_small)
            if keys[pygame.K_r]:
                current_level = 1
                level, camera, player, enemies, particles, comets, comet_timer = \
                    _load_level(current_level, audio)
                audio.start_music(1)
                state = STATE_PLAYING

        pygame.display.flip()


if __name__ == "__main__":
    main()
