using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using System.IO;
using System.Linq;
using TMPro;

namespace HD2DRPG.Editor
{
    /// <summary>
    /// Menu items to build and configure scenes from scratch.
    /// Tools > HD2D RPG > Build Hub Scene  /  Build Battle Scene
    /// </summary>
    public static class SceneBuilder
    {
        // ── Hub Scene ────────────────────────────────────────────────────────

        [MenuItem("Tools/HD2D RPG/Build Hub Scene")]
        public static void BuildHubScene()
        {
            var scene = EditorSceneManager.OpenScene("Assets/Scenes/World/Hub.unity", OpenSceneMode.Single);

            // ── Camera (HD-2D angle: slight top-down tilt) ──────────────────
            var camGO = new GameObject("Main Camera");
            camGO.tag = "MainCamera";
            var cam = camGO.AddComponent<Camera>();
            cam.orthographic      = false;
            cam.fieldOfView       = 40f;
            cam.nearClipPlane     = 0.1f;
            cam.farClipPlane      = 100f;
            cam.backgroundColor   = new Color(0.1f, 0.09f, 0.12f);
            camGO.transform.position     = new Vector3(0, 7, -10);
            camGO.transform.eulerAngles  = new Vector3(30, 0, 0);
            camGO.AddComponent<AudioListener>();

            // ── Directional light (warm sunlight) ───────────────────────────
            var lightGO = new GameObject("Directional Light");
            var light   = lightGO.AddComponent<Light>();
            light.type      = LightType.Directional;
            light.color     = new Color(1f, 0.95f, 0.84f);
            light.intensity = 1.2f;
            light.shadows   = LightShadows.Soft;
            lightGO.transform.eulerAngles = new Vector3(50, -30, 0);

            // ── Ground plane (3D for HD-2D look) ────────────────────────────
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Ground";
            ground.transform.position   = Vector3.zero;
            ground.transform.localScale = new Vector3(5, 1, 5);
            SetColor(ground, new Color(0.25f, 0.38f, 0.22f)); // grassy green

            // ── Hub town buildings (simple cubes as placeholders) ────────────
            CreateBuilding("Inn",       new Vector3(-6, 0, 4),  new Vector3(3, 4, 2), new Color(0.72f, 0.55f, 0.38f));
            CreateBuilding("Shop",      new Vector3( 6, 0, 4),  new Vector3(3, 3, 2), new Color(0.55f, 0.38f, 0.28f));
            CreateBuilding("TowerGate", new Vector3( 0, 0, 12), new Vector3(4, 6, 1), new Color(0.30f, 0.25f, 0.35f));

            // ── Path (flat dark stone strip toward tower) ───────────────────
            var path = GameObject.CreatePrimitive(PrimitiveType.Cube);
            path.name = "Path";
            path.transform.position   = new Vector3(0, 0.01f, 5);
            path.transform.localScale = new Vector3(2, 0.02f, 14);
            SetColor(path, new Color(0.45f, 0.42f, 0.38f));

            // ── Fence posts (visual dressing) ───────────────────────────────
            for (int i = -3; i <= 3; i++)
            {
                CreatePost(new Vector3(i * 2.5f, 0, -8));
            }

            // ── Player (billboard quad with SpriteRenderer) ──────────────────
            var playerGO = new GameObject("Player");
            playerGO.tag = "Player";
            playerGO.transform.position = new Vector3(0, 0.5f, 0);
            var sr = playerGO.AddComponent<SpriteRenderer>();
            // Try the Miro portrait overworld slice first, fall back to generated sprite
            sr.sprite = PortraitImporter.LoadCharacterSprite("Aurora", "_Overworld")
                     ?? LoadSprite("Assets/Art/Sprites/Characters/Aurora.png", new Color(0.3f, 0.55f, 1f));
            sr.sortingOrder  = 10;
            var rb = playerGO.AddComponent<Rigidbody2D>();
            rb.gravityScale  = 0;
            rb.constraints   = RigidbodyConstraints2D.FreezeRotation;
            playerGO.AddComponent<BoxCollider2D>();
            var pc           = playerGO.AddComponent<PlayerController>();
            pc.spriteRenderer = sr;

            // Camera follow script (simple, no Cinemachine dependency)
            playerGO.AddComponent<CameraFollow>();

            // ── NPCs ─────────────────────────────────────────────────────────
            var npcContainer = new GameObject("NPCs");
            CreateNPC(npcContainer, "Blacksmith",  new Vector3(-5, 0.5f,  2), new Color(0.8f, 0.5f, 0.2f),
                      new[] { "Need a new blade? I've got the finest steel in the continent.", "Stay sharp out there, adventurer." });
            CreateNPC(npcContainer, "Elder",       new Vector3( 5, 0.5f,  2), new Color(0.7f, 0.7f, 0.9f),
                      new[] { "The demon tower pulses with dark energy. Be careful.", "Many warriors have entered. Few return." });
            CreateNPC(npcContainer, "Merchant",    new Vector3(-5, 0.5f, -2), new Color(0.9f, 0.8f, 0.3f),
                      new[] { "Potions, elixirs, revival beads — I have it all!", "Discount for repeat customers!" });

            // ── Tower entrance trigger ────────────────────────────────────────
            var towerTrigger = new GameObject("TowerEntrance");
            towerTrigger.transform.position = new Vector3(0, 0.5f, 10);
            var towerMarker = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            towerMarker.name = "TowerMarker";
            towerMarker.transform.SetParent(towerTrigger.transform);
            towerMarker.transform.localPosition = Vector3.zero;
            towerMarker.transform.localScale    = new Vector3(1.5f, 0.05f, 1.5f);
            SetColor(towerMarker, new Color(0.6f, 0.3f, 0.9f));

            // ── HubScene manager ─────────────────────────────────────────────
            var hubManagerGO = new GameObject("HubScene");
            var hub = hubManagerGO.AddComponent<HubScene>();
            hub.playerTransform      = playerGO.transform;
            hub.towerEntranceTrigger = towerTrigger.transform;
            hub.npcContainer         = npcContainer.transform;

            // Assign NPCs array
            var npcComponents = npcContainer.GetComponentsInChildren<HubNPC>();
            hub.npcs = npcComponents;

            // ── Canvas UI — Octopath-style dialogue + party panel ────────────
            var canvasGO = new GameObject("Canvas");
            var canvas   = canvasGO.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            var scaler = canvasGO.AddComponent<UnityEngine.UI.CanvasScaler>();
            scaler.uiScaleMode         = UnityEngine.UI.CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1920, 1080);
            canvasGO.AddComponent<UnityEngine.UI.GraphicRaycaster>();

