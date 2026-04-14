# ui.py — Genshin-inspired HUD: glowing bars, ornate panels, menus

import pygame
import math
from typing import List, Tuple
from constants import *


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def draw_panel(surface: pygame.Surface, rect: pygame.Rect,
               alpha: int = 210, border_color=COLOR_PANEL_BORDER,
               border_width: int = 2, radius: int = 10):
    """Semi-transparent panel with a gradient fill and gold border."""
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

    # Gradient: slightly lighter at top
    for y in range(rect.height):
        t   = y / max(rect.height - 1, 1)
        r   = int(COLOR_PANEL_GRAD[0] * (1 - t * 0.4))
        g   = int(COLOR_PANEL_GRAD[1] * (1 - t * 0.3))
        b   = int(COLOR_PANEL_GRAD[2] * (1 - t * 0.2))
        pygame.draw.line(panel, (r, g, b, alpha), (0, y), (rect.width, y))

    # Clip to rounded rect
    clip = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(clip, (255, 255, 255, 255), clip.get_rect(), border_radius=radius)
    panel.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    surface.blit(panel, rect.topleft)

    # Outer border
    pygame.draw.rect(surface, border_color, rect, border_width, border_radius=radius)
    # Inner highlight line (top edge shimmer)
    hi_rect = pygame.Rect(rect.x + border_width, rect.y + border_width,
                          rect.width - border_width * 2, 1)
    pygame.draw.rect(surface, COLOR_GOLD_BRIGHT, hi_rect)


