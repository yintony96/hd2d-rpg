using UnityEngine;
using System.Collections.Generic;

namespace HD2DRPG
{
    /// <summary>
    /// Tracks shield points, break state, and weakness revelation for a single enemy.
    /// </summary>
    public class EnemyCombatState
    {
        public EnemyData data;
        public int currentHP;
        public int shieldPoints;
        public bool isBreaking;
        public int breakTurnsRemaining;
        public bool isPhase2;

        // Which weaknesses have been revealed to the player
        public HashSet<int> revealedWeaknessIndices = new();

        public List<ActiveStatusEffect> statusEffects = new();

        [System.NonSerialized] public int turnOrderValue;
        [System.NonSerialized] public bool hasTakenTurn;

        public bool IsAlive => currentHP > 0;

        public void Initialize(EnemyData enemyData)
        {
            data = enemyData;
            currentHP = enemyData.hp;
            shieldPoints = enemyData.maxShieldPoints;
            isBreaking = false;
            breakTurnsRemaining = 0;
            isPhase2 = false;
        }

        public void StartTurn()
        {
            hasTakenTurn = false;
            if (isBreaking)
            {
                breakTurnsRemaining--;
                if (breakTurnsRemaining <= 0)
                    RecoverFromBreak();
            }

            // Tick status effects
            for (int i = statusEffects.Count - 1; i >= 0; i--)
            {
                statusEffects[i].turnsRemaining--;
                if (statusEffects[i].turnsRemaining <= 0)
                    statusEffects.RemoveAt(i);
            }
        }

        void RecoverFromBreak()
        {
            isBreaking = false;
            shieldPoints = data.maxShieldPoints;
        }
    }

    public static class WeaknessSystem
    {
        /// <summary>
        /// Returns true if the element hits a weakness.
        /// Side-effects: removes 1 shield point, reveals the weakness.
        /// </summary>
        public static bool ProcessHit(EnemyCombatState enemy, ElementType element, int shieldDamage, out bool justBroke)
        {
            justBroke = false;
            bool isWeakness = false;

            for (int i = 0; i < enemy.data.weaknesses.Length; i++)
            {
                if (enemy.data.weaknesses[i] == element)
                {
                    isWeakness = true;
                    enemy.revealedWeaknessIndices.Add(i);
                    break;
                }
            }

            if (isWeakness && !enemy.isBreaking)
            {
                enemy.shieldPoints = Mathf.Max(0, enemy.shieldPoints - shieldDamage);
                if (enemy.shieldPoints == 0)
                {
                    BreakEnemy(enemy);
                    justBroke = true;
                }
            }

            return isWeakness;
        }

        static void BreakEnemy(EnemyCombatState enemy)
        {
            enemy.isBreaking = true;
            enemy.breakTurnsRemaining = enemy.data.breakTurns;
            // Enemy skips its next turn — handled in TurnQueue
        }

        /// <summary>
        /// Returns damage multiplier for this hit (accounts for break bonus).
        /// </summary>
        public static float GetDamageMultiplier(EnemyCombatState enemy, ElementType element)
        {
            float mult = 1f;

            // Break bonus
            if (enemy.isBreaking)
                mult += enemy.data.breakDamageBonus;

            // Check resistances
            foreach (var res in enemy.data.resistances)
                if (res == element) { mult *= 0.5f; break; }

            // Check immunities
            foreach (var imm in enemy.data.immunities)
                if (imm == element) return 0f;

            return mult;
        }

        /// <summary>
        /// Calculate final damage dealt to enemy.
        /// </summary>
        public static int CalculateDamage(PartyMember attacker, EnemyCombatState enemy,
            SkillData skill, int boostLevel)
        {
            float baseDmg = attacker.str * skill.powerMultiplier;
            int hitCount = boostLevel > 0 ? skill.boostedHitCount : skill.hitCount;
            float perHit = baseDmg / hitCount;

            float mult = GetDamageMultiplier(enemy, skill.element);
            float total = perHit * hitCount * mult;

            // Boost power multiplier
            if (boostLevel > 0)
                total *= skill.boostedPowerMultiplier;

            // Defense mitigation
            total = Mathf.Max(1f, total - enemy.data.hp * 0.01f * (1f - mult)); // simplified

            return Mathf.Max(1, Mathf.RoundToInt(total));
        }
    }
}
