using UnityEngine;
using System.Collections.Generic;
using System.Linq;

namespace HD2DRPG
{
    /// <summary>
    /// Simple pattern-based enemy AI.
    /// Priorities: exploit weaknesses > attack low-HP targets > random action.
    /// </summary>
    public static class EnemyAI
    {
        public static EnemyAction SelectAction(EnemyCombatState enemy, List<PartyMember> party)
        {
            if (enemy.data.actionPool == null || enemy.data.actionPool.Length == 0) return null;

            float hpPercent = (float)enemy.currentHP / enemy.data.hp;
            bool isPhase2 = hpPercent <= 0.5f;

            var pool = (isPhase2 && enemy.data.phase2Actions?.Length > 0)
                ? enemy.data.phase2Actions
                : enemy.data.actionPool;

            // Filter by HP threshold
            var eligible = pool.Where(a => hpPercent <= a.hpThreshold).ToList();
            if (eligible.Count == 0) eligible = new List<EnemyAction>(pool);

            // Weighted random selection
            float totalWeight = eligible.Sum(a => a.weight);
            float roll = Random.value * totalWeight;
            float cumulative = 0f;

            foreach (var action in eligible)
            {
                cumulative += action.weight;
                if (roll <= cumulative) return action;
            }

            return eligible[^1];
        }

        /// <summary>
        /// Pick target: 60% chance to target lowest HP, 40% random.
        /// </summary>
        public static PartyMember SelectTarget(List<PartyMember> party)
        {
            var alive = party.Where(p => p.IsAlive).ToList();
            if (alive.Count == 0) return null;

            if (Random.value < 0.6f)
                return alive.OrderBy(p => p.currentHP).First();

            return alive[Random.Range(0, alive.Count)];
        }
    }
}
