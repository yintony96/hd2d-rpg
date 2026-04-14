# Combat System — HD-2D RPG

## Overview

Turn-based combat with speed-sorted action order. The defining mechanics are the **Weakness/Break system** and **Boost Points (BP)** — both imported from the Octopath Traveler design space.

---

## Turn Order

1. All alive combatants (party + enemies) sorted by **SPD stat** at round start
2. Ties broken by party order (index 0 first)
3. **BREAK** skip: broken enemies are removed from the queue for that round
4. **Boost cost**: spending BP reduces the acting character's SPD this round (slows their subsequent turns in multi-turn rounds)

`TurnQueue.Build()` recomputes at the start of each new round.

---

## Boost Points (BP)

| Rule | Value |
|------|-------|
| Max BP | 3 per character |
| Gain per turn | +1 automatically at turn start |
| Spend range | 0–3 BP per action |
| Effect (1 BP) | ×1.5 power OR +1 extra hit |
| Effect (2 BP) | ×2.0 power OR +2 extra hits |
| Effect (3 BP) | ×3.0 power OR +3 extra hits + guaranteed status |

Boosting costs BP but does **not** skip the turn. The turn order adjusts (boosted character acts slightly slower due to SPD penalty).

---

## Weakness / Break System

### Weakness Hit
- Each enemy has 2–6 elemental/weapon weaknesses
- Weaknesses start **hidden** (`[?]` slot in UI)
- First hit of an element reveals it permanently for the run

### Shield Points (SP)
- Enemies have 2–8 SP (shown as `◆◆◆◆◆` diamonds in UI)
- Each weakness hit: SP − 1
- Normal hits (non-weakness): SP unchanged

### BREAK State
- Triggered when SP reaches 0
- Enemy effects during BREAK:
  - Skips their next turn
  - Takes **+50% damage** from all sources
  - All stats temporarily reduced
  - Duration: 1–2 turns (configurable per enemy)
- After BREAK ends: SP fully restored, enemy resumes normal behavior

---

## Damage Formula

```
damage = attacker.STR × skill.powerMultiplier × hitCount × multiplier

multiplier =
  1.5  if element is weakness (non-break)
  2.0  if element is weakness AND enemy is BREAKING
  0.5  if element is resistance
  0.0  if element is immunity
  1.0  otherwise
```

Multi-hit skills roll each hit independently against the weakness system (each hit can chip SP).

---

## Battle Menu Layout (Octopath-style)

```
┌────────────────────────────────────────────────────────┐
│  [AURORA — PALADIN]        HP ████████  450/450        │
│  MP ████████  120/120      BP ◆◆◇                      │
│  ─────────────────────────────────────────────────     │
│  > Attack                  [ENEMY NAME]                │
│    Skills ▶                ◆◆◆◆  Shield: 4  (BREAK!)   │
│    Items                   [SLIME]                     │
│    Boost (BP: 2) ▸          ◆◆    Shield: 2            │
│    Flee                                                │
└────────────────────────────────────────────────────────┘
  Turn Order: [Aurora] [Slime] [Kael] [Slime2]
```

- **Left panel**: Active character stats + action menu
- **Right panel**: Enemy list with shield pips and weakness slots
- **Bottom strip**: Turn order portraits (party = normal, enemy = red tint)

---

## Status Effects

| Effect | Duration | Behavior |
|--------|----------|---------|
| Poison | 3 turns | Lose 10% max HP per turn |
| Burn | 3 turns | Lose 8% max HP; Fire resistance reduced |
| Blind | 2 turns | 50% chance to miss physical attacks |
| Sleep | 2 turns | Skip turns; broken on damage |
| Stun | 1 turn | Skip turn (no break needed) |
| Regen | 3 turns | Restore 8% max HP per turn |
| Shield | 2 turns | Absorb one hit |
| ATK Up/Down | 3 turns | ×1.3 / ×0.7 STR modifier |
| DEF Up/Down | 3 turns | ×1.3 / ×0.7 DEF modifier |

---

## Enemy AI

**Phase 1 (HP > 50%):**
- Weighted random selection from `actionPool`
- Actions filtered by `hpThreshold` — some actions only available below X% HP
- 60% chance to target the party member with lowest HP
- 40% chance to target a random member

**Phase 2 (HP ≤ 50%):**
- Switches to `phase2Actions` pool
- Bosses gain a phase-change animation + new attack patterns

---

## Victory / Defeat

**Victory:**
- All enemies HP = 0
- Alive party members receive: EXP, Gold, JP
- EXP split equally among alive members
- JP goes to the character's current job

**Defeat:**
- All party members HP = 0
- `GameManager.GameOver()` called
- Return to last hub checkpoint; party fully restored
- Run save is **not** deleted on game over (player can retry)

---

## Combat Flow (Coroutine)

```
CombatManager.StartCombat()
  └─ CombatLoop()
       └─ [Each Round]
            ├─ TurnQueue.Build()
            └─ [Each Turn]
                 ├─ [PartyMember] → PlayerTurn() → wait for BattleMenuUI callback
                 │    └─ ExecutePlayerAction() → PerformSkill() / PerformAttack() / UseItem() / Flee
                 └─ [Enemy] → EnemyTurn() → EnemyAI.SelectAction() + SelectTarget()
                      └─ WeaknessSystem.ProcessHit() per hit
       └─ CheckResult() → Victory / Defeat / continue
```
