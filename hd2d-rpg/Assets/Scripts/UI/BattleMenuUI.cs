using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections.Generic;

namespace HD2DRPG
{
    /// <summary>
    /// Octopath Traveler-style battle command menu.
    /// Layout:
    ///   Left panel:  character name + HP/MP + action list
    ///   Right panel: enemy list with shield gauge + weakness slots
    ///   Bottom strip: turn order icons
    /// </summary>
    public class BattleMenuUI : MonoBehaviour
    {
        [Header("Left Panel")]
        public GameObject menuPanel;
        public TextMeshProUGUI characterNameText;
        public TextMeshProUGUI hpText;
        public TextMeshProUGUI mpText;
        public TextMeshProUGUI bpText;
        public Transform actionList;
        public GameObject actionButtonPrefab;

        [Header("Right Panel — Enemies")]
        public Transform enemyListContainer;
        public GameObject enemyStatusPrefab;

        [Header("Skill Sub-menu")]
        public GameObject skillSubMenu;
        public Transform skillList;
        public GameObject skillButtonPrefab;

        [Header("Boost selector")]
        public GameObject boostPanel;
        public TextMeshProUGUI boostCountText;

        [Header("Log")]
        public TextMeshProUGUI combatLogText;

        [Header("Result Panels")]
        public GameObject victoryPanel;
        public GameObject defeatPanel;
        public TextMeshProUGUI victoryExpText;
        public TextMeshProUGUI victoryGoldText;
        public TextMeshProUGUI victoryJPText;

        // ── State ──
        PartyMember _activeMember;
        List<EnemyCombatState> _enemies;
        int _selectedSkill;
        int _selectedEnemy;
        int _boostLevel;

        public System.Action<PlayerAction> OnActionConfirmed;

        // ──────────────────────────────────────────────────────────────

        public void ShowFor(PartyMember member, List<EnemyCombatState> enemies)
        {
            _activeMember = member;
            _enemies = enemies;
            _selectedAction = 0;
            _boostLevel = 0;

            menuPanel.SetActive(true);
            skillSubMenu.SetActive(false);
            victoryPanel.SetActive(false);
            defeatPanel.SetActive(false);

            RefreshCharacterInfo();
            BuildActionList();
            RefreshEnemyShields(enemies);
        }

        void RefreshCharacterInfo()
        {
            characterNameText.text = $"{_activeMember.data.characterName}  [{_activeMember.currentJob?.jobName ?? "?"}]";
            hpText.text = $"HP  {_activeMember.currentHP}/{_activeMember.maxHP}";
            mpText.text = $"MP  {_activeMember.currentMP}/{_activeMember.maxMP}";
            bpText.text = $"BP  {new string('◆', _activeMember.boostPoints)}{new string('◇', PartyMember.MaxBoostPoints - _activeMember.boostPoints)}";
        }

        void BuildActionList()
        {
            // Clear old buttons
            foreach (Transform child in actionList) Destroy(child.gameObject);

            string[] actions = { "Attack", "Skills", "Items", $"Boost  (BP:{_boostLevel})", "Flee" };
            for (int i = 0; i < actions.Length; i++)
            {
                int idx = i;
                var btn = Instantiate(actionButtonPrefab, actionList);
                btn.GetComponentInChildren<TextMeshProUGUI>().text = actions[i];
                btn.GetComponent<Button>().onClick.AddListener(() => OnActionSelected(idx));
            }
        }

        void OnActionSelected(int idx)
        {
            switch (idx)
            {
                case 0: // Attack
                    ConfirmAttack();
                    break;
                case 1: // Skills
                    OpenSkillMenu();
                    break;
                case 2: // Items
                    ConfirmItem();
                    break;
                case 3: // Boost
                    CycleBoost();
                    break;
                case 4: // Flee
                    ConfirmFlee();
                    break;
            }
        }

        void ConfirmAttack()
        {
            var target = GetSelectedEnemy();
            if (target == null) return;
            OnActionConfirmed?.Invoke(new PlayerAction
            {
                type = PlayerActionType.Attack,
                enemyTarget = target,
                boostPoints = _boostLevel
            });
            menuPanel.SetActive(false);
        }

