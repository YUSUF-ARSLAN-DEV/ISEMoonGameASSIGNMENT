# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  CUTSCENE DATA — all story dialogue in one place                           ║
# ║                                                                             ║
# ║  This file contains ONLY data (no game logic). It tells the cutscene        ║
# ║  engine WHAT to show, not HOW to show it.                                   ║
# ║                                                                             ║
# ║  HOW TO ADD A NEW CUTSCENE:                                                 ║
# ║    1. Add scene tuples to a new list below (e.g. ENDING_CUTSCENE)           ║
# ║    2. Each scene = (background_key, list_of_dialogue)                       ║
# ║    3. Each dialogue = (speaker_id, "text they say")                         ║
# ║    4. Import the list in Main.py and pass it to CutsceneManager             ║
# ║                                                                             ║
# ║  BACKGROUND KEYS (what image shows behind the text):                        ║
# ║    'home'         → assests/sprites/avatars/home.png  (Auren's house)       ║
# ║    'station'      → assests/sprites/avatars/station.png (secret base)       ║
# ║    'moon_surface' → drawn by code (starry sky + Earth, no image file)       ║
# ║                                                                             ║
# ║  SPEAKER IDS (who is talking):                                              ║
# ║    'auren' → portrait on LEFT,  name "Auren"                                ║
# ║    'spy'   → portrait on RIGHT, name "Spy"                                  ║
# ║    'moon'  → portrait on RIGHT, name "Moon"                                 ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 1 — SPEAKER CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────
# This dictionary defines WHO can speak in our cutscenes.
# Each entry tells the engine:
#   - which image file to use as their portrait
#   - what side of the dialog box to put it on
#   - what display name to show under the portrait
#
# WHY: By keeping this here (instead of in the engine), you can add new
# characters just by adding a new entry. No code changes needed.
# ──────────────────────────────────────────────────────────────────────────────

SPEAKERS = {
    # ── Auren (the player character / hero) ──
    # Side: left  → portrait appears on the LEFT side of the dialog box
    # File: auren.png  → loaded from assests/sprites/avatars/auren.png
    'auren': {
        'side': 'left',          # Which side of the box the avatar sits on
        'name': 'Auren',         # Display name shown under the portrait
        'avatar_file': 'auren.png',  # Filename inside the avatars folder
    },

    # ── Spy (the CIA agent who recruits you) ──
    # Side: right → portrait appears on the RIGHT side of the dialog box
    # (because Spy is the "other" character, not the hero)
    'spy': {
        'side': 'right',
        'name': 'Spy',
        'avatar_file': 'spy.png',
    },

    # ── Moon (the talking moon spirit) ──
    # Side: right → also on the right side (not the hero)
    'moon': {
        'side': 'right',
        'name': 'Moon',
        'avatar_file': 'moon.png',
    },
}


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 2 — INTRO CUTSCENE (plays before Level 1)
# ──────────────────────────────────────────────────────────────────────────────
# This cutscene tells the STORY SO FAR:
#   Scene 1: Auren (an astronaut) gets an emergency call about the lunar station
#   Scene 2: Spy arrives to brief him — the station went dark
#   Scene 3: At the base, Auren suits up and heads out
#   Scene 4: Auren arrives on the moon — it's a trap. The Moon spirit helps him
#
# STRUCTURE:
#   INTRO_CUTSCENE is a LIST of SCENES.
#   Each SCENE is a TUPLE: (background_key, [list_of_dialog_lines])
#   Each DIALOG LINE is a TUPLE: (speaker_id, "spoken text")
#
# WHY tuples? Tuples can't be changed accidentally (immutable), which
# prevents bugs where dialogue gets modified during gameplay.
# ──────────────────────────────────────────────────────────────────────────────

