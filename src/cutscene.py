# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  CUTSCENE ENGINE — Undertale-style dialogue cutscenes                      ║
# ║                                                                             ║
# ║  WHAT THIS FILE DOES:                                                       ║
# ║  It creates a "cutscene" — a short story scene where characters talk        ║
# ║  to each other in a text box at the bottom of the screen. The text          ║
# ║  appears one letter at a time (like someone is typing it). You press        ║
# ║  SPACE/ENTER/Z to go to the next line of dialogue.                          ║
# ║                                                                             ║
# ║  HOW IT WORKS (simple explanation):                                        ║
# ║  1. You give it a list of "scenes" (each scene has a background + lines)   ║
# ║  2. Every frame you call update() to reveal text + handle key presses      ║
# ║  3. Every frame you call draw() to render the background, avatars, text    ║
# ║  4. When all scenes and lines are done, .finished becomes True             ║
# ║                                                                             ║
# ║  LAYOUT OF THE SCREEN:                                                     ║
# ║  ┌──────────────────────────────────────────────────────────────────┐       ║
# ║  │                         BACKGROUND                                │       ║
# ║  │                    (full screen image)                            │       ║
# ║  │                                                                   │       ║
# ║  │  ┌─ DIALOG BOX (bottom 25%) ─────────────────────────────────┐   │       ║
# ║  │  │                                                            │   │       ║
# ║  │  │  ┌──────┐   Man... another                                │   │       ║
# ║  │  │  │      │   boring night...                               │   │       ║
# ║  │  │  │AUREN │                                                 │   │       ║
# ║  │  │  │      │   ▾                                             │   │       ║
# ║  │  │  └──────┘                                                 │   │       ║
# ║  │  │   Auren                                                   │   │       ║
# ║  │  └────────────────────────────────────────────────────────────┘   │       ║
# ║  └──────────────────────────────────────────────────────────────────┘       ║
# ║                                                                             ║
# ║  AVATAR ON LEFT  = Auren is speaking (the hero)                            ║
# ║  AVATAR ON RIGHT = Spy or Moon is speaking (other characters)              ║
# ║  TEXT is always on the OPPOSITE side from the avatar                       ║
# ║                                                                             ║
# ║  FILE DEPENDENCIES:                                                        ║
# ║    - data/cutscene_data.py  (for SPEAKERS config + dialogue text)          ║
# ║    - src/audio.py           (for typing sound)                             ║
# ║    - assests/sprites/avatars/*.png  (portrait images)                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# ── IMPORTS ──────────────────────────────────────────────────────────────────
# These are Python's built-in tools that our code needs to work.

import os   # Gives us access to file paths (like finding image files on your computer)
import pygame  # The game library — handles graphics, sounds, keyboard input
import random  # Used to draw random stars in the moon background (not for gameplay randomness)

# Import the SPEAKERS dictionary from our data file.
# SPEAKERS tells us: which avatar image to use, what side to put it on,
# and what display name to show for each character.
from data.cutscene_data import SPEAKERS


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — CONSTANTS (settings you can tweak)
# ══════════════════════════════════════════════════════════════════════════════
#
# All the numbers below control how the cutscene LOOKS and FEELS.
# Change them to customize the visual style or typing speed.
# They are defined at the TOP of the file so they're easy to find.
#
# ══════════════════════════════════════════════════════════════════════════════

# ── Dialog box size ──────────────────────────────────────────────────────────
# The dialog box takes up the bottom portion of the screen.
# 0.25 = 25% of the screen height = 225 pixels (since our screen is 900 tall).
# Bigger number = taller box = more text visible at once.
BOX_HEIGHT_RATIO = 0.25

# ── Dialog box colors ────────────────────────────────────────────────────────
# These control what the text box at the bottom of the screen looks like.
BOX_BG_COLOR     = (0, 0, 0)      # RGB: Red=0, Green=0, Blue=0 = BLACK
BOX_BG_ALPHA     = 180            # Transparency: 0=invisible, 255=solid. 180 = see-through black
BOX_BORDER_COLOR = (255, 255, 255) # RGB: 255 each = WHITE (the border around the box)
BOX_BORDER_WIDTH = 2              # How thick the white border is (in pixels)

# ── Spacing inside the box ───────────────────────────────────────────────────
# "Padding" is the gap between the edge of the box and the content inside it.
# Like the margins on a Word document — text doesn't touch the edges.
BOX_PADDING = 24  # Pixels of empty space inside the box border

# ── Avatar size ──────────────────────────────────────────────────────────────
# Character portraits are small images. This sets how big they appear on screen.
# 96 pixels = roughly 1 inch on a standard monitor.
AVATAR_SIZE = 96

# ── Font sizes ───────────────────────────────────────────────────────────────
# "Font" = the style of text letters. SysFont("Arial", size) means:
# use the Arial font that's already installed on your computer, at this size.
NAME_FONT_SIZE = 20   # The speaker's name (e.g. "Auren") — smaller text
TEXT_FONT_SIZE = 26   # The dialogue text (what they say) — bigger for readability

