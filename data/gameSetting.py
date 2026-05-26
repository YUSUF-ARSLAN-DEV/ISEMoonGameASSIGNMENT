# ─── Window ───────────────────────────────────────────────────────────────────
TITLE         = "Lunar Escape"
WINDOW_WIDTH  = 800
WINDOW_HEIGHT = 600
FPS           = 60

# ─── Tile ─────────────────────────────────────────────────────────────────────
TILE_SIZE     = 48          # pixels per tile cell
LEVEL_COLS    = 40          # tiles wide per level

# ─── Physics ──────────────────────────────────────────────────────────────────
GRAVITY       = 900         # pixels/s²
PLAYER_SPEED  = 200         # pixels/s (horizontal)
JUMP_VELOCITY = -420        # pixels/s  (negative = upward)
TERMINAL_VEL  = 800         # max fall speed

# ─── Player ───────────────────────────────────────────────────────────────────
PLAYER_WIDTH          = 28
PLAYER_HEIGHT         = 40
PLAYER_MAX_HEALTH     = 3
PLAYER_MAX_OXYGEN     = 100
OXYGEN_DRAIN_RATE     = 4   # units per second
OXYGEN_REFILL_AMT     = 55  # gained from one oxygen pickup
INVINCIBLE_DURATION   = 1.5 # seconds of invincibility after being hit

# ─── Enemy ────────────────────────────────────────────────────────────────────
ENEMY_SPEED   = 75          # pixels/s
ENEMY_PATROL  = 110         # pixels from spawn before turning

# ─── Colors ───────────────────────────────────────────────────────────────────
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
GRAY       = (160, 160, 160)
DARK_GRAY  = (55,  55,  65)
RED        = (220, 50,  50)
GREEN      = (50,  210, 80)
BLUE       = (50,  100, 220)
CYAN       = (0,   220, 255)
YELLOW     = (255, 220, 50)
ORANGE     = (255, 140, 0)
PURPLE     = (140, 80,  200)

# ─── Level 1 palette (Moon Surface) ──────────────────────────────────────────
LVL1_BG_COLOR    = (8,   5,  22)    # near-black starfield
LVL1_TILE_COLOR  = (88,  90, 102)   # gray moon rock
LVL1_TILE_ACCENT = (55,  57,  68)   # darker edge highlight

# ─── Level 2 palette (Lunar Cavern) ──────────────────────────────────────────
LVL2_BG_COLOR    = (5,   8,  38)    # deep space blue
LVL2_TILE_COLOR  = (65,  38,  92)   # purple crystal rock
LVL2_TILE_ACCENT = (42,  22,  60)   # dark edge

# ─── Tilemap legend ───────────────────────────────────────────────────────────
#   X = solid tile       P = player spawn
#   E = enemy spawn      O = oxygen tank
#   > = level exit

LEVEL_1_MAP = [
    "                                        ",   # row  0
    "                                        ",   # row  1
    "        XX                              ",   # row  2
    "                     XX                 ",   # row  3
    "                                        ",   # row  4
    "   XXXXX    XX             XXXXX        ",   # row  5
    "                                        ",   # row  6
    "  XXX                            XXX    ",   # row  7
    "  E                     E               ",   # row  8
    "  XXXXX    XXXXXX        XXXXXXX  O     ",   # row  9
    "                                  X     ",   # row 10
    "P                                    >  ",   # row 11
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",   # row 12  (ground)
]

LEVEL_2_MAP = [
    "                                        ",   # row  0
    "   XX                         XX        ",   # row  1
    "                                        ",   # row  2
    "       XXXXX           XXXXX            ",   # row  3
    "   E                               E    ",   # row  4
    "   XX    XXX           XXX         XX   ",   # row  5
    "                                        ",   # row  6
    "     XXXXX    E     XXXXXX              ",   # row  7
    "                                   O    ",   # row  8
    "   XXX      XXXXX         XXXXX    X    ",   # row  9
    "                                        ",   # row 10
    "P                                    >  ",   # row 11
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",   # row 12  (ground)
]
