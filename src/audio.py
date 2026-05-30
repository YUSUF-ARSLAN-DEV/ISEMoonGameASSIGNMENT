import os
import math
import pygame

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False

SAMPLE_RATE = 44100

_AUDIO_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', 'assests', 'audio')
)

_FILE_MAP = {
    'jump':           'JUMP_SOUND.mp3',
    'land':           'JUMP_LANDING_SOUND_MOON.mp3',
    'footstep':       'FOOT_STEP_SOUND_MOOON.mp3',
    'hurt':           'DEATH_SOUND.mp3',
    'enemy_death':    'KNIFE_SWING.mp3',
    'pickup':         'oxygenrefilllingaudio.mp3',
    'low_oxygen':     'BELOW_15_OXYGEN.wav',
    'oxygen_50':      'OXYGEN_BELOW_50_WARNING.mp3',
    'explosion':      'ENEMYLASER_FIRE.mp3',
    'you_died':       'Elden Ring YOU DIED [Sound Effect].mp3',
}

_SYNTH_FALLBACKS = {
    'jump':           (320, 0.14, 0.40, 'sine'),
    'land':           (200, 0.12, 0.35, 'sine'),
    'footstep':       (160, 0.08, 0.20, 'sine'),
    'hurt':           (110, 0.22, 0.50, 'square'),
    'enemy_death':    (180, 0.26, 0.45, 'saw'),
    'pickup':         (660, 0.28, 0.40, 'sine'),
    'low_oxygen':     (440, 0.10, 0.30, 'square'),
    'oxygen_50':      (360, 0.18, 0.30, 'square'),
    'explosion':      (65,  0.55, 0.65, 'square'),
    'level_complete': (523, 0.40, 0.50, 'sine'),
    'you_died':       (110, 0.40, 0.50, 'square'),

    # ── Cutscene typing blip ──────────────────────────────────────────────
    # A short high-pitched 'tick' sound played each time the typewriter
    # reveals a new character in a cutscene dialog box.
    #   Frequency 600Hz = bright, clicky tone (like a keyboard key)
    #   Duration 0.03s  = very short (barely audible, just a tap sound)
    #   Volume 0.15     = quiet (shouldn't be distracting)
    #   Shape 'sine'    = smooth, no harsh buzz
    # ──────────────────────────────────────────────────────────────────────
    'typing':          (600, 0.03, 0.15, 'sine'),
}


def _make_tone(freq, duration, volume=0.80, shape='sine'):
    if not _HAS_NUMPY:
        return None
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0.0, duration, n, endpoint=False)
    if shape == 'sine':
        wave = np.sin(2 * math.pi * freq * t)
    elif shape == 'square':
        wave = np.sign(np.sin(2 * math.pi * freq * t))
    else:
        wave = 2.0 * (t * freq - np.floor(t * freq + 0.5))
    env = np.ones(n)
    attack  = min(int(0.01 * SAMPLE_RATE), n)
    release = min(int(0.06 * SAMPLE_RATE), n)
    env[:attack]    = np.linspace(0, 1, attack)
    env[n-release:] = np.linspace(1, 0, release)
    mono   = (wave * env * volume * 32767).astype(np.int16)
    stereo = np.column_stack([mono, mono])
    return pygame.sndarray.make_sound(stereo)


def _make_ambient(fund_freq, duration=4.0):
    if not _HAS_NUMPY:
        return None
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0.0, duration, n, endpoint=False)
    wave = (
        0.30 * np.sin(2 * math.pi * fund_freq       * t) +
        0.18 * np.sin(2 * math.pi * fund_freq * 1.5 * t) +
        0.10 * np.sin(2 * math.pi * fund_freq * 2.0 * t) +
        0.05 * np.sin(2 * math.pi * fund_freq * 3.0 * t)
    )
    wave  *= 0.65 + 0.35 * np.sin(2 * math.pi * 0.25 * t)
    mono   = (wave * 0.55 * 32767).astype(np.int16)
    stereo = np.column_stack([mono, mono])
    return pygame.sndarray.make_sound(stereo)


class AudioManager:
    def __init__(self):
        try:
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=512)
            pygame.mixer.music.set_volume(1.0)
        except Exception:
            pass
        self._music_channel = None
        self._sounds = {}
        self._load_all()

    def _load_all(self):
        all_names = set(_FILE_MAP.keys()) | set(_SYNTH_FALLBACKS.keys())
        for name in all_names:
            snd = None
            filename = _FILE_MAP.get(name)
            if filename:
                path = os.path.join(_AUDIO_DIR, filename)
                if os.path.exists(path):
                    try:
                        snd = pygame.mixer.Sound(path)
                        vol_map = {'footstep': 0.65, 'low_oxygen': 1.0,
                                   'oxygen_50': 1.0,  'explosion': 1.0,
                                   'jump': 1.0, 'hurt': 1.0, 'land': 0.85,
                                   'enemy_death': 1.0, 'pickup': 1.0}
                        snd.set_volume(vol_map.get(name, 1.0))
                    except Exception:
                        snd = None
            if snd is None and name in _SYNTH_FALLBACKS:
                try:
                    snd = _make_tone(*_SYNTH_FALLBACKS[name])
                except Exception:
                    snd = None
            if snd is not None:
                self._sounds[name] = snd

    def play(self, name):
        snd = self._sounds.get(name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass

    def start_music(self, level_num):
        self.stop_music()
        freq = 110 if level_num == 1 else 82
        try:
            music = _make_ambient(freq)
            if music is not None:
                self._music_channel = pygame.mixer.Channel(0)
                self._music_channel.play(music, loops=-1)
        except Exception:
            pass

    def stop_music(self):
        try:
            if self._music_channel:
                self._music_channel.stop()
        except Exception:
            pass

    @property
    def loaded_sounds(self):
        return list(self._sounds.keys())
