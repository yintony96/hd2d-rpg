using UnityEngine;
using System.Collections.Generic;

namespace HD2DRPG
{
    [System.Serializable]
    public class EnemyAction
    {
        public string actionName;
        public SkillData skill;         // null = regular attack
        public float weight = 1f;       // Relative probability
        public float hpThreshold = 1f;  // Only used below this HP % (1 = always)
    }

    [System.Serializable]
    public class LootEntry
    {
        public string itemName;
        public int dropChancePercent; // 0–100
        public int minQuantity = 1;
        public int maxQuantity = 1;
    }

    [CreateAssetMenu(fileName = "NewEnemy", menuName = "HD2DRPG/Enemy")]
    public class EnemyData : ScriptableObject
    {
        [Header("Identity")]
        public string enemyName;
        public Sprite sprite;
        public Sprite shadowSprite;
        public bool isBoss;

        [Header("Stats")]
        public int hp = 200;
        public int maxShieldPoints = 4; // Break shield; 2–8 typical

        [Header("Weaknesses")]
        public ElementType[] weaknesses;
        public ElementType[] resistances;
        public ElementType[] immunities;

        [Header("Actions")]
        public EnemyAction[] actionPool;
        // Boss phase 2 actions (triggered at 50% HP)
        public EnemyAction[] phase2Actions;

        [Header("Rewards")]
        public int expYield = 50;
        public int goldYield = 30;
        public int jpYield = 20;
        public LootEntry[] lootTable;

        [Header("Break Behaviour")]
        public int breakTurns = 2;         // Turns spent in broken state
        public float breakDamageBonus = 0.5f; // +50% damage taken while broken
    }
}
