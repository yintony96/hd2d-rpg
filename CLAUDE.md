# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projects

This repo contains two independent mini-projects:

- **`anime-rpg/`** — A pygame-based anime RPG (top-down exploration + turn-based combat)
- **`tictactoe.html`** — A standalone single-file Tic Tac Toe game with minimax AI

---

## anime-rpg

### Running

```bash
pip install pygame
python anime-rpg/main.py
```

No test suite or linter is configured.

---

## Git & Backup Policy

After every meaningful change — completing a feature, fixing a bug, or reaching a stable checkpoint — commit and push immediately so work is always backed up to GitHub.

**Commit message format:**
```
<type>: <short description>

# Types: feat, fix, refactor, style, docs
# Examples:
#   feat: add poison status effect to combat
#   fix: prevent player moving into water tiles
#   refactor: extract tile rendering into its own function
```

**Push after every commit:**
```bash
git add <files>
git commit -m "feat: ..."
git push
```

- Prefer small, focused commits over large batched ones — one logical change per commit.
- Never leave the session without pushing. If a remote isn't set up yet, create one with `gh repo create`.

### Architecture

The game uses a **state machine** driven in `main.py`:

| State | Description |
|---|---|
| `STATE_EXPLORE` | Top-down tile map movement, NPC proximity detection |
| `STATE_DIALOGUE` | Blocking NPC conversation; advances line by line |
| `STATE_COMBAT` | Turn-based battle; spawned fresh each encounter |
| `STATE_VICTORY` / `STATE_GAME_OVER` | Overlay shown over last combat frame; Enter to return |

**Module responsibilities:**

- `constants.py` — All magic numbers (screen size, tile types, colors, font cache via `get_font()`). Import with `from constants import *`.
- `entities.py` — `Character` base dataclass → `Player` and `Enemy` subclasses; `NPC` dataclass; `Skill` dataclass. Factory functions: `make_player()`, `make_enemy()`, `make_village_npcs()`.
- `exploration.py` — `ExploreScene`: tile map, player movement (arrow keys / WASD), NPC talk detection, TILE_TRIGGER → combat transition.
- `combat.py` — `CombatScene`: three internal phases (`PHASE_PLAYER`, `PHASE_ENEMY`, `PHASE_RESULT`); `HitEffect` for shake/flash animation; procedurally drawn sprites.
- `dialogue.py` — `DialogueSystem`: holds a list of lines, advances on Space/Enter/E, auto-returns to explore when exhausted.
- `ui.py` — Stateless draw helpers (`draw_panel`, `draw_text`, `draw_combat_status`, `draw_action_menu`, `draw_combat_log`, `draw_victory`, `draw_game_over`).

**Key data flow:**
1. `ExploreScene.update()` returns `STATE_COMBAT` when the player steps on a `TILE_TRIGGER`.
2. `main.py` creates a fresh `CombatScene(player, enemy)` — player HP/MP persist across encounters.
3. `CombatScene.result_state()` returns the next state once a phase concludes.
4. On `STATE_GAME_OVER`, player is fully restored; on `STATE_VICTORY`, HP/MP are kept as-is.

### Controls (Explore)
- Arrow keys / WASD — move
- E — interact with adjacent NPC
- Escape — quit

### Controls (Combat)
- Up/W, Down/S — navigate skill menu
- Space / Enter / Z — confirm action
