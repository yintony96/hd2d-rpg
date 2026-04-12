# dialogue.py — Dialogue box renderer and script runner (Octopath-style)

import pygame
from typing import List
from constants import *
from ui import draw_panel, draw_text


class DialogueSystem:
    def __init__(self):
        self.lines: List[str] = []
        self.index: int = 0
        self.active: bool = False
        self._char_timer: float = 0.0
        self._chars_shown: int = 0
        self._typewriter_speed: float = 40.0  # chars per second

    def start(self, lines: List[str]):
        self.lines = lines
        self.index = 0
        self.active = True
        self._chars_shown = 0
        self._char_timer = 0.0

    def advance(self):
        """SPACE / ENTER pressed."""
        if not self.active:
            return
        current = self.lines[self.index]
        if self._chars_shown < len(current):
            # Skip typewriter — show full line instantly
            self._chars_shown = len(current)
        else:
            self.index += 1
            if self.index >= len(self.lines):
                self.active = False
            else:
                self._chars_shown = 0
                self._char_timer = 0.0

    def update(self, dt: float):
        if not self.active:
            return
        current = self.lines[self.index]
        if self._chars_shown < len(current):
            self._char_timer += dt * self._typewriter_speed
            self._chars_shown = min(int(self._char_timer), len(current))

    def draw(self, surface: pygame.Surface):
        if not self.active:
            return

        box_rect = pygame.Rect(0, SCREEN_H - DIALOGUE_BOX_H, SCREEN_W, DIALOGUE_BOX_H)
        draw_panel(surface, box_rect, alpha=230, border_width=2)

        # Portrait placeholder (left side circle)
        portrait_rect = pygame.Rect(
            DIALOGUE_PADDING,
            SCREEN_H - DIALOGUE_BOX_H + DIALOGUE_PADDING,
            DIALOGUE_BOX_H - DIALOGUE_PADDING * 2,
            DIALOGUE_BOX_H - DIALOGUE_PADDING * 2,
        )
        pygame.draw.rect(surface, (30, 40, 70),    portrait_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, portrait_rect, 2, border_radius=8)

        # Simple face: circle head + dot eyes
        cx = portrait_rect.centerx
        cy = portrait_rect.centery
        r  = portrait_rect.width // 2 - 4
        pygame.draw.circle(surface, COLOR_NPC, (cx, cy), r)
        pygame.draw.circle(surface, (40, 30, 20), (cx - r//3, cy - r//6), r//5)
        pygame.draw.circle(surface, (40, 30, 20), (cx + r//3, cy - r//6), r//5)
        arc_rect = pygame.Rect(cx - r//3, cy + r//8, r*2//3, r//3)
        pygame.draw.arc(surface, (40, 30, 20), arc_rect, 0, 3.14, 2)

        # Speaker name (parse "Name: text" format)
        current = self.lines[self.index]
        visible = current[:self._chars_shown]
        speaker, _, body = visible.partition(": ")
        if not _:
            speaker, body = "", visible

        text_x = portrait_rect.right + DIALOGUE_PADDING
        text_y = SCREEN_H - DIALOGUE_BOX_H + DIALOGUE_PADDING

        if speaker:
            draw_text(surface, speaker, text_x, text_y,
                      COLOR_GOLD, size=17, bold=True)
            text_y += 26

        # Word-wrap the body text
        max_w = SCREEN_W - text_x - DIALOGUE_PADDING
        _draw_wrapped(surface, body, text_x, text_y, max_w,
                      COLOR_WHITE, size=16)

        # Advance hint (blinking arrow)
        ticks = pygame.time.get_ticks()
        if ticks % 1000 < 700:
            hint = "SPACE / ENTER"
            if self._chars_shown < len(current):
                hint = "..."
            draw_text(surface, hint,
                      SCREEN_W - DIALOGUE_PADDING - 120,
                      SCREEN_H - DIALOGUE_PADDING - 20,
                      COLOR_GOLD_DIM, size=13)


def _draw_wrapped(surface: pygame.Surface, text: str, x: int, y: int,
                  max_w: int, color, size: int):
    font = pygame.font.SysFont("arial", size)
    words = text.split()
    line = ""
    line_y = y
    for word in words:
        test = line + (" " if line else "") + word
        if font.size(test)[0] <= max_w:
            line = test
        else:
            if line:
                surface.blit(font.render(line, True, color), (x, line_y))
                line_y += size + 4
            line = word
    if line:
        surface.blit(font.render(line, True, color), (x, line_y))
