# CHANGELOG

All notable design decisions, corrections, and version milestones for the HD-2D RPG project.

---

## [Unreleased] — Initial Implementation

### Added
- Full Unity 6 URP project structure under `hd2d-rpg/`
- HD-2D shaders: `HD2D_Character.shader` (outline + rim lighting), `HD2D_Background.shader` (ambient + point lights + fog + saturation)
- Core ScriptableObjects: `CharacterData`, `EnemyData`, `SkillData`, `StatusEffectData`, `JobData`, `PassiveData`
- Runtime entities: `PartyMember` (HP/MP/BP state, status effects, job integration)
- Combat system: `CombatManager`, `TurnQueue`, `WeaknessSystem`, `EnemyAI`, `CombatAnimator`
- UI scripts: `BattleMenuUI` (Octopath-style), `TurnOrderUI`, `PartyStatusUI`, `DialogueUI` (typewriter)
- World scripts: `PlayerController`, `HubScene`, `TowerGenerator`
- Core systems: `GameManager` (singleton state machine), `SaveSystem` (meta + run JSON)
- Reference images downloaded from Miro board to `docs/img/` (20 images: characters, continents, battle screens, animations)

### Design Decisions
- **Engine:** Unity 6 (URP) chosen over Godot 4 — HD-2D shader ecosystem is more mature on Unity; Octopath Traveler itself uses Unity
- **Art direction:** HD-2D (2D sprites on 3D environments, DOF, bloom, dynamic point lights, parallax)

---

## Design Corrections

### v0.1 — Kael Job Tree
- **Correction:** Kael's base class changed to **Hero** (not Warrior/generic class)
- **Advanced class:** Hero → **Divine Warrior** (Kael's unique advanced job)
- **Removed:** `Saint` was removed as an evolution option from Hero

**Final Hero evolution tree:**
```
Hero ──→ Divine Warrior (Kael)
      └→ Champion
```

---

## Reference

- Miro board: `https://miro.com/app/board/uXjVGjYtNmY=/`
- Implementation plan: `C:\Users\User\.claude\plans\transient-soaring-waterfall.md`
