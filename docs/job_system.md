# Job System — HD-2D RPG

## Overview

Characters advance in **Jobs** — battle archetypes that gate which skills they can use. Defeating enemies earns **JP (Job Points)** that level up the active job, unlocking skills. At job level 20, characters can **evolve** to a more powerful advanced job.

---

## Job Progression

| Job Level | JP Needed (cumulative) | Skills Unlocked |
|-----------|----------------------|-----------------|
| 1 | 0 | Skill 1, Skill 2 |
| 3 | 150 | Skill 3 |
| 5 | 400 | Skill 4 |
| 7 | 750 | Skill 5 |
| 10 | 1500 | Skill 6 |
| 15 | 3000 | Passive 1 |
| 20 | 6000 | Passive 2 + Evolution unlocked |

JP thresholds per level: `[0, 50, 100, 150, 200, 250, 300, 400, 500, 600, 800, 1000, 1200, 1500, 1800, 2200, 2600, 3000, 4000, 6000]`

---

## Job Trees

### Aurora's Jobs

```
Warrior (base)
├── Paladin ★ (Aurora start)
│     Skills: Holy Blade, Shield Bash, Divine Guard, Radiant Smite, Consecrate, Judgment
│     Passives: Iron Will (+15% DEF), Aura of Protection (party DEF +10%)
│     Evolves from: Warrior at lvl 20 + Radiant Crest item
│
└── Berserker
      Skills: Wild Strike (2-3 hits), Fury Slash, Reckless Charge, Battle Cry, Rampage, Last Stand
      Passives: Blood Frenzy (ATK up when HP < 30%), Pain Tolerance (halve first damage each turn)
      Evolves from: Warrior at lvl 20 + Feral Fang item

Mage (base)
├── Necromancer
│     Skills: Shadow Bolt, Soul Drain, Bone Wall, Corpse Explosion, Death Curse, Lich Form
│     Passives: Life Leech (heal 10% of magic damage), Dark Barrier (MND increases DEF)
│     Evolves from: Mage at lvl 20 + Grimoire of Shadows
│
├── Shaman
│     Skills: Spirit Link, Nature's Wrath, Earth Shatter, Totem Stance, Ancestral Fury, Spirit Walk
│     Passives: Earthen Bond (+20% Earth resist), Channel (reduce MP cost by 20%)
│     Evolves from: Mage at lvl 20 + Spirit Stone
│
└── Elementalist
      Skills: Blizzard, Inferno, Thunderbolt, Storm Surge, Prismatic Ray, Elemental Mastery
      Passives: Elemental Attunement (random element bonus each battle), Overflow (excess MP → ATK)
      Evolves from: Mage at lvl 20 + Prism Crystal

Ranger (base)
├── Sniper
│     Skills: Precision Shot, Aimed Arrow, Eagle Eye, Vital Strike, Multi-Shot, Kill Shot
│     Passives: Eagle Eye (+30% SPD when using Bow), Weak Spot (weakness hits do +1 shield damage)
│     Evolves from: Ranger at lvl 20 + Hawk Feather
│
└── Beastmaster
      Skills: Claw Strike, Beast Call, Pack Tactics, Feral Roar, Apex Predator, Primal Bond
      Passives: Feral Bond (beast ally buffs party), Predator Instinct (ATK up vs BROKEN enemies)
      Evolves from: Ranger at lvl 20 + Beast Core
```

### Kael's Jobs

```
Hero (base, Kael exclusive)
├── Divine Warrior ★ (Kael default evolution)
│     Skills: Sacred Slash, Holy Burst, Valor's Edge, Divine Retribution, Heaven's Wrath, Apotheosis
│     Passives: Holy Aura (party resist Dark), Unbreakable (survive 1 KO per battle with 1 HP)
│     Evolves from: Hero at lvl 20 + Divine Sigil item
│
└── Champion
      Skills: War Cry, Iron Shield, Rallying Blow, Commander's Might, Unstoppable, Legendary Strike
      Passives: Inspiring Presence (party ATK +10%), Battle Hardened (DEF scales with turns taken)
      Evolves from: Hero at lvl 20 + Champion's Crest item
```

---

## Respec (The Scribe NPC)

Located in every hub town. Allows resetting a character's job back to its base job (Warrior / Mage / Ranger / Hero).

- **Cost:** 500 gold per respec
- **What is kept:** Passives learned from evolved jobs (remains in the character's passive pool)
- **What is lost:** Current job level progress and unlocked skills (must re-level)
- Use case: Changing evolution path (e.g., already evolved to Paladin but want Berserker)

---

## Equippable Weapons by Job

| Job | Weapons |
|-----|---------|
| Warrior / Paladin / Berserker | Sword, Spear, Axe |
| Mage / Necromancer / Shaman / Elementalist | Staff |
| Ranger / Sniper / Beastmaster | Bow |
| Hero / Divine Warrior / Champion | Sword, Spear, Axe |

---

## Job Stat Modifiers

Each job applies multipliers to the character's base stats:

| Job | HP | MP | STR | DEF | SPD | MND |
|-----|----|----|-----|-----|-----|-----|
| Warrior | 1.2 | 0.8 | 1.2 | 1.1 | 1.0 | 0.8 |
| Paladin | 1.3 | 1.0 | 1.1 | 1.4 | 0.9 | 1.1 |
| Berserker | 1.1 | 0.7 | 1.5 | 0.9 | 1.1 | 0.7 |
| Mage | 0.8 | 1.5 | 0.8 | 0.8 | 1.0 | 1.4 |
| Necromancer | 0.9 | 1.4 | 1.0 | 0.9 | 0.9 | 1.3 |
| Elementalist | 0.8 | 1.6 | 0.8 | 0.7 | 1.1 | 1.5 |
| Ranger | 1.0 | 1.0 | 1.1 | 0.9 | 1.4 | 0.9 |
| Hero | 1.1 | 1.1 | 1.2 | 1.1 | 1.1 | 1.1 |
| Divine Warrior | 1.2 | 1.2 | 1.3 | 1.2 | 1.0 | 1.3 |
| Champion | 1.3 | 0.9 | 1.3 | 1.3 | 1.0 | 1.0 |
