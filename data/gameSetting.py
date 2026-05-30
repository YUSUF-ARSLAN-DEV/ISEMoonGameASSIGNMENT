# ─── Window ───────────────────────────────────────────────────────────────────
TITLE         = "Lunar Escape"
WINDOW_WIDTH  = 1600
WINDOW_HEIGHT = 900
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
OXYGEN_DRAIN_RATE     = 8.5
OXYGEN_REFILL_AMT     = 35
INVINCIBLE_DURATION   = 1.5

# ─── Enemy ────────────────────────────────────────────────────────────────────
ENEMY_SPEED   = 75
ENEMY_PATROL  = 110

# ─── Comet (motion-tracking hazard) ──────────────────────────────────────────
COMET_SPAWN_INTERVAL  = 8    # seconds between spawns on L1 (faster than before)
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

# ─── Level 1 palette (Moon Surface) ──────────────────────────────────────────
LVL1_BG_COLOR    = (8,   5,  22)
LVL1_TILE_COLOR  = (88,  90, 102)
LVL1_TILE_ACCENT = (55,  57,  68)

# ─── Level 2 palette (Lunar Cavern) ──────────────────────────────────────────
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
#
# Spike pit structure (3 rows):
#   Row n   : main floor with 2-tile gaps
#   Row n+1 : T (spike) in those gaps only
#   Row n+2 : X everywhere (sub-floor catches player)

LEVEL_1_MAP = [
    "                                                                                                    ",
    "                                                                                                    ",
    "                                                                                                    ",
    "         O             O                 O                 O                 O             O        ",
    "        XXXX          XXXX              XXXX              XXXX              XXXX          XXXX      ",
    "         E             E                 E                 E                 E             E        ",
    "              XXXXX           XXXXX            XXXXX             XXXXX            XXXXX             ",
    "               O               O                O                 O                O                ",
    "   XXX      XXX     XXX        XXX        XXX         XXX         XXX           XXX          XXX    ",
    "P           E         E          E          E           E             E              E           >  ",
    "XXXXXXX  XXXXXXXX  XXXXXXXX  XXXXXXXXX  XXXXXXXXXX  XXXXXXXXXXX  XXXXXXXXXXXX  XXXXXXXXXXXXXXXXXXXXX",
    "       TT        TT        TT         TT          TT           TT            TT                     ",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
]

LEVEL_2_MAP = [
    "                                                                                                    ",
    "                                                                                                    ",
    "                 O                   O                   O                   O                      ",
    "           E   XXXXX        E      XXXXX      E        XXXXX    E          XXXXX  E                 ",
    "           O                O                 O                 O                 O                 ",
    "        XXXXXXX          XXXXXXX           XXXXXXX           XXXXXXX           XXXXXXX              ",
    "            E              E              E              E              E              E            ",
    "          XXXXXX         XXXXXX         XXXXXX         XXXXXX         XXXXXX         XXXXXX         ",
    "            O              O              O              O              O              O            ",
    "     XXXX         XXXX          XXXX          XXXX          XXXX          XXXX          XXXX        ",
    " P                  E             E             E             E             E             E      >  ",
    "XXXXXXXXXXXXXXX   XXXXXXXXXX   XXXXXXXXXXX   XXXXXXXXXXX   XXXXXXXXXXX   XXXXXXXXXX   XXXXXXXXXXXXXX",
    "               TTT          TTT           TTT           TTT           TTT          TTT              ",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
]

LEVEL_3_MAP = [
    "                                                                                          ",
    "                                                                                          ",
    "                                                                                          ",
    "                                                                                          ",
    "          O           O            O            O             O                           ",
    "         XXX         XXX          XXX          XXX           XXX           XXX            ",
    "       O          E          O          E           O           E           O             ",
    "      XXXX       XXXX       XXXX       XXXX        XXXX        XXXX        XXXX           ",
    "    E        E        E        E         E         E          E          E                ",
    "   XXXX     XXXX     XXXX     XXXX      XXXX      XXXX       XXXX       XXXX              ",
    "  XX      XX      XX     XX      XX       XX       XX        XX        XX       XX        ",
    "P           E       E      E        E        E        E        E         E         E   >  ",
    "XXXXXXXX  XXXXX  XXXXXX  XXXXXX  XXXXXXX  XXXXXXX  XXXXXXX  XXXXXXXX  XXXXXXX  XXXXXXXXXXX",
    "        TT     TT      TT      TT       TT       TT       TT        TT       TT           ",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
]
