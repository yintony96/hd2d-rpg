using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections.Generic;

namespace HD2DRPG
{
    /// <summary>
    /// Horizontal strip of portrait icons showing upcoming turn order.
    /// Updates in real time as boosts are applied.
    /// </summary>
    public class TurnOrderUI : MonoBehaviour
    {
        [Header("References")]
        public Transform iconStrip;
        public GameObject turnIconPrefab; // Image + optional label

        public void Refresh(IReadOnlyList<CombatTurn> queue)
        {
            foreach (Transform child in iconStrip) Destroy(child.gameObject);

            foreach (var turn in queue)
            {
                var icon = Instantiate(turnIconPrefab, iconStrip);
                var img = icon.GetComponentInChildren<Image>();
                if (img && turn.Portrait != null) img.sprite = turn.Portrait;

                var lbl = icon.GetComponentInChildren<TextMeshProUGUI>();
                if (lbl) lbl.text = turn.DisplayName;

                // Tint enemies differently
                if (turn.type == CombatantType.Enemy && img)
                    img.color = new Color(1f, 0.6f, 0.6f);
            }
        }
    }
}