            // ── Dialogue Panel ────────────────────────────────────────────────
            // Outer panel — dark translucent bar at bottom
            var dialoguePanelGO = new GameObject("DialoguePanel");
            dialoguePanelGO.transform.SetParent(canvasGO.transform, false);
            var panelRect = dialoguePanelGO.AddComponent<RectTransform>();
            panelRect.anchorMin = new Vector2(0f,    0f);
            panelRect.anchorMax = new Vector2(1f,    0f);
            panelRect.pivot     = new Vector2(0.5f,  0f);
            panelRect.sizeDelta = new Vector2(0f, 220f);
            panelRect.anchoredPosition = new Vector2(0, 10f);
            var panelImg = dialoguePanelGO.AddComponent<UnityEngine.UI.Image>();
            panelImg.color = new Color(0.04f, 0.04f, 0.10f, 0.93f);
            dialoguePanelGO.SetActive(false);

            // Portrait frame — left side, slightly overlapping top edge
            var portraitFrameGO = new GameObject("PortraitFrame");
            portraitFrameGO.transform.SetParent(dialoguePanelGO.transform, false);
            var pfRect = portraitFrameGO.AddComponent<RectTransform>();
            pfRect.anchorMin        = new Vector2(0f,  1f);
            pfRect.anchorMax        = new Vector2(0f,  1f);
            pfRect.pivot            = new Vector2(0f,  0f);
            pfRect.anchoredPosition = new Vector2(20f, 0f);
            pfRect.sizeDelta        = new Vector2(170f, 210f);
            var pfImg = portraitFrameGO.AddComponent<UnityEngine.UI.Image>();
            pfImg.color = new Color(0.08f, 0.07f, 0.14f, 1f);