# ── TYPING SPEED ─────────────────────────────────────────────────────────────
# This controls how fast the typewriter reveals text.
# 0.035 means one new character every 35 milliseconds.
# That's roughly 28 characters per second — about the speed of a fast typist.
# If you want slower text (more dramatic), increase this number (try 0.08).
# If you want faster text (less waiting), decrease it (try 0.015).
TYPING_SPEED   = 0.035

# ── Asset folder path ────────────────────────────────────────────────────────
# This builds the path to the folder where avatar images are stored.
# os.path.dirname(__file__) = the folder this current file is in (src/)
# '..' = go up one folder (to the project root)
# 'assests/sprites/avatars' = the folder with character portraits
# os.path.normpath() = fix the slashes so they work on any operating system
ASSETS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', 'assests', 'sprites', 'avatars')
)

# ── Window size (matches data/gameSetting.py) ────────────────────────────────
# Our game window is 1600 pixels wide and 900 pixels tall.
# We define these here so cutscene.py doesn't need to import gameSetting.py.
# (Keeping it self-contained = fewer dependencies = easier to understand)
WINDOW_WIDTH  = 1600
WINDOW_HEIGHT = 900


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — THE CUTSCENE MANAGER CLASS
# ══════════════════════════════════════════════════════════════════════════════
#
# A "class" is like a blueprint for creating objects.
# Think of it as a factory that builds CutsceneManager instances.
# Each instance manages ONE cutscene from start to finish.
#
# The CutsceneManager does 3 main jobs:
#   1. LOAD: Prepare all images and fonts when the cutscene starts
#   2. UPDATE: Each frame, reveal more text and check for key presses
#   3. DRAW: Each frame, render the background + dialog box + text to the screen
#
# ══════════════════════════════════════════════════════════════════════════════

