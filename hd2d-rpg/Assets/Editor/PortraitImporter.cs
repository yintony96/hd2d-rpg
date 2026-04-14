using UnityEngine;
using UnityEditor;
using System.IO;

namespace HD2DRPG.Editor
{
    /// <summary>
    /// Cuts the composite Miro portrait sheets into individual PNG files.
    ///
    /// Each sheet is a 2x2 grid — this tool extracts the four quadrants:
    ///   Top-left     → {Char}_Portrait.png   (dialogue panel art)
    ///   Bottom-left  → {Char}_Overworld.png  (hub player sprite)
    ///   Bottom-right → {Char}_Battle.png     (battle scene sprite)
    ///
    /// Output paths:
    ///   Assets/Art/Portraits/{Char}_Portrait.png
    ///   Assets/Art/Sprites/Characters/{Char}_Overworld.png
    ///   Assets/Art/Sprites/Characters/{Char}_Battle.png
    ///
    /// Run via: Tools > HD2D RPG > Slice Portrait Sheets
    /// </summary>
    public static class PortraitImporter
    {
        [MenuItem("Tools/HD2D RPG/Slice Portrait Sheets")]
        public static void SliceAll()
        {
            ExtractQuadrants("Assets/Art/Portraits/aurora_portrait.png", "Aurora");
            ExtractQuadrants("Assets/Art/Portraits/kael_portrait.png",   "Kael");
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("[HD2DRPG] Portrait sheets sliced into individual PNG files.");
        }

        // ─────────────────────────────────────────────────────────────────────

        static void ExtractQuadrants(string sourcePath, string charName)
        {
            // Step 1 — make source texture CPU-readable so GetPixels works
            var srcImporter = AssetImporter.GetAtPath(sourcePath) as TextureImporter;
            if (srcImporter == null)
            {
                Debug.LogError($"[HD2DRPG] Portrait not found: {sourcePath}");
                return;
            }
            srcImporter.isReadable          = true;
            srcImporter.textureCompression  = TextureImporterCompression.Uncompressed;
            srcImporter.maxTextureSize      = 2048;
            srcImporter.SaveAndReimport();

            var src = AssetDatabase.LoadAssetAtPath<Texture2D>(sourcePath);
            if (src == null)
            {
                Debug.LogError($"[HD2DRPG] Could not load {sourcePath}");
                return;
            }

            int hw = src.width  / 2;
            int hh = src.height / 2;

            // Unity GetPixels: x=0,y=0 is BOTTOM-LEFT
            //   Visual top-left  = pixel coords (0,  hh)
            //   Visual top-right = pixel coords (hw, hh)
            //   Visual bot-left  = pixel coords (0,  0 )
            //   Visual bot-right = pixel coords (hw, 0 )

            SaveQuadrant(src, hw, hh,  0,  hh, $"Assets/Art/Portraits/{charName}_Portrait.png",
                         new Vector2(0.5f, 0.5f), 100f);

            SaveQuadrant(src, hw, hh,  0,  0,  $"Assets/Art/Sprites/Characters/{charName}_Overworld.png",
                         new Vector2(0.5f, 0f), 64f);

            SaveQuadrant(src, hw, hh, hw,  0,  $"Assets/Art/Sprites/Characters/{charName}_Battle.png",
                         new Vector2(0.5f, 0f), 64f);

            // Step 4 — restore source as non-readable
            srcImporter.isReadable = false;
            srcImporter.SaveAndReimport();

            Debug.Log($"[HD2DRPG] {charName}: extracted Portrait / Overworld / Battle sprites.");
        }

        static void SaveQuadrant(Texture2D src, int w, int h, int srcX, int srcY,
                                 string destPath, Vector2 pivot, float ppu)
        {
            // Copy pixels from the source quadrant
            var pixels = src.GetPixels(srcX, srcY, w, h);
            var dst = new Texture2D(w, h, TextureFormat.RGBA32, false);
            dst.SetPixels(pixels);
            dst.Apply();

            // Write PNG
            Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(destPath)));
            File.WriteAllBytes(Path.GetFullPath(destPath), dst.EncodeToPNG());
            Object.DestroyImmediate(dst);

            // Import as sprite
            AssetDatabase.ImportAsset(destPath, ImportAssetOptions.ForceSynchronousImport);
            var imp = AssetImporter.GetAtPath(destPath) as TextureImporter;
            if (imp == null) return;

            imp.textureType         = TextureImporterType.Sprite;
            imp.spriteImportMode    = SpriteImportMode.Single;
            imp.spritePivot         = pivot;
            imp.spritePixelsPerUnit = ppu;
            imp.filterMode          = FilterMode.Point;   // crisp pixel art
            imp.textureCompression  = TextureImporterCompression.Uncompressed;
            imp.isReadable          = false;
            imp.SaveAndReimport();
        }

        // ── Public helper called by SceneBuilder ──────────────────────────────

        /// <summary>
        /// Load a previously extracted sprite by character name and suffix.
        /// suffix: "_Portrait" | "_Overworld" | "_Battle"
        /// Returns null (with a warning) if the slice hasn't been run yet.
        /// </summary>
        public static Sprite LoadCharacterSprite(string charName, string suffix)
        {
            string path = suffix == "_Portrait"
                ? $"Assets/Art/Portraits/{charName}_Portrait.png"
                : $"Assets/Art/Sprites/Characters/{charName}{suffix}.png";

            var sprite = AssetDatabase.LoadAssetAtPath<Sprite>(path);
            if (sprite == null)
                Debug.LogWarning($"[HD2DRPG] '{path}' not found — " +
                                 "run Tools > HD2D RPG > Slice Portrait Sheets first.");
            return sprite;
        }
    }
}
