# HD-2D RPG — Project Summary

*Source: Miro board `uXjVGjYtNmY` | Engine: Unity 6 URP*

---

## Concept

An HD-2D exploration RPG inspired by Octopath Traveler. 2D pixel-art sprites inhabit fully-rendered 3D environments with depth-of-field, bloom, and dynamic lighting. The game spans 4–5 continents, each sealed by a demon-infested tower the player must conquer to restore the world.

Estimated playtime: ~45 hours main story + post-game underground towers and superbosses.

---

## Characters

### Aurora — Paladin
- Starting job: **Paladin** (Warrior evolution)
- Role: Front-line tank/healer hybrid
- Innate affinity: Light element
- Evolution path: Paladin → (Paladin stays, or new paths unlocked via items)

### Kael — Divine Warrior
- Starting job: **Hero**, evolves to **Divine Warrior**
- Role: High-damage holy striker
- Innate affinity: Light + Sword
- Evolution path: Hero → Divine Warrior (unique) / Champion

Party is 4 active + bench; characters recruited from NPC hubs.

---

## World Structure

```
World Map
├── Continent 1 — Forest Kingdom      → Tower: Verdant Spire
├── Continent 2 — Desert Ruins        → Tower: Sandstone Labyrinth
├── Continent 3 — Frozen Tundra       → Tower: Glacial Citadel
├── Continent 4 — Volcanic Wasteland  → Tower: Infernal Bastion
└── Continent 5 — Celestial Skylands  → Tower: Heavenfall Sanctum
```

Each continent has a hub town with NPCs, shops, and a tower entrance. Completing a tower's Crystal Guardian boss destroys the seal and unlocks the next continent.

---

## Tower Structure

Each tower: 20–30 floors with branching paths.

| Floor Room | Frequency | Description |
|------------|-----------|-------------|
| Combat     | 40%       | Standard random encounter |
| Elite      | 15%       | 1 powerful enemy, bonus loot |
| Event      | 15%       | Text choice with consequences |
| Shop       | 10%       | Buy items/gear |
| Rest       | 10%       | Restore 30% HP/MP |
| Puzzle     | 5%        | Mini-puzzle for rare reward |
| Secret     | 5%        | Hidden room, rare drop |
| Boss       | 1/tower   | Crystal Guardian (floor 20–30) |

Path branching: 2–3 choices per floor. High-risk paths lead to Elite/Secret rooms.

---

## Combat System

Turn-based, speed-ordered. Party of 4 active characters.

### Core Mechanics
- **Boost Points (BP):** Each character holds up to 3 BP. Gain 1 per turn. Spend 1–3 to amplify a skill (more hits, higher multiplier, guaranteed status)
- **Weakness System:** Every enemy has elemental/weapon weaknesses. First hit of each type reveals it
- **Shield Points (SP):** 2–8 per enemy. Each weakness hit reduces SP by 1
- **BREAK:** SP = 0 → enemy stunned for 1–2 turns, takes +50% damage, stats reduced. SP fully restores after break ends

### Elements
Fire · Ice · Lightning · Wind · Dark · Light · Earth · Sword · Spear · Axe · Bow · Staff

### Status Effects
Poison · Burn · Blind · Sleep · Stun · Regen · Shield · ATK↑↓ · DEF↑↓

---

## Job System

Characters earn **JP (Job Points)** in battle. Skills unlock at JP milestones within a job (every ~2 job levels, up to level 20).

### Evolution
- At job level 20 + specific item → choose 1 of 2–3 advanced jobs
- Advanced jobs have new skill sets and enhanced passives
- Respec available at NPC "The Scribe" in hub (costs gold)

### Starting Job Trees
```
Aurora              Kael
──────              ────
Warrior             Hero
  └─ Paladin ★        ├─ Divine Warrior ★
  └─ Berserker        └─ Champion

Mage
  ├─ Necromancer   (any party member)
  ├─ Shaman
  └─ Elementalist

Ranger
  ├─ Sniper
  └─ Beastmaster
```
★ = default starting job

---

## Art Direction (HD-2D)

| Layer | Technique |
|-------|-----------|
| Characters | 2D pixel-art sprites on billboard quads |
| Environments | 3D low-poly meshes with hand-painted textures |
| Lighting | Directional sun + dynamic point lights (torches, magic) |
| Post-process | Bloom + Depth-of-Field (Bokeh) + Color Grading + Vignette |
| Parallax | Background 3D at ×0.5 scroll speed vs. character layer |
| Characters shader | Rim lighting, outline, depth write (integrates with DOF) |
| Background shader | Ambient + point lights + saturation control + distance fog |

Reference images: `docs/img/`

---

## Audio

- BGM per zone: Hub theme, battle theme, tower theme, boss theme, victory fanfare
- SFX: Hit impact (by element), skill cast, BREAK trigger, UI navigate/confirm, level-up
- Orchestral JRPG style (royalty-free sources: OpenGameArt.org, itch.io audio packs)
- Unity AudioMixer: Master → BGM bus + SFX bus

---

## Save System

| Save Type | Contents | File |
|-----------|----------|------|
| Meta | Unlocked continents, roster, job progression | `meta.json` |
| Run | Current tower floor, party HP/MP, inventory | `run.json` |

Meta persists across runs. Run save deleted on tower completion or game over.
