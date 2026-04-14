using UnityEngine;

namespace HD2DRPG
{
    [CreateAssetMenu(fileName = "NewSkill", menuName = "HD2DRPG/Skill")]
    public class SkillData : ScriptableObject
    {
        [Header("Identity")]
        public string skillName;
        [TextArea] public string description;
        public Sprite icon;

        [Header("Cost")]
        public int mpCost;
        public int bpCost;          // Boost Points required to activate bonus

        [Header("Combat")]
        public ElementType element;
        public TargetType targetType;
        public float powerMultiplier = 1f;
        public int hitCount = 1;    // Number of hits; boosting can increase this
        public int shieldDamage = 1; // Shield points removed on weakness hit

        [Header("Boost Scaling")]
        public int boostedHitCount = 2;
        public float boostedPowerMultiplier = 1.5f;
        public bool guaranteedStatusOnBoost;

        [Header("Status Effects")]
        public StatusEffectData[] appliedEffects;
        public float statusChance = 0.3f; // 0–1

        [Header("Healing")]
        public bool isHealing;
        public float healMultiplier;
    }
}
