using UnityEngine;

namespace HD2DRPG
{
    [CreateAssetMenu(fileName = "NewPassive", menuName = "HD2DRPG/Passive")]
    public class PassiveData : ScriptableObject
    {
        public string passiveName;
        [TextArea] public string description;
        public Sprite icon;

        // Stat bonuses
        public float hpPercentBonus;
        public float mpPercentBonus;
        public float strPercentBonus;
        public float defPercentBonus;
        public float spdPercentBonus;

        // Special flags
        public bool doubleItemEffect;
        public bool reviveOnKO;
        public float reviveHpPercent = 0.25f;
        public ElementType resistedElement;
        public float elementResistance; // 0–1
    }
}
