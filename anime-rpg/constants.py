# constants.py — Screen config, colors, game states, fonts

import pygame

# --- Screen ---
SCREEN_W = 1280
SCREEN_H = 720
FPS = 60
TITLE = "Shattered Realm"

# --- Tile ---
TILE_SIZE = 64
MAP_COLS = 20
MAP_ROWS = 11

# --- Game States ---
STATE_EXPLORE  = "explore"
STATE_DIALOGUE = "dialogue"
STATE_COMBAT   = "combat"
STATE_VICTORY  = "victory"
STATE_GAME_OVER = "game_over"

# --- Tile Types ---
TILE_FLOOR   = 0
TILE_WALL    = 1
TILE_GRASS   = 2
TILE_TRIGGER = 3   # steps here → combat
TILE_WATER   = 4

# --- Anime Color Palette ---
COLOR_BG          = (15,  18,  40)   # deep midnight blue
COLOR_FLOOR       = (42,  52,  80)
COLOR_WALL        = (22,  28,  55)
COLOR_WALL_TOP    = (55,  65, 100)
COLOR_GRASS       = (34,  72,  44)
COLOR_GRASS_LIGHT = (50, 100,  60)
COLOR_TRIGGER     = (80,  30,  30)
COLOR_WATER       = (20,  60, 120)
COLOR_WATER_LIGHT = (40,  90, 160)

COLOR_GOLD        = (255, 210,  80)
COLOR_GOLD_DIM    = (180, 145,  40)
COLOR_WHITE       = (240, 240, 255)
COLOR_WHITE_DIM   = (160, 160, 190)
COLOR_BLACK       = (  5,   5,  15)

COLOR_HP_GREEN    = ( 80, 220, 120)
COLOR_HP_RED      = (220,  60,  60)
COLOR_MP_BLUE     = ( 80, 160, 255)
COLOR_XP_YELLOW   = (255, 200,  50)

COLOR_PANEL_BG    = ( 10,  12,  30, 200)   # semi-transparent (needs special surface)
COLOR_PANEL_BORDER= (200, 170,  60)

COLOR_HERO        = ( 80, 200, 220)   # teal — player sprite
COLOR_HERO_DARK   = ( 40, 120, 140)
COLOR_NPC         = (200, 180, 120)   # warm tan — NPC
COLOR_ENEMY       = (200,  60,  60)   # crimson — enemy
COLOR_ENEMY_DARK  = (120,  30,  30)

COLOR_SKILL_BLUE  = ( 60, 140, 255)
COLOR_SKILL_RED   = (255,  80,  80)
COLOR_SKILL_GREEN = ( 80, 220, 100)

# --- UI Geometry ---
DIALOGUE_BOX_H    = 160
DIALOGUE_PADDING  = 20
ACTION_MENU_W     = 220
ACTION_MENU_H     = 200
COMBAT_LOG_LINES  = 4

# --- Font helper (call after pygame.init) ---
_fonts = {}

def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont("arial", size, bold=bold)
    return _fonts[key]
