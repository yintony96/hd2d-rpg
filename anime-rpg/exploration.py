# exploration.py — Village exploration with real sprite art

import pygame
import math
import random
from typing import List, Optional
from constants import *
from entities import Player, NPC
from ui import draw_panel, draw_text, draw_explore_hud, draw_hint, draw_glow
from particles import ParticleSystem
from sprite_loader import get_map_sprite, get_env_sprite, ENV_TREE_HEIGHT, ENV_BUILDING_HEIGHT


# ---------------------------------------------------------------------------
# Starfield
# ---------------------------------------------------------------------------
_STAR_RNG = random.Random(0xBEEF_CAFE)
_STARS = [
    (_STAR_RNG.randint(0, SCREEN_W),
     _STAR_RNG.randint(0, SCREEN_H // 2),
     _STAR_RNG.uniform(0.5, 2.5),
     _STAR_RNG.uniform(0, math.pi * 2))
    for _ in range(90)
]


def _draw_sky(surface: pygame.Surface):
    for y in range(SCREEN_H):
        t = y / SCREEN_H
        pygame.draw.line(surface, (int(10+12*t), int(8+10*t), int(28+22*t)),
                         (0, y), (SCREEN_W, y))
    ticks = pygame.time.get_ticks() / 1000.0
    for sx, sy, sr, phase in _STARS:
        twinkle = 0.6 + 0.4 * math.sin(ticks * 1.2 + phase)
        alpha   = int(180 * twinkle)
        r_px    = max(1, int(sr))
        buf     = pygame.Surface((r_px*2+2, r_px*2+2), pygame.SRCALPHA)
        pygame.draw.circle(buf, (220, 220, 255, alpha), (r_px+1, r_px+1), r_px)
        surface.blit(buf, (sx-r_px-1, sy-r_px-1))


# ---------------------------------------------------------------------------
# Tilemap
# ---------------------------------------------------------------------------
_RAW_MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,0,0,0,0,0,0,2,2,0,0,0,0,0,0,0,2,2,1],
    [1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,1],
    [1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,2,2,1],
    [1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,1],
    [1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,1],
    [1,2,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,2,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]
_RAW_MAP[6][16] = 3
_RAW_MAP[7][16] = 3
_RAW_MAP[6][17] = 3


class Tilemap:
    def __init__(self):
        self.data = _RAW_MAP
        self.rows = len(self.data)
        self.cols = len(self.data[0])

    def tile_at(self, col, row):
        return self.data[row][col] if 0 <= row < self.rows and 0 <= col < self.cols else TILE_WALL

    def walkable(self, col, row):
        return self.tile_at(col, row) in (TILE_FLOOR, TILE_GRASS, TILE_TRIGGER)

    def is_trigger(self, col, row):
        return self.tile_at(col, row) == TILE_TRIGGER

    def draw(self, surface: pygame.Surface):
        ticks = pygame.time.get_ticks() / 1000.0
        for row in range(self.rows):
            for col in range(self.cols):
                t = self.data[row][col]
                x, y = col * TILE_SIZE, row * TILE_SIZE
                rect  = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

                if t == TILE_FLOOR:
                    pygame.draw.rect(surface, COLOR_FLOOR, rect)
                    for lx in range(x, x+TILE_SIZE, 16):
                        pygame.draw.line(surface, (38,48,72), (lx,y), (lx,y+TILE_SIZE))
                    for ly in range(y, y+TILE_SIZE, 16):
                        pygame.draw.line(surface, (38,48,72), (x,ly), (x+TILE_SIZE,ly))

                elif t == TILE_WALL:
                    pygame.draw.rect(surface, COLOR_WALL, rect)
                    pygame.draw.rect(surface, COLOR_WALL_TOP, pygame.Rect(x,y,TILE_SIZE,10))
                    pygame.draw.rect(surface, (18,24,48),     pygame.Rect(x,y+TILE_SIZE-4,TILE_SIZE,4))

                elif t == TILE_GRASS:
                    pygame.draw.rect(surface, COLOR_GRASS, rect)
                    sway = math.sin(ticks*1.8 + col*0.7) * 2
                    for gx in range(x+6, x+TILE_SIZE-6, 11):
                        tip_x = gx + int(sway)
                        pygame.draw.line(surface, COLOR_GRASS_LIGHT, (gx, y+TILE_SIZE-4), (tip_x-3, y+TILE_SIZE-15), 2)
                        pygame.draw.line(surface, COLOR_GRASS_LIGHT, (gx, y+TILE_SIZE-4), (tip_x+3, y+TILE_SIZE-15), 2)

                elif t == TILE_TRIGGER:
                    pygame.draw.rect(surface, (25,8,40), rect)
                    cx_t, cy_t = x+TILE_SIZE//2, y+TILE_SIZE//2
                    for ring_r, base_col, speed in [(24,COLOR_SHADOW,1.5),(16,COLOR_ELECTRO,2.2),(8,COLOR_ANEMO,3.0)]:
                        angle = ticks * speed
                        for dot in range(6):
                            da  = angle + dot * math.pi/3
                            dpx = cx_t + int(ring_r * math.cos(da))
                            dpy = cy_t + int(ring_r * math.sin(da))
                            pygame.draw.circle(surface, base_col, (dpx,dpy), 3)
                    pulse = int(20 * abs(math.sin(ticks*2.5)))
                    pygame.draw.circle(surface, (60+pulse,10,80+pulse), (cx_t,cy_t), 6)

                elif t == TILE_WATER:
                    pygame.draw.rect(surface, COLOR_WATER, rect)
                    for wi in range(3):
                        wave_off = int(5*math.sin(ticks*1.2+col*0.5+wi))
                        wy = y+12+wi*14+wave_off
                        if wy < y+TILE_SIZE-4:
                            pygame.draw.line(surface, COLOR_WATER_LIGHT, (x+4,wy), (x+TILE_SIZE-4,wy), 2)


