# sound.py — Procedural audio engine (Genshin-inspired atmospheric sounds)
# Requires: numpy, pygame-ce

import pygame
import math

try:
    import numpy as np
    _HAS_NP = True
except ImportError:
    _HAS_NP = False

SR = 44100  # sample rate


# ---------------------------------------------------------------------------
# Low-level synthesis helpers
# ---------------------------------------------------------------------------

if _HAS_NP:
    def _t(freq: float, dur: float, vol: float = 0.3,
           wave: str = 'sine', atk: float = 0.05, rel: float = 0.2) -> 'np.ndarray':
        n = max(1, int(SR * dur))
        t = np.linspace(0, dur, n, endpoint=False)
        if wave == 'sine':
            s = np.sin(2 * math.pi * freq * t)
        elif wave == 'sq':
            s = np.sign(np.sin(2 * math.pi * freq * t)) * 0.5
        elif wave == 'saw':
            s = 2 * (t * freq - np.floor(0.5 + t * freq))
        elif wave == 'tri':
            s = 2 * np.abs(2 * (t * freq - np.floor(0.5 + t * freq))) - 1
        elif wave == 'noise':
            rng = np.random.default_rng(int(freq * 7) & 0xFFFFFFFF)
            s = rng.uniform(-1, 1, n).astype(np.float64)
        else:
            s = np.sin(2 * math.pi * freq * t)

        env = np.ones(n)
        a = min(int(atk * SR), n)
        r = min(int(rel * SR), n - a)
        if a > 0:
            env[:a] = np.linspace(0, 1, a)
        if r > 0:
            env[n - r:] = np.linspace(1, 0, r)
        return (s * env * vol).astype(np.float64)

    def _mix(*arrs: 'np.ndarray') -> 'np.ndarray':
        L = max(len(a) for a in arrs)
        out = np.zeros(L, dtype=np.float64)
        for a in arrs:
            out[:len(a)] += a
        return np.clip(out, -1., 1.)

    def _after(arr: 'np.ndarray', sec: float) -> 'np.ndarray':
        pad = np.zeros(int(SR * sec), dtype=np.float64)
        return np.concatenate([pad, arr])

    def _sound(arr: 'np.ndarray') -> pygame.mixer.Sound:
        mono = np.ascontiguousarray(
            (np.clip(arr, -1., 1.) * 32767).astype(np.int16)
        )
        n_ch = pygame.mixer.get_init()[2]
        if n_ch == 1:
            data = mono
        else:
            # Replicate mono into all output channels
            data = np.ascontiguousarray(
                np.stack([mono] * n_ch, axis=-1)
            )
        return pygame.sndarray.make_sound(data)

    def _hz(name: str) -> float:
        """'C4', 'A#3', 'Gb5', etc. → Hz"""
        SEMI = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
        n = name.strip()
        sharp = len(n) > 1 and n[1] in ('#', 'b')
        if sharp:
            acc = 1 if n[1] == '#' else -1
            oct_ = int(n[2])
            base = SEMI[n[0]] + acc
        else:
            oct_ = int(n[1])
            base = SEMI[n[0]]
        midi = (oct_ + 1) * 12 + base
        return 440.0 * 2 ** ((midi - 69) / 12)

    def _bell(freq: float, dur: float, vol: float = 0.25) -> 'np.ndarray':
        """Bell tone with natural harmonics."""
        return _mix(
            _t(freq,        dur, vol * 1.0, 'sine', atk=0.005, rel=0.6),
            _t(freq * 2.0,  dur, vol * 0.5, 'sine', atk=0.005, rel=0.5),
            _t(freq * 3.0,  dur, vol * 0.2, 'sine', atk=0.005, rel=0.4),
            _t(freq * 4.52, dur, vol * 0.1, 'sine', atk=0.005, rel=0.35),
        )


# ---------------------------------------------------------------------------
# SoundManager
# ---------------------------------------------------------------------------

