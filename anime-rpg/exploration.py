# exploration.py — Village tilemap, player movement, NPC rendering, camera

import pygame
import math
from typing import List, Tuple, Optional
from constants import *
from entities import Player, NPC
from ui import draw_panel, draw_text, draw_explore_hud, draw_hint


# ---------------------------------------------------------------------------
# Tilemap
# ---------------------------------------------------------------------------

# 20 cols × 11 rows (fits 1280×704; bottom 16px is dialogue-safe margin)
# 0=floor, 1=wall, 2=grass, 3=trigger(red zone), 4=water
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

# Place the trigger tile (red zone at bottom-right of walkable area)
_RAW_MAP[6][16] = 3
_RAW_MAP[7][16] = 3
_RAW_MAP[6][17] = 3


class Tilemap:
    def __init__(self):
        self.data = _RAW_MAP
        self.rows = len(self.data)
        self.cols = len(self.data[0])

    def tile_at(self, col: int, row: int) -> int:
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.data[row][col]
        return TILE_WALL

    def walkable(self, col: int, row: int) -> bool:
        t = self.tile_at(col, row)
        return t in (TILE_FLOOR, TILE_GRASS, TILE_TRIGGER)

    def is_trigger(self, col: int, row: int) -> bool:
        return self.tile_at(col, row) == TILE_TRIGGER

    def draw(self, surface: pygame.Surface):
        for row in range(self.rows):
            for col in range(self.cols):
                t = self.data[row][col]
                x, y = col * TILE_SIZE, row * TILE_SIZE
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

                if t == TILE_FLOOR:
                    pygame.draw.rect(surface, COLOR_FLOOR, rect)
                    # subtle grid lines
                    pygame.draw.rect(surface, (35, 45, 70), rect, 1)

                elif t == TILE_WALL:
                    pygame.draw.rect(surface, COLOR_WALL, rect)
                    # top highlight
                    pygame.draw.rect(surface, COLOR_WALL_TOP,
                                     pygame.Rect(x, y, TILE_SIZE, 8))

                elif t == TILE_GRASS:
                    pygame.draw.rect(surface, COLOR_GRASS, rect)
                    # grass tufts
                    for gx in range(x + 8, x + TILE_SIZE - 8, 14):
                        pygame.draw.line(surface, COLOR_GRASS_LIGHT,
                                         (gx, y + TILE_SIZE - 6),
                                         (gx - 3, y + TILE_SIZE - 16), 2)
                        pygame.draw.line(surface, COLOR_GRASS_LIGHT,
                                         (gx, y + TILE_SIZE - 6),
                                         (gx + 3, y + TILE_SIZE - 16), 2)

                elif t == TILE_TRIGGER:
                    # Animated red glow
                    pulse = int(30 * abs(math.sin(pygame.time.get_ticks() / 400)))
                    col_r = (COLOR_TRIGGER[0] + pulse,
                             COLOR_TRIGGER[1], COLOR_TRIGGER[2])
                    pygame.draw.rect(surface, col_r, rect)
                    pygame.draw.rect(surface, (160, 50, 50), rect, 2)

                elif t == TILE_WATER:
                    pygame.draw.rect(surface, COLOR_WATER, rect)
                    wave_off = int(4 * math.sin(pygame.time.get_ticks() / 600 + col))
                    for wy in range(y + 10 + wave_off, y + TILE_SIZE, 14):
                        pygame.draw.line(surface, COLOR_WATER_LIGHT,
                                         (x + 4, wy), (x + TILE_SIZE - 4, wy), 2)


# ---------------------------------------------------------------------------
# Sprite drawing
# ---------------------------------------------------------------------------

