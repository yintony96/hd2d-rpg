using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using System.IO;

namespace HD2DRPG.Editor
{
    /// <summary>
    /// Menu items to build and configure scenes from scratch.
    /// Tools > HD2D RPG > ...
    /// </summary>
    public static class SceneBuilder
    {
        // ── Hub Scene ────────────────────────────────────────────────────────

        [MenuItem("Tools/HD2D RPG/Build Hub Scene")]
        public static void BuildHubScene()
        {
            var scene = EditorSceneManager.OpenScene("Assets/Scenes/World/Hub.unity", OpenSceneMode.Single);

            // Camera
            var camGO = new GameObject("Main Camera");
            var cam   = camGO.AddComponent<Camera>();
            cam.orthographic     = false;
            cam.fieldOfView      = 40f;
            cam.nearClipPlane    = 0.1f;
            cam.farClipPlane     = 100f;
            cam.transform.position = new Vector3(0, 8, -10);
            cam.transform.eulerAngles = new Vector3(35, 0, 0);
            camGO.tag = "MainCamera";

            // Directional light
            var lightGO = new GameObject("Directional Light");
            var light   = lightGO.AddComponent<Light>();
            light.type      = LightType.Directional;
            light.color     = new Color(1f, 0.95f, 0.84f);
            light.intensity = 1.2f;
            lightGO.transform.eulerAngles = new Vector3(50, -30, 0);

            // Player placeholder
            var playerGO = new GameObject("Player");
            playerGO.AddComponent<Rigidbody2D>();
            playerGO.AddComponent<BoxCollider2D>();
            var pc = playerGO.AddComponent<PlayerController>();
            playerGO.tag = "Player";

            // HubScene manager
            var hubManagerGO = new GameObject("HubScene");
            var hub = hubManagerGO.AddComponent<HubScene>();
            hub.playerTransform = playerGO.transform;

            // NPC container
            var npcContainer = new GameObject("NPCs");
            hub.npcContainer = npcContainer.transform;

            // Tower entrance
            var towerGO = new GameObject("Tower Entrance");
            towerGO.transform.position = new Vector3(10, 0, 0);
            hub.towerEntranceTrigger = towerGO.transform;

            // Post-process volume (add Bloom/DOF/ColorGrading via Inspector after building)
            var volumeGO = new GameObject("Post Processing Volume");
            // Volume component requires URP — add manually via Add Component > Rendering > Volume

            EditorSceneManager.SaveScene(scene);
            Debug.Log("[HD2DRPG] Hub scene built. Add URP Bloom/DOF/ColorGrading to the Volume component.");
        }

        // ── Battle Scene ─────────────────────────────────────────────────────

        [MenuItem("Tools/HD2D RPG/Build Battle Scene")]
        public static void BuildBattleScene()
        {
            var scene = EditorSceneManager.OpenScene("Assets/Scenes/Combat/Battle.unity", OpenSceneMode.Single);

            // Camera
            var camGO = new GameObject("Main Camera");
            var cam   = camGO.AddComponent<Camera>();
            cam.orthographic  = false;
            cam.fieldOfView   = 45f;
            cam.transform.position = new Vector3(0, 3, -12);
            cam.transform.eulerAngles = new Vector3(10, 0, 0);
            camGO.tag = "MainCamera";

            // Directional light
            var lightGO = new GameObject("Directional Light");
            var light   = lightGO.AddComponent<Light>();
            light.type      = LightType.Directional;
            light.color     = new Color(1f, 0.9f, 0.75f);
            light.intensity = 1.0f;
            lightGO.transform.eulerAngles = new Vector3(45, -20, 0);

            // Combat manager
            var combatGO = new GameObject("CombatManager");
            var cm = combatGO.AddComponent<CombatManager>();

            // Battle Menu UI
            var uiRoot = new GameObject("BattleUI");
            uiRoot.AddComponent<Canvas>();
            uiRoot.AddComponent<UnityEngine.UI.CanvasScaler>();
            uiRoot.AddComponent<UnityEngine.UI.GraphicRaycaster>();

            var battleMenuGO = new GameObject("BattleMenu", typeof(BattleMenuUI));
            battleMenuGO.transform.SetParent(uiRoot.transform, false);

            var turnOrderGO = new GameObject("TurnOrderUI", typeof(TurnOrderUI));
            turnOrderGO.transform.SetParent(uiRoot.transform, false);

            var partyStatusGO = new GameObject("PartyStatusUI", typeof(PartyStatusUI));
            partyStatusGO.transform.SetParent(uiRoot.transform, false);

            // Link
            cm.battleMenuUI  = battleMenuGO.GetComponent<BattleMenuUI>();
            cm.turnOrderUI   = turnOrderGO.GetComponent<TurnOrderUI>();
            cm.partyStatusUI = partyStatusGO.GetComponent<PartyStatusUI>();

            EditorSceneManager.SaveScene(scene);
            Debug.Log("[HD2DRPG] Battle scene built.");
        }

        // ── Create sample enemy asset ────────────────────────────────────────

        [MenuItem("Tools/HD2D RPG/Create Sample Enemy (Slime)")]
        public static void CreateSlimeEnemy()
        {
            string path = "Assets/Data/Enemies/Slime.asset";
            if (File.Exists(Path.GetFullPath(path)))
            {
                Debug.Log("[HD2DRPG] Slime.asset already exists.");
                return;
            }

            var enemy = ScriptableObject.CreateInstance<EnemyData>();
            enemy.enemyName     = "Slime";
            enemy.hp            = 120;
            enemy.maxShieldPoints = 3;
            enemy.expYield      = 20;
            enemy.goldYield     = 10;
            enemy.jpYield       = 8;
            enemy.weaknesses    = new[] { ElementType.Fire, ElementType.Axe };
            enemy.resistances   = new[] { ElementType.Ice };
            enemy.breakTurns    = 1;
            enemy.breakDamageBonus = 0.5f;

            AssetDatabase.CreateAsset(enemy, path);
            AssetDatabase.SaveAssets();
            Debug.Log($"[HD2DRPG] Created {path}");
            Selection.activeObject = enemy;
        }

        // ── Create sample skill asset ────────────────────────────────────────

        [MenuItem("Tools/HD2D RPG/Create Sample Skill (Holy Blade)")]
        public static void CreateHolyBladeSkill()
        {
            string path = "Assets/Data/Skills/HolyBlade.asset";
            if (File.Exists(Path.GetFullPath(path)))
            {
                Debug.Log("[HD2DRPG] HolyBlade.asset already exists.");
                return;
            }

            var skill = ScriptableObject.CreateInstance<SkillData>();
            skill.skillName    = "Holy Blade";
            skill.mpCost       = 12;
            skill.bpCost       = 0;
            skill.element      = ElementType.Light;
            skill.targetType   = TargetType.SingleEnemy;
            skill.powerMultiplier = 1.5f;
            skill.hitCount     = 1;
            skill.shieldDamage = 1;
            skill.boostedHitCount = 3;
            skill.boostedPowerMultiplier = 2.0f;

            AssetDatabase.CreateAsset(skill, path);
            AssetDatabase.SaveAssets();
            Debug.Log($"[HD2DRPG] Created {path}");
            Selection.activeObject = skill;
        }
    }
}
