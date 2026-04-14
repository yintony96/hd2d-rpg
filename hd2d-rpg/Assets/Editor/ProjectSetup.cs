using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using System.IO;

namespace HD2DRPG.Editor
{
    /// <summary>
    /// Runs once when the project is first opened in Unity.
    /// Creates scenes, folders, and default assets automatically.
    /// </summary>
    [InitializeOnLoad]
    public static class ProjectSetup
    {
        const string SetupDoneKey = "HD2DRPG_SetupDone";

        static ProjectSetup()
        {
            if (SessionState.GetBool(SetupDoneKey, false)) return;
            SessionState.SetBool(SetupDoneKey, true);

            EditorApplication.delayCall += RunSetup;
        }

        static void RunSetup()
        {
            Debug.Log("[HD2DRPG] Running first-time project setup...");

            CreateFolders();
            CreateScenes();
            CreateURPAssets();
            CreateDefaultData();

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            Debug.Log("[HD2DRPG] Project setup complete! Open Assets/Scenes/World/Hub.unity to start.");
        }

        // ── Folder structure ────────────────────────────────────────────────

        static void CreateFolders()
        {
            string[] folders =
            {
                "Assets/Scenes",
                "Assets/Scenes/World",
                "Assets/Scenes/Combat",
                "Assets/Data",
                "Assets/Data/Characters",
                "Assets/Data/Jobs",
                "Assets/Data/Skills",
                "Assets/Data/Enemies",
                "Assets/Data/StatusEffects",
                "Assets/Art/Portraits",
                "Assets/Art/Sprites/Characters",
                "Assets/Art/Sprites/Enemies",
                "Assets/Art/Backgrounds",
                "Assets/Art/UI",
                "Assets/Audio/BGM",
                "Assets/Audio/SFX",
                "Assets/Prefabs/UI",
                "Assets/Prefabs/Characters",
                "Assets/Prefabs/Enemies",
                "Assets/Prefabs/Effects",
                "Assets/Settings",
            };

            foreach (var path in folders)
            {
                var parts = path.Split('/');
                var current = parts[0];
                for (int i = 1; i < parts.Length; i++)
                {
                    var next = current + "/" + parts[i];
                    if (!AssetDatabase.IsValidFolder(next))
                        AssetDatabase.CreateFolder(current, parts[i]);
                    current = next;
                }
            }
        }

        // ── Scenes ──────────────────────────────────────────────────────────

        static void CreateScenes()
        {
            CreateSceneIfMissing("Assets/Scenes/Main.unity");
            CreateSceneIfMissing("Assets/Scenes/World/Hub.unity");
            CreateSceneIfMissing("Assets/Scenes/Combat/Battle.unity");
        }

        static void CreateSceneIfMissing(string path)
        {
            if (File.Exists(Path.GetFullPath(path))) return;

            var scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
            EditorSceneManager.SaveScene(scene, path);
            Debug.Log($"[HD2DRPG] Created scene: {path}");
        }

        // ── URP Pipeline Asset ───────────────────────────────────────────────

        static void CreateURPAssets()
        {
            // URP Renderer Data
            if (!File.Exists("Assets/Settings/HD2D_UniversalRenderPipelineAsset.asset"))
            {
                Debug.Log("[HD2DRPG] URP asset creation requires manual setup via Edit > Project Settings > Graphics. " +
                          "Set Scriptable Render Pipeline Settings to a URP Asset.");
            }
        }

        // ── Default ScriptableObject Data ───────────────────────────────────

        static void CreateDefaultData()
        {
            // Status effects
            CreateStatusEffect("Poison",   StatusEffectType.Poison,   3, 0.10f);
            CreateStatusEffect("Burn",     StatusEffectType.Burn,     3, 0.08f);
            CreateStatusEffect("Blind",    StatusEffectType.Blind,    2, 0.50f);
            CreateStatusEffect("Sleep",    StatusEffectType.Sleep,    2, 0f);
            CreateStatusEffect("Stun",     StatusEffectType.Stun,     1, 0f);
            CreateStatusEffect("Regen",    StatusEffectType.Regen,    3, 0.08f);
            CreateStatusEffect("Shield",   StatusEffectType.Shield,   2, 0f);
            CreateStatusEffect("ATK Up",   StatusEffectType.AttackUp, 3, 0.30f);
            CreateStatusEffect("ATK Down", StatusEffectType.AttackDown,3,0.30f);
            CreateStatusEffect("DEF Up",   StatusEffectType.DefenseUp,3, 0.30f);
            CreateStatusEffect("DEF Down", StatusEffectType.DefenseDown,3,0.30f);

            // Characters
            CreateCharacterData("Aurora", "Paladin");
            CreateCharacterData("Kael",   "Hero");
        }

        static void CreateStatusEffect(string name, StatusEffectType type, int duration, float magnitude)
        {
            string path = $"Assets/Data/StatusEffects/{name}.asset";
            if (File.Exists(Path.GetFullPath(path))) return;

            var so = ScriptableObject.CreateInstance<StatusEffectData>();
            so.effectType   = type;
            so.displayName  = name;
            so.duration     = duration;
            so.magnitude    = magnitude;
            so.stackable    = false;
            AssetDatabase.CreateAsset(so, path);
        }

        static void CreateCharacterData(string charName, string jobName)
        {
            string path = $"Assets/Data/Characters/{charName}.asset";
            if (File.Exists(Path.GetFullPath(path))) return;

            var so = ScriptableObject.CreateInstance<CharacterData>();
            so.characterName = charName;

            if (charName == "Aurora")
            {
                so.baseHP  = 450; so.baseMP  = 120;
                so.baseSTR = 28;  so.baseDEF = 32;
                so.baseSPD = 24;  so.baseMND = 22;
                so.innateWeaknesses   = new[] { ElementType.Dark };
                so.innateResistances  = new[] { ElementType.Light };
            }
            else // Kael
            {
                so.baseHP  = 380; so.baseMP  = 100;
                so.baseSTR = 35;  so.baseDEF = 26;
                so.baseSPD = 30;  so.baseMND = 28;
                so.innateWeaknesses   = new[] { ElementType.Dark };
                so.innateResistances  = new[] { ElementType.Light };
            }

            AssetDatabase.CreateAsset(so, path);
            Debug.Log($"[HD2DRPG] Created character asset: {path}");
        }
    }
}
