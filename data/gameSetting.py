# ─── Window ───────────────────────────────────────────────────────────────────
TITLE         = "Lunar Escape"
WINDOW_WIDTH  = 800
WINDOW_HEIGHT = 600
FPS           = 60

# ─── Tile ─────────────────────────────────────────────────────────────────────
TILE_SIZE     = 40
LEVEL_COLS    = 55

# ─── Physics ──────────────────────────────────────────────────────────────────
GRAVITY       = 900
PLAYER_SPEED  = 200
JUMP_VELOCITY = -420
TERMINAL_VEL  = 800

# ─── Player ───────────────────────────────────────────────────────────────────
PLAYER_WIDTH          = 28
PLAYER_HEIGHT         = 32
PLAYER_MAX_HEALTH     = 3
PLAYER_MAX_OXYGEN     = 100
OXYGEN_DRAIN_RATE     = 1.5
OXYGEN_REFILL_AMT     = 55
INVINCIBLE_DURATION   = 1.5

# ─── Enemy ────────────────────────────────────────────────────────────────────
ENEMY_SPEED   = 75
ENEMY_PATROL  = 110

# ─── Comet (motion-tracking hazard) ──────────────────────────────────────────
# The comet continuously recalculates its direction toward the player each
# frame — normalise(target - self) * force — this is the "motion tracking"
# technique named in the assignment overview.
COMET_SPAWN_INTERVAL  = 18   # seconds between spawns
COMET_STEER_FORCE     = 380  # px/s² steering acceleration toward player
COMET_MAX_SPEED       = 500  # px/s terminal speed
COMET_RADIUS          = 14   # collision / draw radius
COMET_DAMAGE_RADIUS   = 90   # px from impact that hurts the player
COMET_FRACTURE_RADIUS = 100  # px from impact where tiles are removed

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
LVL1_BG_COLOR    = (8,   5,  22)
LVL1_TILE_COLOR  = (88,  90, 102)
LVL1_TILE_ACCENT = (55,  57,  68)

# ─── Level 2 palette (Lunar Cavern) ──────────────────────────────────────────
LVL2_BG_COLOR    = (5,   8,  38)
LVL2_TILE_COLOR  = (65,  38,  92)
LVL2_TILE_ACCENT = (42,  22,  60)

# ─── Tilemap legend ───────────────────────────────────────────────────────────
#   X = solid tile       P = player spawn
#   E = enemy spawn      O = oxygen tank
#   > = level exit

LEVEL_1_MAP = [
    "                                        ",
    "                                        ",
    "              E                         ",
    "             XXX                        ",
    "                                        ",
    "                         O              ",
    "                 XXXXXXXXX              ",
    "                                        ",
    "           XXXXXX                       ",
    "P                          E          > ",
    "XXXXXXXXXXXXX    XXXXXXXXXXXXXXXXXXXXXXXX",
]

LEVEL_2_MAP = [
    "                                                       ",
    "                                                 X     ",
    "                                       XXXXXXX       > ",
    "                                 XXXXXXXX              ",
    "                          O                            ",
    "                      XXXXXXXXX                        ",
    "                  XXXXX                                ",
    "                                                       ",
    "           XXXXXX                                      ",
    "P                         E                            ",
    "XXXXXXXX           XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
]
