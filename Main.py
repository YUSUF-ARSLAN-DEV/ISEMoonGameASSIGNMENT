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
from src.cutscene  import CutsceneManager
from data.cutscene_data import INTRO_CUTSCENE, MID_CUTSCENE

STATE_MENU           = 'menu'
STATE_LEVEL_SELECT   = 'level_select'
STATE_PLAYING        = 'playing'
STATE_PAUSED         = 'paused'
STATE_TRANSITION     = 'transition'
STATE_DYING          = 'dying'
STATE_DEAD           = 'dead'
STATE_WIN            = 'win'
STATE_EXIT_CONFIRM   = 'exit_confirm'
STATE_INTRO_CUTSCENE = 'intro_cutscene'
STATE_MID_CUTSCENE   = 'mid_cutscene'

_FONT_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), 'assests', 'sprites',
                 'SimplePixelArtUIpack', 'SimplePixelArtUIpack',
                 'fonts', 'font 1', 'pixelfont.ttf')
)


def _make_fonts(big_size=50, mid_size=34, small_size=20):
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


def _draw_menu(surface, font_big, font_mid, font_small, elapsed, cursor):
    """Main menu — two options: Play Game / Select Level."""
    surface.fill(LVL1_BG_COLOR)
    # Stars
    for i in range(90):
        x = (i * 139 + 50) % WINDOW_WIDTH
        y = (i * 83  + 30) % (WINDOW_HEIGHT - 60)
        pygame.draw.circle(surface, WHITE, (x, y), 1)
    # Moon
    moon_x = WINDOW_WIDTH // 2
    moon_y = 140 + int(6 * math.sin(elapsed * 0.8))
    pygame.draw.circle(surface, (205, 208, 220), (moon_x, moon_y), 72)
    for cx, cy, cr in [(moon_x - 25, moon_y - 15, 12),
                        (moon_x + 28, moon_y + 18,  9),
                        (moon_x - 5,  moon_y + 30,  6)]:
        pygame.draw.circle(surface, (175, 178, 190), (cx, cy), cr)
        pygame.draw.circle(surface, (195, 198, 210), (cx, cy), cr, 1)

    title = font_big.render("LUNAR  ESCAPE", True, (218, 228, 255))
    surface.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 252))

    # Menu options
    options = ["PLAY  GAME", "SELECT  LEVEL"]
    for i, opt in enumerate(options):
        selected = (cursor == i)
        col  = (255, 245, 100) if selected else (155, 165, 205)
        text = ("  >  " if selected else "     ") + opt
        lbl  = font_mid.render(text, True, col)
        y    = 340 + i * 62
        surface.blit(lbl, (WINDOW_WIDTH // 2 - lbl.get_width() // 2, y))

    hint = font_small.render(
        "Up / Down  to navigate      Enter / Space  to select      ESC  to quit",
        True, (70, 75, 110)
    )
    surface.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, 490))

    instructions = font_small.render(
        "How to Play:",
        True, (100, 105, 140)
    )
    surface.blit(instructions, (WINDOW_WIDTH // 2 - instructions.get_width() // 2, 555))

    move_hint = font_small.render(
        "Move:  A / D   or   Left / Right",
        True, (100, 105, 140)
    )
    surface.blit(move_hint, (WINDOW_WIDTH // 2 - move_hint.get_width() // 2, 585))

    jump_hint = font_small.render(
        "Jump:  W   /   Up   /   Space",
        True, (100, 105, 140)
    )
    surface.blit(jump_hint, (WINDOW_WIDTH // 2 - jump_hint.get_width() // 2, 615))

    goal_title = font_small.render(
        "Objective:",
        True, (100, 105, 140)
    )
    surface.blit(goal_title, (WINDOW_WIDTH // 2 - goal_title.get_width() // 2, 670))

    goal_hint = font_small.render(
        "Avoid hazards, collect blue oxygen orbs, and reach the exit to escape the moon!",
        True, (100, 105, 140)
    )
    surface.blit(goal_hint, (WINDOW_WIDTH // 2 - goal_hint.get_width() // 2, 700))

def _draw_level_select(surface, font_big, font_mid, font_small, elapsed, cursor):
    """Level select screen."""
    surface.fill(LVL1_BG_COLOR)
    for i in range(90):
        x = (i * 139 + 50) % WINDOW_WIDTH
        y = (i * 83  + 30) % (WINDOW_HEIGHT - 60)
        pygame.draw.circle(surface, WHITE, (x, y), 1)

    title = font_big.render("SELECT  LEVEL", True, (218, 228, 255))
    surface.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 80))

    levels = [
        ("LEVEL  1", "Moon Surface",              (170, 175, 200)),
        ("LEVEL  2", "Lunar Cavern",               (140, 90,  210)),
        ("LEVEL  3", "Blood Moon    (INSANE)",      (210, 60,  60)),
    ]
    for i, (name, desc, desc_col) in enumerate(levels):
        selected = (cursor == i)
        name_col = (255, 245, 100) if selected else (190, 195, 220)
        prefix   = "  >  " if selected else "     "
        name_lbl = font_mid.render(prefix + name, True, name_col)
        desc_lbl = font_small.render(desc, True, desc_col if selected else (80, 85, 115))
        base_y   = 185 + i * 90
        surface.blit(name_lbl, (WINDOW_WIDTH // 2 - name_lbl.get_width() // 2, base_y))
        surface.blit(desc_lbl, (WINDOW_WIDTH // 2 - desc_lbl.get_width() // 2, base_y + 38))

    hint = font_small.render(
        "Up / Down  to navigate      Enter / Space  to confirm      ESC  to go back",
        True, (70, 75, 110)
    )
    surface.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, 510))


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
    comet_timer = -5.0 if level_num == 2 else 0.0
    audio.start_music(level_num)
    return level, camera, player, enemies, particles, comets, comet_timer


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
    pygame.display.set_caption(TITLE)
    clock  = pygame.time.Clock()

    font_big, font_mid, font_small = _make_fonts()

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
    death_timer     = 0.0
    last_frame      = None
    footstep_timer    = 0.0
    oxygen_beep_timer = 0.0
    oxygen_leak_timer = 0.0
    comets      = []
    comet_timer = 0.0
    menu_cursor       = 0   # 0 = Play Game, 1 = Select Level
    level_cursor      = 0   # 0 = L1, 1 = L2, 2 = L3
    exit_confirm_prev_state = STATE_MENU
    cutscene          = None   # The active CutsceneManager (None when not in a cutscene)
    show_insane_prompt = False # After mid cutscene, show the INSANE mode offer?

    # Cheat codes
    CHEAT_OXYGEN = (pygame.K_9, pygame.K_l, pygame.K_9, pygame.K_l, pygame.K_o)
    CHEAT_SPEED  = (pygame.K_w, pygame.K_x, pygame.K_w, pygame.K_x, pygame.K_s)
    cheat_buffer = []

    # Placeholders so references work before first _load_level
    level = None; camera = None; player = None; enemies = []; particles = None

    while True:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)
        elapsed += dt

        # ── Track "just pressed" keys ─────────────────────────────────────────
        # This set captures keys that were PRESSED this exact frame (not held).
        # We build it from KEYDOWN events and pass it to the cutscene system.
        # WHY: The cutscene engine needs "tap" input (press → release) so that
        # holding down SPACE doesn't skip 30 lines in one frame.
        just_pressed = set()

        # ── Event handling ────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if state in (STATE_MENU, STATE_PLAYING):
                    last_frame = screen.copy()
                    exit_confirm_prev_state = state
                    state = STATE_EXIT_CONFIRM
                else:
                    pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                # Record this key press for the cutscene system (just_pressed set)
                just_pressed.add(event.key)

                # ── Exit confirmation ──────────────────────────────────────────
                if state == STATE_EXIT_CONFIRM:
                    if event.key == pygame.K_y:
                        pygame.quit(); sys.exit()
                    else:
                        state = exit_confirm_prev_state
                    continue

                # Global ESC: back to menu or quit
                if event.key == pygame.K_ESCAPE:
                    if state == STATE_LEVEL_SELECT:
                        state = STATE_MENU
                    elif state == STATE_MENU:
                        last_frame = screen.copy()
                        exit_confirm_prev_state = state
                        state = STATE_EXIT_CONFIRM
                    elif state == STATE_PLAYING:
                        last_frame = screen.copy()
                        state = STATE_PAUSED
                    elif state == STATE_PAUSED:
                        state = STATE_PLAYING

                # ── Menu navigation ───────────────────────────────────────────
                elif state == STATE_MENU:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        menu_cursor = (menu_cursor - 1) % 2
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        menu_cursor = (menu_cursor + 1) % 2
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if menu_cursor == 0:
                            # Play Game → show intro cutscene first, then Level 1
                            current_level = 1
                            cutscene = CutsceneManager(INTRO_CUTSCENE, audio)
                            state = STATE_INTRO_CUTSCENE
                        else:
                            state = STATE_LEVEL_SELECT

                # ── Level select navigation ───────────────────────────────────
                elif state == STATE_LEVEL_SELECT:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        level_cursor = (level_cursor - 1) % 3
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        level_cursor = (level_cursor + 1) % 3
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        current_level = level_cursor + 1
                        level, camera, player, enemies, particles, comets, comet_timer = \
                            _load_level(current_level, audio)
                        oxygen_beep_timer = oxygen_leak_timer = 0.0
                        state = STATE_PLAYING

                # ── Cheat codes ────────────────────────────────────────────────
                elif state == STATE_PLAYING:
                    cheat_buffer.append(event.key)
                    if len(cheat_buffer) > 5:
                        cheat_buffer.pop(0)
                    if tuple(cheat_buffer) == CHEAT_OXYGEN:
                        player.cheat_infinite_oxygen = not player.cheat_infinite_oxygen
                        cheat_buffer.clear()
                        particles.emit_sparks(player.rect.centerx, player.rect.centery, count=20)
                    elif tuple(cheat_buffer) == CHEAT_SPEED:
                        player.cheat_speed_multiplier = 2.5 if player.cheat_speed_multiplier == 1.0 else 1.0
                        cheat_buffer.clear()
                        particles.emit_sparks(player.rect.centerx, player.rect.centery, count=20)

        keys = pygame.key.get_pressed()

        # ── MENU ──────────────────────────────────────────────────────────────
        if state == STATE_MENU:
            _draw_menu(screen, font_big, font_mid, font_small, elapsed, menu_cursor)

        # ── LEVEL SELECT ──────────────────────────────────────────────────────
        elif state == STATE_LEVEL_SELECT:
            _draw_level_select(screen, font_big, font_mid, font_small, elapsed, level_cursor)

        # ── PLAYING ───────────────────────────────────────────────────────────
        elif state == STATE_PLAYING:

            player.update(dt, level.tiles)
            camera.follow(player.rect)
            for enemy in enemies:
                enemy.update(dt, level.tiles, player.rect)
            particles.update(dt)

            if player.just_landed:
                particles.emit_dust(player.rect.centerx, player.rect.bottom)
                audio.play('land')

            if player.on_ground and abs(player.vx) > 0:
                footstep_timer += dt
                if footstep_timer >= 0.35:
                    footstep_timer = 0.0
                    audio.play('footstep')
            else:
                footstep_timer = 0.0

            if player.just_jumped:
                audio.play('jump')

            oxygen_beep_timer += dt
            if player.oxygen <= 0:
                pass
            elif player.oxygen < 25:
                oxygen_leak_timer += dt
                if oxygen_leak_timer >= 0.20:
                    oxygen_leak_timer = 0.0
                    particles.emit_oxygen_leak(player.rect.centerx, player.rect.top)
                if oxygen_beep_timer >= 1.2:
                    oxygen_beep_timer = 0.0
                    audio.play('low_oxygen')
            elif player.oxygen < 50:
                if oxygen_beep_timer >= 3.0:
                    oxygen_beep_timer = 0.0
                    audio.play('oxygen_50')
            else:
                oxygen_beep_timer = 0.0

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

            for trap in level.trap_rects:
                if player.rect.colliderect(trap):
                    if player.take_damage():
                        particles.emit_sparks(player.rect.centerx, player.rect.centery)
                        audio.play('hurt')
                        shake_time = 0.25
                        shake_mag  = 6
                    break

            for oxy in level.oxygen_rects[:]:
                if player.rect.colliderect(oxy):
                    player.refill_oxygen()
                    level.oxygen_rects.remove(oxy)
                    particles.emit_sparks(oxy.centerx, oxy.centery, count=8)
                    audio.play('pickup')
                    oxygen_beep_timer = 0.0
                    oxygen_leak_timer = 0.0

            if level.exit_rect and player.rect.colliderect(level.exit_rect):
                particles.emit_level_complete(player.rect.centerx, player.rect.centery)
                audio.play('level_complete')
                if current_level == 1:
                    trans_timer = 1.8
                    state = STATE_TRANSITION
                elif current_level == 2:
                    # Level 2 complete → play mid cutscene, then offer INSANE mode
                    audio.stop_music()
                    cutscene = CutsceneManager(MID_CUTSCENE, audio)
                    show_insane_prompt = False
                    state = STATE_MID_CUTSCENE
                else:
                    audio.stop_music()
                    state = STATE_WIN

            comet_timer += dt
            comet_interval = {1: COMET_SPAWN_INTERVAL, 2: 5, 3: 2.0}.get(current_level, 8)
            if comet_timer >= comet_interval:
                comet_timer = 0.0
                bias_x  = player.rect.centerx + random.randint(-200, 200)
                spawn_x = max(camera.offset_x + 40,
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

            if not player.alive or player.rect.top > WINDOW_HEIGHT + 50:
                audio.stop_music()
                last_frame  = screen.copy()
                death_timer = 0.0
                audio.play('you_died')   
                state       = STATE_DYING

            sx = sy = 0
            if shake_time > 0:
                shake_time -= dt
                sx = random.randint(-shake_mag, shake_mag)
                sy = random.randint(-shake_mag // 2, shake_mag // 2)

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

            # Darkness overlay: Level 2 (torch) and Level 3 (tight nearsight)
            if current_level in (2, 3):
                level.draw_darkness(screen, pr.centerx, pr.centery)

            # Level 3: pulsing blood-red edge vignette
            if current_level == 3:
                pulse_a = int(30 + 20 * math.sin(elapsed * 4.0))
                edge = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                pygame.draw.rect(edge, (180, 0, 0, pulse_a),
                                 (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT), 28)
                screen.blit(edge, (0, 0))

            draw_hud(screen, player, current_level)

            pause_hint = font_small.render("ESC  -  Pause Menu", True, (150, 160, 210))
            screen.blit(
                pause_hint,
                (WINDOW_WIDTH // 2 - pause_hint.get_width() // 2, 14)
            )

        # ── PAUSED ────────────────────────────────────────────────────────────
        elif state == STATE_PAUSED:
            if last_frame:
                screen.blit(last_frame, (0, 0))

            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 190))
            screen.blit(overlay, (0, 0))

            paused = font_big.render("PAUSED", True, (255, 220, 80))
            screen.blit(paused, (
                WINDOW_WIDTH // 2 - paused.get_width() // 2,
                WINDOW_HEIGHT // 2 - paused.get_height() // 2 - 24
            ))

            sub = font_small.render(
                "R  -  Retry level     M  -  Main Menu     ESC  -  Resume",
                True, GRAY
            )
            screen.blit(sub, (
                WINDOW_WIDTH // 2 - sub.get_width() // 2,
                WINDOW_HEIGHT // 2 + 28
            ))

            if keys[pygame.K_r]:
                level, camera, player, enemies, particles, comets, comet_timer = \
                    _load_level(current_level, audio)
                oxygen_beep_timer = oxygen_leak_timer = 0.0
                last_frame = None
                state = STATE_PLAYING
            elif keys[pygame.K_m]:
                last_frame = None
                menu_cursor = 0
                state = STATE_MENU

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
            if last_frame:
                screen.blit(last_frame, (0, 0))

            overlay_a = min(190, int(190 * (death_timer / 1.8)))
            overlay   = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, overlay_a))
            screen.blit(overlay, (0, 0))

            if death_timer > 0.7:
                t_prog  = min(1.0, (death_timer - 0.7) / 1.4)
                txt_a   = int(255 * t_prog)
                drift_y = int(22 * (1.0 - t_prog))

                you_died = font_elden.render("YOU  DIED", True, (185, 20, 20))
                you_died.set_alpha(txt_a)
                tx = WINDOW_WIDTH  // 2 - you_died.get_width()  // 2
                ty = WINDOW_HEIGHT // 2 - you_died.get_height() // 2 + drift_y
                screen.blit(you_died, (tx, ty))

            if death_timer >= 4.0:
                state = STATE_DEAD

        # ── DEAD ──────────────────────────────────────────────────────────────
        elif state == STATE_DEAD:
            if last_frame:
                screen.blit(last_frame, (0, 0))
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 190))
            screen.blit(overlay, (0, 0))

            you_died = font_elden.render("YOU  DIED", True, (185, 20, 20))
            screen.blit(you_died, (WINDOW_WIDTH  // 2 - you_died.get_width()  // 2,
                                   WINDOW_HEIGHT // 2 - you_died.get_height() // 2 - 24))
            sub = font_small.render(
                "R  -  Retry level     M  -  Main Menu",
                True, GRAY
            )
            screen.blit(sub, (WINDOW_WIDTH // 2 - sub.get_width() // 2,
                               WINDOW_HEIGHT // 2 + 28))

            if keys[pygame.K_r]:
                level, camera, player, enemies, particles, comets, comet_timer = \
                    _load_level(current_level, audio)
                oxygen_beep_timer = oxygen_leak_timer = 0.0
                last_frame = None
                state = STATE_PLAYING
            elif keys[pygame.K_m]:
                last_frame   = None
                menu_cursor  = 0
                state        = STATE_MENU

        # ── WIN ───────────────────────────────────────────────────────────────
        elif state == STATE_WIN:
            if show_insane_prompt and last_frame:
                screen.blit(last_frame, (0, 0))
                _draw_overlay(screen, "INSANE  MODE?", (255, 100, 100), font_big,
                              "The alien mothership awaits...  Y  -  Yes      N  -  No      M  -  Menu",
                              font_small, (200, 200, 200))
                if keys[pygame.K_y]:
                    current_level = 3
                    level, camera, player, enemies, particles, comets, comet_timer = \
                        _load_level(current_level, audio)
                    oxygen_beep_timer = oxygen_leak_timer = 0.0
                    show_insane_prompt = False
                    last_frame = None
                    state = STATE_PLAYING
                elif keys[pygame.K_n]:
                    show_insane_prompt = False
                    last_frame = None
                elif keys[pygame.K_m]:
                    show_insane_prompt = False
                    last_frame = None
                    menu_cursor = 0
                    state = STATE_MENU
            else:
                # Show "WELCOME HOME" over Auren's house background
                try:
                    home_bg = pygame.image.load(
                        os.path.join(os.path.dirname(__file__), 'assests', 'sprites', 'avatars', 'home.png')
                    ).convert()
                    home_bg = pygame.transform.scale(home_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
                    screen.blit(home_bg, (0, 0))
                except Exception:
                    screen.fill((4, 4, 28))
                if current_level < 3:
                    sub_msg = "R - Play again   |   3 - Try INSANE mode   |   M - Menu   |   ESC - Quit"
                else:
                    sub_msg = "You conquered INSANE!   R - Play again   |   M - Menu   |   ESC - Quit"
                _draw_overlay(screen, "WELCOME  HOME", (100, 255, 200), font_big,
                              sub_msg, font_small)
                if keys[pygame.K_r]:
                    level, camera, player, enemies, particles, comets, comet_timer = \
                        _load_level(current_level, audio)
                    oxygen_beep_timer = oxygen_leak_timer = 0.0
                    audio.start_music(current_level)
                    state = STATE_PLAYING
                elif keys[pygame.K_3] and current_level < 3:
                    current_level = 3
                    level, camera, player, enemies, particles, comets, comet_timer = \
                        _load_level(current_level, audio)
                    oxygen_beep_timer = oxygen_leak_timer = 0.0
                    state = STATE_PLAYING
                elif keys[pygame.K_m]:
                    menu_cursor = 0
                    state       = STATE_MENU

        elif state == STATE_INTRO_CUTSCENE or state == STATE_MID_CUTSCENE:
            cutscene.update(dt, just_pressed)

            if cutscene:
                cutscene.draw(screen)

            if cutscene and cutscene.finished:
                if state == STATE_INTRO_CUTSCENE:
                    level, camera, player, enemies, particles, comets, comet_timer = \
                        _load_level(current_level, audio)
                    oxygen_beep_timer = oxygen_leak_timer = 0.0
                    state = STATE_PLAYING
                elif state == STATE_MID_CUTSCENE:
                    show_insane_prompt = True
                    last_frame = screen.copy()
                    state = STATE_WIN

        # ── EXIT CONFIRM ──────────────────────────────────────────────────────
        elif state == STATE_EXIT_CONFIRM:
            if last_frame:
                screen.blit(last_frame, (0, 0))
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            screen.blit(overlay, (0, 0))
            msg = font_big.render("EXIT  GAME?", True, (255, 220, 80))
            screen.blit(msg, (WINDOW_WIDTH // 2 - msg.get_width() // 2,
                              WINDOW_HEIGHT // 2 - msg.get_height() // 2 - 20))
            label_y = WINDOW_HEIGHT // 2 + 20
            yes_txt = font_small.render("Y  -  Yes", True, (80, 255, 80))
            no_txt  = font_small.render("      Any other key  -  No", True, (255, 80, 80))
            both_w  = yes_txt.get_width() + no_txt.get_width()
            start_x = WINDOW_WIDTH // 2 - both_w // 2
            screen.blit(yes_txt, (start_x, label_y))
            screen.blit(no_txt,  (start_x + yes_txt.get_width(), label_y))

        pygame.display.flip()


if __name__ == "__main__":
    main()
