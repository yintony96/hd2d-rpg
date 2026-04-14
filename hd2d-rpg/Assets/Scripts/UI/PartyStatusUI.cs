using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections.Generic;

namespace HD2DRPG
{
    /// <summary>
    /// Bottom-of-screen party status bars shown during combat.
    /// Shows HP, MP, and BP pips for each active party member.
    /// </summary>
    public class PartyStatusUI : MonoBehaviour
    {
        [Header("References")]
        public Transform memberContainer;
        public GameObject memberStatusPrefab;

        public void Refresh(List<PartyMember> party)
        {
            foreach (Transform child in memberContainer) Destroy(child.gameObject);

            foreach (var member in party)
            {
                var slot = Instantiate(memberStatusPrefab, memberContainer);
                var texts = slot.GetComponentsInChildren<TextMeshProUGUI>();

                if (texts.Length >= 4)
                {
                    texts[0].text = member.data.characterName;
                    texts[1].text = $"HP {member.currentHP}/{member.maxHP}";
                    texts[2].text = $"MP {member.currentMP}/{member.maxMP}";
                    texts[3].text = $"BP {new string('◆', member.boostPoints)}";
                }

                // HP bar fill
                var fills = slot.GetComponentsInChildren<Image>();
                if (fills.Length >= 2)
                {
                    float hpRatio = (float)member.currentHP / member.maxHP;
                    fills[1].fillAmount = hpRatio;
                    fills[1].color = hpRatio > 0.5f ? Color.green
                        : hpRatio > 0.25f ? Color.yellow
                        : Color.red;
                }

                // Grey out if dead
                if (!member.IsAlive)
                    slot.GetComponent<CanvasGroup>().alpha = 0.4f;
            }
        }
    }
}