INTRO_CUTSCENE = [
    # ╔══════════════════════════════════════════════════════════════╗
    # ║  SCENE 1 — Auren's House (minding his own business)         ║
    # ║  Background: home.png (Auren's home)                        ║
    # ║  Story: Auren is off-duty, Spy bursts in with urgent news   ║
    # ╚══════════════════════════════════════════════════════════════╝
    ('home', [
        ('auren', "Just another quiet night..."),
        ('spy',   "Auren. The lunar station went dark. Everyone on board is unaccounted for."),
        ('auren', "I was off-duty. What happened?"),
        ('spy',   "No idea. That's why I'm here. You're the closest astronaut we've got."),
        ('auren', "...Alright. Talk to me on the way."),
    ]),

    # ╔══════════════════════════════════════════════════════════════╗
    # ║  SCENE 2 — Briefing                                         ║
    # ║  Background: home.png (same location)                       ║
    # ║  Story: Spy fills in the details as Auren gears up          ║
    # ╚══════════════════════════════════════════════════════════════╝
    ('home', [
        ('spy',   "Station went silent two hours ago. Life support is failing. No distress call."),
        ('auren', "No distress call? That doesn't make sense."),
        ('spy',   "Nothing about this makes sense. That's why we need you up there."),
        ('auren', "Well, I'm not gonna find answers sitting here."),
    ]),

    # ╔══════════════════════════════════════════════════════════════╗
    # ║  SCENE 3 — Mission Prep at the Base                         ║
    # ║  Background: station.png (the prep facility)                 ║
    # ║  Story: Standard equipment briefing before launch            ║
    # ╚══════════════════════════════════════════════════════════════╝
    ('station', [
        ('spy',   "Standard gear. Oxygen, beacon, tools. You know the drill."),
        ('auren', "Check the station, figure out what happened, get home alive. Got it."),
    ]),

    # ╔══════════════════════════════════════════════════════════════╗
    # ║  SCENE 4 — Moon Landing (the trap)                          ║
    # ║  Background: moon_surface (starry sky)                      ║
    # ║  Story: Station is empty — it was a trap. Moon spirit helps ║
    # ╚══════════════════════════════════════════════════════════════╝
    ('moon_surface', [
        ('auren', "The station's empty... Everything's running, but there's no one here."),
        ('moon',  "Auren... I am the spirit of this world. You are in danger."),
        ('auren', "Who's there?"),
        ('moon',  "The beacon was a trap. Others came before you. They did not leave."),
        ('auren', "Then I'm not sticking around to find out what happened to them."),
        ('moon',  "The creatures are coming. I can guide you to an escape pod."),
        ('auren', "Guide me. I'm getting off this rock."),
    ]),
]


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 3 — MID CUTSCENE (plays after Level 2 is completed)
# ──────────────────────────────────────────────────────────────────────────────
# This cutscene plays when the player finishes Level 2.
# Story: Auren returns to Earth, Spy debriefs him.
# The story ends here — no hooks to additional content.

MID_CUTSCENE = [
    # ╔══════════════════════════════════════════════════════════════╗
    # ║  SCENE 1 — Back at the Secret Base                          ║
    # ║  Background: station.png (same as intro scene 3)             ║
    # ║  Story: Auren returns — mission accomplished                 ║
    # ╚══════════════════════════════════════════════════════════════╝
    ('station', [
        ('spy',   "You're back. We thought we lost you."),
        ('auren', "So did I. That station was a trap. Whatever took the crew is still out there."),
        ('spy',   "We've locked down all deep-space beacons. If anything tries that again, we'll know."),
        ('auren', "Good. Because I'm not going back up there."),
        ('spy',   "Get some rest. You've done enough."),
        ('auren', "Yeah. I think I have."),
    ]),
]


# ══════════════════════════════════════════════════════════════════════════════
# END OF CUTSCENE DATA
# ══════════════════════════════════════════════════════════════════════════════
# 
# HOW THE ENGINE USES THIS FILE:
#   1. Main.py imports INTRO_CUTSCENE and MID_CUTSCENE from here
#   2. Main.py creates a CutsceneManager(scenes_list, audio_manager)
#   3. Each frame, Main.py calls cutscene.update(dt, just_pressed_keys)
#   4. Each frame, Main.py calls cutscene.draw(screen)
#   5. When cutscene.finished is True, Main.py transitions to gameplay
# 
# THAT'S IT. The engine handles everything else automatically.
# ══════════════════════════════════════════════════════════════════════════════