            // Portrait image inside frame
            var portraitImgGO = new GameObject("PortraitImage");
            portraitImgGO.transform.SetParent(portraitFrameGO.transform, false);
            var piRect = portraitImgGO.AddComponent<RectTransform>();
            piRect.anchorMin  = new Vector2(0f, 0f);
            piRect.anchorMax  = new Vector2(1f, 1f);
            piRect.offsetMin  = new Vector2(4f, 4f);
            piRect.offsetMax  = new Vector2(-4f, -4f);
            var portraitImgComp = portraitImgGO.AddComponent<UnityEngine.UI.Image>();
            portraitImgComp.preserveAspect = true;
            // Default to Aurora portrait; changes at runtime when NPCs speak
            var auroraPortrait = PortraitImporter.LoadCharacterSprite("Aurora", "_Portrait");
            if (auroraPortrait != null) portraitImgComp.sprite = auroraPortrait;

            // Text area — right of portrait
            var textAreaGO = new GameObject("TextArea");
            textAreaGO.transform.SetParent(dialoguePanelGO.transform, false);
            var taRect = textAreaGO.AddComponent<RectTransform>();
            taRect.anchorMin        = new Vector2(0f, 0f);
            taRect.anchorMax        = new Vector2(1f, 1f);
            taRect.offsetMin        = new Vector2(210f,  10f);
            taRect.offsetMax        = new Vector2(-20f, -10f);

            // Speaker name plate
            var nameGO = new GameObject("SpeakerName");
            nameGO.transform.SetParent(textAreaGO.transform, false);
            var nameRect = nameGO.AddComponent<RectTransform>();
            nameRect.anchorMin        = new Vector2(0f, 1f);
            nameRect.anchorMax        = new Vector2(0.6f, 1f);
            nameRect.pivot            = new Vector2(0f, 1f);
            nameRect.anchoredPosition = new Vector2(0f, 0f);
            nameRect.sizeDelta        = new Vector2(0f, 36f);
            var nameBg = nameGO.AddComponent<UnityEngine.UI.Image>();
            nameBg.color = new Color(0.10f, 0.08f, 0.20f, 0.95f);
            var nameTMP = nameGO.AddComponent<TextMeshProUGUI>();
            nameTMP.text      = "SPEAKER";
            nameTMP.fontSize  = 22f;
            nameTMP.fontStyle = FontStyles.Bold;
            nameTMP.color     = new Color(1f, 0.92f, 0.70f, 1f); // warm gold
            nameTMP.margin    = new Vector4(10f, 4f, 6f, 4f);
            nameTMP.alignment = TextAlignmentOptions.MidlineLeft;

            // Body text
            var bodyGO = new GameObject("BodyText");
            bodyGO.transform.SetParent(textAreaGO.transform, false);
            var bodyRect = bodyGO.AddComponent<RectTransform>();
            bodyRect.anchorMin  = new Vector2(0f, 0f);
            bodyRect.anchorMax  = new Vector2(1f, 1f);
            bodyRect.offsetMin  = new Vector2(0f,  10f);
            bodyRect.offsetMax  = new Vector2(0f, -42f);
            var bodyTMP = bodyGO.AddComponent<TextMeshProUGUI>();
            bodyTMP.text      = "";
            bodyTMP.fontSize  = 20f;
            bodyTMP.color     = new Color(0.95f, 0.94f, 0.90f, 1f);
            bodyTMP.margin    = new Vector4(8f, 6f, 8f, 6f);
            bodyTMP.alignment = TextAlignmentOptions.TopLeft;
            bodyTMP.textWrappingMode = TextWrappingModes.Normal;

            // Advance indicator ▼
            var advanceIndicatorGO = new GameObject("AdvanceIndicator");
            advanceIndicatorGO.transform.SetParent(dialoguePanelGO.transform, false);
            var advRect = advanceIndicatorGO.AddComponent<RectTransform>();
            advRect.anchorMin        = new Vector2(1f, 0f);
            advRect.anchorMax        = new Vector2(1f, 0f);
            advRect.pivot            = new Vector2(1f, 0f);
            advRect.anchoredPosition = new Vector2(-16f, 14f);
            advRect.sizeDelta        = new Vector2(28f, 28f);
            var advTMP = advanceIndicatorGO.AddComponent<TextMeshProUGUI>();
            advTMP.text      = "▼";
            advTMP.fontSize  = 20f;
            advTMP.color     = new Color(1f, 0.92f, 0.55f, 1f);
            advTMP.alignment = TextAlignmentOptions.Center;
            advanceIndicatorGO.SetActive(false);