class SoundManager:
    """Central audio manager.  Call init() before using."""

    def __init__(self):
        self._sfx: dict = {}
        self._music: dict = {}
        self._music_ch: 'pygame.mixer.Channel | None' = None
        self._music_vol = 0.35
        self._sfx_vol   = 0.65
        self._cur_music  = ""
        self._ready = False

    def init(self):
        """Call after pygame.init()."""
        try:
            # Use mono (1 channel) — works regardless of system audio config
            pygame.mixer.quit()
            pygame.mixer.init(SR, -16, 1, 1024)
            pygame.mixer.set_num_channels(16)
            self._music_ch = pygame.mixer.Channel(0)
            if _HAS_NP:
                self._build_sfx()
                self._build_music()
            self._ready = True
        except Exception as e:
            print(f"[Audio] init failed: {e}")  # non-fatal

    # ------------------------------------------------------------------
    # SFX construction
    # ------------------------------------------------------------------

    def _build_sfx(self):
        hz = _hz

        # Basic attack — sharp percussive crack
        self._sfx['attack'] = _sound(_mix(
            _t(180, 0.10, 0.45, 'noise', atk=0.003, rel=0.85),
            _t(hz('G3'), 0.12, 0.20, 'sine', atk=0.003, rel=0.70),
        ))

        # Power Slash — dramatic elemental burst
        self._sfx['power_slash'] = _sound(_mix(
            _t(90,  0.35, 0.40, 'noise', atk=0.01, rel=0.50),
            _t(hz('D4'), 0.30, 0.30, 'sq',   atk=0.01, rel=0.50),
            _after(_t(hz('A4'), 0.25, 0.25, 'sine', atk=0.01, rel=0.45), 0.05),
        ))

        # Heal — ascending C-E-G-C bell chord (Genshin heal shimmer)
        chord = [('C4', 0.0), ('E4', 0.10), ('G4', 0.20), ('C5', 0.32)]
        self._sfx['heal'] = _sound(_mix(*[
            _after(_bell(hz(n), 0.55, 0.22), t) for n, t in chord
        ]))

        # Enemy attack — dark rumble
        self._sfx['enemy_attack'] = _sound(_mix(
            _t(75,  0.28, 0.45, 'sq',    atk=0.01, rel=0.60),
            _t(150, 0.18, 0.20, 'noise', atk=0.01, rel=0.70),
        ))

        # Victory fanfare — ascending arpegio
        fanfare = [('C4', 0.0), ('E4', 0.18), ('G4', 0.36), ('C5', 0.54)]
        self._sfx['victory'] = _sound(_mix(*[
            _after(_bell(hz(n), 0.6, 0.28), t) for n, t in fanfare
        ]))

        # Game over — descending minor
        go_notes = [('G4', 0.0), ('Eb4', 0.28), ('C4', 0.56), ('A3', 0.84)]
        self._sfx['game_over'] = _sound(_mix(*[
            _after(_t(hz(n), 0.45, 0.22, 'sq', rel=0.55), t) for n, t in go_notes
        ]))

        # Dialogue tick — soft high chirp
        self._sfx['dialogue'] = _sound(
            _t(hz('A5'), 0.045, 0.12, 'sine', atk=0.004, rel=0.75)
        )

        # Combat start sting — ominous hit
        self._sfx['combat_start'] = _sound(_mix(
            _t(hz('A2'), 0.40, 0.40, 'sq',    atk=0.01, rel=0.35),
            _after(_t(hz('E3'), 0.30, 0.30, 'sq',   atk=0.01, rel=0.35), 0.18),
            _after(_t(500,      0.50, 0.20, 'noise', atk=0.01, rel=0.40), 0.35),
        ))

        # Flee — rising doppler whoosh
        pieces = [_t(250 * (1 + i * 0.3), 0.065, 0.18, 'saw', atk=0.01, rel=0.45)
                  for i in range(6)]
        self._sfx['flee'] = _sound(np.clip(np.concatenate(pieces), -1., 1.))

        # No MP — flat buzzer
        self._sfx['no_mp'] = _sound(_mix(
            _t(hz('A3'), 0.10, 0.18, 'sq', atk=0.01, rel=0.5),
            _after(_t(hz('G3'), 0.10, 0.18, 'sq', atk=0.01, rel=0.5), 0.11),
        ))

    # ------------------------------------------------------------------
    # Music construction
    # ------------------------------------------------------------------

    def _build_music(self):
        hz = _hz

        # --- Exploration BGM: ethereal 4-bar pentatonic loop (4 s) ---
        DUR_E = 4.0
        frames_e = int(SR * DUR_E)

        drone_e = _mix(
            _t(hz('C3'), DUR_E, 0.055, 'sine', atk=0.3, rel=0.3),
            _t(hz('G3'), DUR_E, 0.035, 'sine', atk=0.3, rel=0.3),
            _t(hz('E3'), DUR_E, 0.025, 'sine', atk=0.4, rel=0.3),
        )

        penta  = ['C4', 'E4', 'G4', 'A4', 'C5']
        pat_e  = [0, 2, 4, 3, 1, 2, 4, 3]
        step_e = DUR_E / len(pat_e)
        arp_e  = _mix(*[
            _after(_bell(hz(penta[idx]), step_e * 0.75, 0.10), i * step_e)
            for i, idx in enumerate(pat_e)
        ])

        explore_arr = _mix(drone_e[:frames_e], arp_e[:frames_e])
        self._music['explore'] = _sound(explore_arr)

        # --- Combat BGM: ominous A-minor loop (2 s) ---
        DUR_C = 2.0
        frames_c = int(SR * DUR_C)

        minor = ['A3', 'C4', 'E4', 'G4', 'A4']

        bass_beats = [(0.0, 'A2'), (0.5, 'A2'), (1.0, 'G2'), (1.5, 'G2')]
        bass_parts = [
            _after(_t(hz(n), 0.40, 0.18, 'sq', atk=0.02, rel=0.40), t)
            for t, n in bass_beats
        ]

        mel_beats = [(0.0,3),(0.25,4),(0.5,2),(0.75,1),(1.0,4),(1.25,2),(1.5,0),(1.75,3)]
        mel_parts = [
            _after(_t(hz(minor[idx]), 0.18, 0.11, 'sq', atk=0.01, rel=0.40), t)
            for t, idx in mel_beats
        ]

        combat_arr = _mix(*bass_parts, *mel_parts)
        self._music['combat'] = _sound(combat_arr[:frames_c])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def play_sfx(self, name: str):
        if not self._ready or name not in self._sfx:
            return
        ch = pygame.mixer.find_channel(True)
        if ch:
            ch.set_volume(self._sfx_vol)
            ch.play(self._sfx[name])

    def play_music(self, name: str):
        if not self._ready or not self._music_ch:
            return
        if self._cur_music == name:
            return
        self._cur_music = name
        if name in self._music:
            self._music_ch.set_volume(self._music_vol)
            self._music_ch.play(self._music[name], loops=-1)
        else:
            self._music_ch.stop()

    def stop_music(self):
        if self._music_ch:
            self._music_ch.stop()
        self._cur_music = ""
