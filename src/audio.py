"""
Audio manager — synthesises all sounds in code via numpy.
No external audio files needed.  Fails silently if numpy is missing.
"""
import pygame
import math

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False

SAMPLE_RATE = 44100


def _make_tone(freq, duration, volume=0.35, shape='sine'):
    if not _HAS_NUMPY:
        return None
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0.0, duration, n, endpoint=False)

    if shape == 'sine':
        wave = np.sin(2 * math.pi * freq * t)
    elif shape == 'square':
        wave = np.sign(np.sin(2 * math.pi * freq * t))
    else:  # sawtooth
        wave = 2.0 * (t * freq - np.floor(t * freq + 0.5))

    env     = np.ones(n)
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
    wave *= 0.65 + 0.35 * np.sin(2 * math.pi * 0.25 * t)
    mono   = (wave * 0.55 * 32767).astype(np.int16)
    stereo = np.column_stack([mono, mono])
    return pygame.sndarray.make_sound(stereo)


class AudioManager:
    """
    Generates and plays all game audio.

    Sound names:
        'jump', 'hurt', 'pickup', 'enemy_death',
        'level_complete', 'low_oxygen', 'explosion'

    Music:
        start_music(level_num)  — looping ambient drone
        stop_music()
    """

    def __init__(self):
        try:
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=512)
        except Exception:
            pass
        self._music_channel = None
        self._sounds        = {}
        self._build_sounds()

    def _build_sounds(self):
        defs = {
            'jump':           (320, 0.14, 0.40, 'sine'),
            'hurt':           (110, 0.22, 0.50, 'square'),
            'pickup':         (660, 0.28, 0.40, 'sine'),
            'enemy_death':    (180, 0.26, 0.45, 'saw'),
            'level_complete': (523, 0.40, 0.50, 'sine'),
            'low_oxygen':     (440, 0.10, 0.30, 'square'),
            'explosion':      (65,  0.55, 0.65, 'square'),  # deep thud for comet impact
        }
        for name, (freq, dur, vol, shape) in defs.items():
            try:
                snd = _make_tone(freq, dur, vol, shape)
                if snd is not None:
                    self._sounds[name] = snd
            except Exception:
                pass

    def play(self, name):
        snd = self._sounds.get(name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass

    def start_music(self, level_num):
        """Level 1 = A2 (110 Hz), Level 2 = E2 (82 Hz) — darker mood."""
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
