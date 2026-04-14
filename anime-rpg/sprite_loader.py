# sprite_loader.py — Load, cache and serve all game art assets

import pygame
import pathlib
from typing import Tuple, Optional

_BASE = pathlib.Path(__file__).parent / "assets"
_cache: dict = {}

# ---------------------------------------------------------------------------
# Target display sizes (px).  Sprites are scaled to these on load.
# ---------------------------------------------------------------------------
MAP_CHAR_HEIGHT    = 54    # character on the exploration map
BATTLE_HEIGHT      = 260   # battle sprite height
ENV_TREE_HEIGHT    = 100   # tree decoration
ENV_BUILDING_HEIGHT = 140  # village house / forge / tower


def _load(path: pathlib.Path, height: int) -> Optional[pygame.Surface]:
    key = str(path)
    if key in _cache:
        return _cache[key]
    if not path.exists():
        _cache[key] = None
        return None
    try:
        img = pygame.image.load(str(path)).convert_alpha()
        # Scale to target height, preserving aspect ratio
        w, h = img.get_size()
        new_w = max(1, int(w * height / h))
        img = pygame.transform.smoothscale(img, (new_w, height))
        _cache[key] = img
        return img
    except Exception as e:
        print(f"[sprite_loader] failed to load {path.name}: {e}")
        _cache[key] = None
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_map_sprite(name: str) -> Optional[pygame.Surface]:
    """Small character sprite for the exploration map."""
    return _load(_BASE / "sprites" / "map" / f"{name}.png", MAP_CHAR_HEIGHT)


def get_battle_sprite(name: str) -> Optional[pygame.Surface]:
    """Tall side-view sprite for the combat scene."""
    return _load(_BASE / "sprites" / "battle" / f"{name}.png", BATTLE_HEIGHT)


def get_env_sprite(name: str, height: int = None) -> Optional[pygame.Surface]:
    """Environment decoration (tree, building, etc.)."""
    h = height or ENV_BUILDING_HEIGHT
    return _load(_BASE / "sprites" / "environment" / f"{name}.png", h)


def get_portrait(name: str, size: Tuple[int, int] = (120, 120)) -> Optional[pygame.Surface]:
    path = _BASE / "portraits" / f"{name}.png"
    key  = (str(path), size)
    if key in _cache:
        return _cache[key]
    if not path.exists():
        _cache[key] = None
        return None
    try:
        img = pygame.image.load(str(path)).convert_alpha()
        img = pygame.transform.smoothscale(img, size)
        _cache[key] = img
        return img
    except Exception:
        _cache[key] = None
        return None


# Speaker-name → portrait file id
SPEAKER_MAP = {
    "Elder Mira":  "elder_mira",
    "Blacksmith":  "blacksmith",
    "Kairu":       "kairu",
}

ENTITY_MAP = {
    "Kairu":         "kairu",
    "Shadow Lurker": "shadow_lurker",
}


def get_speaker_portrait(speaker: str,
                          size: Tuple[int, int] = (120, 120)) -> Optional[pygame.Surface]:
    fid = SPEAKER_MAP.get(speaker)
    return get_portrait(fid, size) if fid else None


def get_entity_portrait(entity: str,
                         size: Tuple[int, int] = (80, 80)) -> Optional[pygame.Surface]:
    fid = ENTITY_MAP.get(entity)
    return get_portrait(fid, size) if fid else None