# ---------------------------------------------------------------------------
# Environment decorations — (sprite_id, tile_x, tile_y)
# drawn as overlays, sorted by tile_y so foreground objects appear on top
# ---------------------------------------------------------------------------
_DECORATIONS = [
    # Sprite id            tx   ty   height_override (None = default)
    ("castle_tower",        2,   1,  ENV_BUILDING_HEIGHT + 20),
    ("village_house",      10,   2,  ENV_BUILDING_HEIGHT),
    ("blacksmith_forge",   13,   5,  ENV_BUILDING_HEIGHT),
    ("oak_tree",            4,   3,  ENV_TREE_HEIGHT),
    ("oak_tree",           17,   2,  ENV_TREE_HEIGHT),
    ("pine_cluster",       17,   5,  ENV_TREE_HEIGHT + 10),
    ("pine_cluster",        2,   6,  ENV_TREE_HEIGHT),
]
# Sort by tile_y so tiles further up are drawn first
_DECORATIONS.sort(key=lambda d: d[2])


def _draw_decorations(surface: pygame.Surface):
    for sprite_id, tx, ty, height in _DECORATIONS:
        spr = get_env_sprite(sprite_id, height=height)
        if spr:
            # Anchor bottom-center of sprite to bottom-center of tile
            px = tx * TILE_SIZE + TILE_SIZE // 2 - spr.get_width() // 2
            py = (ty + 1) * TILE_SIZE - spr.get_height()
            surface.blit(spr, (px, py))


# ---------------------------------------------------------------------------
# Character sprite drawing
# ---------------------------------------------------------------------------

def _draw_sprite(surface: pygame.Surface, tile_x: int, tile_y: int,
                 sprite_name: str,
                 fallback_color, fallback_dark, bob: float = 0.0,
                 element_color=None):
    """Draw a character: real sprite if available, else programmatic fallback."""
    spr = get_map_sprite(sprite_name)
    px  = tile_x * TILE_SIZE
    py  = tile_y * TILE_SIZE
    cx  = px + TILE_SIZE // 2
    cy  = py + TILE_SIZE // 2

    if spr:
        # Centre horizontally, anchor feet to bottom of tile
        bx = cx - spr.get_width() // 2
        by = py + TILE_SIZE - spr.get_height() + int(bob)
        if element_color:
            draw_glow(surface, cx, py + TILE_SIZE - 8, element_color, radius=28, alpha_max=70)
        surface.blit(spr, (bx, by))
    else:
        # Programmatic fallback
        _draw_character_sprite_fallback(surface, px, py, fallback_color, fallback_dark,
                                        element_color=element_color, bob=bob)


