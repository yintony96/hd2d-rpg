# AGENTS.md — HD-2D RPG Development Guidelines

## Project Overview

HD-2D RPG inspired by Octopath Traveler. Unity 6 + URP.  
Characters: Aurora (Paladin), Kael (Hero → Divine Warrior).  
4–5 continents, each with a demon tower (20–30 branching floors), turn-based combat.

---

## Implementation Status

| Step | Description | Status |
|------|-------------|--------|
| 0 | Unity Hub installed | ✅ Done |
| 0 | Unity 6 Editor install | ⏳ Requires user action |
| 1 | Project structure created | ✅ Done |
| 1 | HD-2D shaders | ✅ Done |
| 1 | URP post-processing setup | ⏳ Requires Unity Editor |
| 2 | ScriptableObject data models | ✅ Scripts done / ⏳ .asset files need Editor |
| 3 | Combat system (CombatManager, WeaknessSystem, TurnQueue) | ✅ Scripts done |
| 3 | Battle UI (BattleMenuUI, TurnOrderUI, PartyStatusUI) | ✅ Scripts done |
| 4 | Job system (JobData, JobSystem, PassiveData) | ✅ Scripts done |
| 5 | Tower generator (TowerGenerator) | ✅ Scripts done |
| 6 | Hub scene (HubScene, PlayerController, DialogueUI) | ✅ Scripts done |
| 7 | Audio integration | ⏳ Pending |
| 8 | Save system (SaveSystem) | ✅ Scripts done |

---

## Unity Setup (Manual Steps Required)

### Install Unity Editor
1. Open Unity Hub (installed via `winget install Unity.UnityHub`)
2. Sign in to your Unity account
3. Installs → Install Editor → **Unity 6000.x LTS**
4. Include modules: **Windows Build Support**
5. Open project: `C:\Users\User\Documents\Claude Code Test\hd2d-rpg\`

### URP Post-Processing Volume
Add a global Volume GameObject to each scene with:
- **Bloom**: Intensity 0.8, Threshold 0.9, Scatter 0.7
- **Depth of Field**: Bokeh mode, Aperture 5.6, Focal Length 50, Focus Distance (set via Cinemachine)
- **Color Grading**: Mode = HDR, Lift/Gamma/Gain (warm tones), Post-Exposure +0.3
- **Chromatic Aberration**: Intensity 0.1
- **Vignette**: Intensity 0.2

### Assembly Definition
Place `HD2DRPG.asmdef` at `Assets/Scripts/` for the `HD2DRPG` namespace to compile.

---

## Architecture

```
GameManager (singleton, DontDestroyOnLoad)
├── State: Explore / Combat / Dialogue / Menu
├── activeParty: PartyMember[4]
├── reserveBench: PartyMember[]
└── SceneLoader (additive loading)

Combat Scene
├── CombatManager (coroutine loop)
│   ├── TurnQueue.Build() — speed-sorted, BP-aware
│   ├── WeaknessSystem.ProcessHit() — shield damage, BREAK
│   ├── EnemyAI.SelectAction() — weighted, phase-aware
│   └── CombatAnimator — screen shake, hit flash
└── UI
    ├── BattleMenuUI — Octopath command layout
    ├── TurnOrderUI — portrait strip
    └── PartyStatusUI — HP/MP/BP bars

Hub Scene
├── PlayerController (Rigidbody2D, 8-dir, Lock/Unlock)
├── HubScene — NPC proximity, party menu, tower entry
└── DialogueUI — typewriter, portrait, advance on E/Space

Tower
└── TowerGenerator — seed-based branching FloorNode graph
    Room types: Combat / Elite / Event / Shop / Rest / Puzzle / Secret / Boss
```

---

## Code Conventions

- **Namespace:** All scripts use `namespace HD2DRPG { }`
- **ScriptableObjects:** `[CreateAssetMenu]` on all data classes; stored in `Assets/Data/`
- **Coroutines:** Combat phases driven entirely by coroutines; no Update() polling in combat
- **Events/Callbacks:** Use `System.Action<T>` delegates, not UnityEvents, for combat callbacks
- **No singletons in data:** ScriptableObjects hold only serialized data, never runtime state

---

## Job Trees

**Aurora:**
```
Warrior → Paladin (default)
       └→ Berserker
Mage    → Necromancer
       ├→ Shaman
       └→ Elementalist
Ranger  → Sniper
       └→ Beastmaster
```

**Kael:**
```
Hero → Divine Warrior (default, unique to Kael)
    └→ Champion
```

**Job evolution unlock:** Job level 20 + specific evolution item (held by NPC "The Scribe" in hub)

---

## Combat Rules Summary

| Mechanic | Rule |
|----------|------|
| Turn order | Sorted by SPD stat; ties broken by party order |
| Boost Points | Max 3 per character; gain 1 per turn; spent to amplify skills |
| Shield Points | Enemies have 2–8 SP; reduced by hitting weaknesses |
| BREAK | SP = 0 → enemy loses turn + takes +50% damage for 1–2 turns |
| Weakness reveal | Hidden until hit with correct element — shown as `[?]` before, `[Fire]` after |

---

## File Locations

| Type | Path |
|------|------|
| Scripts | `Assets/Scripts/<Category>/` |
| Data assets | `Assets/Data/<Category>/` |
| Shaders | `Assets/Shaders/` |
| Art (portraits) | `Assets/Art/Portraits/` |
| Art (sprites) | `Assets/Art/Sprites/` |
| UI | `Assets/Art/UI/` |
| Audio | `Assets/Audio/BGM/`, `Assets/Audio/SFX/` |
| Scenes | `Assets/Scenes/` |
| Reference images | `docs/img/` |
| Documentation | `docs/` |
