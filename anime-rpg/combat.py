# combat.py — Turn-based battle system (Unicorn Overlord style)

import pygame
import math
import random
from typing import List, Optional
from constants import *
from entities import Character, Player, Enemy, Skill, SKILL_FLEE
from ui import (draw_panel, draw_text, draw_combat_status,
                draw_action_menu, draw_combat_log,
                draw_victory, draw_game_over)


# ---------------------------------------------------------------------------
# Hit / shake animation
# ---------------------------------------------------------------------------

class HitEffect:
    def __init__(self, target_is_enemy: bool):
        self.target_is_enemy = target_is_enemy
        self.timer   = 0.0
        self.duration = 0.4   # seconds
        self.active  = True

    def update(self, dt: float):
        self.timer += dt
        if self.timer >= self.duration:
            self.active = False

    def shake_offset(self) -> int:
        """Returns horizontal shake pixel offset."""
        progress = self.timer / self.duration
        return int(8 * math.sin(progress * math.pi * 6) * (1 - progress))

    def flash_alpha(self) -> int:
        progress = self.timer / self.duration
        return int(200 * max(0.0, 1.0 - progress * 3))


# ---------------------------------------------------------------------------
# Sprite drawing helpers (combat view)
# ---------------------------------------------------------------------------

def _draw_hero_sprite(surface: pygame.Surface, cx: int, cy: int,
                      color, color_dark, shake: int = 0, flash_alpha: int = 0):
    x = cx + shake
    size = 80

    # Body
    body = pygame.Rect(x - size // 4, cy - size // 4 + 14, size // 2, size * 2 // 3)
    pygame.draw.rect(surface, color_dark, body, border_radius=6)
    pygame.draw.rect(surface, color, body.inflate(-6, -6), border_radius=6)

    # Cape
    cape_pts = [
        (x - size // 3, cy + size // 4),
        (x + size // 3, cy + size // 4),
        (x + size // 4, cy + size),
        (x - size // 4, cy + size),
    ]
    pygame.draw.polygon(surface, color_dark, cape_pts)

    # Head
    hr = size // 3
    pygame.draw.circle(surface, color, (x, cy - size // 4), hr)
    pygame.draw.circle(surface, color_dark, (x, cy - size // 4), hr, 3)

    # Hair (spiky — anime style)
    for i, angle in enumerate([-40, -20, 0, 20, 40]):
        rad = math.radians(angle - 90)
        hx = x + int((hr + 6) * math.cos(rad))
        hy = (cy - size // 4) + int((hr + 6) * math.sin(rad))
        pygame.draw.circle(surface, color_dark, (hx, hy), 6)

    # Eyes
    eye_r = 5
    pygame.draw.circle(surface, (20, 10, 40), (x - 10, cy - size // 4 - 4), eye_r)
    pygame.draw.circle(surface, (20, 10, 40), (x + 10, cy - size // 4 - 4), eye_r)
    pygame.draw.circle(surface, COLOR_WHITE, (x - 9, cy - size // 4 - 5), 2)
    pygame.draw.circle(surface, COLOR_WHITE, (x + 11, cy - size // 4 - 5), 2)

    # Flash overlay
    if flash_alpha > 0:
        flash_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        flash_surf.fill((255, 255, 255, flash_alpha))
        surface.blit(flash_surf, (x - size, cy - size), special_flags=pygame.BLEND_RGBA_ADD)


def _draw_enemy_sprite(surface: pygame.Surface, cx: int, cy: int,
                       color, color_dark, shake: int = 0, flash_alpha: int = 0):
    x = cx + shake
    size = 70

    # Body blob
    pygame.draw.ellipse(surface, color_dark,
                        pygame.Rect(x - size // 2, cy - size // 3, size, size * 2 // 3))
    pygame.draw.ellipse(surface, color,
                        pygame.Rect(x - size // 2 + 4, cy - size // 3 + 4,
                                    size - 8, size * 2 // 3 - 8))

    # Head
    hr = size // 2 + 6
    pygame.draw.circle(surface, color, (x, cy - size // 3), hr)
    pygame.draw.circle(surface, color_dark, (x, cy - size // 3), hr, 3)

    # Evil eyes
    pygame.draw.ellipse(surface, (220, 220, 0),
                        pygame.Rect(x - 20, cy - size // 3 - 8, 16, 20))
    pygame.draw.ellipse(surface, (220, 220, 0),
                        pygame.Rect(x + 4,  cy - size // 3 - 8, 16, 20))
    pygame.draw.ellipse(surface, (40, 0, 0),
                        pygame.Rect(x - 16, cy - size // 3 - 4, 8, 14))
    pygame.draw.ellipse(surface, (40, 0, 0),
                        pygame.Rect(x + 8,  cy - size // 3 - 4, 8, 14))

    # Jagged mouth
    mpts = [(x - 18, cy - size // 3 + 16)]
    for i in range(5):
        mx = x - 14 + i * 8
        my = (cy - size // 3 + 22) if i % 2 == 0 else (cy - size // 3 + 14)
        mpts.append((mx, my))
    mpts.append((x + 18, cy - size // 3 + 16))
    if len(mpts) >= 2:
        pygame.draw.lines(surface, color_dark, False, mpts, 3)

    # Tendrils
    for i, angle in enumerate([200, 230, 260, 290, 320]):
        rad = math.radians(angle)
        tx = x + int((hr + 20) * math.cos(rad))
        ty = (cy - size // 3) + int((hr + 20) * math.sin(rad))
        pygame.draw.line(surface, color_dark, (x, cy - size // 3), (tx, ty), 3)
        pygame.draw.circle(surface, color, (tx, ty), 5)

    if flash_alpha > 0:
        flash_surf = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
        flash_surf.fill((255, 255, 255, flash_alpha))
        surface.blit(flash_surf, (x - size, cy - size), special_flags=pygame.BLEND_RGBA_ADD)


# ---------------------------------------------------------------------------
# Combat background
# ---------------------------------------------------------------------------

def _draw_combat_bg(surface: pygame.Surface):
    # Sky gradient
    for y in range(SCREEN_H // 2):
        ratio = y / (SCREEN_H // 2)
        r = int(10 + 30 * ratio)
        g = int(5  + 15 * ratio)
        b = int(30 + 40 * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_W, y))

    # Ground
    pygame.draw.rect(surface, (30, 20, 50),
                     pygame.Rect(0, SCREEN_H // 2, SCREEN_W, SCREEN_H // 2))
    pygame.draw.line(surface, (80, 50, 100),
                     (0, SCREEN_H // 2), (SCREEN_W, SCREEN_H // 2), 2)

    # Distant mountains
    for i, (mx, mh, mc) in enumerate([
        (150, 180, (25, 15, 45)),
        (450, 220, (30, 18, 55)),
        (750, 160, (22, 12, 40)),
        (1050, 200, (28, 16, 50)),
    ]):
        pts = [(mx - mh, SCREEN_H // 2),
               (mx, SCREEN_H // 2 - mh),
               (mx + mh, SCREEN_H // 2)]
        pygame.draw.polygon(surface, mc, pts)

    # Stars
    rng = random.Random(42)
    for _ in range(60):
        sx = rng.randint(0, SCREEN_W)
        sy = rng.randint(0, SCREEN_H // 2 - 20)
        sr = rng.randint(1, 3)
        alpha = rng.randint(100, 220)
        star = pygame.Surface((sr * 2, sr * 2), pygame.SRCALPHA)
        pygame.draw.circle(star, (255, 255, 255, alpha), (sr, sr), sr)
        surface.blit(star, (sx - sr, sy - sr))


# ---------------------------------------------------------------------------
# CombatScene
# ---------------------------------------------------------------------------

PHASE_PLAYER = "player"
PHASE_ENEMY  = "enemy"
PHASE_RESULT = "result"

class CombatScene:
    def __init__(self, player: Player, enemy: Enemy):
        self.player   = player
        self.enemy    = enemy
        self.log: List[str] = ["A Shadow Lurker appeared!"]
        self.phase    = PHASE_PLAYER
        self.selected = 0
        self.actions  = player.skills
        self._hit_effect: Optional[HitEffect] = None
        self._enemy_timer = 0.0
        self._enemy_delay = 1.2  # seconds before enemy acts
        self._result: Optional[str] = None  # STATE_VICTORY / STATE_GAME_OVER

        # Restore player HP/MP slightly for fresh fight feel
        # (keep persistent HP so battles have stakes)

    # --- Input ---

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

    # --- Logic ---

    def _execute_player_action(self):
        skill = self.actions[self.selected]

        if skill is SKILL_FLEE:
            self.log.append("You fled from battle!")
            self._result = STATE_EXPLORE
            self.phase = PHASE_RESULT
            return

        if not self.player.use_mp(skill.mp_cost):
            self.log.append("Not enough MP!")
            return

        if skill.heal_amount > 0:
            healed = self.player.heal(skill.heal_amount)
            self.log.append(f"Kairu uses {skill.name} — restored {healed} HP!")
            self.phase = PHASE_ENEMY
            self._enemy_timer = 0.0
            return

        # Damage enemy
        dmg = self.enemy.take_damage(int(self.player.atk * skill.damage_mult))
        self.log.append(f"Kairu uses {skill.name} — {dmg} dmg to {self.enemy.name}!")
        self._hit_effect = HitEffect(target_is_enemy=True)

        if not self.enemy.alive:
            self.log.append(f"{self.enemy.name} is defeated!")
            self._result = STATE_VICTORY
            self.phase = PHASE_RESULT
        else:
            self.phase = PHASE_ENEMY
            self._enemy_timer = 0.0

    def _execute_enemy_action(self):
        skill = self.enemy.choose_action()
        dmg = self.player.take_damage(int(self.enemy.atk * skill.damage_mult))
        self.log.append(f"{self.enemy.name} uses {skill.name} — {dmg} dmg to Kairu!")
        self._hit_effect = HitEffect(target_is_enemy=False)

        if not self.player.alive:
            self.log.append("Kairu has fallen...")
            self._result = STATE_GAME_OVER
            self.phase = PHASE_RESULT
        else:
            self.phase = PHASE_PLAYER

    def update(self, dt: float) -> Optional[str]:
        if self._hit_effect and self._hit_effect.active:
            self._hit_effect.update(dt)

        if self.phase == PHASE_ENEMY:
            self._enemy_timer += dt
            if self._enemy_timer >= self._enemy_delay:
                self._execute_enemy_action()

        return None

    def result_state(self) -> Optional[str]:
        return self._result

    # --- Draw ---

    def draw(self, surface: pygame.Surface):
        _draw_combat_bg(surface)

        # Sprite positions
        hero_cx = SCREEN_W // 4
        hero_cy = SCREEN_H // 2 + 10
        enemy_cx = SCREEN_W * 3 // 4
        enemy_cy = SCREEN_H // 2 - 10

        # Shake offsets
        hero_shake  = 0
        enemy_shake = 0
        flash_hero  = 0
        flash_enemy = 0

        if self._hit_effect and self._hit_effect.active:
            if self._hit_effect.target_is_enemy:
                enemy_shake = self._hit_effect.shake_offset()
                flash_enemy = self._hit_effect.flash_alpha()
            else:
                hero_shake = self._hit_effect.shake_offset()
                flash_hero = self._hit_effect.flash_alpha()

        # Draw sprites
        if self.player.alive:
            _draw_hero_sprite(surface, hero_cx, hero_cy,
                              self.player.color, self.player.color_dark,
                              hero_shake, flash_hero)

        if self.enemy.alive:
            _draw_enemy_sprite(surface, enemy_cx, enemy_cy,
                               self.enemy.color, self.enemy.color_dark,
                               enemy_shake, flash_enemy)

        # Status panels
        draw_combat_status(surface, self.player, 20, 20, w=250)
        draw_combat_status(surface, self.enemy, SCREEN_W - 270, 20, w=250)

        # Action menu (only during player phase)
        if self.phase == PHASE_PLAYER:
            menu_x = 20
            menu_y = SCREEN_H - ACTION_MENU_H - 30
            draw_action_menu(surface, self.actions, self.selected, menu_x, menu_y)

        elif self.phase == PHASE_ENEMY:
            draw_text(surface, f"{self.enemy.name}'s turn...",
                      SCREEN_W // 2, SCREEN_H - 60,
                      COLOR_WHITE_DIM, size=18, center=True)

        # Combat log
        if self.log:
            draw_combat_log(surface, self.log,
                            x=SCREEN_W // 2 - 250,
                            y=SCREEN_H - 110,
                            w=500)

        # Result overlays
        if self.phase == PHASE_RESULT:
            if self._result == STATE_VICTORY:
                draw_victory(surface)
            elif self._result == STATE_GAME_OVER:
                draw_game_over(surface)
