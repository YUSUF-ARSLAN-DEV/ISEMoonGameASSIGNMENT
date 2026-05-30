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
#   Scene 1: Auren is bored at home
#   Scene 2: A spy breaks in and tells him about the alien threat
#   Scene 3: At the secret base, the Spy equips Auren for the mission
#   Scene 4: Auren lands on the moon and the Moon spirit explains what's happening
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
    # ║  SCENE 1 — Auren's House (boredom)                          ║
    # ║  Background: home.png (Auren's living room)                  ║
    # ║  Story: We establish that Auren is an ordinary guy           ║
    # ║  who wants adventure — setting up his Hero's Journey.        ║
    # ╚══════════════════════════════════════════════════════════════╝
    ('home', [
        # Each tuple = (WHO speaks, "WHAT they say")
        ('auren', "Man... another boring night."),
        ('auren', "I wish something exciting would happen for once."),
    ]),

    # ╔══════════════════════════════════════════════════════════════╗
    # ║  SCENE 2 — Spy arrives at Auren's house                     ║
    # ║  Background: home.png (same location, different scene)       ║
    # ║  Story: The inciting incident — the call to adventure        ║
    # ╚══════════════════════════════════════════════════════════════╝
    ('home', [
        # Spy appears and delivers the urgent mission briefing
        ('spy',   "Auren. We need you."),
        # Auren is surprised — he wasn't expecting a secret agent in his living room
        ('auren', "Whoa! How did you get in here?!"),
        # Spy explains the stakes (the "why" of the whole game)
        ('spy',   "Aliens are corrupting the moon. They're pulling it closer to Earth."),
        ('spy',   "If we don't stop them, the moon will crash into us."),
        ('spy',   "You're our only hope. We need you up there."),
        # Auren doubts himself — relatable hero moment
        ('auren', "The moon?! I'm just a regular guy!"),
        # Spy reassures him — the hero accepts the call
        ('spy',   "Not anymore. Gear up."),
    ]),

    # ╔══════════════════════════════════════════════════════════════╗
    # ║  SCENE 3 — Mission Prep at the Secret Base                  ║
    # ║  Background: station.png (high-tech spy headquarters)        ║
    # ║  Story: The "equipment montage" — establishing the tools     ║
    # ╚══════════════════════════════════════════════════════════════╝
    ('station', [
        # Spy lists what Auren gets (this explains the HUD/game mechanics)
        ('spy',   "We've equipped you with everything. Oxygen suit, weapons, coms."),
        # Spy states the mission objective (this explains what the player must do)
        ('spy',   "Your mission: reach the alien hive and break their hold on the moon."),
        # Auren accepts — character arc moment
        ('auren', "Alright... let's save the world."),
    ]),

    # ╔══════════════════════════════════════════════════════════════╗
    # ║  SCENE 4 — Moon Landing                                     ║
    # ║  Background: moon_surface (drawn by code — starry sky)       ║
    # ║  Story: The moon itself is alive and asks for help           ║
    # ╚══════════════════════════════════════════════════════════════╝
    ('moon_surface', [
        # The Moon reveals itself as a sentient being
        ('moon',  "Welcome, child. I am the spirit of the Moon."),
        # Auren is shocked — natural reaction to a talking celestial body
        ('auren', "The moon... talks?"),
        # Moon explains the alien backstory (the lore of the game world)
        ('moon',  "The aliens have corrupted my core. They are pulling me toward Earth."),
        ('moon',  "If they succeed, we will collide. Everything will be destroyed."),
        # Moon gives the gameplay direction (go down, find the hive mind)
        ('moon',  "You must destroy their hive mind in the caverns below. It is our only hope."),
        # Auren commits to the mission — final character affirmation
        ('auren', "I'll take care of it."),
        # Moon's farewell — emotional sendoff before gameplay starts
        ('moon',  "Be careful, Auren. I will guide you as I can."),
    ]),
]


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 3 — MID CUTSCENE (plays after Level 2 is completed)
# ──────────────────────────────────────────────────────────────────────────────
# This cutscene plays when the player finishes Level 2.
# Story: Auren returns to Earth, Spy congratulates him, then reveals
# there's ONE MORE mission — a suicide run against the alien mothership.
# This leads to the choice: try INSANE mode (Level 3) or finish the game.
#
# WHY separate from INTRO? Because the two cutscenes play at completely
# different times in the game loop, and they might be created with
# different context (e.g. we might add variables later).
# ──────────────────────────────────────────────────────────────────────────────

MID_CUTSCENE = [
    # ╔══════════════════════════════════════════════════════════════╗
    # ║  SCENE 1 — Back at the Secret Base                          ║
    # ║  Background: station.png (same as intro scene 3)             ║
    # ║  Story: Victory celebration → surprise final mission         ║
    # ╚══════════════════════════════════════════════════════════════╝
    ('station', [
        # Spy congratulates the player — positive reinforcement
        ('spy',   "Auren! You did it! The moon is back in orbit!"),
        ('spy',   "You saved us all. Earth owes you everything."),
        # Auren shows humility — character growth from the cocky "I wish something would happen" guy
        ('auren', "It was a team effort."),
        # The twist: it's not over yet. This creates the "one more thing..." tension
        ('spy',   "There's one more thing... the mothership is sending one final signal."),
        # Spy frames it as a suicide mission — raising stakes
        ('spy',   "It's a suicide run. Shut it down, the aliens lose their grip for good."),
        # Auren's dramatic pause (silence = weight of the decision)
        ('auren', "..."),
        # Auren accepts — final hero moment before INSANE mode
        ('auren', "Send me in."),
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
