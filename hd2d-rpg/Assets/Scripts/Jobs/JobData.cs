using UnityEngine;

namespace HD2DRPG
{
    [CreateAssetMenu(fileName = "NewJob", menuName = "HD2DRPG/Job")]
    public class JobData : ScriptableObject
    {
        [Header("Identity")]
        public string jobName;
        public Sprite jobIcon;
        [TextArea] public string jobDescription;

        [Header("Base Stats (additive modifiers)")]
        public int hpModifier;
        public int mpModifier;
        public int strModifier;
        public int defModifier;
        public int spdModifier;
        public int mndModifier;

        [Header("Skills")]
        public SkillData[] skills;   // 6–8 skills unlocked progressively

        [Header("Passives")]
        public PassiveData[] passives; // 2–3 passives

        [Header("Equipment")]
        public WeaponType[] equippableWeapons;

        [Header("Evolution")]
        public JobData[] evolutionOptions; // Branching paths
        public int evolutionRequiredLevel = 20;
        public string evolutionRequiredItemName;

        [Header("Base Job Reference")]
        public JobData baseJob; // null if this IS a base job
    }
}