            // ── Party panel (M key) ───────────────────────────────────────────
            var partyPanelGO = new GameObject("PartyPanel");
            partyPanelGO.transform.SetParent(canvasGO.transform, false);
            var partyRect = partyPanelGO.AddComponent<RectTransform>();
            partyRect.anchorMin = new Vector2(0.25f, 0.08f);
            partyRect.anchorMax = new Vector2(0.75f, 0.92f);
            partyRect.offsetMin = Vector2.zero;
            partyRect.offsetMax = Vector2.zero;
            var partyImg = partyPanelGO.AddComponent<UnityEngine.UI.Image>();
            partyImg.color = new Color(0.05f, 0.05f, 0.12f, 0.95f);
            partyPanelGO.SetActive(false);

            // ── Wire DialogueUI component ─────────────────────────────────────
            var dialogueUIGO = new GameObject("DialogueUI");
            dialogueUIGO.transform.SetParent(canvasGO.transform, false);
            var dui = dialogueUIGO.AddComponent<DialogueUI>();
            dui.dialoguePanel    = dialoguePanelGO;
            dui.portraitImage    = portraitImgComp;
            dui.speakerNameText  = nameTMP;
            dui.bodyText         = bodyTMP;
            dui.advanceIndicator = advanceIndicatorGO;