def draw_bar(surface: pygame.Surface, x: int, y: int, w: int, h: int,
             value: float, max_value: float,
             fill_color: Tuple, bg_color: Tuple = (30, 35, 60),
             label: str = "", font_size: int = 14):
    """Rounded progress bar with glow highlight."""
    bg_rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surface, bg_color, bg_rect, border_radius=h // 2)

    if max_value > 0 and value > 0:
        fill_w = max(h, int(w * min(1.0, value / max_value)))
        fill_rect = pygame.Rect(x, y, fill_w, h)
        pygame.draw.rect(surface, fill_color, fill_rect, border_radius=h // 2)

        # Bright highlight stripe on top of fill
        hi_h = max(1, h // 4)
        r, g, b = fill_color
        hi_col  = (min(255, r + 80), min(255, g + 80), min(255, b + 80))
        hi_rect = pygame.Rect(x + 4, y + 1, fill_w - 8, hi_h)
        if hi_rect.width > 0:
            pygame.draw.rect(surface, hi_col, hi_rect, border_radius=hi_h)

    pygame.draw.rect(surface, COLOR_WHITE_DIM, bg_rect, 1, border_radius=h // 2)

    if label:
        font = get_font(font_size)
        txt  = font.render(label, True, COLOR_WHITE)
        surface.blit(txt, (x + 5, y + h // 2 - txt.get_height() // 2))


def draw_text(surface: pygame.Surface, text: str, x: int, y: int,
              color=COLOR_WHITE, size: int = 16, bold: bool = False,
              center: bool = False, shadow: bool = True):
    font = get_font(size, bold)
    if shadow:
        sh = font.render(text, True, COLOR_BLACK)
        ox = x - sh.get_width() // 2 if center else x
        surface.blit(sh, (ox + 2, y + 2))
    surf = font.render(text, True, color)
    ox   = x - surf.get_width() // 2 if center else x
    surface.blit(surf, (ox, y))
    return surf.get_width()


# ---------------------------------------------------------------------------
# Genshin-style glow circle (aura under characters)
# ---------------------------------------------------------------------------

def draw_glow(surface: pygame.Surface, cx: int, cy: int,
              color: Tuple, radius: int = 36, alpha_max: int = 90):
    """Soft radial glow painted under a character."""
    buf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    r, g, b = color[:3]
    steps   = radius // 4
    for i in range(steps, 0, -1):
        frac = i / steps
        a    = int(alpha_max * (1 - frac) ** 1.5)
        pygame.draw.circle(buf, (r, g, b, a),
                           (radius, radius), int(radius * frac))
    surface.blit(buf, (cx - radius, cy - radius),
                 special_flags=pygame.BLEND_RGBA_ADD)


# ---------------------------------------------------------------------------
# Exploration HUD
# ---------------------------------------------------------------------------

def draw_explore_hud(surface: pygame.Surface, player):
    rect = pygame.Rect(10, 10, 210, 76)
    draw_panel(surface, rect)

    draw_text(surface, player.name, 22, 16, COLOR_GOLD, size=17, bold=True)

    draw_bar(surface, 22, 38, 176, 13,
             player.hp, player.max_hp, COLOR_HP_GREEN,
             label=f"HP {player.hp}/{player.max_hp}", font_size=11)

    draw_bar(surface, 22, 57, 176, 13,
             player.mp, player.max_mp, COLOR_MP_BLUE,
             label=f"MP {player.mp}/{player.max_mp}", font_size=11)


# ---------------------------------------------------------------------------
# Combat Status Panels
# ---------------------------------------------------------------------------

def draw_combat_status(surface: pygame.Surface, character, x: int, y: int,
                       w: int = 250):
    from portrait_loader import get_entity_portrait
    PORTRAIT_SZ = 72
    rect = pygame.Rect(x, y, w, 110)
    draw_panel(surface, rect)

    portrait = get_entity_portrait(character.name, size=(PORTRAIT_SZ, PORTRAIT_SZ))
    if portrait:
        # Portrait on the left inside the panel
        px = x + 10
        py = y + (110 - PORTRAIT_SZ) // 2
        # Rounded mask
        mask = pygame.Surface((PORTRAIT_SZ, PORTRAIT_SZ), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255),
                         mask.get_rect(), border_radius=8)
        masked = portrait.copy()
        masked.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surface.blit(masked, (px, py))
        pygame.draw.rect(surface, COLOR_PANEL_BORDER,
                         pygame.Rect(px, py, PORTRAIT_SZ, PORTRAIT_SZ), 2,
                         border_radius=8)
        text_x = px + PORTRAIT_SZ + 10
    else:
        text_x = x + 14

    bar_w = w - (text_x - x) - 14
    draw_text(surface, character.name, text_x, y + 10,
              COLOR_GOLD, size=17, bold=True)
    draw_bar(surface, text_x, y + 38, bar_w, 15,
             character.hp, character.max_hp, COLOR_HP_GREEN,
             label=f"HP  {character.hp}/{character.max_hp}", font_size=12)
    if character.max_mp > 0:
        draw_bar(surface, text_x, y + 62, bar_w, 15,
                 character.mp, character.max_mp, COLOR_MP_BLUE,
                 label=f"MP  {character.mp}/{character.max_mp}", font_size=12)


# ---------------------------------------------------------------------------
# Action Menu
# ---------------------------------------------------------------------------

# Elemental color per skill name
_SKILL_COLORS = {
    "Attack":      COLOR_GOLD,
    "Power Slash": COLOR_ANEMO,
    "Mend":        COLOR_HP_GREEN,
    "Flee":        COLOR_WHITE_DIM,
}

def draw_action_menu(surface: pygame.Surface, actions: List,
                     selected: int, x: int, y: int):
    row_h   = 40
    padding = 14
    w       = ACTION_MENU_W + 20
    h       = padding * 2 + row_h * len(actions)

    rect = pygame.Rect(x, y, w, h)
    draw_panel(surface, rect)
    draw_text(surface, "ACTION", x + padding, y + 6, COLOR_GOLD_DIM, size=12, bold=True)

    for i, action in enumerate(actions):
        ry    = y + padding + i * row_h + 12
        label = str(action)
        skill_col = _SKILL_COLORS.get(label, COLOR_WHITE)

        if i == selected:
            sel_rect = pygame.Rect(x + 6, ry - 6, w - 12, row_h - 2)
            # Genshin-style selection: dark blue fill with elemental color border
            sel_surf = pygame.Surface((sel_rect.width, sel_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(sel_surf, (40, 65, 130, 200),
                             sel_surf.get_rect(), border_radius=6)
            surface.blit(sel_surf, sel_rect.topleft)
            pygame.draw.rect(surface, skill_col, sel_rect, 2, border_radius=6)
            draw_text(surface, f"  {label}", x + padding + 2, ry,
                      COLOR_WHITE, size=17, bold=True)
        else:
            draw_text(surface, label, x + padding + 16, ry,
                      COLOR_WHITE_DIM, size=15)

        if hasattr(action, 'mp_cost') and action.mp_cost > 0:
            draw_text(surface, f"{action.mp_cost}MP",
                      x + w - 52, ry, COLOR_MP_BLUE, size=13)


# ---------------------------------------------------------------------------
# Combat Log
# ---------------------------------------------------------------------------

def draw_combat_log(surface: pygame.Surface, messages: List[str],
                    x: int, y: int, w: int = 500):
    visible = messages[-COMBAT_LOG_LINES:]
    h       = 22 + len(visible) * 23
    rect    = pygame.Rect(x, y, w, h)
    draw_panel(surface, rect, alpha=175)

    for i, msg in enumerate(visible):
        col = COLOR_WHITE if i == len(visible) - 1 else COLOR_WHITE_DIM
        draw_text(surface, msg, x + 14, y + 11 + i * 23, col, size=14)


# ---------------------------------------------------------------------------
# Hint prompt
# ---------------------------------------------------------------------------

def draw_hint(surface: pygame.Surface, text: str):
    ticks = pygame.time.get_ticks()
    pulse = 0.5 + 0.5 * math.sin(ticks / 400)
    r = int(COLOR_GOLD[0] * 0.7 + COLOR_GOLD_BRIGHT[0] * 0.3 * pulse)
    g = int(COLOR_GOLD[1] * 0.7 + COLOR_GOLD_BRIGHT[1] * 0.3 * pulse)
    b = int(COLOR_GOLD[2] * 0.7 + COLOR_GOLD_BRIGHT[2] * 0.3 * pulse)

    font = get_font(15)
    surf = font.render(text, True, (r, g, b))
    x    = SCREEN_W // 2 - surf.get_width() // 2
    y    = SCREEN_H - DIALOGUE_BOX_H - 40
    bg   = pygame.Rect(x - 12, y - 6, surf.get_width() + 24, surf.get_height() + 12)
    draw_panel(surface, bg, alpha=185, border_width=1)
    surface.blit(surf, (x, y))


# ---------------------------------------------------------------------------
# Full-screen overlays
# ---------------------------------------------------------------------------

def draw_victory(surface: pygame.Surface):
    _draw_overlay(surface, "VICTORY!", COLOR_ANEMO,
                  "The shadow is vanquished.",
                  "Press ENTER to return to the village.")


def draw_game_over(surface: pygame.Surface):
    _draw_overlay(surface, "FALLEN", COLOR_HP_RED,
                  "The darkness claims you...",
                  "Press ENTER to return to the village.")


def _draw_overlay(surface: pygame.Surface, title: str, title_color,
                  subtitle: str, hint: str):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    surface.blit(overlay, (0, 0))

    # Decorative horizontal lines
    cx = SCREEN_W // 2
    mid_y = SCREEN_H // 2
    for dx, col in [(-300, COLOR_GOLD_DIM), (300, COLOR_GOLD_DIM)]:
        pygame.draw.line(surface, col, (cx + dx, mid_y - 48), (cx, mid_y - 48), 1)

    draw_text(surface, title, cx, mid_y - 72,
              title_color, size=68, bold=True, center=True)
    draw_text(surface, subtitle, cx, mid_y + 14,
              COLOR_WHITE, size=24, center=True)
    draw_text(surface, hint, cx, mid_y + 56,
              COLOR_GOLD_DIM, size=18, center=True)
