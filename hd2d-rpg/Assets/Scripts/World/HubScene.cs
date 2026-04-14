using UnityEngine;
using System.Collections;
using System.Collections.Generic;

namespace HD2DRPG
{
    /// <summary>
    /// Manages the continent hub: NPC spawning, party management screen,
    /// tower entrance trigger, and shop/facility access.
    /// </summary>
    public class HubScene : MonoBehaviour
    {
        [Header("References")]
        public Transform playerTransform;
        public DialogueUI dialogueUI;
        public GameObject partyManagementPanel;
        public Transform npcContainer;

        [Header("NPCs")]
        public HubNPC[] npcs;

        [Header("Tower Entrance")]
        public Transform towerEntranceTrigger;
        public float triggerRadius = 1.5f;
        public int continentIndex = 0;

        bool _inDialogue;
        bool _partyOpen;

        void Update()
        {
            if (_inDialogue || _partyOpen) return;

            CheckNPCInteraction();
            CheckTowerEntrance();
            HandlePartyMenuInput();
        }

        void CheckNPCInteraction()
        {
            if (!Input.GetKeyDown(KeyCode.E)) return;

            foreach (var npc in npcs)
            {
                float dist = Vector2.Distance(playerTransform.position, npc.transform.position);
                if (dist < 1.8f)
                {
                    StartCoroutine(StartDialogue(npc));
                    return;
                }
            }
        }

        IEnumerator StartDialogue(HubNPC npc)
        {
            _inDialogue = true;
            dialogueUI.Show(npc.npcName, npc.portrait, npc.GetNextLine());
            while (dialogueUI.IsActive)
                yield return null;
            _inDialogue = false;
        }

        void CheckTowerEntrance()
        {
            if (towerEntranceTrigger == null) return;
            float dist = Vector2.Distance(playerTransform.position, towerEntranceTrigger.position);
            if (dist < triggerRadius && Input.GetKeyDown(KeyCode.E))
            {
                if (GameManager.Instance != null)
                    GameManager.Instance.EnterTower(continentIndex);
            }
        }

        void HandlePartyMenuInput()
        {
            if (Input.GetKeyDown(KeyCode.M) || Input.GetKeyDown(KeyCode.Tab))
            {
                _partyOpen = !_partyOpen;
                partyManagementPanel.SetActive(_partyOpen);
            }
        }
    }

    [System.Serializable]
    public class HubNPC : MonoBehaviour
    {
        public string npcName;
        public Sprite portrait;
        [TextArea] public string[] dialogueLines;
        int _lineIndex;

        public string GetNextLine()
        {
            if (dialogueLines == null || dialogueLines.Length == 0) return "...";
            string line = dialogueLines[_lineIndex % dialogueLines.Length];
            _lineIndex++;
            return line;
        }
    }
}