            hub.dialogueUI           = dui;
            hub.partyManagementPanel = partyPanelGO;

            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene);
            Debug.Log("[HD2DRPG] Hub scene fully built! Press Play to walk around. E = interact with NPCs, M = party menu.");
        }

        // ── Battle Scene ─────────────────────────────────────────────────────

        [MenuItem("Tools/HD2D RPG/Build Battle Scene")]
        public static void BuildBattleScene()
        {
            var scene = EditorSceneManager.OpenScene("Assets/Scenes/Combat/Battle.unity", OpenSceneMode.Single);

            // Camera
            var camGO = new GameObject("Main Camera");
            camGO.tag = "MainCamera";
            var cam = camGO.AddComponent<Camera>();
            cam.orthographic     = false;
            cam.fieldOfView      = 45f;
            cam.backgroundColor  = new Color(0.08f, 0.06f, 0.12f);
            cam.transform.position    = new Vector3(0, 3, -12);
            cam.transform.eulerAngles = new Vector3(10, 0, 0);
            camGO.AddComponent<AudioListener>();

            // Directional light
            var lightGO = new GameObject("Directional Light");
            var light   = lightGO.AddComponent<Light>();
            light.type      = LightType.Directional;
            light.color     = new Color(1f, 0.9f, 0.75f);
            light.intensity = 1.0f;
            lightGO.transform.eulerAngles = new Vector3(45, -20, 0);

            // ── Battle background (3D ground plane) ─────────────────────────
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "BattleGround";
            ground.transform.position   = new Vector3(0, -0.5f, 0);
            ground.transform.localScale = new Vector3(3, 1, 2);
            SetColor(ground, new Color(0.18f, 0.14f, 0.22f));

            // ── Background geometry (depth layers) ──────────────────────────
            var bgWall = GameObject.CreatePrimitive(PrimitiveType.Cube);
            bgWall.name = "BackWall";
            bgWall.transform.position   = new Vector3(0, 2, 8);
            bgWall.transform.localScale = new Vector3(30, 8, 0.5f);
            SetColor(bgWall, new Color(0.12f, 0.10f, 0.18f));

            // Atmospheric pillars
            CreatePillar(new Vector3(-8, 1, 4));
            CreatePillar(new Vector3( 8, 1, 4));
            CreatePillar(new Vector3(-5, 1, 6));
            CreatePillar(new Vector3( 5, 1, 6));

            // ── Party member placeholders (left side) ────────────────────────
            CreateBattleCharacter("Aurora", new Vector3(-4, 0, -2), new Color(0.3f, 0.55f, 1f));
            CreateBattleCharacter("Kael",   new Vector3(-2, 0, -1), new Color(1f, 0.85f, 0.3f));

            // ── Enemy placeholders (right side) ─────────────────────────────
            CreateBattleCharacter("Slime_1", new Vector3(3, 0, 1),  new Color(0.3f, 0.9f, 0.3f));
            CreateBattleCharacter("Slime_2", new Vector3(5, 0, 0),  new Color(0.2f, 0.8f, 0.2f));

            // ── Combat manager ───────────────────────────────────────────────
            var combatGO = new GameObject("CombatManager");
            combatGO.AddComponent<CombatManager>();

            // ── Canvas UI ───────────────────────────────────────────────────
            var canvasGO = new GameObject("BattleUI");
            var canvas   = canvasGO.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvasGO.AddComponent<UnityEngine.UI.CanvasScaler>();
            canvasGO.AddComponent<UnityEngine.UI.GraphicRaycaster>();

            // Bottom action panel
            var actionPanelGO = new GameObject("ActionPanel");
            actionPanelGO.transform.SetParent(canvasGO.transform, false);
            var apRect = actionPanelGO.AddComponent<RectTransform>();
            apRect.anchorMin = new Vector2(0, 0);
            apRect.anchorMax = new Vector2(0.4f, 0.35f);
            apRect.offsetMin = new Vector2(10, 10);
            apRect.offsetMax = new Vector2(-5, -5);
            var apImg = actionPanelGO.AddComponent<UnityEngine.UI.Image>();
            apImg.color = new Color(0.05f, 0.05f, 0.1f, 0.92f);

            // Enemy status panel (right)
            var enemyPanelGO = new GameObject("EnemyPanel");
            enemyPanelGO.transform.SetParent(canvasGO.transform, false);
            var epRect = enemyPanelGO.AddComponent<RectTransform>();
            epRect.anchorMin = new Vector2(0.6f, 0.6f);
            epRect.anchorMax = new Vector2(1f,   1f);
            epRect.offsetMin = new Vector2(5, 5);
            epRect.offsetMax = new Vector2(-10, -10);
            var epImg = enemyPanelGO.AddComponent<UnityEngine.UI.Image>();
            epImg.color = new Color(0.05f, 0.05f, 0.1f, 0.92f);

            // Turn order strip (top center)
            var turnStripGO = new GameObject("TurnStrip");
            turnStripGO.transform.SetParent(canvasGO.transform, false);
            var tsRect = turnStripGO.AddComponent<RectTransform>();
            tsRect.anchorMin = new Vector2(0.2f, 0.88f);
            tsRect.anchorMax = new Vector2(0.8f, 1f);
            tsRect.offsetMin = Vector2.zero;
            tsRect.offsetMax = Vector2.zero;
            var tsImg = turnStripGO.AddComponent<UnityEngine.UI.Image>();
            tsImg.color = new Color(0.05f, 0.05f, 0.1f, 0.75f);

            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene);
            Debug.Log("[HD2DRPG] Battle scene built with party + enemy placeholders.");
        }

        // ── Helpers ──────────────────────────────────────────────────────────

        static void SetColor(GameObject go, Color color)
        {
            var r = go.GetComponent<Renderer>();
            if (r == null) return;
            var mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
            if (mat.shader.name == "Hidden/InternalErrorShader")
                mat = new Material(Shader.Find("Standard"));
            mat.color = color;
            r.sharedMaterial = mat;
        }

        static void CreateBuilding(string name, Vector3 pos, Vector3 scale, Color color)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = name;
            go.transform.position   = new Vector3(pos.x, pos.y + scale.y * 0.5f, pos.z);
            go.transform.localScale = scale;
            SetColor(go, color);

            // Roof
            var roof = GameObject.CreatePrimitive(PrimitiveType.Cube);
            roof.name = name + "_Roof";
            roof.transform.position   = new Vector3(pos.x, pos.y + scale.y + 0.3f, pos.z);
            roof.transform.localScale = new Vector3(scale.x + 0.4f, 0.6f, scale.z + 0.4f);
            SetColor(roof, color * 0.7f);
        }

        static void CreatePost(Vector3 pos)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            go.name = "FencePost";
            go.transform.position   = new Vector3(pos.x, 0.6f, pos.z);
            go.transform.localScale = new Vector3(0.15f, 0.6f, 0.15f);
            SetColor(go, new Color(0.55f, 0.42f, 0.28f));
        }

        static void CreateNPC(GameObject container, string npcName, Vector3 pos, Color fallback, string[] lines)
        {
            var go = new GameObject(npcName);
            go.transform.SetParent(container.transform);
            go.transform.position = pos;

            var sr = go.AddComponent<SpriteRenderer>();
            sr.sprite       = LoadSprite($"Assets/Art/Sprites/NPCs/{npcName}.png", fallback);
            sr.sortingOrder = 10;

            var npc = go.AddComponent<HubNPC>();
            npc.npcName       = npcName;
            npc.dialogueLines = lines;
            // NPCs don't have portrait sheets — portrait slot stays null,
            // DialogueUI will leave the portrait panel showing whatever was last set
            npc.portrait = null;
        }

        static void CreateBattleCharacter(string charName, Vector3 pos, Color fallback)
        {
            var go = new GameObject(charName);
            go.transform.position = pos;

            Sprite sprite = null;

            // Aurora and Kael: use their battle stance slice from the Miro portrait sheet
            if (charName == "Aurora" || charName == "Kael")
                sprite = PortraitImporter.LoadCharacterSprite(charName, "_Battle");

            // Slimes and other enemies: use generated sprite
            if (sprite == null)
            {
                string spriteName = charName.StartsWith("Slime") ? "Slime" : charName;
                bool isEnemy = charName.StartsWith("Slime") || charName == "CrystalGuardian";
                string folder = isEnemy ? "Enemies" : "Characters";
                sprite = LoadSprite($"Assets/Art/Sprites/{folder}/{spriteName}.png", fallback);
            }

            var sr = go.AddComponent<SpriteRenderer>();
            sr.sprite       = sprite;
            sr.sortingOrder = 10;
            go.transform.localScale = new Vector3(1.5f, 2f, 1f);
        }

        static void CreatePillar(Vector3 pos)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            go.name = "Pillar";
            go.transform.position   = pos;
            go.transform.localScale = new Vector3(0.6f, 3f, 0.6f);
            SetColor(go, new Color(0.20f, 0.16f, 0.25f));
        }

        /// <summary>
        /// Tries to load a generated PNG sprite from the AssetDatabase.
        /// Falls back to a colored silhouette if the asset doesn't exist yet
        /// (i.e. SpriteGenerator hasn't been run).
        /// </summary>
        static Sprite LoadSprite(string assetPath, Color fallback)
        {
            // Import the asset so Unity knows about it (no-op if already imported)
            AssetDatabase.ImportAsset(assetPath, ImportAssetOptions.ForceSynchronousImport);
            var tex = AssetDatabase.LoadAssetAtPath<Texture2D>(assetPath);
            if (tex != null)
            {
                return Sprite.Create(tex,
                    new Rect(0, 0, tex.width, tex.height),
                    new Vector2(0.5f, 0f), 16f);
            }
            Debug.LogWarning($"[HD2DRPG] Sprite not found at {assetPath}. " +
                             "Run Tools > HD2D RPG > Generate All Sprites first.");
            return CreatePlaceholderSprite(fallback);
        }

        static Sprite CreatePlaceholderSprite(Color color)
        {
            var tex = new Texture2D(64, 128);
            var pixels = new Color[64 * 128];
            for (int i = 0; i < pixels.Length; i++)
            {
                int x = i % 64, y = i / 64;
                // Simple silhouette: rounded body
                bool inBody = (x >= 8 && x <= 56 && y >= 0  && y <= 80);
                bool inHead = (x >= 16 && x <= 48 && y >= 84 && y <= 116);
                pixels[i] = (inBody || inHead) ? color : Color.clear;
            }
            tex.SetPixels(pixels);
            tex.Apply();
            return Sprite.Create(tex, new Rect(0, 0, 64, 128), new Vector2(0.5f, 0f), 64f);
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
            enemy.enemyName        = "Slime";
            enemy.hp               = 120;
            enemy.maxShieldPoints  = 3;
            enemy.expYield         = 20;
            enemy.goldYield        = 10;
            enemy.jpYield          = 8;
            enemy.weaknesses       = new[] { ElementType.Fire, ElementType.Axe };
            enemy.resistances      = new[] { ElementType.Ice };
            enemy.breakTurns       = 1;
            enemy.breakDamageBonus = 0.5f;
            AssetDatabase.CreateAsset(enemy, path);
            AssetDatabase.SaveAssets();
            Selection.activeObject = enemy;
        }

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
            skill.skillName             = "Holy Blade";
            skill.mpCost                = 12;
            skill.element               = ElementType.Light;
            skill.targetType            = TargetType.SingleEnemy;
            skill.powerMultiplier       = 1.5f;
            skill.hitCount              = 1;
            skill.shieldDamage          = 1;
            skill.boostedHitCount       = 3;
            skill.boostedPowerMultiplier = 2.0f;
            AssetDatabase.CreateAsset(skill, path);
            AssetDatabase.SaveAssets();
            Selection.activeObject = skill;
        }
    }
}