def _draw_character_sprite_fallback(surface, px, py, color, color_dark,
                                     size=48, element_color=None, bob=0.0):
    cx = px + TILE_SIZE // 2
    cy = py + TILE_SIZE // 2 + int(bob)
    if element_color:
        draw_glow(surface, cx, cy + size//3, element_color, radius=28, alpha_max=80)
    body_rect = pygame.Rect(cx-size//4, cy-size//4+8, size//2, size//2)
    pygame.draw.rect(surface, color_dark, body_rect, border_radius=5)
    pygame.draw.rect(surface, color, body_rect.inflate(-4,-4), border_radius=5)
    head_r = size//4+2
    pygame.draw.circle(surface, color,      (cx, cy-size//4), head_r)
    pygame.draw.circle(surface, color_dark, (cx, cy-size//4), head_r, 2)
    eye_r = max(2, head_r//4)
    for ex in [-eye_r*2, eye_r*2]:
        pygame.draw.circle(surface, COLOR_BLACK, (cx+ex, cy-size//4-1), eye_r)
        pygame.draw.circle(surface, COLOR_WHITE, (cx+ex+1, cy-size//4-2), 1)


# ---------------------------------------------------------------------------
# Ambient orb spawner
# ---------------------------------------------------------------------------
_FIREFLY_COLS = [(80,230,200),(180,230,100),(230,200,60)]
_ORB_INTERVAL = 0.4


# ---------------------------------------------------------------------------
# ExploreScene
# ---------------------------------------------------------------------------

class ExploreScene:
    def __init__(self, player: Player, npcs: List[NPC],
                 particles: Optional[ParticleSystem] = None):
        self.tilemap        = Tilemap()
        self.player         = player
        self.npcs           = npcs
        self.particles      = particles
        self._move_cooldown = 0.0
        self._move_delay    = 0.15
        self._near_npc: Optional[NPC] = None
        self._bob_t         = 0.0
        self._orb_timer     = 0.0

    def handle_event(self, event): pass

    def update(self, dt: float) -> Optional[str]:
        self._move_cooldown = max(0.0, self._move_cooldown - dt)
        self._bob_t        += dt
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if self._move_cooldown <= 0:
            if   keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx = -1
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx =  1
            elif keys[pygame.K_UP]   or keys[pygame.K_w]: dy = -1
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]: dy =  1
            if dx or dy:
                self.player.move(dx, dy, self.tilemap)
                self._move_cooldown = self._move_delay

        if self.tilemap.is_trigger(self.player.tile_x, self.player.tile_y):
            return STATE_COMBAT

        self._near_npc = None
        for npc in self.npcs:
            if npc.near(self.player):
                self._near_npc = npc
                break

        if self.particles:
            self._orb_timer += dt
            if self._orb_timer >= _ORB_INTERVAL:
                self._orb_timer = 0.0
                ox = random.randint(TILE_SIZE, SCREEN_W-TILE_SIZE)
                oy = random.randint(TILE_SIZE*2, SCREEN_H-TILE_SIZE*3)
                self.particles.emit_ambient_orb(float(ox), float(oy),
                                                random.choice(_FIREFLY_COLS))
            self.particles.update(dt)

        return None

    def handle_talk(self) -> Optional[List[str]]:
        return self._near_npc.dialogue if self._near_npc else None

    def draw(self, surface: pygame.Surface):
        _draw_sky(surface)
        self.tilemap.draw(surface)

        # Environment decorations (behind characters)
        _draw_decorations(surface)

        if self.particles:
            self.particles.draw_below(surface)

        bob = math.sin(self._bob_t * 2.5) * 1.5

        # NPC sprites
        for npc in self.npcs:
            sprite_name = {
                "Elder Mira": "elder_mira",
                "Blacksmith": "blacksmith",
            }.get(npc.name, npc.name.lower().replace(" ", "_"))

            _draw_sprite(surface, npc.tile_x, npc.tile_y,
                         sprite_name, npc.color, (100,80,40),
                         element_color=COLOR_GEO)

            # Name tag
            font = pygame.font.SysFont("arial", 12)
            ns   = font.render(npc.name, True, COLOR_GOLD)
            nx   = npc.tile_x * TILE_SIZE + TILE_SIZE//2 - ns.get_width()//2
            surface.blit(ns, (nx, npc.tile_y * TILE_SIZE - 18))

        # Player sprite
        _draw_sprite(surface, self.player.tile_x, self.player.tile_y,
                     "kairu", self.player.color, self.player.color_dark,
                     bob=bob, element_color=COLOR_ANEMO)

        if self.particles:
            self.particles.draw_above(surface)

        draw_explore_hud(surface, self.player)

        if self._near_npc:
            draw_hint(surface, f"[E]  Talk to {self._near_npc.name}")
        elif self.tilemap.is_trigger(self.player.tile_x, self.player.tile_y):
            draw_hint(surface, "A rift in the realm...")

        draw_text(surface, "Move: WASD / Arrows     Talk: E",
                  10, SCREEN_H-22, COLOR_WHITE_DIM, size=13, shadow=False)
