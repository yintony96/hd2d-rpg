using UnityEngine;
using System.Collections.Generic;

namespace HD2DRPG
{
    [CreateAssetMenu(fileName = "NewCharacter", menuName = "HD2DRPG/Character")]
    public class CharacterData : ScriptableObject
    {
        [Header("Identity")]
        public string characterName;
        public Sprite portrait;
        public Sprite portraitExpressive; // alternate expression
        public Sprite battleSprite;
        public Sprite overworldSprite;
        [TextArea] public string backstory;

        [Header("Base Stats (level 1)")]
        public int baseHP = 300;
        public int baseMP = 80;
        public int baseSTR = 20;
        public int baseDEF = 15;
        public int baseSPD = 12;
        public int baseMND = 10; // Magic/mind stat

        [Header("Growth Rates (per level)")]
        public float hpGrowth = 15f;
        public float mpGrowth = 4f;
        public float strGrowth = 1.5f;
        public float defGrowth = 1.2f;
        public float spdGrowth = 1f;
        public float mndGrowth = 1f;

        [Header("Starting Job")]
        public JobData startingJob;

        [Header("Weaknesses (innate)")]
        public ElementType[] innateWeaknesses;
        public ElementType[] innateResistances;

        [Header("Unique Traits")]
        [TextArea] public string uniquePassiveDescription;
        public PassiveData[] uniquePassives;

        [Header("Recruit Info")]
        public string recruitLocation;
        public int recruitCost;
    }
}
