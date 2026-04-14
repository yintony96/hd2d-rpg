# particles.py — Elemental particle effects + floating damage numbers
# Genshin Impact-inspired: Anemo (teal), Pyro (orange), shadow (dark purple)

import pygame
import random
import math
from typing import List, Tuple
from constants import COLOR_HP_GREEN, COLOR_WHITE, COLOR_BLACK


# ---------------------------------------------------------------------------
# Single particle
# ---------------------------------------------------------------------------

class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'color', 'lifetime', 'age', 'size', 'gravity')

    def __init__(self, x: float, y: float, vx: float, vy: float,
                 color: Tuple, lifetime: float, size: float = 3.0,
                 gravity: float = 60.0):
        self.x, self.y   = x, y
        self.vx, self.vy = vx, vy
        self.color       = color
        self.lifetime    = lifetime
        self.age         = 0.0
        self.size        = size
        self.gravity     = gravity

    @property
    def alive(self) -> bool:
        return self.age < self.lifetime

    def update(self, dt: float):
        self.age += dt
        self.x   += self.vx * dt
        self.y   += self.vy * dt
        self.vy  += self.gravity * dt

    def draw(self, surface: pygame.Surface):
        progress = min(1.0, self.age / self.lifetime)
        alpha    = max(0, int(255 * (1.0 - progress) ** 1.4))
        sz       = max(1, int(self.size * (1.0 - progress * 0.55)))
        if alpha < 6:
            return
        buf = pygame.Surface((sz * 2 + 2, sz * 2 + 2), pygame.SRCALPHA)
        r, g, b = self.color[:3]
        pygame.draw.circle(buf, (r, g, b, alpha), (sz + 1, sz + 1), sz)
        surface.blit(buf, (int(self.x) - sz - 1, int(self.y) - sz - 1))


# ---------------------------------------------------------------------------
# Floating damage / heal numbers
# ---------------------------------------------------------------------------

