# dialogue.py — Dialogue box renderer with real portrait support

import pygame
import math
from typing import List
from constants import *
from ui import draw_panel, draw_text
from portrait_loader import get_speaker_portrait


class DialogueSystem:
    def __init__(self, sound=None):
        self.lines: List[str] = []
        self.index: int       = 0
        self.active: bool     = False
        self._char_timer:  float = 0.0
        self._chars_shown: int   = 0
        self._typewriter_speed: float = 40.0
        self._sound           = sound
        self._last_tick_char: int = 0

    def start(self, lines: List[str]):
        self.lines        = lines
        self.index        = 0
        self.active       = True
        self._chars_shown = 0
        self._char_timer  = 0.0
        self._last_tick_char = 0

    def advance(self):
        if not self.active:
            return
        current = self.lines[self.index]
        if self._chars_shown < len(current):
            self._chars_shown = len(current)
        else:
            self.index += 1
            if self.index >= len(self.lines):
                self.active = False
            else:
                self._chars_shown    = 0
                self._char_timer     = 0.0
                self._last_tick_char = 0

    def update(self, dt: float):
        if not self.active:
            return
        current = self.lines[self.index]
        if self._chars_shown < len(current):
            self._char_timer  += dt * self._typewriter_speed
            self._chars_shown  = min(int(self._char_timer), len(current))
            if self._sound and self._chars_shown - self._last_tick_char >= 3:
                self._last_tick_char = self._chars_shown
                self._sound.play_sfx('dialogue')

    def draw(self, surface: pygame.Surface):
        if not self.active:
            return

        # Parse speaker from current line
        current = self.lines[self.index]
        visible = current[:self._chars_shown]
        speaker, sep, body = visible.partition(": ")
        if not sep:
            speaker, body = "", visible

        # Also parse from full line for portrait lookup
        full_speaker, _, _ = current.partition(": ")
        if not _:
            full_speaker = ""

        # --- Dialogue box ---
        box_rect = pygame.Rect(0, SCREEN_H - DIALOGUE_BOX_H, SCREEN_W, DIALOGUE_BOX_H)
        draw_panel(surface, box_rect, alpha=235, border_width=2)

        # --- Portrait area ---
        portrait_size = DIALOGUE_BOX_H - DIALOGUE_PADDING * 2
        portrait_rect = pygame.Rect(
            DIALOGUE_PADDING,
            SCREEN_H - DIALOGUE_BOX_H + DIALOGUE_PADDING,
            portrait_size, portrait_size,
        )

        # Try real portrait first
        real_portrait = get_speaker_portrait(full_speaker,
                                             size=(portrait_size, portrait_size))
        if real_portrait:
            # Rounded-corner mask
            mask = pygame.Surface((portrait_size, portrait_size), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255, 255),
                             mask.get_rect(), border_radius=10)
            masked = real_portrait.copy()
            masked.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            surface.blit(masked, portrait_rect.topleft)
            # Gold border over the top
            pygame.draw.rect(surface, COLOR_PANEL_BORDER,
                             portrait_rect, 2, border_radius=10)
        else:
            # Fallback: programmatic face
            _draw_fallback_portrait(surface, portrait_rect, speaker)

        # --- Speaker name ---
        text_x = portrait_rect.right + DIALOGUE_PADDING + 4
        text_y = SCREEN_H - DIALOGUE_BOX_H + DIALOGUE_PADDING

        if speaker:
            # Name banner
            name_font  = pygame.font.SysFont("arial", 18, bold=True)
            name_surf  = name_font.render(speaker, True, COLOR_GOLD)
            banner_rect = pygame.Rect(text_x - 6, text_y - 4,
                                      name_surf.get_width() + 16, name_surf.get_height() + 8)
            banner = pygame.Surface((banner_rect.width, banner_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(banner, (20, 15, 50, 200), banner.get_rect(), border_radius=5)
            surface.blit(banner, banner_rect.topleft)
            pygame.draw.rect(surface, COLOR_GOLD_DIM, banner_rect, 1, border_radius=5)
            surface.blit(name_surf, (text_x, text_y))
            text_y += name_surf.get_height() + 10

        # --- Body text ---
        max_w = SCREEN_W - text_x - DIALOGUE_PADDING - 10
        _draw_wrapped(surface, body, text_x, text_y, max_w, COLOR_WHITE, size=16)

        # --- Advance hint (blinking) ---
        ticks = pygame.time.get_ticks()
        if ticks % 900 < 600:
            if self._chars_shown < len(current):
                hint, col = "▼ ...", COLOR_WHITE_DIM
            else:
                hint, col = "▼  SPACE / ENTER", COLOR_GOLD_DIM
            draw_text(surface, hint,
                      SCREEN_W - DIALOGUE_PADDING - 140,
                      SCREEN_H - DIALOGUE_PADDING - 22,
                      col, size=13)


def _draw_fallback_portrait(surface: pygame.Surface,
                             rect: pygame.Rect, speaker: str):
    """Programmatic face for speakers without a portrait PNG."""
    pygame.draw.rect(surface, (30, 40, 70),        rect, border_radius=8)
    pygame.draw.rect(surface, COLOR_PANEL_BORDER,  rect, 2, border_radius=8)
    cx, cy = rect.centerx, rect.centery
    r  = rect.width // 2 - 6
    pygame.draw.circle(surface, COLOR_NPC, (cx, cy), r)
    pygame.draw.circle(surface, (40, 30, 20), (cx - r//3, cy - r//6), r//5)
    pygame.draw.circle(surface, (40, 30, 20), (cx + r//3, cy - r//6), r//5)
    arc_rect = pygame.Rect(cx - r//3, cy + r//8, r*2//3, r//3)
    pygame.draw.arc(surface, (40, 30, 20), arc_rect, 0, 3.14, 2)
    if speaker:
        font = pygame.font.SysFont("arial", 10)
        init = font.render(speaker[0].upper(), True, COLOR_WHITE)
        surface.blit(init, (cx - init.get_width()//2, cy + r//3))


def _draw_wrapped(surface: pygame.Surface, text: str, x: int, y: int,
                  max_w: int, color, size: int):
    font  = pygame.font.SysFont("arial", size)
    words = text.split()
    line  = ""
    ly    = y
    for word in words:
        test = line + (" " if line else "") + word
        if font.size(test)[0] <= max_w:
            line = test
        else:
            if line:
                surface.blit(font.render(line, True, color), (x, ly))
                ly += size + 5
            line = word
    if line:
        surface.blit(font.render(line, True, color), (x, ly))
