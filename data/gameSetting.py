# ─── Window ───────────────────────────────────────────────────────────────────
TITLE         = "Lunar Escape"
WINDOW_WIDTH  = 800
WINDOW_HEIGHT = 600
FPS           = 60

# ─── Tile ─────────────────────────────────────────────────────────────────────
TILE_SIZE     = 40
LEVEL_COLS    = 100

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
OXYGEN_DRAIN_RATE     = 2.5
OXYGEN_REFILL_AMT     = 35
INVINCIBLE_DURATION   = 1.5

# ─── Enemy ────────────────────────────────────────────────────────────────────
ENEMY_SPEED   = 75
ENEMY_PATROL  = 110

# ─── Comet (motion-tracking hazard) ──────────────────────────────────────────
COMET_SPAWN_INTERVAL  = 10
COMET_STEER_FORCE     = 460
COMET_MAX_SPEED       = 500
COMET_RADIUS          = 14
COMET_DAMAGE_RADIUS   = 90
COMET_FRACTURE_RADIUS = 100

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

# ─── Level 1 palette ──────────────────────────────────────────────────────────
LVL1_BG_COLOR    = (8,   5,  22)
LVL1_TILE_COLOR  = (88,  90, 102)
LVL1_TILE_ACCENT = (55,  57,  68)

# ─── Level 2 palette ──────────────────────────────────────────────────────────
LVL2_BG_COLOR    = (5,   8,  38)
LVL2_TILE_COLOR  = (65,  38,  92)
LVL2_TILE_ACCENT = (42,  22,  60)

# ─── Level 3 palette (Blood Moon) ─────────────────────────────────────────────
LVL3_BG_COLOR    = (18,  2,   2)
LVL3_TILE_COLOR  = (78,  48,  48)
LVL3_TILE_ACCENT = (48,  22,  22)

# ─── Tilemap legend ───────────────────────────────────────────────────────────
#   X = solid tile       P = player spawn
#   E = enemy spawn      O = oxygen tank
#   T = spike trap       > = level exit

LEVEL_1_MAP = [
    "                                                                                                    ",
    "                                                                                                    ",
    "                                                                                                    ",
    "                                                                                                    ",
    "          O             O                                    O                          O           ",
    "         XXXX          XXXX           XXXX                  XXXX                      XXXX          ",
    "        E             E              E                     E              E                         ",
    "       XXXX          XXXX           XXXX                  XXXX           XXXX       XXXX            ",
    "                                                                                                    ",
    "     XXX           XXXX           XXXX                  XXXX           XXX                          ",
    "P    E      TTT     E      TTT     E        TTT          E     TTT      E         TTT     E      >  ",
    "XXXXX   XXXXXXXXXXX    XXXXXXXXXXX    XXXXXXXXXXXXXXXXXX    XXXXXXXXXXX   XXXXXXXXXXXXXXXXXXXXXXXXXX",
]

LEVEL_2_MAP = [
    "                                                                                                    ",
    "                                                                                                    ",
    "                                                                                                    ",
    "               O                E               E                 O                E                ",
    "             XXXXXX          XXXXXXX          XXXXXXX          XXXXXXX          XXXXXXX             ",
    "     E              E               E                E               E               E              ",
    "   XXXXXX        XXXXXXX         XXXXXXX          XXXXXXX         XXXXXXX         XXXXXXX           ",
    "          O               E                 O               E                 E               O     ",
    "        XXXXXX          XXXXXXX          XXXXXXX          XXXXXXX          XXXXXXX          XXXXXX  ",
    "                  E                O                E                O                E             ",
    "                 XXXX             XXXX             XXXX             XXXX             XXXX           ",
    "P   E                                                                                            >  ",
    "XXXXXXXXXXXXXXXXX    XXXXXXXXXXXXX    XXXXXXXXXXXXX    XXXXXXXXXXXXX    XXXXXXXXXXXXX    XXXXXXXXXXX",
]

LEVEL_3_MAP = [
    "                                                                      ",
    "                                                                      ",
    "                                                                      ",
    "                                                                      ",
    "    E           O                              O                      ",
    "   XXX         XXX      XXX       XXX         XXX         XXX         ",
    "  E           O                  E           O           E            ",
    " XXX         XXX      XXX       XXX         XXX         XXX     XXX   ",
    "    E                O                     O          E               ",
    "   XXX      XXX      XXX    E   XXX        XXX      E  XXX      XXX   ",
    "      XX       XX          XX          XX          XX          XX     ",
    "P  T E   TT E      TT  ETT      TTE TT      TTE TT      TTE TT    T>  ",
    "XXXXXX  XXXXXXX  XXXXXXXXXX  XXXXXXXXXX  XXXXXXXXXX  XXXXXXXXXX  XXXXX",
]
