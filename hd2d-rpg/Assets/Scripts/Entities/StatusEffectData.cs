using UnityEngine;

namespace HD2DRPG
{
    [CreateAssetMenu(fileName = "NewStatusEffect", menuName = "HD2DRPG/StatusEffect")]
    public class StatusEffectData : ScriptableObject
    {
        public StatusEffectType effectType;
        public string displayName;
        public Sprite icon;
        public int duration;        // Turns
        public float magnitude;     // Damage per turn (poison/burn) or stat % change
        public bool stackable;
    }
}
