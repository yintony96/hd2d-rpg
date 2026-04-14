using UnityEngine;
using UnityEditor;
using System.Linq;

namespace HD2DRPG.Editor
{
    /// <summary>
    /// Slices the composite portrait reference sheets (from Miro board) into
    /// individual named sprites that the rest of the project can reference.
    ///
    /// Each sheet is a 2x2 grid:
    ///   Top-left     → CharName_Portrait   (dialogue panel, large art)
    ///   Top-right    → CharName_Faces      (3 expression thumbnails)
    ///   Bottom-left  → CharName_Overworld  (full-body chibi, pivot = bottom)
    ///   Bottom-right → CharName_Battle     (battle stance, pivot = bottom)
    ///
    /// Run via: Tools > HD2D RPG > Slice Portrait Sheets
    /// Must be run before "Build Hub Scene" or "Build Battle Scene" to get
    /// proper character art instead of placeholder silhouettes.
    /// </summary>
    public static class PortraitImporter
    {
        [MenuItem("Tools/HD2D RPG/Slice Portrait Sheets")]
        public static void SliceAll()
        {
            Slice("Assets/Art/Portraits/aurora_portrait.png", "Aurora");
            Slice("Assets/Art/Portraits/kael_portrait.png",   "Kael");
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("[HD2DRPG] Portrait sheets sliced. " +
                      "Sprites are now available as Aurora_Portrait, Aurora_Overworld, " +
                      "Aurora_Battle, Kael_Portrait, Kael_Overworld, Kael_Battle.");
        }

        static void Slice(string path, string charName)
        {
            var importer = AssetImporter.GetAtPath(path) as TextureImporter;
            if (importer == null)
            {
                Debug.LogError($"[HD2DRPG] Portrait not found at {path}. " +
                               "Make sure the file exists before running this tool.");
                return;
            }

            // First pass: import as default to read actual pixel dimensions
            importer.textureType        = TextureImporterType.Sprite;
            importer.spriteImportMode   = SpriteImportMode.Single; // temp
            importer.isReadable         = true;
            importer.filterMode         = FilterMode.Point;        // crisp pixel art
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.maxTextureSize     = 2048;
            importer.SaveAndReimport();

            var tex = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            if (tex == null)
            {
                Debug.LogError($"[HD2DRPG] Could not load texture at {path} after reimport.");
                return;
            }

            int w = tex.width;
            int h = tex.height;
            int hw = w / 2;
            int hh = h / 2;

            // Second pass: switch to Multiple and define 4 slices
            // Unity Rect origin is BOTTOM-LEFT, so the visual top row has y = hh
            importer.spriteImportMode = SpriteImportMode.Multiple;
            importer.spritesheet = new[]
            {
                // Large portrait art — used in dialogue box
                new SpriteMetaData
                {
                    name   = charName + "_Portrait",
                    rect   = new Rect(0,  hh, hw, hh),
                    pivot  = new Vector2(0.5f, 0.5f),
                    alignment = (int)SpriteAlignment.Center
                },
                // Three face expression thumbnails
                new SpriteMetaData
                {
                    name   = charName + "_Faces",
                    rect   = new Rect(hw, hh, hw, hh),
                    pivot  = new Vector2(0.5f, 0.5f),
                    alignment = (int)SpriteAlignment.Center
                },
                // Full-body overworld chibi sprite — pivot at feet
                new SpriteMetaData
                {
                    name   = charName + "_Overworld",
                    rect   = new Rect(0, 0, hw, hh),
                    pivot  = new Vector2(0.5f, 0f),
                    alignment = (int)SpriteAlignment.BottomCenter
                },
                // Battle stance sprite — pivot at feet
                new SpriteMetaData
                {
                    name   = charName + "_Battle",
                    rect   = new Rect(hw, 0, hw, hh),
                    pivot  = new Vector2(0.5f, 0f),
                    alignment = (int)SpriteAlignment.BottomCenter
                },
            };

            importer.isReadable = false; // no longer need CPU access
            EditorUtility.SetDirty(importer);
            importer.SaveAndReimport();

            Debug.Log($"[HD2DRPG] Sliced {path} into {charName}_Portrait / _Faces / _Overworld / _Battle");
        }

        // ── Public helper — load a named sub-sprite by suffix ──────────────────

        /// <summary>
        /// Load one of the sliced sub-sprites by name suffix (e.g. "_Portrait").
        /// Returns null if the sheet hasn't been sliced yet.
        /// </summary>
        public static Sprite LoadCharacterSprite(string charName, string suffix)
        {
            string path = $"Assets/Art/Portraits/{charName.ToLower()}_portrait.png";
            string spriteName = charName + suffix; // e.g. "Aurora_Portrait"

            var sprites = AssetDatabase.LoadAllAssetsAtPath(path)
                                       .OfType<Sprite>()
                                       .ToArray();
            var found = sprites.FirstOrDefault(s => s.name == spriteName);
            if (found == null)
                Debug.LogWarning($"[HD2DRPG] Sprite '{spriteName}' not found at {path}. " +
                                 "Run Tools > HD2D RPG > Slice Portrait Sheets first.");
            return found;
        }
    }
}