def _draw_character_sprite(surface: pygame.Surface, px: int, py: int,
                            color, color_dark, size: int = 48):
    """Draw a simple anime-style character (circle head + body)."""
    cx = px + TILE_SIZE // 2
    cy = py + TILE_SIZE // 2

    # Shadow
    pygame.draw.ellipse(surface, (0, 0, 0, 0),
                        pygame.Rect(cx - size // 3, cy + size // 2 - 4,
                                    size * 2 // 3, 8))

    body_rect = pygame.Rect(cx - size // 4, cy - size // 4 + 8,
                             size // 2, size // 2)
    pygame.draw.rect(surface, color_dark, body_rect, border_radius=4)
    pygame.draw.rect(surface, color, body_rect.inflate(-4, -4), border_radius=4)

    # Head
    head_r = size // 4 + 2
    pygame.draw.circle(surface, color, (cx, cy - size // 4), head_r)
    pygame.draw.circle(surface, color_dark, (cx, cy - size // 4), head_r, 2)

    # Eyes
    eye_r = max(2, head_r // 4)
    pygame.draw.circle(surface, COLOR_BLACK, (cx - eye_r * 2, cy - size // 4 - 1), eye_r)
    pygame.draw.circle(surface, COLOR_BLACK, (cx + eye_r * 2, cy - size // 4 - 1), eye_r)
    # Eye shine
    pygame.draw.circle(surface, COLOR_WHITE, (cx - eye_r * 2 + 1, cy - size // 4 - 2), 1)
    pygame.draw.circle(surface, COLOR_WHITE, (cx + eye_r * 2 + 1, cy - size // 4 - 2), 1)


# ---------------------------------------------------------------------------
# ExploreScene
# ---------------------------------------------------------------------------

class ExploreScene:
    def __init__(self, player: Player, npcs: List[NPC]):
        self.tilemap  = Tilemap()
        self.player   = player
        self.npcs     = npcs
        self._move_cooldown = 0.0
        self._move_delay    = 0.15   # seconds between moves
        self._near_npc: Optional[NPC] = None

    def handle_event(self, event: pygame.event.Event):
        pass  # movement handled in update()

    def update(self, dt: float) -> Optional[str]:
        """Return next state string or None."""
        self._move_cooldown = max(0.0, self._move_cooldown - dt)

        keys = pygame.key.get_pressed()
        dx = dy = 0
        if self._move_cooldown <= 0:
            if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx = -1
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = 1
            elif keys[pygame.K_UP]   or keys[pygame.K_w]: dy = -1
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = 1

            if dx != 0 or dy != 0:
                self.player.move(dx, dy, self.tilemap)
                self._move_cooldown = self._move_delay

        # Check trigger
        if self.tilemap.is_trigger(self.player.tile_x, self.player.tile_y):
            return STATE_COMBAT

        # Check NPC proximity
        self._near_npc = None
        for npc in self.npcs:
            if npc.near(self.player):
                self._near_npc = npc
                break

        return None

    def handle_talk(self) -> Optional[List[str]]:
        """Called when E is pressed. Returns dialogue lines or None."""
        if self._near_npc:
            return self._near_npc.dialogue
        return None

    def draw(self, surface: pygame.Surface):
        # Background sky gradient (top portion above map)
        surface.fill(COLOR_BG)

        self.tilemap.draw(surface)

        # Draw NPCs
        for npc in self.npcs:
            _draw_character_sprite(surface, npc.px, npc.py,
                                   npc.color, (100, 80, 40))
            # Name tag
            font = pygame.font.SysFont("arial", 12)
            name_surf = font.render(npc.name, True, COLOR_GOLD)
            nx = npc.px + TILE_SIZE // 2 - name_surf.get_width() // 2
            surface.blit(name_surf, (nx, npc.py - 16))

        # Draw player
        _draw_character_sprite(surface, self.player.px, self.player.py,
                               self.player.color, self.player.color_dark)

        # HUD
        draw_explore_hud(surface, self.player)

        # Talk hint
        if self._near_npc:
            draw_hint(surface, f"Press E — talk to {self._near_npc.name}")
        elif self.tilemap.is_trigger(self.player.tile_x, self.player.tile_y):
            draw_hint(surface, "Danger lurks here...")

        # Controls reminder (bottom-left)
        draw_text(surface, "Move: WASD / Arrows   Talk: E",
                  10, SCREEN_H - 22, COLOR_WHITE_DIM, size=13, shadow=False)
