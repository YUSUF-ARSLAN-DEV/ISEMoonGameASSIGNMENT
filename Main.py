import os
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

STATE_MENU       = 'menu'
STATE_PLAYING    = 'playing'
STATE_TRANSITION = 'transition'
STATE_DEAD       = 'dead'
STATE_WIN        = 'win'

_FONT_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), 'assests', 'sprites',
                 'SimplePixelArtUIpack', 'SimplePixelArtUIpack',
                 'fonts', 'font 1', 'pixelfont.ttf')
)


def _make_fonts(big_size=50, mid_size=34, small_size=20):
    """Return (font_big, font_mid, font_small) using pixel TTF when available."""
    if os.path.exists(_FONT_PATH):
        try:
            return (
                pygame.font.Font(_FONT_PATH, big_size),
                pygame.font.Font(_FONT_PATH, mid_size),
                pygame.font.Font(_FONT_PATH, small_size),
            )
        except Exception:
            pass
    return (
        pygame.font.SysFont("Arial", big_size,   bold=True),
        pygame.font.SysFont("Arial", mid_size,   bold=True),
        pygame.font.SysFont("Arial", small_size),
    )


def _draw_overlay(surface, text, color, font, sub_text='', sub_font=None, sub_color=None):
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surface.blit(overlay, (0, 0))
    msg = font.render(text, True, color)
    surface.blit(msg, (WINDOW_WIDTH // 2 - msg.get_width() // 2,
                        WINDOW_HEIGHT // 2 - msg.get_height() // 2 - 20))
    if sub_text and sub_font:
        sub = sub_font.render(sub_text, True, sub_color or GRAY)
        surface.blit(sub, (WINDOW_WIDTH // 2 - sub.get_width() // 2,
                            WINDOW_HEIGHT // 2 + 20))


def _draw_menu(surface, font_big, font_small, elapsed):
    surface.fill(LVL1_BG_COLOR)
    for i in range(90):
        x = (i * 139 + 50) % WINDOW_WIDTH
        y = (i * 83  + 30) % (WINDOW_HEIGHT - 60)
        pygame.draw.circle(surface, WHITE, (x, y), 1)
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
    ctrl   = font_small.render("Arrow Keys / WASD - Move & Jump      ESC - Quit", True, (90, 95, 130))
    tip    = font_small.render("Stomp enemies  |  Collect O2 canisters  |  Dodge comets!", True, (70, 75, 110))
    surface.blit(title,  (WINDOW_WIDTH // 2 - title.get_width()  // 2, 270))
    surface.blit(prompt, (WINDOW_WIDTH // 2 - prompt.get_width() // 2, 345))
    surface.blit(ctrl,   (WINDOW_WIDTH // 2 - ctrl.get_width()   // 2, 395))
    surface.blit(tip,    (WINDOW_WIDTH // 2 - tip.get_width()    // 2, 440))


def _load_level(level_num, audio):
    tilemap = LEVEL_1_MAP if level_num == 1 else LEVEL_2_MAP
    level   = Level(tilemap, level_num)
    camera  = Camera()
    all_sprites = pygame.sprite.Group()
    player      = Player(level.player_spawn, all_sprites)
    enemies     = [Enemy(ex, ey, all_sprites) for ex, ey in level.enemy_spawns]
    particles   = ParticleSystem()
    comets      = []
    # Pre-charge the comet timer on Level 2 so the first comet arrives
    # almost immediately (interval is 9s, starting at 7s = 2s wait)
    comet_timer = 7.0 if level_num == 2 else 0.0
    audio.start_music(level_num)
    return level, camera, player, enemies, particles, comets, comet_timer


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock  = pygame.time.Clock()

    font_big, font_mid, font_small = _make_fonts()

    audio = AudioManager()

    state           = STATE_MENU
    current_level   = 1
    elapsed         = 0.0
    shake_time      = 0.0
    shake_mag       = 6
    trans_timer     = 0.0
    footstep_timer    = 0.0
    oxygen_beep_timer = 0.0
    oxygen_leak_timer = 0.0
    comets      = []
    comet_timer = 0.0

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

        # ── MENU ──────────────────────────────────────────────────────────────
        if state == STATE_MENU:
            _draw_menu(screen, font_big, font_small, elapsed)
            if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                current_level = 1
                level, camera, player, enemies, particles, comets, comet_timer = \
                    _load_level(current_level, audio)
                oxygen_beep_timer = 0.0
                oxygen_leak_timer = 0.0
                state = STATE_PLAYING

        # ── PLAYING ───────────────────────────────────────────────────────────
        elif state == STATE_PLAYING:

            player.update(dt, level.tiles)
            camera.follow(player.rect)
            for enemy in enemies:
                enemy.update(dt, level.tiles, player.rect)
            particles.update(dt)

            # Dust + landing thud
            if player.just_landed:
                particles.emit_dust(player.rect.centerx, player.rect.bottom)
                audio.play('land')

            # Footstep sound while walking
            if player.on_ground and abs(player.vx) > 0:
                footstep_timer += dt
                if footstep_timer >= 0.35:
                    footstep_timer = 0.0
                    audio.play('footstep')
            else:
                footstep_timer = 0.0

            # Jump sound — fires exactly on the frame the player leaves the ground
            if player.just_jumped:
                audio.play('jump')

            # Oxygen warning system — timer-driven so beeps repeat reliably
            oxygen_beep_timer += dt
            if player.oxygen <= 0:
                pass   # suffocation handled in player.update
            elif player.oxygen < 25:
                oxygen_leak_timer += dt
                if oxygen_leak_timer >= 0.20:
                    oxygen_leak_timer = 0.0
                    particles.emit_oxygen_leak(player.rect.centerx, player.rect.top)
                if oxygen_beep_timer >= 1.2:
                    oxygen_beep_timer = 0.0
                    audio.play('low_oxygen')
            elif player.oxygen < 50:
                # Warning zone: repeat the 50% alarm every 3 s
                if oxygen_beep_timer >= 3.0:
                    oxygen_beep_timer = 0.0
                    audio.play('oxygen_50')
            else:
                oxygen_beep_timer = 0.0   # above 50% — reset so warning fires promptly if it drops again

            # Player <-> Enemy
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

            # Oxygen pickup
            for oxy in level.oxygen_rects[:]:
                if player.rect.colliderect(oxy):
                    player.refill_oxygen()
                    level.oxygen_rects.remove(oxy)
                    particles.emit_sparks(oxy.centerx, oxy.centery, count=8)
                    audio.play('pickup')
                    oxygen_beep_timer = 0.0
                    oxygen_leak_timer = 0.0

            # Exit portal
            if level.exit_rect and player.rect.colliderect(level.exit_rect):
                particles.emit_level_complete(player.rect.centerx, player.rect.centery)
                audio.play('level_complete')
                if current_level == 1:
                    trans_timer = 1.8
                    state = STATE_TRANSITION
                else:
                    audio.stop_music()
                    state = STATE_WIN

            # Comet system
            comet_timer += dt
            comet_interval = COMET_SPAWN_INTERVAL if current_level == 1 else 9
            if comet_timer >= comet_interval:
                comet_timer = 0.0
                spawn_x = camera.offset_x + random.randint(60, WINDOW_WIDTH - 60)
                comets.append(Comet(spawn_x, camera.offset_x))

            for comet in comets:
                comet.update(dt, player.rect, level.tiles, particles)
                if comet.exploded:
                    audio.play('explosion')
                    shake_time = 0.55
                    shake_mag  = 12
                    ix, iy = comet.impact_x, comet.impact_y
                    level.tiles = [
                        t for t in level.tiles
                        if math.dist((t.centerx, t.centery), (ix, iy)) > COMET_FRACTURE_RADIUS
                    ]
                    pdist = math.dist(
                        (player.rect.centerx, player.rect.centery), (ix, iy)
                    )
                    if pdist <= COMET_DAMAGE_RADIUS:
                        if player.take_damage():
                            particles.emit_sparks(player.rect.centerx, player.rect.centery)
                            audio.play('hurt')

            comets = [c for c in comets if c.alive]

            # Death check
            if not player.alive or player.rect.top > WINDOW_HEIGHT + 50:
                audio.stop_music()
                state = STATE_DEAD

            # Screen shake
            sx = sy = 0
            if shake_time > 0:
                shake_time -= dt
                sx = random.randint(-shake_mag, shake_mag)
                sy = random.randint(-shake_mag // 2, shake_mag // 2)

            # Draw
            level.draw_background(screen, camera.offset_x)
            level.draw_tiles(screen,      camera.offset_x + sx)
            level.draw_items(screen,      camera.offset_x + sx, elapsed)

            for comet in comets:
                comet.draw(screen, camera.offset_x + sx)

            pr = camera.apply(player.rect)
            pr.x += player._sprite_offset_x + sx
            pr.y += player._sprite_offset_y + sy
            screen.blit(player.image, pr)

            for enemy in enemies:
                er = camera.apply(enemy.rect)
                er.x += enemy._sprite_offset_x
                er.y += enemy._sprite_offset_y
                screen.blit(enemy.image, er)

            particles.draw(screen, camera.offset_x)

            # Level 2 darkness overlay — torch-light special effect
            if current_level == 2:
                level.draw_darkness(screen, pr.centerx, pr.centery)

            draw_hud(screen, player, current_level)

        # ── TRANSITION ────────────────────────────────────────────────────────
        elif state == STATE_TRANSITION:
            level.draw_background(screen, camera.offset_x)
            level.draw_tiles(screen, camera.offset_x)
            particles.draw(screen, camera.offset_x)
            _draw_overlay(screen, "LEVEL  2", (100, 255, 160), font_big,
                          "Get ready...", font_small)
            trans_timer -= dt
            if trans_timer <= 0:
                current_level = 2
                level, camera, player, enemies, particles, comets, comet_timer = \
                    _load_level(current_level, audio)
                oxygen_beep_timer = 0.0
                oxygen_leak_timer = 0.0
                state = STATE_PLAYING

        # ── DEAD ──────────────────────────────────────────────────────────────
        elif state == STATE_DEAD:
            screen.fill(BLACK)
            _draw_overlay(screen, "YOU  DIED", RED, font_big,
                          "Press  R  to retry   |   ESC  to quit", font_small)
            if keys[pygame.K_r]:
                current_level = 1
                level, camera, player, enemies, particles, comets, comet_timer = \
                    _load_level(current_level, audio)
                oxygen_beep_timer = 0.0
                oxygen_leak_timer = 0.0
                state = STATE_PLAYING

        # ── WIN ───────────────────────────────────────────────────────────────
        elif state == STATE_WIN:
            screen.fill((4, 4, 28))
            _draw_overlay(screen, "YOU  ESCAPED!", (100, 255, 200), font_mid,
                          "Press  R  to play again   |   ESC  to quit", font_small)
            if keys[pygame.K_r]:
                current_level = 1
                level, camera, player, enemies, particles, comets, comet_timer = \
                    _load_level(current_level, audio)
                oxygen_beep_timer = 0.0
                oxygen_leak_timer = 0.0
                audio.start_music(1)
                state = STATE_PLAYING

        pygame.display.flip()


if __name__ == "__main__":
    main()
