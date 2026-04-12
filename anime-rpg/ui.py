# ui.py — Anime-style HUD: HP/MP bars, action menu, combat log, status panels

import pygame
from typing import List, Tuple, Optional
from constants import *


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def draw_panel(surface: pygame.Surface, rect: pygame.Rect,
               alpha: int = 210, border_color=COLOR_PANEL_BORDER,
               border_width: int = 2, radius: int = 8):
    """Draw a semi-transparent dark panel with a gold border."""
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, (*COLOR_BLACK, alpha), panel.get_rect(), border_radius=radius)
    surface.blit(panel, rect.topleft)
    pygame.draw.rect(surface, border_color, rect, border_width, border_radius=radius)


def draw_bar(surface: pygame.Surface, x: int, y: int, w: int, h: int,
             value: float, max_value: float,
             fill_color: Tuple, bg_color: Tuple = (40, 40, 60),
             label: str = "", font_size: int = 14):
    """Draw a rounded progress bar with optional label."""
    bg_rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surface, bg_color, bg_rect, border_radius=h // 2)

    if max_value > 0:
        fill_w = int(w * max(0.0, min(1.0, value / max_value)))
        if fill_w > 0:
            fill_rect = pygame.Rect(x, y, fill_w, h)
            pygame.draw.rect(surface, fill_color, fill_rect, border_radius=h // 2)

    pygame.draw.rect(surface, COLOR_WHITE_DIM, bg_rect, 1, border_radius=h // 2)

    if label:
        font = get_font(font_size)
        txt = font.render(label, True, COLOR_WHITE)
        surface.blit(txt, (x + 4, y + h // 2 - txt.get_height() // 2))


def draw_text(surface: pygame.Surface, text: str, x: int, y: int,
              color=COLOR_WHITE, size: int = 16, bold: bool = False,
              center: bool = False, shadow: bool = True):
    font = get_font(size, bold)
    if shadow:
        shadow_surf = font.render(text, True, COLOR_BLACK)
        ox = x - shadow_surf.get_width() // 2 if center else x
        surface.blit(shadow_surf, (ox + 1, y + 1))
    surf = font.render(text, True, color)
    ox = x - surf.get_width() // 2 if center else x
    surface.blit(surf, (ox, y))
    return surf.get_width()


# ---------------------------------------------------------------------------
# Status Panel (exploration HUD — top-left)
# ---------------------------------------------------------------------------

def draw_explore_hud(surface: pygame.Surface, player):
    rect = pygame.Rect(10, 10, 200, 70)
    draw_panel(surface, rect)

    draw_text(surface, player.name, 20, 16, COLOR_GOLD, size=16, bold=True)

    draw_bar(surface, 20, 36, 170, 12,
             player.hp, player.max_hp, COLOR_HP_GREEN,
             label=f"HP {player.hp}/{player.max_hp}", font_size=11)

    draw_bar(surface, 20, 54, 170, 12,
             player.mp, player.max_mp, COLOR_MP_BLUE,
             label=f"MP {player.mp}/{player.max_mp}", font_size=11)


# ---------------------------------------------------------------------------
# Combat Status Panels
# ---------------------------------------------------------------------------

def draw_combat_status(surface: pygame.Surface, character, x: int, y: int,
                       w: int = 240):
    rect = pygame.Rect(x, y, w, 90)
    draw_panel(surface, rect)

    draw_text(surface, character.name, x + 12, y + 10,
              COLOR_GOLD, size=17, bold=True)

    draw_bar(surface, x + 12, y + 34, w - 24, 14,
             character.hp, character.max_hp, COLOR_HP_GREEN,
             label=f"HP  {character.hp}/{character.max_hp}", font_size=12)

    if character.max_mp > 0:
        draw_bar(surface, x + 12, y + 56, w - 24, 14,
                 character.mp, character.max_mp, COLOR_MP_BLUE,
                 label=f"MP  {character.mp}/{character.max_mp}", font_size=12)


# ---------------------------------------------------------------------------
# Action Menu
# ---------------------------------------------------------------------------

def draw_action_menu(surface: pygame.Surface, actions: List,
                     selected: int, x: int, y: int):
    """Draw the combat action selector. `actions` can be Skill objects or strings."""
    row_h = 38
    padding = 12
    w = ACTION_MENU_W
    h = padding * 2 + row_h * len(actions)

    rect = pygame.Rect(x, y, w, h)
    draw_panel(surface, rect)
    draw_text(surface, "ACTION", x + padding, y + 6, COLOR_GOLD_DIM, size=12, bold=True)

    for i, action in enumerate(actions):
        ry = y + padding + i * row_h + 10
        label = str(action)
        if i == selected:
            sel_rect = pygame.Rect(x + 6, ry - 4, w - 12, row_h - 4)
            pygame.draw.rect(surface, (50, 80, 140), sel_rect, border_radius=5)
            pygame.draw.rect(surface, COLOR_GOLD, sel_rect, 1, border_radius=5)
            draw_text(surface, f"> {label}", x + padding + 4, ry,
                      COLOR_WHITE, size=16, bold=True)
        else:
            draw_text(surface, label, x + padding + 14, ry,
                      COLOR_WHITE_DIM, size=15)

        # Show MP cost if Skill
        if hasattr(action, 'mp_cost') and action.mp_cost > 0:
            cost_txt = f"{action.mp_cost}MP"
            draw_text(surface, cost_txt, x + w - 50, ry,
                      COLOR_MP_BLUE, size=13)


# ---------------------------------------------------------------------------
# Combat Log
# ---------------------------------------------------------------------------

def draw_combat_log(surface: pygame.Surface, messages: List[str],
                    x: int, y: int, w: int = 500):
    visible = messages[-COMBAT_LOG_LINES:]
    h = 20 + len(visible) * 22
    rect = pygame.Rect(x, y, w, h)
    draw_panel(surface, rect, alpha=180)

    for i, msg in enumerate(visible):
        alpha_val = 150 + int(105 * (i + 1) / len(visible)) if visible else 255
        col = (*COLOR_WHITE_DIM[:3],) if i < len(visible) - 1 else COLOR_WHITE
        draw_text(surface, msg, x + 12, y + 10 + i * 22, col, size=14)


# ---------------------------------------------------------------------------
# Prompt hint (e.g. "Press E to talk")
# ---------------------------------------------------------------------------

def draw_hint(surface: pygame.Surface, text: str):
    font = get_font(15)
    surf = font.render(text, True, COLOR_GOLD)
    x = SCREEN_W // 2 - surf.get_width() // 2
    y = SCREEN_H - DIALOGUE_BOX_H - 36
    bg = pygame.Rect(x - 10, y - 4, surf.get_width() + 20, surf.get_height() + 8)
    draw_panel(surface, bg, alpha=180, border_width=1)
    surface.blit(surf, (x, y))


# ---------------------------------------------------------------------------
# Full-screen overlays
# ---------------------------------------------------------------------------

def draw_victory(surface: pygame.Surface):
    _draw_overlay(surface, "VICTORY!", COLOR_HP_GREEN,
                  "You defeated the Shadow Lurker!",
                  "Press ENTER to return to the village.")


def draw_game_over(surface: pygame.Surface):
    _draw_overlay(surface, "GAME OVER", COLOR_HP_RED,
                  "You have fallen in battle...",
                  "Press ENTER to return to the village.")


def _draw_overlay(surface: pygame.Surface, title: str, title_color,
                  subtitle: str, hint: str):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    draw_text(surface, title, SCREEN_W // 2, SCREEN_H // 2 - 70,
              title_color, size=64, bold=True, center=True)
    draw_text(surface, subtitle, SCREEN_W // 2, SCREEN_H // 2 + 10,
              COLOR_WHITE, size=24, center=True)
    draw_text(surface, hint, SCREEN_W // 2, SCREEN_H // 2 + 55,
              COLOR_GOLD_DIM, size=18, center=True)
