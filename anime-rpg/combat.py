# combat.py — Genshin-inspired turn-based battle system

import pygame
import math
import random
from typing import List, Optional
from constants import *
from entities import Character, Player, Enemy, Skill, SKILL_FLEE
from ui import (draw_panel, draw_text, draw_combat_status,
                draw_action_menu, draw_combat_log,
                draw_victory, draw_game_over, draw_glow)
from particles import ParticleSystem
from sprite_loader import get_battle_sprite


# ---------------------------------------------------------------------------
# Skill → element colour mapping
# ---------------------------------------------------------------------------

_SKILL_ELEMENT = {
    "Attack":      COLOR_GOLD,
    "Power Slash": COLOR_ANEMO,
    "Mend":        COLOR_HP_GREEN,
    "Flee":        COLOR_WHITE_DIM,
    "Dark Claw":   COLOR_SHADOW,
}


# ---------------------------------------------------------------------------
# Hit-shake animation
# ---------------------------------------------------------------------------

class HitEffect:
    def __init__(self, target_is_enemy: bool):
        self.target_is_enemy = target_is_enemy
        self.timer    = 0.0
        self.duration = 0.45
        self.active   = True

    def update(self, dt: float):
        self.timer += dt
        if self.timer >= self.duration:
            self.active = False

    def shake_offset(self) -> int:
        p = self.timer / self.duration
        return int(10 * math.sin(p * math.pi * 7) * (1 - p))

    def flash_alpha(self) -> int:
        p = self.timer / self.duration
        return int(210 * max(0.0, 1.0 - p * 2.8))


# ---------------------------------------------------------------------------
# Combat background — aurora dark sky + magic battle circle
# ---------------------------------------------------------------------------

# Pre-generate stable star positions for combat scene
_C_RNG   = random.Random(0xDEAD_BEEF)
_C_STARS = [
    (_C_RNG.randint(0, SCREEN_W),
     _C_RNG.randint(0, int(SCREEN_H * 0.55)),
     _C_RNG.uniform(0.8, 2.5),
     _C_RNG.uniform(0, math.pi * 2))
    for _ in range(70)
]