        void OpenSkillMenu()
        {
            skillSubMenu.SetActive(true);
            foreach (Transform child in skillList) Destroy(child.gameObject);

            var skills = _activeMember.unlockedSkills;
            foreach (var skill in skills)
            {
                var sk = skill;
                var btn = Instantiate(skillButtonPrefab, skillList);
                var texts = btn.GetComponentsInChildren<TextMeshProUGUI>();
                if (texts.Length >= 2)
                {
                    texts[0].text = sk.skillName;
                    texts[1].text = $"{sk.element}  MP:{sk.mpCost}";
                }
                btn.GetComponent<Button>().onClick.AddListener(() => ConfirmSkill(sk));
            }
        }

        void ConfirmSkill(SkillData skill)
        {
            var target = GetSelectedEnemy();
            if (target == null) return;
            OnActionConfirmed?.Invoke(new PlayerAction
            {
                type = PlayerActionType.Skill,
                skill = skill,
                enemyTarget = target,
                boostPoints = _boostLevel
            });
            skillSubMenu.SetActive(false);
            menuPanel.SetActive(false);
        }

        void ConfirmItem()
        {
            OnActionConfirmed?.Invoke(new PlayerAction { type = PlayerActionType.Item });
            menuPanel.SetActive(false);
        }

        void CycleBoost()
        {
            if (_activeMember.boostPoints == 0) return;
            _boostLevel = (_boostLevel % _activeMember.boostPoints) + 1;
            BuildActionList(); // refresh with new BP level
        }

        void ConfirmFlee()
        {
            OnActionConfirmed?.Invoke(new PlayerAction { type = PlayerActionType.Flee });
            menuPanel.SetActive(false);
        }

        EnemyCombatState GetSelectedEnemy()
        {
            var alive = _enemies.FindAll(e => e.IsAlive);
            if (alive.Count == 0) return null;
            _selectedEnemy = Mathf.Clamp(_selectedEnemy, 0, alive.Count - 1);
            return alive[_selectedEnemy];
        }

        // ──────────────────────────────────────────────────────────────
        // Enemy shield display
        // ──────────────────────────────────────────────────────────────

        public void RefreshEnemyShields(List<EnemyCombatState> enemies)
        {
            foreach (Transform child in enemyListContainer) Destroy(child.gameObject);

            foreach (var enemy in enemies)
            {
                if (!enemy.IsAlive) continue;
                var slot = Instantiate(enemyStatusPrefab, enemyListContainer);
                var texts = slot.GetComponentsInChildren<TextMeshProUGUI>();
                if (texts.Length >= 3)
                {
                    texts[0].text = enemy.data.enemyName;
                    texts[1].text = enemy.isBreaking
                        ? "BROKEN"
                        : $"Shield: {new string('◆', enemy.shieldPoints)}{new string('◇', enemy.data.maxShieldPoints - enemy.shieldPoints)}";
                    // Weakness slots (revealed / hidden)
                    string weakSlots = "";
                    for (int i = 0; i < enemy.data.weaknesses.Length; i++)
                        weakSlots += enemy.revealedWeaknessIndices.Contains(i)
                            ? $"[{enemy.data.weaknesses[i]}] "
                            : "[?] ";
                    texts[2].text = weakSlots;
                }
            }
        }

        // ──────────────────────────────────────────────────────────────
        // Log & result screens
        // ──────────────────────────────────────────────────────────────

        public void AppendLog(string line)
        {
            if (combatLogText == null) return;
            combatLogText.text += "\n" + line;
        }

        public void ShowVictory(int exp, int gold, int jp)
        {
            menuPanel.SetActive(false);
            victoryPanel.SetActive(true);
            if (victoryExpText)  victoryExpText.text  = $"EXP  +{exp}";
            if (victoryGoldText) victoryGoldText.text = $"Gold +{gold}";
            if (victoryJPText)   victoryJPText.text   = $"JP   +{jp}";
        }

        public void ShowDefeat()
        {
            menuPanel.SetActive(false);
            defeatPanel.SetActive(true);
        }
    }
}
