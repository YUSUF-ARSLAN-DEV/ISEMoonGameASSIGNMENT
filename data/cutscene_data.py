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
    # ║  SCENE 1 — Auren's House (emergency call)                   ║
    # ║  Background: home.png (Auren's home)                        ║
    # ║  Story: Auren, an astronaut, gets an urgent distress call   ║
    # ║  He's professional — this is his job, not a fantasy         ║
    # ╚══════════════════════════════════════════════════════════════╝
    ('home', [
        # Auren gets the call — professional astronaut, just doing his job
        ('auren', "Emergency beacon from the lunar station. Life support is failing."),
        # He understands the stakes immediately (no "I wish something would happen")
        ('auren', "I'm the closest astronaut on standby. Mission control is sending me up."),
    ]),

    # ╔══════════════════════════════════════════════════════════════╗
    # ║  SCENE 2 — Briefing with the Spy                            ║
    # ║  Background: home.png (same location)                       ║
    # ║  Story: Spy delivers the full picture — station went dark   ║
    # ╚══════════════════════════════════════════════════════════════╝
    ('home', [
        # Spy arrives with intel — no surprises, Auren was expecting him
        ('spy',   "Auren. The situation is worse than we thought. The station went dark."),
        # Auren responds like a pro, not a surprised civilian
        ('auren', "What do you mean dark? What happened up there?"),
        # Spy admits they don't know — raising tension
        ('spy',   "We don't know. All communication cut two hours ago."),
        # Auren takes charge — he knows his job
        ('auren', "Alright. Prep the shuttle. I'll suit up."),
    ]),

    # ╔══════════════════════════════════════════════════════════════╗
    # ║  SCENE 3 — Mission Prep at the Base                         ║
    # ║  Background: station.png (the prep facility)                 ║
    # ║  Story: Standard equipment briefing before launch            ║
    # ╚══════════════════════════════════════════════════════════════╝
    ('station', [
        # Spy lists standard issue gear — establishes the tools
        ('spy',   "Standard repair kit, oxygen for 72 hours, emergency beacon."),
        # Spy explains the emergency protocol
        ('spy',   "If anything goes wrong, you trigger that beacon and we pull you out."),
        # Auren sums up the mission — simple, professional
        ('auren', "Fix the station, check for survivors, get home. Simple."),
    ]),

    # ╔══════════════════════════════════════════════════════════════╗
    # ║  SCENE 4 — Moon Landing (the trap)                          ║
    # ║  Background: moon_surface (starry sky)                      ║
    # ║  Story: Auren arrives — station is empty, it was a trap     ║
    # ║  The Moon spirit takes pity and helps him escape             ║
    # ╚══════════════════════════════════════════════════════════════╝
    ('moon_surface', [
        # Auren realizes something is wrong immediately
        ('auren', "The station is empty... but the equipment is still running. Where is everyone?"),
        # The Moon speaks for the first time — surprising both Auren and the player
        ('moon',  "Auren... can you hear me? I am the spirit of this world."),
        # Auren's professional confusion — he trusts his instruments
        ('auren', "Who said that? There's no one here."),
        # Moon explains the trap with pity in her voice
        ('moon',  "The ones who came before — they took your people. They set this beacon as a trap."),
        # Moon's sorrow for the ones she couldn't save
        ('moon',  "I could not warn them. But you... you still have time."),
        # Auren snaps back to mission mode
        ('auren', "Time for what?"),
        # Moon offers help — the escape plan
        ('moon',  "To escape. There is an old pod near the far ridge. I can guide you there."),
        # Moon warns about the danger ahead
        ('moon',  "The creatures will hunt you. But I will help where I can."),
        # Auren accepts — no hesitation, survival mode
        ('auren', "Then guide me. I'm not dying on this rock."),
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
        # Spy can't believe Auren made it back alive
        ('spy',   "You made it. I can't believe you made it."),
        # Auren reveals the truth — it was a deliberate trap
        ('auren', "Barely. It was a trap from the start. They lured me there."),
        # Spy admits they suspected but couldn't confirm
        ('spy',   "We know. The mothership is sending one last signal."),
        # Spy raises the stakes — Earth is now in danger
        ('spy',   "If it reaches the hive, they'll know where Earth is."),
        # Auren doesn't hesitate — he's already decided
        ('auren', "Then I need to finish this."),
        # Spy offers one last support run
        ('spy',   "One last run. We'll drop you at the hot zone. Then you're done."),
        # Auren accepts — determined, professional
        ('auren', "Let's end this."),
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
