from email.mime import audio
import os
import pygame
import sys
import math
import random
from data.gameSetting import *
import os as _os
_CINZEL_PATH = _os.path.join(_os.path.dirname(__file__), 'assests', 'fonts', 'Cinzel-Bold.ttf')
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
STATE_DYING      = 'dying'   # Elden Ring animated death screen
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
    if level_num == 1:
        tilemap = LEVEL_1_MAP
    elif level_num == 2:
        tilemap = LEVEL_2_MAP
    else:
        tilemap = LEVEL_3_MAP
    level   = Level(tilemap, level_num)
    camera  = Camera()
    all_sprites = pygame.sprite.Group()
    player      = Player(level.player_spawn, all_sprites)
    enemies     = [Enemy(ex, ey, all_sprites) for ex, ey in level.enemy_spawns]
    particles   = ParticleSystem()
    comets      = []
    # Comet timer starting offsets:
    #   L1/L3: 0 (first comet fires after 1 full interval)
    #   L2: -5 (gives ~14 s grace period in the dark before first comet)
    comet_timer = -5.0 if level_num == 2 else 0.0
    audio.start_music(level_num)
    return level, camera, player, enemies, particles, comets, comet_timer


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock  = pygame.time.Clock()

    font_big, font_mid, font_small = _make_fonts()

    # Cinzel-Bold for the Elden Ring YOU DIED screen
    try:
        font_elden = pygame.font.Font(_CINZEL_PATH, 78)
    except Exception:
        font_elden = pygame.font.SysFont("Georgia", 78, bold=True)

    audio = AudioManager()

    state           = STATE_MENU
    current_level   = 1
    elapsed         = 0.0
    shake_time      = 0.0
    shake_mag       = 6
    trans_timer     = 0.0
    death_timer     = 0.0   # drives the YOU DIED animation
    last_frame      = None  # snapshot of the last gameplay frame for death screen
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

            # Spike trap collision
            for trap in level.trap_rects:
                if player.rect.colliderect(trap):
                    if player.take_damage():
                        particles.emit_sparks(player.rect.centerx, player.rect.centery)
                        audio.play('hurt')
                        shake_time = 0.25
                        shake_mag  = 6
                    break

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
                elif current_level == 2:
                    audio.stop_music()
                    state = STATE_WIN
                else:  # Level 3 complete
                    audio.stop_music()
                    state = STATE_WIN

            # Comet system — interval per level; spawn biased toward player
            comet_timer += dt
            comet_interval = {1: COMET_SPAWN_INTERVAL, 2: 6, 3: 2.5}.get(current_level, 10)
            if comet_timer >= comet_interval:
                comet_timer = 0.0
                # Bias spawn above the player (±200 px) so comets feel like they're targeting you
                bias_x   = player.rect.centerx + random.randint(-200, 200)
                spawn_x  = max(camera.offset_x + 40,
                               min(camera.offset_x + WINDOW_WIDTH - 40, bias_x))
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

            # Death check → animated death screen
            if not player.alive or player.rect.top > WINDOW_HEIGHT + 50:
                audio.stop_music()
                last_frame = screen.copy()
                death_timer = 0.0
                audio.play('you_died')   # Play immediately
                state = STATE_DYING

            # Screen shake
            sx = sy = 0
            if shake_time > 0:
                shake_time -= dt
                sx = random.randint(-shake_mag, shake_mag)
                sy = random.randint(-shake_mag // 2, shake_mag // 2)

            # Draw
            level.draw_background(screen, camera.offset_x)
            level.draw_tiles(screen,      camera.offset_x + sx)
            level.draw_traps(screen,      camera.offset_x + sx)
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

            # Level 2 darkness overlay — torch-light special effect (not on L3)
            if current_level == 2:
                level.draw_darkness(screen, pr.centerx, pr.centery)

            # Level 3: blood-red atmospheric pulse at screen edges
            if current_level == 3:
                pulse_a = int(30 + 20 * math.sin(elapsed * 4.0))
                edge = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                pygame.draw.rect(edge, (180, 0, 0, pulse_a), (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT), 28)
                screen.blit(edge, (0, 0))

            draw_hud(screen, player, current_level)

        # ── TRANSITION ────────────────────────────────────────────────────────
        elif state == STATE_TRANSITION:
            level.draw_background(screen, camera.offset_x)
            level.draw_tiles(screen, camera.offset_x)
            particles.draw(screen, camera.offset_x)
            next_lv = current_level + 1
            _draw_overlay(screen, f"LEVEL  {next_lv}", (100, 255, 160), font_big,
                          "Get ready...", font_small)
            trans_timer -= dt
            if trans_timer <= 0:
                current_level = next_lv
                level, camera, player, enemies, particles, comets, comet_timer = \
                    _load_level(current_level, audio)
                oxygen_beep_timer = 0.0
                oxygen_leak_timer = 0.0
                state = STATE_PLAYING

        # ── DYING (Elden Ring YOU DIED animation) ─────────────────────────────
        elif state == STATE_DYING:
            death_timer += dt

            # Keep last gameplay frame as backdrop
            if last_frame:
                screen.blit(last_frame, (0, 0))

            # Dark overlay fades in over 1.8 s
            overlay_a = min(190, int(190 * (death_timer / 1.8)))
            overlay   = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, overlay_a))
            screen.blit(overlay, (0, 0))

            # "YOU DIED" fades in + drifts upward starting at t = 0.7 s
            if death_timer > 0.7:
                t_prog   = min(1.0, (death_timer - 0.7) / 1.4)
                txt_a    = int(255 * t_prog)
                drift_y  = int(22 * (1.0 - t_prog))   # drifts up 22 px as it appears

                you_died = font_elden.render("YOU  DIED", True, (185, 20, 20))
                you_died.set_alpha(txt_a)
                tx = WINDOW_WIDTH  // 2 - you_died.get_width()  // 2
                ty = WINDOW_HEIGHT // 2 - you_died.get_height() // 2 + drift_y
                screen.blit(you_died, (tx, ty))



            # After 4 s switch to static DEAD screen (shows retry prompt)
            if death_timer >= 4.0:
                state = STATE_DEAD


        # ── DEAD ──────────────────────────────────────────────────────────────
        elif state == STATE_DEAD:
            # Keep last frame visible behind the prompt
  
        
            if last_frame:
                screen.blit(last_frame, (0, 0))
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 190))
            screen.blit(overlay, (0, 0))

            you_died = font_elden.render("YOU  DIED", True, (185, 20, 20))
            screen.blit(you_died, (WINDOW_WIDTH  // 2 - you_died.get_width()  // 2,
                                   WINDOW_HEIGHT // 2 - you_died.get_height() // 2 - 24))
            sub = font_small.render("Press  R  to retry   |   ESC  to quit", True, GRAY)
            screen.blit(sub, (WINDOW_WIDTH // 2 - sub.get_width() // 2,
                               WINDOW_HEIGHT // 2 + 28))
            


            if keys[pygame.K_r]:
                current_level = 1
                level, camera, player, enemies, particles, comets, comet_timer = \
                    _load_level(current_level, audio)
                oxygen_beep_timer = 0.0
                oxygen_leak_timer = 0.0
                last_frame = None
                state = STATE_PLAYING

        # ── WIN ───────────────────────────────────────────────────────────────
        elif state == STATE_WIN:
            screen.fill((4, 4, 28))
            if current_level < 3:
                sub_msg = "R - Play again   |   3 - Try INSANE mode   |   ESC - Quit"
            else:
                sub_msg = "You beat INSANE mode!   R - Play again   |   ESC - Quit"
            _draw_overlay(screen, "YOU  ESCAPED!", (100, 255, 200), font_mid,
                          sub_msg, font_small)
            if keys[pygame.K_r]:
                current_level = 1
                level, camera, player, enemies, particles, comets, comet_timer = \
                    _load_level(current_level, audio)
                oxygen_beep_timer = 0.0
                oxygen_leak_timer = 0.0
                audio.start_music(1)
                state = STATE_PLAYING
            elif keys[pygame.K_3] and current_level < 3:
                current_level = 3
                level, camera, player, enemies, particles, comets, comet_timer = \
                    _load_level(current_level, audio)
                oxygen_beep_timer = 0.0
                oxygen_leak_timer = 0.0
                state = STATE_PLAYING

        pygame.display.flip()


if __name__ == "__main__":
    main()