class DamageNumber:
    def __init__(self, x: float, y: float, value: int,
                 is_crit: bool = False, is_heal: bool = False):
        self.x, self.y = float(x), float(y)
        self.value     = value
        self.age       = 0.0
        self.lifetime  = 1.4
        self.vy        = -90.0

        if is_heal:
            self.color = COLOR_HP_GREEN
            self.text  = f"+{value}"
            self.size  = 21
        elif is_crit:
            self.color = (255, 130, 0)
            self.text  = f"{value}!!"
            self.size  = 26
        else:
            self.color = (230, 230, 255)
            self.text  = str(value)
            self.size  = 19

    @property
    def alive(self) -> bool:
        return self.age < self.lifetime

    def update(self, dt: float):
        self.age += dt
        self.y   += self.vy * dt
        self.vy  += 55 * dt   # decelerate, slight drift back

    def draw(self, surface: pygame.Surface):
        progress = min(1.0, self.age / self.lifetime)
        alpha    = max(0, int(255 * (1.0 - progress ** 1.6)))
        font     = pygame.font.SysFont("arial", self.size, bold=True)
        r, g, b  = self.color[:3]
        ix = int(self.x)
        iy = int(self.y)
        # Shadow
        sh = font.render(self.text, True, (0, 0, 0))
        sh.set_alpha(alpha)
        surface.blit(sh, (ix - sh.get_width() // 2 + 2, iy + 2))
        # Main text
        surf = font.render(self.text, True, (r, g, b))
        surf.set_alpha(alpha)
        surface.blit(surf, (ix - surf.get_width() // 2, iy))


# ---------------------------------------------------------------------------
# Ambient glow orb (firefly / elemental wisp)
# ---------------------------------------------------------------------------

class GlowOrb:
    """Slowly drifting elemental wisp — ambient decoration."""
    def __init__(self, x: float, y: float, color: Tuple):
        self.x, self.y  = x, y
        self.ox, self.oy = x, y
        self.color       = color
        self.age         = random.uniform(0, math.pi * 2)
        self.lifetime    = random.uniform(3.5, 6.0)
        self.elapsed     = 0.0
        self.radius      = random.uniform(20, 60)
        self.speed       = random.uniform(0.6, 1.4)
        self.size        = random.uniform(2.5, 5.0)

    @property
    def alive(self) -> bool:
        return self.elapsed < self.lifetime

    def update(self, dt: float):
        self.elapsed += dt
        self.age     += dt * self.speed
        self.x = self.ox + self.radius * math.sin(self.age)
        self.y = self.oy + self.radius * 0.4 * math.cos(self.age * 1.3)

    def draw(self, surface: pygame.Surface):
        progress = min(1.0, self.elapsed / self.lifetime)
        # Fade in + out
        if progress < 0.15:
            alpha = int(180 * progress / 0.15)
        elif progress > 0.75:
            alpha = int(180 * max(0.0, (1.0 - progress)) / 0.25)
        else:
            alpha = 180 + int(40 * math.sin(self.age * 3))

        alpha = max(0, min(255, alpha))
        sz    = max(1, int(self.size))
        buf   = pygame.Surface((sz * 4 + 2, sz * 4 + 2), pygame.SRCALPHA)
        cx, cy = sz * 2 + 1, sz * 2 + 1
        r, g, b = int(self.color[0]), int(self.color[1]), int(self.color[2])
        glow_a = max(0, min(255, alpha // 4))
        core_a = max(0, min(255, alpha))
        pygame.draw.circle(buf, (r, g, b, glow_a), (cx, cy), sz * 2)
        pygame.draw.circle(buf, (r, g, b, core_a), (cx, cy), sz)
        surface.blit(buf, (int(self.x) - sz * 2 - 1, int(self.y) - sz * 2 - 1))


# ---------------------------------------------------------------------------
# Elemental ring effect (Genshin burst-style)
# ---------------------------------------------------------------------------

class ElementalRing:
    """Expanding ring flash on skill use."""
    def __init__(self, x: float, y: float, color: Tuple):
        self.x, self.y = x, y
        self.color     = color
        self.age       = 0.0
        self.lifetime  = 0.5
        self.max_r     = 80

    @property
    def alive(self) -> bool:
        return self.age < self.lifetime

    def update(self, dt: float):
        self.age += dt

    def draw(self, surface: pygame.Surface):
        progress = min(1.0, self.age / self.lifetime)
        r_now    = int(self.max_r * progress)
        alpha    = max(0, int(200 * (1 - progress) ** 1.5))
        width    = max(1, int(6 * (1 - progress)))
        if r_now < 2 or alpha < 5:
            return
        buf = pygame.Surface((r_now * 2 + 4, r_now * 2 + 4), pygame.SRCALPHA)
        rc, gc, bc = self.color[:3]
        pygame.draw.circle(buf, (rc, gc, bc, alpha),
                           (r_now + 2, r_now + 2), r_now, width)
        surface.blit(buf, (int(self.x) - r_now - 2, int(self.y) - r_now - 2))


# ---------------------------------------------------------------------------
# ParticleSystem — manages all live effects
# ---------------------------------------------------------------------------

class ParticleSystem:
    def __init__(self):
        self._particles:   List[Particle]     = []
        self._numbers:     List[DamageNumber]  = []
        self._orbs:        List[GlowOrb]       = []
        self._rings:       List[ElementalRing] = []

    # ---- emitters -------------------------------------------------------

    def emit_hit(self, x: float, y: float, color: Tuple, count: int = 14):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 220)
            vx    = math.cos(angle) * speed
            vy    = math.sin(angle) * speed - random.uniform(30, 80)
            sz    = random.uniform(2.5, 6.5)
            lt    = random.uniform(0.30, 0.75)
            self._particles.append(Particle(x, y, vx, vy, color, lt, sz, gravity=90))

    def emit_skill(self, x: float, y: float, color: Tuple, count: int = 24):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(100, 400)
            vx    = math.cos(angle) * speed
            vy    = math.sin(angle) * speed - random.uniform(60, 180)
            sz    = random.uniform(3.5, 9.0)
            lt    = random.uniform(0.45, 1.10)
            self._particles.append(Particle(x, y, vx, vy, color, lt, sz, gravity=55))
        self._rings.append(ElementalRing(x, y, color))

    def emit_heal(self, x: float, y: float):
        GREEN = (80, 220, 120)
        for _ in range(18):
            vx = random.uniform(-35, 35)
            vy = random.uniform(-100, -180)
            sz = random.uniform(3.5, 7.5)
            lt = random.uniform(0.55, 1.30)
            self._particles.append(Particle(x, y, vx, vy, GREEN, lt, sz, gravity=-5))
        self._rings.append(ElementalRing(x, y, GREEN))

    def emit_ambient_orb(self, x: float, y: float, color: Tuple):
        if len(self._orbs) < 40:
            self._orbs.append(GlowOrb(x, y, color))

    def add_number(self, x: float, y: float, value: int,
                   is_crit: bool = False, is_heal: bool = False):
        self._numbers.append(DamageNumber(x, y, value, is_crit, is_heal))

    # ---- lifecycle -------------------------------------------------------

    def update(self, dt: float):
        self._particles = [p for p in self._particles if p.alive]
        for p in self._particles:
            p.update(dt)

        self._numbers = [n for n in self._numbers if n.alive]
        for n in self._numbers:
            n.update(dt)

        self._orbs = [o for o in self._orbs if o.alive]
        for o in self._orbs:
            o.update(dt)

        self._rings = [r for r in self._rings if r.alive]
        for r in self._rings:
            r.update(dt)

    def draw_below(self, surface: pygame.Surface):
        """Draw effects that should appear under characters."""
        for r in self._rings:
            r.draw(surface)
        for o in self._orbs:
            o.draw(surface)

    def draw_above(self, surface: pygame.Surface):
        """Draw effects that should appear above characters."""
        for p in self._particles:
            p.draw(surface)
        for n in self._numbers:
            n.draw(surface)

    def clear(self):
        self._particles.clear()
        self._numbers.clear()
        self._orbs.clear()
        self._rings.clear()
