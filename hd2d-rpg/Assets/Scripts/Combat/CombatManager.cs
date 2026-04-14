using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.Linq;

namespace HD2DRPG
{
    public enum CombatPhase
    {
        Initializing,
        PlayerInput,
        ExecutingAction,
        EnemyTurn,
        CheckResult,
        Victory,
        Defeat
    }

    /// <summary>
    /// Central turn-based combat engine.
    /// Coordinates TurnQueue, WeaknessSystem, UI, and animations.
    /// </summary>
    public class CombatManager : MonoBehaviour
    {
        [Header("References")]
        public BattleMenuUI battleMenuUI;
        public TurnOrderUI turnOrderUI;
        public PartyStatusUI partyStatusUI;
        public CombatAnimator combatAnimator;

        [Header("State")]
        public CombatPhase phase = CombatPhase.Initializing;

        // Runtime data
        public List<PartyMember> party = new();
        public List<EnemyCombatState> enemies = new();
        TurnQueue _queue = new();
        CombatTurn _currentTurn;

        // Events
        public System.Action<CombatPhase> OnPhaseChanged;
        public System.Action<string> OnCombatLog;

        // ──────────────────────────────────────────────────────────────
        // Public entry point
        // ──────────────────────────────────────────────────────────────

        public void StartCombat(List<PartyMember> combatParty, List<EnemyData> enemyDatas)
        {
            party = combatParty;
            enemies = enemyDatas.Select(e =>
            {
                var state = new EnemyCombatState();
                state.Initialize(e);
                return state;
            }).ToList();

            StartCoroutine(CombatLoop());
        }

        // ──────────────────────────────────────────────────────────────
        // Main loop
        // ──────────────────────────────────────────────────────────────

        IEnumerator CombatLoop()
        {
            SetPhase(CombatPhase.Initializing);
            yield return new WaitForSeconds(0.5f);

            while (true)
            {
                // Build turn order for this round
                _queue.Build(party, enemies);
                turnOrderUI?.Refresh(_queue.Queue);

                while (!_queue.IsEmpty)
                {
                    _currentTurn = _queue.Dequeue();

                    // Skip dead combatants
                    if (_currentTurn.type == CombatantType.Player && !_currentTurn.player.IsAlive) continue;
                    if (_currentTurn.type == CombatantType.Enemy  && !_currentTurn.enemy.IsAlive)  continue;

                    // Tick turn start effects
                    if (_currentTurn.type == CombatantType.Player) _currentTurn.player.StartTurn();
                    else _currentTurn.enemy.StartTurn();

                    if (_currentTurn.type == CombatantType.Player)
                    {
                        yield return StartCoroutine(PlayerTurn(_currentTurn.player));
                    }
                    else
                    {
                        yield return StartCoroutine(EnemyTurn(_currentTurn.enemy));
                    }

                    // Check end conditions after each action
                    if (AllEnemiesDead()) { yield return StartCoroutine(HandleVictory()); yield break; }
                    if (AllPlayersDead())  { yield return StartCoroutine(HandleDefeat());  yield break; }
                }
            }
        }

        // ──────────────────────────────────────────────────────────────
        // Player turn
        // ──────────────────────────────────────────────────────────────

        IEnumerator PlayerTurn(PartyMember member)
        {
            SetPhase(CombatPhase.PlayerInput);
            battleMenuUI.ShowFor(member, enemies);

            // Wait for the player to select an action
            PlayerAction action = null;
            battleMenuUI.OnActionConfirmed = (a) => action = a;
            yield return new WaitUntil(() => action != null);

            SetPhase(CombatPhase.ExecutingAction);
            yield return StartCoroutine(ExecutePlayerAction(member, action));
        }

        IEnumerator ExecutePlayerAction(PartyMember member, PlayerAction action)
        {
            switch (action.type)
            {
                case PlayerActionType.Attack:
                    yield return StartCoroutine(PerformAttack(member, action));
                    break;
                case PlayerActionType.Skill:
                    yield return StartCoroutine(PerformSkill(member, action));
                    break;
                case PlayerActionType.Item:
                    yield return StartCoroutine(UseItem(member, action));
                    break;
                case PlayerActionType.Flee:
                    Log("Attempted to flee...");
                    if (Random.value > 0.5f) { yield return StartCoroutine(HandleDefeat()); }
                    else { Log("Couldn't escape!"); }
                    break;
            }
        }

        IEnumerator PerformAttack(PartyMember attacker, PlayerAction action)
        {
            var target = action.enemyTarget;
            int boostLevel = action.boostPoints;

            // Spend boost points
            attacker.boostPoints -= boostLevel;

            int damage = WeaknessSystem.CalculateDamage(attacker, target,
                GetBasicAttackSkill(attacker), boostLevel);

            WeaknessSystem.ProcessHit(target, ElementType.Sword, 1, out bool broke);
            damage = Mathf.RoundToInt(damage * WeaknessSystem.GetDamageMultiplier(target, ElementType.Sword));

            target.currentHP -= damage;
            Log($"{attacker.data.characterName} attacks {target.data.enemyName} for {damage} damage!");
            if (broke) Log($"{target.data.enemyName} is BROKEN!");

            yield return combatAnimator?.PlayAttack(attacker, target);
            partyStatusUI?.Refresh(party);
            battleMenuUI?.RefreshEnemyShields(enemies);
        }

