# entities.py — Player, NPC, Enemy data classes and skills

from dataclasses import dataclass, field
from typing import List, Tuple
import random
from constants import (
    COLOR_HERO, COLOR_HERO_DARK, COLOR_ENEMY, COLOR_ENEMY_DARK,
    COLOR_NPC, TILE_SIZE
)


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------

@dataclass
class Skill:
    name: str
    mp_cost: int
    damage_mult: float   # multiplier on atk; 0 = no damage (e.g. heal)
    heal_amount: int     # flat HP heal (0 = none)
    description: str

    def __str__(self):
        return self.name


SKILL_ATTACK      = Skill("Attack",       mp_cost=0,  damage_mult=1.0, heal_amount=0,  description="Basic strike.")
SKILL_POWER_SLASH = Skill("Power Slash",  mp_cost=5,  damage_mult=1.8, heal_amount=0,  description="Heavy blow. 1.8x damage.")
SKILL_HEAL        = Skill("Mend",         mp_cost=8,  damage_mult=0.0, heal_amount=25, description="Restore 25 HP.")
SKILL_FLEE        = Skill("Flee",         mp_cost=0,  damage_mult=0.0, heal_amount=0,  description="Escape from battle.")

PLAYER_SKILLS: List[Skill] = [SKILL_ATTACK, SKILL_POWER_SLASH, SKILL_HEAL, SKILL_FLEE]


# ---------------------------------------------------------------------------
# Base Character
# ---------------------------------------------------------------------------

@dataclass
class Character:
    name: str
    hp: int
    max_hp: int
    mp: int
    max_mp: int
    atk: int
    def_: int
    spd: int
    color: Tuple[int, int, int]
    color_dark: Tuple[int, int, int]

    @property
    def alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> int:
        """Apply damage after defence. Returns actual damage dealt."""
        dmg = max(1, amount - self.def_ + random.randint(-2, 2))
        self.hp = max(0, self.hp - dmg)
        return dmg

    def heal(self, amount: int) -> int:
        """Heal HP. Returns amount actually healed."""
        before = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - before

    def use_mp(self, cost: int) -> bool:
        if self.mp < cost:
            return False
        self.mp -= cost
        return True

    def hp_fraction(self) -> float:
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0

    def mp_fraction(self) -> float:
        return self.mp / self.max_mp if self.max_mp > 0 else 0.0


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------

@dataclass
class Player(Character):
    # Map position (tile coords)
    tile_x: int = 5
    tile_y: int = 5
    # Facing direction: 0=down 1=up 2=left 3=right
    facing: int = 0
    skills: List[Skill] = field(default_factory=lambda: list(PLAYER_SKILLS))

    @property
    def px(self) -> int:
        return self.tile_x * TILE_SIZE

    @property
    def py(self) -> int:
        return self.tile_y * TILE_SIZE

    def move(self, dx: int, dy: int, tilemap) -> bool:
        """Attempt to move by (dx, dy) tiles. Returns True if moved."""
        nx, ny = self.tile_x + dx, self.tile_y + dy
        if tilemap.walkable(nx, ny):
            self.tile_x = nx
            self.tile_y = ny
            # Update facing
            if dx == 1:  self.facing = 3
            elif dx == -1: self.facing = 2
            elif dy == 1:  self.facing = 0
            elif dy == -1: self.facing = 1
            return True
        return False


def make_player() -> Player:
    return Player(
        name="Kairu",
        hp=80, max_hp=80,
        mp=30, max_mp=30,
        atk=18, def_=8, spd=12,
        color=COLOR_HERO,
        color_dark=COLOR_HERO_DARK,
        tile_x=5, tile_y=5,
    )


# ---------------------------------------------------------------------------
# NPC
# ---------------------------------------------------------------------------

@dataclass
class NPC:
    name: str
    tile_x: int
    tile_y: int
    color: Tuple[int, int, int]
    dialogue: List[str]

    @property
    def px(self) -> int:
        return self.tile_x * TILE_SIZE

    @property
    def py(self) -> int:
        return self.tile_y * TILE_SIZE

    def near(self, player: Player, radius: int = 1) -> bool:
        return abs(self.tile_x - player.tile_x) <= radius and \
               abs(self.tile_y - player.tile_y) <= radius


def make_village_npcs() -> List[NPC]:
    return [
        NPC(
            name="Elder Mira",
            tile_x=9, tile_y=4,
            color=COLOR_NPC,
            dialogue=[
                "Elder Mira: Welcome to Ashenveil, traveller.",
                "Elder Mira: Strange shadows have gathered at the forest's edge.",
                "Elder Mira: The red stones glow at night... something stirs beyond.",
                "Elder Mira: Approach the glowing ground to face what lurks there.",
                "Elder Mira: May the stars guide your blade.",
            ]
        ),
        NPC(
            name="Blacksmith",
            tile_x=14, tile_y=7,
            color=(160, 100, 60),
            dialogue=[
                "Blacksmith: Oi, watch yerself out there.",
                "Blacksmith: Those creatures don't go down easy.",
                "Blacksmith: Use your skills wisely — MP is precious.",
            ]
        ),
    ]


# ---------------------------------------------------------------------------
# Enemy
# ---------------------------------------------------------------------------

@dataclass
class Enemy(Character):
    level: int = 1

    def choose_action(self) -> Skill:
        """Simple enemy AI: occasionally power attack, usually basic attack."""
        roll = random.random()
        if roll < 0.25:
            return Skill("Dark Claw", mp_cost=0, damage_mult=1.6,
                         heal_amount=0, description="A vicious swipe.")
        return SKILL_ATTACK


def make_enemy() -> Enemy:
    return Enemy(
        name="Shadow Lurker",
        hp=60, max_hp=60,
        mp=0, max_mp=0,
        atk=14, def_=5, spd=8,
        color=COLOR_ENEMY,
        color_dark=COLOR_ENEMY_DARK,
        level=1,
    )