class CutsceneManager:
    """
    The main controller that runs a cutscene from start to finish.

    HOW TO USE:
        cm = CutsceneManager(my_scenes, audio_manager)
        # In your game loop:
        cm.update(dt, just_pressed_keys_set)
        cm.draw(screen_surface)
        if cm.finished:
            # move to the next game state

    PARAMETERS for __init__:
        scenes : list of tuples
            Each tuple = (background_key_string, list_of_dialog_tuples)
            Example: ('home', [('auren', "Hello!"), ('spy', "Hi!")])
        audio : AudioManager object or None
            Used to play the typing blip sound. Pass None if you don't have audio.
    """

    def __init__(self, scenes, audio):
        """
        Set up the cutscene — load images, create fonts, get ready to play.

        WHAT HAPPENS INSIDE:
        1. We save the scenes list for later use
        2. We save the audio manager (for playing typing sounds)
        3. We set counters to 0 (starting at the first scene, first line)
        4. We load all background images from files
        5. We load all avatar portraits from files
        6. We create font objects for rendering text
        7. We create a pre-made dialog box surface (so we don't redraw it every frame)

        Think of this as "setting the stage" before the play begins.
        """

        # ── Store input parameters ────────────────────────────────────────────
        # These are the things we were given when this object was created.
        # We save them as "instance variables" (with self.) so ALL methods
        # in this class can access them.
        self.scenes = scenes   # The list of scenes to play through
        self.audio  = audio    # The audio manager (for playing typing sounds)

        # ╔══════════════════════════════════════════════════════════════════════╗
        # ║  WHAT ARE scene_idx AND line_idx?                                   ║
        # ║                                                                     ║
        # ║  Think of the cutscene as a BOOK:                                   ║
        # ║    - scenes    = chapters in the book                               ║
        # ║    - lines     = sentences in each chapter                          ║
        # ║    - scene_idx = which chapter we're on (0 = first chapter)         ║
        # ║    - line_idx  = which sentence in that chapter (0 = first sentence)║
        # ║                                                                     ║
        # ║  We start at CHAPTER 0, SENTENCE 0.                                ║
        # ╚══════════════════════════════════════════════════════════════════════╝
        self.scene_idx = 0   # Which scene (chapter) we are currently showing
        self.line_idx  = 0   # Which line (sentence) within that scene

        # ╔══════════════════════════════════════════════════════════════════════╗
        # ║  TYPWRITER STATE VARIABLES                                         ║
        # ║                                                                     ║
        # ║  Instead of showing the whole line at once, we reveal ONE letter    ║
        # ║  at a time (like someone is typing it in real time).               ║
        # ║                                                                     ║
        # ║  _revealed_chars = how many letters have been shown so far          ║
        # ║  _type_timer     = a stopwatch that counts up every frame           ║
        # ║                                                                     ║
 # ║  Example: For "Hello world!" (12 characters):                       ║
        # ║    _revealed_chars = 0  →  nothing shown on screen                  ║
        # ║    _revealed_chars = 5  →  "Hello" shown on screen                 ║
        # ║    _revealed_chars = 12 →  "Hello world!" fully shown              ║
        # ║                                                                     ║
        # ║  Each frame, we add dt (seconds elapsed) to _type_timer.            ║
        # ║  When _type_timer >= TYPING_SPEED, we reveal ONE more character.    ║
        # ║  Then we reset _type_timer and wait for the next frame.             ║
        # ╚══════════════════════════════════════════════════════════════════════╝
        self._revealed_chars = 0   # Number of characters currently visible (starts at 0)
        self._type_timer     = 0.0 # Time accumulator for typewriter effect

        # ── Finished flag ──────────────────────────────────────────────────────
        # This starts as False (the cutscene is NOT finished).
        # It becomes True when ALL scenes and ALL lines have been shown.
        # The game loop checks this to know when to move on.
        self._finished = False

        # ── Load fonts ────────────────────────────────────────────────────────
        # A "font" is a set of letters in a particular style and size.
        # SysFont("Arial", 20) means: use the Arial font that's installed on
        # your computer, at size 20 pixels tall.
        #
        # We create two fonts because names and text have different sizes.
        # The speaker name (e.g. "Auren") is smaller and bold.
        # The dialogue text is slightly bigger for easy reading.
        #
        # We create them ONCE in __init__ (not every frame) because creating
        # fonts is slow — doing it every frame would lag the game.
        self.name_font = pygame.font.SysFont("Arial", NAME_FONT_SIZE, bold=True)
        self.text_font = pygame.font.SysFont("Arial", TEXT_FONT_SIZE)

        # ── Load background images ────────────────────────────────────────────
        # Backgrounds are big pictures that fill the entire screen behind the
        # dialog box. They set the scene location (home, station, etc.).
        #
        # self._backgrounds is a DICTIONARY that maps background_key → image.
        # Dictionary = like a phonebook: you look up a key, you get its value.
        #   Example: self._backgrounds['home'] = the loaded home.png image
        #
        # We iterate through each scene ONCE during setup and load its background.
        # This way, we don't have to load images during gameplay (which would lag).
        self._backgrounds = {}

        # Loop through every scene in the cutscene
        for scene_key, _ in self.scenes:
            # scene_key is the background identifier ('home', 'station', or 'moon_surface')
            # The underscore _ means we don't care about the dialog lines right now

            if scene_key == 'moon_surface':
                # Special case: 'moon_surface' doesn't have an image file.
                # Instead, it's drawn by code (a starry sky with Earth).
                # We set the value to None and handle it specially in draw().
                self._backgrounds[scene_key] = None
                continue  # Skip the rest of the loop — go to the next scene

            # Build the full file path: ASSETS_DIR + '/' + 'home' + '.png'
            path = os.path.join(ASSETS_DIR, scene_key + '.png')

            # Check if the image file actually exists on the computer
            if os.path.exists(path):
                # Load the image using pygame
                # .convert() converts it to a faster display format
                img = pygame.image.load(path).convert()

                # The image might be any size (e.g. home.png is 4360×1550).
                # We need to SCALE it to fit our 1600×900 window exactly.
                # pygame.transform.scale() stretches/shrinks the image.
                self._backgrounds[scene_key] = pygame.transform.scale(
                    img, (WINDOW_WIDTH, WINDOW_HEIGHT)
                )
            else:
                # If the file is missing, use None as fallback.
                # Black screen is better than crashing with an error.
                self._backgrounds[scene_key] = None

        # ── Load avatar images ────────────────────────────────────────────────
        # Avatars are small character portraits (e.g. auren.png, spy.png).
        # Each speaker has their own avatar, defined in the SPEAKERS config.
        #
        # self._avatars is a DICTIONARY that maps speaker_key → scaled image.
        #   Example: self._avatars['auren'] = the loaded and scaled auren.png

        self._avatars = {}

        # Loop through every speaker defined in cutscene_data.py
        for speaker_key, config in SPEAKERS.items():
            # config is a dictionary with 'side', 'name', and 'avatar_file' keys
            # Build the path to their avatar image
            path = os.path.join(ASSETS_DIR, config['avatar_file'])

            if os.path.exists(path):
                # Load the image with convert_alpha() to preserve transparency
                # (avatars usually have transparent backgrounds)
                img = pygame.image.load(path).convert_alpha()

                # Scale the avatar to our desired size (AVATAR_SIZE × AVATAR_SIZE)
                # The original images might be small (e.g. 39×38), so we enlarge them.
                self._avatars[speaker_key] = pygame.transform.scale(
                    img, (AVATAR_SIZE, AVATAR_SIZE)
                )
            else:
                # ╔══════════════════════════════════════════════════════════════╗
                # ║  FALLBACK: If an avatar image file is missing,              ║
                # ║  we draw a colored circle as a placeholder.                 ║
                # ║  This prevents the game from crashing due to a missing file.║
                # ╚══════════════════════════════════════════════════════════════╝

                # Create an empty transparent surface of the right size
                surf = pygame.Surface((AVATAR_SIZE, AVATAR_SIZE), pygame.SRCALPHA)

                # Pick a color based on who the speaker is
                # (so each character has a distinct placeholder color)
                colors = {
                    'auren': (100, 150, 255),  # Blue for Auren
                    'spy':   (50, 50, 50),      # Dark gray for Spy
                    'moon':  (200, 200, 150),   # Pale yellow for Moon
                }
                color = colors.get(speaker_key, (100, 100, 100))  # Default gray if unknown

                # Draw a filled circle in the center of the surface
                # AVATAR_SIZE // 2 = the middle of the square
                # pygame.draw.circle fills a circle shape
                pygame.draw.circle(
                    surf, color,
                    (AVATAR_SIZE // 2, AVATAR_SIZE // 2),  # Center position
                    AVATAR_SIZE // 2                        # Radius (half the size)
                )

                self._avatars[speaker_key] = surf

        # ── Create dialog box rectangle ───────────────────────────────────────
        # A "rectangle" in pygame is defined by (x, y, width, height).
        # This calculates WHERE the dialog box will be drawn on screen.
        #
        # The box goes from the bottom of the screen UPWARD by BOX_HEIGHT_RATIO.
        #   y = WINDOW_HEIGHT - box_h  → starts at 75% of screen height
        #   height = box_h             → goes down to the bottom edge
        box_h = int(WINDOW_HEIGHT * BOX_HEIGHT_RATIO)  # Height of the box in pixels
        self._box_rect = pygame.Rect(
            0,                      # x = 0 (left edge of screen)
            WINDOW_HEIGHT - box_h,  # y = (screen height - box height) = 675
            WINDOW_WIDTH,           # width = 1600 (full screen width)
            box_h                   # height = 225 (25% of 900)
        )

        # ── Create a pre-rendered dialog box surface ──────────────────────────
        # Instead of drawing the semi-transparent black box + white border
        # every single frame, we draw it ONCE here and store it.
        # Each frame, we just blit (copy) this pre-made surface onto the screen.
        # This is faster and more efficient.
        #
        # SRCALPHA flag means this surface supports per-pixel transparency.
        self._box_surface = pygame.Surface((WINDOW_WIDTH, box_h), pygame.SRCALPHA)

        # Fill the surface with semi-transparent black
        # The * before BOX_BG_COLOR unpacks (0,0,0) into three separate arguments
        # So fill(0, 0, 0, 180) = black at 70% opacity
        self._box_surface.fill((*BOX_BG_COLOR, BOX_BG_ALPHA))

        # Draw a white rectangle border around the surface
        # get_rect() returns the rectangle that bounds this surface
        # BOX_BORDER_WIDTH = 2 pixels thick
        pygame.draw.rect(
            self._box_surface,
            BOX_BORDER_COLOR,
            self._box_surface.get_rect(),
            BOX_BORDER_WIDTH
        )

        # ── Arrow blink timer ──────────────────────────────────────────────────
        # When the typewriter has finished revealing a line of text,
        # we show a little arrow "▾" at the bottom to tell the player
        # "press a key to continue." This timer makes the arrow blink
        # (appear and disappear) to draw attention to it.
        self._arrow_timer = 0.0

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 3 — UPDATE METHOD (called every frame)
    # ══════════════════════════════════════════════════════════════════════════
    #
    # The update() method is called ONCE per frame (60 times per second).
    # It does 3 things:
    #   1. Reveals one more character of the current line (typewriter)
    #   2. If the full line is shown and player presses advance → next line
    #   3. Blinks the "press to continue" arrow
    #
    # ══════════════════════════════════════════════════════════════════════════

    def update(self, dt, just_pressed_keys):
        """
        Advance the cutscene by one frame.

        WHAT THIS METHOD DOES (step by step):
        1. Check if the cutscene is already finished — if so, do nothing.
        2. Get the CURRENT line of dialogue text.
        3. If the text is still being revealed:
           - Add dt (time since last frame) to our typewriter timer
           - When enough time has passed, reveal one more character
           - Play the typing sound for each non-space character
        4. If the text is fully revealed:
           - Check if player pressed SPACE/ENTER/Z to advance
           - If yes, move to the next line (or next scene, or finish)
        5. Update the arrow blink timer.

        PARAMETERS:
            dt : float
                Delta time = seconds since the last frame.
                Usually around 0.016 (at 60 FPS).
                This ensures the typewriter runs at the same speed
                regardless of how fast the computer is.
            just_pressed_keys : set
                A Python set containing pygame key constants that were
                PRESSED this frame (not held down).
                Example: {pygame.K_SPACE, pygame.K_z}
                We use a set instead of the regular key state so that
                holding down SPACE doesn't skip 30 lines instantly.
        """

        # ── Guard clause: if finished, do nothing ─────────────────────────────
        # If the cutscene is already done, we just return immediately.
        # This prevents any further processing.
        if self._finished:
            return

        # ── Get the current line of dialogue ──────────────────────────────────
        # _get_current_line() returns a dictionary with 'speaker' and 'text'
        # keys, or None if there's no current line (shouldn't happen normally).
        current_line = self._get_current_line()

        # If there's no current line, mark the cutscene as finished and stop.
        if current_line is None:
            self._finished = True
            return

        # Extract the full text of this dialogue line
        # e.g., "Man... another boring night."
        full_text = current_line['text']

        # ╔══════════════════════════════════════════════════════════════════════╗
        # ║  TYPWRITER LOGIC                                                    ║
        # ║                                                                     ║
        # ║  _revealed_chars starts at 0 and counts UP to len(full_text).       ║
        # ║  Each frame we check: has enough time passed to reveal another char?║
        # ║                                                                     ║
        # ║  The WHILE loop handles the case where the game lagged and dt was   ║
        # ║  very large — we reveal MULTIPLE characters at once to catch up.    ║
        # ╚══════════════════════════════════════════════════════════════════════╝
        if self._revealed_chars < len(full_text):
            # Text is NOT fully revealed yet — keep typing

            # Add the time elapsed this frame to our typewriter timer
            self._type_timer += dt

            # Keep revealing characters while enough time has accumulated
            # The WHILE loop (instead of IF) prevents text getting stuck
            # if the game lags (multiple characters revealed at once to catch up)
            while self._type_timer >= TYPING_SPEED and self._revealed_chars < len(full_text):
                # Subtract the typing speed from the timer (consume the time)
                self._type_timer -= TYPING_SPEED

                # Reveal one more character
                self._revealed_chars += 1

                # ── Play typing sound ──────────────────────────────────────
                # Only play the sound for non-space characters, otherwise
                # it sounds like "tick-tick-tick-tick" even on spaces.
                # Check the character that was JUST revealed (index - 1)
                # because we already incremented _revealed_chars above.
                last_char = full_text[self._revealed_chars - 1]
                if last_char != ' ' and self.audio:
                    # Call the play() method on our audio manager
                    # with the sound name 'typing'
                    self.audio.play('typing')

        else:
            # ── Text is fully revealed — wait for player input ────────────────
            # The entire line of text is now visible.
            # We advance _arrow_timer to make the "▾" indicator blink.

            self._arrow_timer += dt

            # ── Check for advance key presses ─────────────────────────────────
            # Define which keys the player can press to continue to next line.
            # These are stored as a SET (curly braces) for fast membership testing.
            advance_keys = {pygame.K_RETURN, pygame.K_SPACE, pygame.K_z}

            # Check if ANY of the advance keys was just pressed this frame.
            # any() returns True if at least one element in the list is True.
            # We use a "generator expression" (the thing inside any()) to check
            # each key individually without writing 3 if statements.
            if any(k in just_pressed_keys for k in advance_keys):
                # Player wants to advance → call _advance() to move to next
                self._advance()

        # ── ESC skips the entire cutscene ─────────────────────────────────
        # If the player presses Escape, they want to skip ALL remaining
        # dialogue and jump straight to the game.
        # NOTE: This check is OUTSIDE the if/else so it runs regardless of
        # whether text is still typing or fully revealed — fixing the
        # "need to press ESC twice" bug.
        if pygame.K_ESCAPE in just_pressed_keys:
            self._finished = True

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 4 — DRAW METHOD (called every frame)
    # ══════════════════════════════════════════════════════════════════════════
    #
    # The draw() method renders everything to the screen.
    # It's called ONCE per frame, AFTER update().
    #
    # LAYER ORDER (drawn back to front, like painting a picture):
    #   1. Background image (fills the entire 1600×900 screen)
    #   2. Semi-transparent dialog box (bottom 25%, over the background)
    #   3. Character avatar + name tag (left or right side of box)
    #   4. Speaker name + dialogue text (on the opposite side from avatar)
    #   5. "▾" blinking arrow indicator (when line is complete)
    #
    # ══════════════════════════════════════════════════════════════════════════

    def draw(self, surface):
        """
        Render the cutscene onto the screen surface.

        WHAT THIS METHOD DOES:
        1. Paints the background (image or programmatic starry sky)
        2. Paints the semi-transparent dialog box at the bottom
        3. Paints the character portrait on the correct side
        4. Paints the speaker name under the portrait
        5. Paints the revealed text on the opposite side
        6. Paints a blinking arrow when the line is complete

        PARAMETERS:
            surface : pygame.Surface
                The screen to draw on. In Main.py this is the 'screen' variable.
                Think of it as a digital canvas that gets flipped to the monitor.
        """

        # ── Guard clause: if finished, don't draw anything ────────────────────
        if self._finished:
            return

        # ── 1. DRAW THE BACKGROUND ────────────────────────────────────────────
        # Get the background key for the CURRENT scene ('home', 'station', etc.)
        current_bg_key = self.scenes[self.scene_idx][0]  # [0] = first element of tuple

        # Look up the pre-loaded background image from our dictionary
        bg = self._backgrounds.get(current_bg_key)

        if bg is not None:
            # If we have a loaded image, just copy (blit) it onto the screen
            # blit = "block image transfer" = copy pixels from one surface to another
            surface.blit(bg, (0, 0))  # (0, 0) = top-left corner of the screen

        elif current_bg_key == 'moon_surface':
            # ── Draw moon surface programmatically ─────────────────────────
            # For 'moon_surface', we don't have an image file.
            # Instead, we DRAW the scene using pygame shapes.
            # This creates a starry night sky with Earth in the distance
            # (matching the Level 1 gameplay background).
            self._draw_moon_background(surface)

        else:
            # ── Fallback: solid black ──────────────────────────────────────────
            # If the background key is unknown or the image failed to load,
            # just fill the screen with black. Not pretty, but doesn't crash.
            surface.fill((0, 0, 0))

        # ── 2. DRAW THE DIALOG BOX ────────────────────────────────────────────
        # Copy our pre-made dialog box surface onto the screen at the box position.
        # The box_surface was created in __init__ and already has the
        # semi-transparent black fill and white border.
        surface.blit(self._box_surface, (self._box_rect.x, self._box_rect.y))

        # ── 3. GET CURRENT LINE INFO ─────────────────────────────────────────
        # We need to know WHO is speaking and WHAT they're saying.
        current_line = self._get_current_line()

        # If there's no current line (shouldn't happen), stop drawing.
        if current_line is None:
            return

        # Extract data from the current line
        speaker_key = current_line['speaker']  # e.g., 'auren', 'spy', 'moon'
        full_text   = current_line['text']     # e.g., "Man... another boring night."

        # Look up the speaker's configuration from our data file
        speaker_cfg = SPEAKERS.get(speaker_key, {})

        # Determine if this speaker is on the LEFT side (Auren) or RIGHT side (everyone else)
        is_left = speaker_cfg.get('side') == 'left'

        # Get the display name (e.g., "Auren", "Spy", "Moon")
        speaker_name = speaker_cfg.get('name', speaker_key)

        # ── 4. DRAW AVATAR + NAME TAG ─────────────────────────────────────────
        # The avatar (character portrait) goes on one side of the dialog box.
        # The name tag goes right under the avatar.
        avatar = self._avatars.get(speaker_key)

        if avatar:
            # ── Calculate avatar X position ───────────────────────────────────
            if is_left:
                # Speaker is on the LEFT side (Auren)
                # x = padding from the left edge of the dialog box
                av_x = BOX_PADDING
            else:
                # Speaker is on the RIGHT side (Spy, Moon)
                # x = screen width - avatar width - padding from the right edge
                av_x = WINDOW_WIDTH - AVATAR_SIZE - BOX_PADDING

            # ── Calculate avatar Y position ───────────────────────────────────
            # Vertically center the avatar inside the dialog box.
            # self._box_rect.y = top of the dialog box
            # self._box_rect.height = total height of the dialog box
            # Subtract 10 to shift it slightly upward (looks better with the name tag below)
            av_y = self._box_rect.y + (self._box_rect.height - AVATAR_SIZE) // 2 - 10

            # Draw (blit) the avatar image onto the screen at the calculated position
            surface.blit(avatar, (av_x, av_y))

            # ── Draw name tag under avatar ────────────────────────────────────
            # Render the speaker name as a text surface
            name_surf = self.name_font.render(speaker_name, True, (255, 255, 255))

            # Center the name horizontally under the avatar
            # Avatar is AVATAR_SIZE wide. Name has name_surf.get_width() width.
            # Center x = avatar_x + (avatar_width - name_width) / 2
            nx = av_x + (AVATAR_SIZE - name_surf.get_width()) // 2

            # Position the name just below the avatar (4 pixels gap)
            ny = av_y + AVATAR_SIZE + 4

            # Draw the name text onto the screen
            surface.blit(name_surf, (nx, ny))

        # ── 5. DRAW SPEAKER NAME + DIALOGUE TEXT ──────────────────────────────
        # The text goes on the OPPOSITE side from the avatar:
        #   - If avatar is on LEFT  → text starts on the RIGHT side
        #   - If avatar is on RIGHT → text starts on the LEFT side

        if is_left:
            # Avatar is on LEFT → text starts to the RIGHT of the avatar
            # text_x = avatar width + some padding + left padding
            text_x = AVATAR_SIZE + BOX_PADDING * 2
            # Text width = screen width - text_start_x - right padding
            # ...minus the space reserved for the right-side avatar area
            text_w = WINDOW_WIDTH - text_x - (AVATAR_SIZE + BOX_PADDING * 2)
        else:
            # Avatar is on RIGHT → text starts on the LEFT side of the box
            text_x = BOX_PADDING
            # Text width = screen width - left padding - avatar area - right padding
            text_w = WINDOW_WIDTH - text_x - BOX_PADDING - AVATAR_SIZE - BOX_PADDING * 2

        # Vertically position the text near the top of the dialog box
        text_y = self._box_rect.y + BOX_PADDING

        # ── Draw the revealed portion of text ─────────────────────────────────
        # We only show characters up to _revealed_chars (typewriter effect).
        visible_text = full_text[:self._revealed_chars]

        # Word-wrap: split the visible text into lines that fit in text_w width
        lines = self._wrap_text(visible_text, self.text_font, text_w)

        # Draw each line of text, one below the other
        for i, line_surf in enumerate(lines):
            # y position increases for each line (line height ≈ TEXT_FONT_SIZE + 6)
            # i = line number (0 for first line, 1 for second, etc.)
            surface.blit(line_surf, (text_x, text_y + i * (TEXT_FONT_SIZE + 6)))

        # ── 6. DRAW "▾" INDICATOR ─────────────────────────────────────────────
        # When the entire line is revealed, show a blinking arrow to tell
        # the player to press a key to continue.
        if self._revealed_chars >= len(full_text):
            # Blink logic: int(self._arrow_timer * 3) % 2 alternates 0, 1, 0, 1
            # 0 = draw arrow, 1 = don't draw arrow → blinking effect
            # The * 3 makes it blink 3 times per second
            if int(self._arrow_timer * 3) % 2 == 0:
                # Render the arrow character as text
                arrow = self.text_font.render("▾", True, (255, 255, 255))

                # Position the arrow at the bottom-right of the text area
                ax = text_x + text_w - arrow.get_width() - 4  # Right-aligned with 4px margin
                ay = self._box_rect.bottom - arrow.get_height() - 8  # 8px from bottom of box

                surface.blit(arrow, (ax, ay))

        # ── 7. DRAW "ESC - Skip" HINT ─────────────────────────────────────────
        # Show a small label in the top-right corner so players know they can
        # skip the cutscene by pressing Escape.
        skip_surf = self.name_font.render("ESC - Skip", True, (150, 150, 150))
        skip_surf.set_alpha(120)
        sx = WINDOW_WIDTH - skip_surf.get_width() - 16
        sy = 12
        surface.blit(skip_surf, (sx, sy))

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 5 — PROPERTIES (like variables that run code when you read them)
    # ══════════════════════════════════════════════════════════════════════════
    #
    # A "property" looks like a variable (cm.finished) but actually runs code
    # when you access it. The @property decorator makes this possible.
    #
    # ══════════════════════════════════════════════════════════════════════════

    @property
    def finished(self):
        """
        Is the cutscene completely done?

        RETURNS:
            True  → All scenes and all dialogue lines have been shown.
            False → There's still more cutscene to play.

        HOW TO USE IT:
            cm = CutsceneManager(my_scenes, audio)
            while not cm.finished:
                cm.update(dt, keys)
                cm.draw(screen)
            print("Cutscene is done! Start the game!")
        """
        return self._finished

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 6 — INTERNAL HELPERS (private methods)
    # ══════════════════════════════════════════════════════════════════════════
    #
    # These methods start with an underscore (_) which means "private" —
    # they're meant to be used ONLY inside this class, not from outside.
    # Think of them as internal machinery that the public methods (update/draw)
    # use to get their job done.
    #
    # ══════════════════════════════════════════════════════════════════════════

    def _get_current_line(self):
        """
        Get the dialogue line we're currently on.

        HOW IT WORKS:
        1. Use scene_idx to pick the right scene from our list
        2. Use line_idx to pick the right line within that scene
        3. Return a dictionary with 'speaker' and 'text' keys

        RETURNS:
            {'speaker': 'auren', 'text': 'Hello!'} or None if finished
        """

        # Safety check: are we past the end of all scenes?
        if self._finished or self.scene_idx >= len(self.scenes):
            return None

        # Get the current scene tuple: (background_key, [list_of_lines])
        # _ = we ignore the background key (first element)
        # lines = the list of dialogue tuples (second element)
        _, lines = self.scenes[self.scene_idx]

        # Safety check: are we past the end of this scene's lines?
        if self.line_idx >= len(lines):
            return None

        # Unpack the dialogue tuple: (speaker, text)
        speaker, text = lines[self.line_idx]

        # Return as a dictionary for clear key names
        return {'speaker': speaker, 'text': text}

    def _advance(self):
        """
        Move to the next piece of dialogue.

        WHAT THIS DOES:
        - If there's another line in the CURRENT scene → advance to it
        - If the current scene is done but more scenes exist → go to NEXT scene
        - If ALL scenes and ALL lines are done → mark as finished

        This is the "page turn" logic of the cutscene.
        """

        # Get the current scene's lines
        _, lines = self.scenes[self.scene_idx]

        # ── Check if there are more lines in this scene ──────────────────────
        if self.line_idx + 1 < len(lines):
            # Yes! Move to the next line within this scene
            self.line_idx += 1

            # Reset typewriter state so the new line starts typing from scratch
            self._revealed_chars = 0   # No characters shown yet
            self._type_timer     = 0.0 # Reset the typing timer
            self._arrow_timer    = 0.0 # Reset the arrow blink timer

        # ── Check if there are more scenes ────────────────────────────────────
        elif self.scene_idx + 1 < len(self.scenes):
            # Yes! Move to the next scene, starting at its first line
            self.scene_idx += 1  # Go to next scene
            self.line_idx = 0    # Start at the first line of that scene

            # Reset all timers for the new scene
            self._revealed_chars = 0
            self._type_timer     = 0.0
            self._arrow_timer    = 0.0

        else:
            # ── No more scenes AND no more lines — we're done! ────────────────
            self._finished = True

    def _wrap_text(self, text, font, max_width):
        """
        Split text into multiple lines so it fits inside a box.

        WHAT IS WORD-WRAPPING?
        When you type in a text editor and reach the end of the line,
        it automatically moves to the next line. That's word-wrapping.
        This method does the same thing for our dialogue text.

        HOW IT WORKS:
        1. Split the text into individual words (by spaces)
        2. Try adding each word to the current line
        3. If the line becomes too wide, start a NEW line with that word
        4. Return a list of rendered text surfaces (one per line)

        PARAMETERS:
            text     : string  — the text to wrap (e.g., "Hello world foo bar")
            font     : pygame.Font — the font to measure and render text with
            max_width : int — the maximum width in pixels before wrapping

        RETURNS:
            A list of pygame.Surface objects, each containing one rendered line.
            Example: [surface("Hello world"), surface("foo bar")]
        """

        # Split the text into individual words using space as separator
        # Example: "Hello world foo" → ["Hello", "world", "foo"]
        words = text.split(' ')

        lines = []          # Will hold the final rendered line surfaces
        current_line = ''   # Builds up the current line word by word

        # Loop through each word and decide where to put it
        for word in words:
            # ╔══════════════════════════════════════════════════════════════════╗
            # ║  TEST: Would adding this word make the line too long?           ║
            # ║                                                                 ║
            # ║  We simulate adding the word to the current line, then measure  ║
            # ║  the width using font.size(). If it fits, we add it.            ║
            # ║  If it doesn't fit, we store the current line and start a new   ║
            # ║  one with just this word.                                       ║
            # ╚══════════════════════════════════════════════════════════════════╝

            # Build a test string: current_line + space + new_word
            if current_line:
                test_line = current_line + ' ' + word
            else:
                test_line = word

            # Measure the width of the test line in pixels
            # font.size() returns (width_in_pixels, height_in_pixels)
            test_width = font.size(test_line)[0]  # [0] = width

            if test_width <= max_width:
                # The word FITS on the current line — add it
                current_line = test_line
            else:
                # The word DOESN'T FIT — save the current line and start a new one
                if current_line:
                    # Render the completed line as a surface and add to our list
                    lines.append(font.render(current_line, True, (255, 255, 255)))
                # Start a new line with this word
                current_line = word

        # ── Don't forget the last line! ────────────────────────────────────────
        # After the loop, there's always one "current_line" that hasn't been
        # added to the list yet. This adds it.
        if current_line:
            lines.append(font.render(current_line, True, (255, 255, 255)))

        # ── If somehow we got no lines at all, add an empty one ───────────────
        # This prevents crashes from trying to blit an empty list.
        if not lines:
            lines.append(font.render('', True, (255, 255, 255)))

        return lines

    def _draw_moon_background(self, surface):
        """
        Draw a starry moon sky with Earth in the background.

        This is used INSTEAD of loading an image file for 'moon_surface' scenes.
        It creates a dark space sky with:
        - A very dark blue-black background (like space)
        - White dots for stars (randomly placed, but always the same spots)
        - A blue Earth in the distance with green continents

        The colors match the Level 1 gameplay background so it feels consistent.

        PARAMETERS:
            surface : pygame.Surface — the screen to draw on
        """

        # ── Step 1: Fill the sky with dark space color ────────────────────────
        # RGB (8, 5, 22) = very dark blue, almost black.
        # This is the same color as LVL1_BG_COLOR in gameSetting.py.
        surface.fill((8, 5, 22))

        # ── Step 2: Draw stars ────────────────────────────────────────────────
        # We use a "seeded" Random object (Random(42)) so the stars are
        # always in the SAME positions every time (they look hand-placed).
        # If we used random.random(), the stars would move every frame.
        rng = random.Random(42)  # 42 = any number, just for consistency

        for _ in range(120):  # Draw 120 stars
            # Random x position anywhere on screen
            x = rng.randint(0, WINDOW_WIDTH)
            # Random y position anywhere on screen
            y = rng.randint(0, WINDOW_HEIGHT)
            # Draw a small white circle (1 pixel radius) as the star
            # RGB (255, 255, 255) = pure white
            pygame.draw.circle(surface, (255, 255, 255), (x, y), 1)

        # ── Step 3: Draw Earth in the distance ────────────────────────────────
        # Earth position: slightly left of center, near the top of the screen
        cx, cy = 660, 95  # Center of Earth

        # Draw the ocean (big blue circle)
        # RGB (28, 68, 180) = deep ocean blue
        # Radius 68 pixels
        pygame.draw.circle(surface, (28, 68, 180), (cx, cy), 68)

        # Draw green land masses (three overlapping circles)
        # RGB (38, 115, 55) = forest green
        # These are placed at offsets from center to look like continents
        pygame.draw.circle(surface, (38, 115, 55), (cx - 22, cy - 20), 28)
        pygame.draw.circle(surface, (38, 115, 55), (cx + 28, cy + 10), 18)

        # Draw Earth's atmosphere glow (light blue outline)
        # RGB (60, 100, 200) = lighter blue
        # Radius 70 (slightly bigger than Earth), only the outline (width=3)
        pygame.draw.circle(surface, (60, 100, 200), (cx, cy), 70, 3)


# ══════════════════════════════════════════════════════════════════════════════
# END OF CUTSCENE ENGINE
# ══════════════════════════════════════════════════════════════════════════════
#
# SUMMARY:
#
# This file creates a reusable cutscene system that:
# 1. Loads background images + character portraits
# 2. Shows them in an Undertale-style dialog box
# 3. Types text one character at a time (typewriter effect)
# 4. Advances to the next line when the player presses SPACE/ENTER/Z
# 5. Supports ESC to skip the entire cutscene
# 6. Automatically word-wraps long text
# 7. Is COMPLETELY SEPARATE from the game logic — you can use it in any
#    Pygame project by just changing the data file.
#
# To add a new cutscene:
# 1. Add your scenes to data/cutscene_data.py
# 2. Create a CutsceneManager with your scenes
# 3. Call update() + draw() each frame until finished
#
# ══════════════════════════════════════════════════════════════════════════════