        IEnumerator PerformSkill(PartyMember attacker, PlayerAction action)
        {
            var skill = action.skill;
            var target = action.enemyTarget;
            int boostLevel = action.boostPoints;

            // Check MP and BP cost
            if (attacker.currentMP < skill.mpCost) { Log("Not enough MP!"); yield break; }
            attacker.UseMP(skill.mpCost);
            attacker.boostPoints -= boostLevel;

            int hitCount = boostLevel > 0 ? skill.boostedHitCount : skill.hitCount;
            int totalDamage = 0;

            for (int i = 0; i < hitCount; i++)
            {
                bool isWeak = WeaknessSystem.ProcessHit(target, skill.element, skill.shieldDamage, out bool broke);
                int dmg = WeaknessSystem.CalculateDamage(attacker, target, skill, boostLevel);
                target.currentHP -= dmg;
                totalDamage += dmg;

                if (isWeak) Log($"WEAKNESS! {skill.element} hits {target.data.enemyName}!");
                if (broke)  Log($"{target.data.enemyName} is BROKEN!");
            }

            Log($"{attacker.data.characterName} uses {skill.skillName} for {totalDamage} total damage!");

            yield return combatAnimator?.PlaySkill(attacker, target, skill);
            partyStatusUI?.Refresh(party);
            battleMenuUI?.RefreshEnemyShields(enemies);
        }

        IEnumerator UseItem(PartyMember user, PlayerAction action)
        {
            // Placeholder
            Log($"{user.data.characterName} uses an item.");
            yield return new WaitForSeconds(0.5f);
        }

        // ──────────────────────────────────────────────────────────────
        // Enemy turn
        // ──────────────────────────────────────────────────────────────

        IEnumerator EnemyTurn(EnemyCombatState enemy)
        {
            if (enemy.isBreaking)
            {
                Log($"{enemy.data.enemyName} is broken and cannot act!");
                yield return new WaitForSeconds(0.8f);
                yield break;
            }

            SetPhase(CombatPhase.EnemyTurn);
            var action = EnemyAI.SelectAction(enemy, party);

            if (action == null || action.skill == null)
            {
                // Regular attack
                var target = EnemyAI.SelectTarget(party);
                if (target == null) yield break;

                int dmg = Mathf.Max(1, 15 + Random.Range(-3, 4) - target.def / 2);
                target.TakeDamage(dmg);
                Log($"{enemy.data.enemyName} attacks {target.data.characterName} for {dmg}!");
            }
            else
            {
                var target = EnemyAI.SelectTarget(party);
                if (target == null) yield break;
                int dmg = Mathf.Max(1, 20 + Random.Range(-5, 6) - target.def / 2);
                target.TakeDamage(dmg);
                Log($"{enemy.data.enemyName} uses {action.actionName} on {target.data.characterName} for {dmg}!");
            }

            yield return combatAnimator?.PlayEnemyAttack(enemy);
            partyStatusUI?.Refresh(party);
        }

        // ──────────────────────────────────────────────────────────────
        // End conditions
        // ──────────────────────────────────────────────────────────────

        bool AllEnemiesDead() => enemies.All(e => !e.IsAlive);
        bool AllPlayersDead() => party.All(p => !p.IsAlive);

        IEnumerator HandleVictory()
        {
            SetPhase(CombatPhase.Victory);
            Log("Victory!");
            int totalExp = enemies.Sum(e => e.data.expYield);
            int totalGold = enemies.Sum(e => e.data.goldYield);
            int totalJP  = enemies.Sum(e => e.data.jpYield);

            foreach (var p in party.Where(m => m.IsAlive))
            {
                p.jobPoints += totalJP;
                // XP/levelling omitted for brevity — extend here
            }

            battleMenuUI?.ShowVictory(totalExp, totalGold, totalJP);
            yield return new WaitForSeconds(2f);
        }

        IEnumerator HandleDefeat()
        {
            SetPhase(CombatPhase.Defeat);
            Log("Defeated...");
            battleMenuUI?.ShowDefeat();
            yield return new WaitForSeconds(2f);
        }

        // ──────────────────────────────────────────────────────────────
        // Helpers
        // ──────────────────────────────────────────────────────────────

        void SetPhase(CombatPhase newPhase)
        {
            phase = newPhase;
            OnPhaseChanged?.Invoke(newPhase);
        }

        void Log(string msg)
        {
            Debug.Log($"[Combat] {msg}");
            OnCombatLog?.Invoke(msg);
        }

        SkillData GetBasicAttackSkill(PartyMember member)
        {
            // Returns a default "basic attack" skill
            var skill = ScriptableObject.CreateInstance<SkillData>();
            skill.element = ElementType.Sword;
            skill.powerMultiplier = 1f;
            skill.hitCount = 1;
            skill.shieldDamage = 1;
            return skill;
        }
    }

    // ──────────────────────────────────────────────────────────────────
    // Action data (populated by BattleMenuUI)
    // ──────────────────────────────────────────────────────────────────

    public enum PlayerActionType { Attack, Skill, Item, Flee }

    public class PlayerAction
    {
        public PlayerActionType type;
        public SkillData skill;
        public EnemyCombatState enemyTarget;
        public PartyMember allyTarget;
        public int boostPoints;
    }
}