def _draw_combat_bg(surface: pygame.Surface):
    ticks = pygame.time.get_ticks() / 1000.0

    # --- Deep sky gradient ---
    for y in range(SCREEN_H):
        t = y / SCREEN_H
        r = int( 8 + 18 * t)
        g = int( 4 + 10 * t)
        b = int(22 + 30 * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_W, y))

    # --- Aurora bands (Genshin dramatic sky) ---
    aurora_cols = [
        ((60, 20, 120), 0.25, 1.0),
        ((20, 60, 140), 0.60, 0.7),
        ((80, 30, 100), 0.40, 1.3),
        ((30, 80, 120), 0.20, 0.9),
    ]
    hor_mid = int(SCREEN_H * 0.45)
    for i, (col, amp, spd) in enumerate(aurora_cols):
        base_y = hor_mid - 30 + i * 18
        wave   = int(amp * 18 * math.sin(ticks * spd + i * 1.6))
        band_y = base_y + wave
        bh     = 28 + int(8 * math.sin(ticks * spd * 0.6 + i))
        alpha  = int(55 + 25 * math.sin(ticks * spd + i * 2.1))
        band_s = pygame.Surface((SCREEN_W, bh), pygame.SRCALPHA)
        # Gradient within the band
        for by in range(bh):
            fade = math.sin(by / bh * math.pi)
            band_s.fill((*col, int(alpha * fade)), (0, by, SCREEN_W, 1))
        surface.blit(band_s, (0, band_y))

    # --- Twinkling stars ---
    for sx, sy, sr, phase in _C_STARS:
        twinkle = 0.5 + 0.5 * math.sin(ticks * 1.5 + phase)
        alpha   = int(160 * twinkle)
        r_px    = max(1, int(sr))
        buf     = pygame.Surface((r_px * 2 + 2, r_px * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(buf, (210, 210, 255, alpha), (r_px + 1, r_px + 1), r_px)
        surface.blit(buf, (sx - r_px - 1, sy - r_px - 1))

    # --- Ground plane ---
    gy = int(SCREEN_H * 0.60)
    for y in range(gy, SCREEN_H):
        t = (y - gy) / (SCREEN_H - gy)
        r = int(15 + 10 * t)
        g = int( 8 +  6 * t)
        b = int(30 + 18 * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_W, y))

    # --- Ground edge glow ---
    edge_s = pygame.Surface((SCREEN_W, 3), pygame.SRCALPHA)
    edge_s.fill((120, 70, 200, 90))
    surface.blit(edge_s, (0, gy))

    # --- Elemental battle circle on ground ---
    _draw_battle_circle(surface, ticks)

    # --- Distant mountain silhouettes ---
    silhouettes = [(130, 160, (18, 10, 35)), (400, 200, (22, 12, 42)),
                   (700, 145, (16,  8, 32)), (1000, 180, (20, 11, 38)),
                   (1200, 140, (18,  9, 34))]
    for mx, mh, mc in silhouettes:
        pts = [(mx - mh, gy), (mx, gy - mh), (mx + mh, gy)]
        pygame.draw.polygon(surface, mc, pts)


def _draw_battle_circle(surface: pygame.Surface, ticks: float):
    """Genshin-style elemental domain circle on the ground."""
    cx = SCREEN_W // 2
    cy = int(SCREEN_H * 0.68)

    for ring_r, col, speed in [
        (160, (80, 40, 160), 0.30),
        (120, (60, 80, 200), 0.50),
        ( 80, (100, 50, 180), 0.80),
    ]:
        alpha = int(35 + 15 * math.sin(ticks * speed))
        buf   = pygame.Surface((ring_r * 2 + 4, ring_r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.ellipse(buf, (*col, alpha),
                            (2, ring_r // 2, ring_r * 2, ring_r),
                            2)
        surface.blit(buf, (cx - ring_r - 2, cy - ring_r // 2 - 2))

    # Rotating rune dots
    for i in range(8):
        angle = ticks * 0.4 + i * math.pi / 4
        rx    = cx + int(140 * math.cos(angle))
        ry    = cy + int(40  * math.sin(angle))
        pygame.draw.circle(surface, (100, 60, 200), (rx, ry), 3)

    for i in range(6):
        angle = -ticks * 0.7 + i * math.pi / 3
        rx    = cx + int(95 * math.cos(angle))
        ry    = cy + int(27 * math.sin(angle))
        pygame.draw.circle(surface, (60, 80, 200), (rx, ry), 2)


# ---------------------------------------------------------------------------
# Combat sprite helpers — detailed Genshin-ish designs
# ---------------------------------------------------------------------------

def _draw_hero_sprite(surface: pygame.Surface, cx: int, cy: int,
                      color, color_dark,
                      shake: int = 0, flash_alpha: int = 0,
                      ticks: float = 0.0):
    x   = cx + shake
    bob = int(3 * math.sin(ticks * 2.0))

    spr = get_battle_sprite("kairu")
    if spr:
        bx = x - spr.get_width() // 2
        by = cy - spr.get_height() + bob
        draw_glow(surface, x, cy + 20, COLOR_ANEMO, radius=55, alpha_max=60)
        surface.blit(spr, (bx, by))
        if flash_alpha > 0:
            fs = pygame.Surface(spr.get_size(), pygame.SRCALPHA)
            fs.fill((255, 255, 255, flash_alpha))
            surface.blit(fs, (bx, by), special_flags=pygame.BLEND_RGBA_ADD)
    else:
        _draw_hero_sprite_fallback(surface, x, cy, color, color_dark,
                                   bob, flash_alpha, ticks)


def _draw_hero_sprite_fallback(surface: pygame.Surface, x: int, cy: int,
                                color, color_dark,
                                bob: int = 0, flash_alpha: int = 0,
                                ticks: float = 0.0):
    size = 82
    y0   = cy + bob

    draw_glow(surface, x, y0 + size // 2, COLOR_ANEMO, radius=55, alpha_max=60)

    cape_pts = [
        (x - size // 3, y0 + size // 5),
        (x + size // 3, y0 + size // 5),
        (x + size // 4 + int(4 * math.sin(ticks * 1.8)), y0 + size + 10),
        (x - size // 4 - int(4 * math.sin(ticks * 1.8)), y0 + size + 10),
    ]
    pygame.draw.polygon(surface, color_dark, cape_pts)

    body = pygame.Rect(x - size // 4, y0 - size // 4 + 12, size // 2, size * 2 // 3)
    pygame.draw.rect(surface, color_dark, body, border_radius=7)
    pygame.draw.rect(surface, color,      body.inflate(-6, -6), border_radius=7)
    pygame.draw.line(surface, COLOR_ANEMO,
                     (x - size // 6, y0 - size // 4 + 16),
                     (x + size // 6, y0 - size // 4 + 16), 2)

    hr = size // 3
    pygame.draw.circle(surface, color,      (x, y0 - size // 4), hr)
    pygame.draw.circle(surface, color_dark, (x, y0 - size // 4), hr, 3)
    for angle in [-50, -28, -6, 16, 38]:
        rad = math.radians(angle - 90)
        hx  = x + int((hr + 7) * math.cos(rad))
        hy  = (y0 - size // 4) + int((hr + 7) * math.sin(rad))
        pygame.draw.circle(surface, color_dark, (hx, hy), 7)

    eye_r = 5
    pygame.draw.circle(surface, (20, 10, 40),     (x - 10, y0 - size // 4 - 4), eye_r)
    pygame.draw.circle(surface, (20, 10, 40),     (x + 10, y0 - size // 4 - 4), eye_r)
    pygame.draw.circle(surface, COLOR_ANEMO,      (x - 10, y0 - size // 4 - 4), 2)
    pygame.draw.circle(surface, COLOR_ANEMO,      (x + 10, y0 - size // 4 - 4), 2)
    pygame.draw.circle(surface, COLOR_WHITE,      (x -  9, y0 - size // 4 - 6), 2)
    pygame.draw.circle(surface, COLOR_WHITE,      (x + 11, y0 - size // 4 - 6), 2)

    if flash_alpha > 0:
        fs = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
        fs.fill((255, 255, 255, flash_alpha))
        surface.blit(fs, (x - size, y0 - size),
                     special_flags=pygame.BLEND_RGBA_ADD)


def _draw_enemy_sprite(surface: pygame.Surface, cx: int, cy: int,
                       color, color_dark,
                       shake: int = 0, flash_alpha: int = 0,
                       ticks: float = 0.0):
    x   = cx + shake
    bob = int(4 * math.sin(ticks * 1.5 + 1.0))

    spr = get_battle_sprite("shadow_lurker")
    if spr:
        bx = x - spr.get_width() // 2
        by = cy - spr.get_height() + bob
        draw_glow(surface, x, cy + 20, COLOR_SHADOW, radius=60, alpha_max=70)
        surface.blit(spr, (bx, by))
        if flash_alpha > 0:
            fs = pygame.Surface(spr.get_size(), pygame.SRCALPHA)
            fs.fill((255, 255, 255, flash_alpha))
            surface.blit(fs, (bx, by), special_flags=pygame.BLEND_RGBA_ADD)
    else:
        _draw_enemy_sprite_fallback(surface, x, cy, color, color_dark,
                                    bob, flash_alpha, ticks)


def _draw_enemy_sprite_fallback(surface: pygame.Surface, x: int, cy: int,
                                 color, color_dark,
                                 bob: int = 0, flash_alpha: int = 0,
                                 ticks: float = 0.0):
    size = 72
    y0   = cy + bob

    draw_glow(surface, x, y0 + size // 3, COLOR_SHADOW, radius=60, alpha_max=70)

    for i, angle in enumerate([210, 240, 270, 300, 330]):
        rad = math.radians(angle + ticks * 30)
        tx  = x + int((size // 2 + 28 + i * 3) * math.cos(rad))
        ty  = y0 + int((size // 2 + 28 + i * 3) * math.sin(rad))
        pygame.draw.line(surface, color_dark, (x, y0), (tx, ty), 3)
        pygame.draw.circle(surface, color, (tx, ty), 5)

    pygame.draw.ellipse(surface, color_dark,
                        pygame.Rect(x - size // 2, y0 - size // 3, size, size * 2 // 3))
    pygame.draw.ellipse(surface, color,
                        pygame.Rect(x - size // 2 + 4, y0 - size // 3 + 4,
                                    size - 8, size * 2 // 3 - 8))

    hr = size // 2 + 8
    pygame.draw.circle(surface, color,      (x, y0 - size // 3), hr)
    pygame.draw.circle(surface, color_dark, (x, y0 - size // 3), hr, 3)

    for ex_off in [-20, 6]:
        pygame.draw.ellipse(surface, (220, 220, 0),
                            pygame.Rect(x + ex_off, y0 - size // 3 - 9, 16, 20))
        pygame.draw.ellipse(surface, (40, 0, 0),
                            pygame.Rect(x + ex_off + 4, y0 - size // 3 - 5, 8, 14))
        buf = pygame.Surface((20, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(buf, (220, 220, 0, 60), (0, 0, 20, 24))
        surface.blit(buf, (x + ex_off, y0 - size // 3 - 9))

    mpts = [(x - 18, y0 - size // 3 + 17)]
    for i in range(5):
        mx = x - 14 + i * 8
        my = (y0 - size // 3 + 23) if i % 2 == 0 else (y0 - size // 3 + 14)
        mpts.append((mx, my))
    mpts.append((x + 18, y0 - size // 3 + 17))
    if len(mpts) >= 2:
        pygame.draw.lines(surface, color_dark, False, mpts, 3)

    if flash_alpha > 0:
        fs = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
        fs.fill((255, 255, 255, flash_alpha))
        surface.blit(fs, (x - size, y0 - size),
                     special_flags=pygame.BLEND_RGBA_ADD)


# ---------------------------------------------------------------------------
# Skill flash label (momentary text burst on skill use)
# ---------------------------------------------------------------------------

class SkillLabel:
    def __init__(self, text: str, x: float, y: float, color):
        self.text     = text
        self.x, self.y = x, y
        self.color    = color
        self.age      = 0.0
        self.lifetime = 0.8

    @property
    def alive(self) -> bool:
        return self.age < self.lifetime

    def update(self, dt: float):
        self.age += dt
        self.y   -= 30 * dt

    def draw(self, surface: pygame.Surface):
        progress = min(1.0, self.age / self.lifetime)
        alpha    = max(0, int(255 * (1 - progress) ** 1.5))
        size     = int(22 - 4 * progress)
        font     = pygame.font.SysFont("arial", max(10, size), bold=True)
        r, g, b  = self.color[:3]
        surf     = font.render(self.text, True, (r, g, b))
        surf.set_alpha(alpha)
        sh = font.render(self.text, True, (0, 0, 0))
        sh.set_alpha(alpha)
        ix = int(self.x) - surf.get_width() // 2
        iy = int(self.y)
        surface.blit(sh, (ix + 2, iy + 2))
        surface.blit(surf, (ix, iy))


# ---------------------------------------------------------------------------
# CombatScene
# ---------------------------------------------------------------------------

PHASE_PLAYER = "player"
PHASE_ENEMY  = "enemy"
PHASE_RESULT = "result"


class CombatScene:
    def __init__(self, player: Player, enemy: Enemy,
                 particles: Optional[ParticleSystem] = None,
                 sound=None):
        self.player      = player
        self.enemy       = enemy
        self.particles   = particles
        self.sound       = sound
        self.log: List[str] = ["A Shadow Lurker appeared!"]
        self.phase       = PHASE_PLAYER
        self.selected    = 0
        self.actions     = player.skills
        self._hit_effect: Optional[HitEffect] = None
        self._enemy_timer = 0.0
        self._enemy_delay = 1.3
        self._result: Optional[str] = None
        self._skill_labels: List[SkillLabel] = []

        # Sprite positions
        self._hero_cx  = SCREEN_W // 4
        self._hero_cy  = int(SCREEN_H * 0.56)
        self._enemy_cx = SCREEN_W * 3 // 4
        self._enemy_cy = int(SCREEN_H * 0.52)

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if self.phase != PHASE_PLAYER:
            return None
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.actions)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.actions)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                self._execute_player_action()
        return None

    # ------------------------------------------------------------------
    # Logic
    # ------------------------------------------------------------------

    def _execute_player_action(self):
        skill = self.actions[self.selected]

        if skill is SKILL_FLEE:
            self.log.append("You fled from battle!")
            if self.sound:
                self.sound.play_sfx('flee')
            self._result = STATE_EXPLORE
            self.phase   = PHASE_RESULT
            return

        if not self.player.use_mp(skill.mp_cost):
            self.log.append("Not enough MP!")
            if self.sound:
                self.sound.play_sfx('no_mp')
            return

        skill_col = _SKILL_ELEMENT.get(skill.name, COLOR_GOLD)

        if skill.heal_amount > 0:
            healed = self.player.heal(skill.heal_amount)
            self.log.append(f"Kairu uses {skill.name} — +{healed} HP!")
            if self.sound:
                self.sound.play_sfx('heal')
            if self.particles:
                self.particles.emit_heal(float(self._hero_cx), float(self._hero_cy))
                self.particles.add_number(float(self._hero_cx),
                                          float(self._hero_cy - 60),
                                          healed, is_heal=True)
            self._add_skill_label(skill.name, self._hero_cx, self._hero_cy - 90, skill_col)
            self.phase       = PHASE_ENEMY
            self._enemy_timer = 0.0
            return

        dmg = self.enemy.take_damage(int(self.player.atk * skill.damage_mult))
        is_crit = dmg > int(self.player.atk * skill.damage_mult * 0.85)
        self.log.append(f"Kairu uses {skill.name} — {dmg} dmg!")
        if self.sound:
            sfx = 'power_slash' if skill.name == "Power Slash" else 'attack'
            self.sound.play_sfx(sfx)
        if self.particles:
            self.particles.emit_skill(float(self._enemy_cx), float(self._enemy_cy),
                                      skill_col)
            self.particles.add_number(float(self._enemy_cx),
                                      float(self._enemy_cy - 60), dmg,
                                      is_crit=is_crit)
        self._add_skill_label(skill.name, self._hero_cx, self._hero_cy - 90, skill_col)
        self._hit_effect = HitEffect(target_is_enemy=True)

        if not self.enemy.alive:
            self.log.append(f"{self.enemy.name} is defeated!")
            if self.sound:
                self.sound.play_sfx('victory')
            self._result = STATE_VICTORY
            self.phase   = PHASE_RESULT
        else:
            self.phase        = PHASE_ENEMY
            self._enemy_timer = 0.0

    def _execute_enemy_action(self):
        skill = self.enemy.choose_action()
        dmg   = self.player.take_damage(int(self.enemy.atk * skill.damage_mult))
        self.log.append(f"{self.enemy.name} uses {skill.name} — {dmg} dmg!")
        if self.sound:
            self.sound.play_sfx('enemy_attack')
        if self.particles:
            self.particles.emit_hit(float(self._hero_cx), float(self._hero_cy),
                                    COLOR_SHADOW, count=16)
            self.particles.add_number(float(self._hero_cx),
                                      float(self._hero_cy - 60), dmg)
        self._hit_effect = HitEffect(target_is_enemy=False)

        if not self.player.alive:
            self.log.append("Kairu has fallen...")
            if self.sound:
                self.sound.play_sfx('game_over')
            self._result = STATE_GAME_OVER
            self.phase   = PHASE_RESULT
        else:
            self.phase = PHASE_PLAYER

    def _add_skill_label(self, text: str, x: float, y: float, color):
        self._skill_labels.append(SkillLabel(text, x, y, color))

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt: float) -> Optional[str]:
        ticks = pygame.time.get_ticks() / 1000.0

        if self._hit_effect and self._hit_effect.active:
            self._hit_effect.update(dt)

        if self.phase == PHASE_ENEMY:
            self._enemy_timer += dt
            if self._enemy_timer >= self._enemy_delay:
                self._execute_enemy_action()

        self._skill_labels = [l for l in self._skill_labels if l.alive]
        for l in self._skill_labels:
            l.update(dt)

        if self.particles:
            self.particles.update(dt)

        return None

    def result_state(self) -> Optional[str]:
        return self._result

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface):
        ticks = pygame.time.get_ticks() / 1000.0
        _draw_combat_bg(surface)

        # Shake offsets
        hero_shake  = enemy_shake = 0
        flash_hero  = flash_enemy = 0
        if self._hit_effect and self._hit_effect.active:
            if self._hit_effect.target_is_enemy:
                enemy_shake = self._hit_effect.shake_offset()
                flash_enemy = self._hit_effect.flash_alpha()
            else:
                hero_shake  = self._hit_effect.shake_offset()
                flash_hero  = self._hit_effect.flash_alpha()

        # Particles below sprites
        if self.particles:
            self.particles.draw_below(surface)

        # Sprites
        if self.player.alive:
            _draw_hero_sprite(surface,
                              self._hero_cx, self._hero_cy,
                              self.player.color, self.player.color_dark,
                              hero_shake, flash_hero, ticks)
        if self.enemy.alive:
            _draw_enemy_sprite(surface,
                               self._enemy_cx, self._enemy_cy,
                               self.enemy.color, self.enemy.color_dark,
                               enemy_shake, flash_enemy, ticks)

        # Particles above sprites
        if self.particles:
            self.particles.draw_above(surface)

        # Skill labels
        for lbl in self._skill_labels:
            lbl.draw(surface)

        # Status panels
        draw_combat_status(surface, self.player,  20, 20, w=260)
        draw_combat_status(surface, self.enemy,  SCREEN_W - 280, 20, w=260)

        # Action menu / phase indicator
        if self.phase == PHASE_PLAYER:
            menu_x = 20
            menu_y = SCREEN_H - ACTION_MENU_H - 40
            draw_action_menu(surface, self.actions, self.selected, menu_x, menu_y)

        elif self.phase == PHASE_ENEMY:
            # Pulsing "enemy turn" indicator
            pulse = 0.5 + 0.5 * math.sin(ticks * 4)
            col   = (int(COLOR_HP_RED[0] * pulse + COLOR_WHITE_DIM[0] * (1 - pulse)),
                     int(COLOR_HP_RED[1] * pulse + COLOR_WHITE_DIM[1] * (1 - pulse)),
                     int(COLOR_HP_RED[2] * pulse + COLOR_WHITE_DIM[2] * (1 - pulse)))
            draw_text(surface, f"{self.enemy.name}'s turn...",
                      SCREEN_W // 2, SCREEN_H - 65,
                      col, size=20, center=True)

        # Combat log
        if self.log:
            draw_combat_log(surface, self.log,
                            x=SCREEN_W // 2 - 260,
                            y=SCREEN_H - 120, w=520)

        # Result overlays
        if self.phase == PHASE_RESULT:
            if self._result == STATE_VICTORY:
                draw_victory(surface)
            elif self._result == STATE_GAME_OVER:
                draw_game_over(surface)
