using UnityEngine;
using UnityEngine.SceneManagement;
using System.Collections.Generic;

namespace HD2DRPG
{
    public enum GameState
    {
        MainMenu,
        Hub,
        Tower,
        Combat,
        Dialogue,
        GameOver
    }

    /// <summary>
    /// Singleton state machine. Persists across scenes.
    /// Holds party data and transitions between game states.
    /// </summary>
    public class GameManager : MonoBehaviour
    {
        public static GameManager Instance { get; private set; }

        [Header("State")]
        public GameState currentState = GameState.MainMenu;

        [Header("Party")]
        public List<PartyMember> activeParty = new();   // Max 4
        public List<PartyMember> reserveBench = new();  // Max ~12

        [Header("Resources")]
        public int gold;
        public int currentTowerSeed;
        public int currentFloorIndex;

        [Header("Continent Progress")]
        public bool[] continentUnlocked = new bool[5];

        // ──────────────────────────────────────────────────────────────

        void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }

        // ──────────────────────────────────────────────────────────────

        public void StartNewGame(List<CharacterData> startingCharacters)
        {
            activeParty.Clear();
            foreach (var cd in startingCharacters)
            {
                var member = new PartyMember { data = cd };
                member.Initialize();
                activeParty.Add(member);
            }
            continentUnlocked[0] = true;
            gold = 500;
            TransitionTo(GameState.Hub, "Scenes/World/Hub");
        }

        public void EnterTower(int continentIndex)
        {
            currentTowerSeed = Random.Range(0, int.MaxValue);
            currentFloorIndex = 0;
            TransitionTo(GameState.Tower, "Scenes/World/Tower");
        }

        public void StartCombat(List<EnemyData> enemies)
        {
            // Store pending enemies for CombatScene to pick up
            PendingEnemies = enemies;
            TransitionTo(GameState.Combat, "Scenes/Combat/Battle");
        }

        public void ReturnToHub()
        {
            TransitionTo(GameState.Hub, "Scenes/World/Hub");
        }

        public void GameOver()
        {
            // Restore party HP/MP fully on game over
            foreach (var m in activeParty)
            {
                m.currentHP = m.maxHP;
                m.currentMP = m.maxMP;
            }
            currentState = GameState.GameOver;
        }

        // ──────────────────────────────────────────────────────────────

        public List<EnemyData> PendingEnemies { get; private set; }

        void TransitionTo(GameState state, string sceneName)
        {
            currentState = state;
            SceneManager.LoadScene(sceneName);
        }
    }
}
