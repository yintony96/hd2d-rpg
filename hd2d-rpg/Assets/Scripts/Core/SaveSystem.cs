using UnityEngine;
using System.IO;
using System.Runtime.Serialization.Formatters.Binary;

namespace HD2DRPG
{
    /// <summary>
    /// JSON-based save system.
    /// Meta save: roster, job progression, continents unlocked.
    /// Run save:  current tower state, HP/MP, floor index.
    /// </summary>
    public static class SaveSystem
    {
        static string MetaSavePath => Path.Combine(Application.persistentDataPath, "meta.json");
        static string RunSavePath  => Path.Combine(Application.persistentDataPath, "run.json");

        // ── Meta Save ──────────────────────────────────────────────────

        [System.Serializable]
        public class MetaSaveData
        {
            public bool[] continentUnlocked = new bool[5];
            public int gold;
            // Party member snapshots would go here (simplified)
        }

        public static void SaveMeta()
        {
            var gm = GameManager.Instance;
            if (gm == null) return;

            var data = new MetaSaveData
            {
                continentUnlocked = gm.continentUnlocked,
                gold = gm.gold
            };
            File.WriteAllText(MetaSavePath, JsonUtility.ToJson(data, prettyPrint: true));
            Debug.Log($"[Save] Meta saved to {MetaSavePath}");
        }

        public static bool LoadMeta()
        {
            if (!File.Exists(MetaSavePath)) return false;
            var gm = GameManager.Instance;
            if (gm == null) return false;

            var data = JsonUtility.FromJson<MetaSaveData>(File.ReadAllText(MetaSavePath));
            gm.continentUnlocked = data.continentUnlocked;
            gm.gold = data.gold;
            Debug.Log("[Save] Meta loaded.");
            return true;
        }

        // ── Run Save ───────────────────────────────────────────────────

        [System.Serializable]
        public class RunSaveData
        {
            public int towerSeed;
            public int floorIndex;
            public int[] partyCurrentHP;
            public int[] partyCurrentMP;
        }

        public static void SaveRun()
        {
            var gm = GameManager.Instance;
            if (gm == null) return;

            var data = new RunSaveData
            {
                towerSeed = gm.currentTowerSeed,
                floorIndex = gm.currentFloorIndex
            };

            int n = gm.activeParty.Count;
            data.partyCurrentHP = new int[n];
            data.partyCurrentMP = new int[n];
            for (int i = 0; i < n; i++)
            {
                data.partyCurrentHP[i] = gm.activeParty[i].currentHP;
                data.partyCurrentMP[i] = gm.activeParty[i].currentMP;
            }

            File.WriteAllText(RunSavePath, JsonUtility.ToJson(data, prettyPrint: true));
            Debug.Log($"[Save] Run saved to {RunSavePath}");
        }

        public static bool LoadRun()
        {
            if (!File.Exists(RunSavePath)) return false;
            var gm = GameManager.Instance;
            if (gm == null) return false;

            var data = JsonUtility.FromJson<RunSaveData>(File.ReadAllText(RunSavePath));
            gm.currentTowerSeed = data.towerSeed;
            gm.currentFloorIndex = data.floorIndex;

            for (int i = 0; i < Mathf.Min(data.partyCurrentHP.Length, gm.activeParty.Count); i++)
            {
                gm.activeParty[i].currentHP = data.partyCurrentHP[i];
                gm.activeParty[i].currentMP = data.partyCurrentMP[i];
            }

            Debug.Log("[Save] Run loaded.");
            return true;
        }

        public static void DeleteRunSave()
        {
            if (File.Exists(RunSavePath)) File.Delete(RunSavePath);
        }
    }
}
