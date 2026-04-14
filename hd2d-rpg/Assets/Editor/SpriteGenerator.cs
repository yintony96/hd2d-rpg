using UnityEngine;
using UnityEditor;
using System.IO;

namespace HD2DRPG.Editor
{
    /// <summary>
    /// Generates pixel-art sprite PNG assets for characters, enemies, tiles and NPCs.
    /// Run via: Tools > HD2D RPG > Generate All Sprites
    /// </summary>
    public static class SpriteGenerator
    {
        // ─────────────────────────────────────────────────────────────────────
        // Entry point
        // ─────────────────────────────────────────────────────────────────────

        [MenuItem("Tools/HD2D RPG/Generate All Sprites")]
        public static void GenerateAll()
        {
            EnsureFolders();
            GenerateAurora();
            GenerateKael();
            GenerateSlime();
            GenerateCrystalGuardian();
            GenerateGrassTile();
            GenerateStoneTile();
            GenerateBlacksmith();
            GenerateElder();
            GenerateMerchant();
            AssetDatabase.Refresh();
            Debug.Log("[HD2DRPG] All sprites generated in Assets/Art/Sprites/");
        }

        // ─────────────────────────────────────────────────────────────────────
        // Canvas helper — wraps width so all draw calls are safe
        // ─────────────────────────────────────────────────────────────────────

        class Canvas
        {
            public readonly Color[] p;
            public readonly int W, H;
            public Canvas(int w, int h) { W = w; H = h; p = new Color[w * h]; }

            public void Set(int x, int y, Color c)
            {
                if (x < 0 || y < 0 || x >= W || y >= H) return;
                p[y * W + x] = c;
            }
            public Color Get(int x, int y)
            {
                if (x < 0 || y < 0 || x >= W || y >= H) return Color.clear;
                return p[y * W + x];
            }
            public void Rect(int x, int y, int w, int h, Color c)
            {
                for (int dy = 0; dy < h; dy++)
                for (int dx = 0; dx < w; dx++) Set(x+dx, y+dy, c);
            }
            public void HLine(int x, int y, int w, Color c)
            {
                for (int i = 0; i < w; i++) Set(x+i, y, c);
            }
            public void VLine(int x, int y, int h, Color c)
            {
                for (int i = 0; i < h; i++) Set(x, y+i, c);
            }
            public void Circle(int cx, int cy, int r, Color c)
            {
                for (int dy = -r; dy <= r; dy++)
                for (int dx = -r; dx <= r; dx++)
                    if (dx*dx+dy*dy <= r*r) Set(cx+dx, cy+dy, c);
            }
            public void Diamond(int cx, int cy, int rx, int ry, Color c)
            {
                for (int dy = -ry; dy <= ry; dy++)
                for (int dx = -rx; dx <= rx; dx++)
                    if (Mathf.Abs(dx)/(float)rx + Mathf.Abs(dy)/(float)ry <= 1f)
                        Set(cx+dx, cy+dy, c);
            }
            public void Outline(Color col)
            {
                var copy = (Color[])p.Clone();
                int[] ox = {1,-1,0,0}; int[] oy = {0,0,1,-1};
                for (int y = 0; y < H; y++)
                for (int x = 0; x < W; x++)
                {
                    if (copy[y*W+x].a < 0.1f) continue;
                    for (int d = 0; d < 4; d++)
                    {
                        int nx = x+ox[d], ny = y+oy[d];
                        if (nx<0||ny<0||nx>=W||ny>=H) continue;
                        if (copy[ny*W+nx].a < 0.1f) p[ny*W+nx] = col;
                    }
                }
            }
            public void Save(string path)
            {
                var tex = new Texture2D(W, H, TextureFormat.RGBA32, false);
                var flipped = new Color[W * H];
                for (int y = 0; y < H; y++)
                for (int x = 0; x < W; x++)
                    flipped[y*W+x] = p[(H-1-y)*W+x]; // flip Y
                tex.SetPixels(flipped);
                tex.Apply();
                File.WriteAllBytes(Path.GetFullPath(path), tex.EncodeToPNG());
                Object.DestroyImmediate(tex);
                Debug.Log($"[HD2DRPG] Saved {path}");
            }
        }

        static Color C(string hex)
        {
            ColorUtility.TryParseHtmlString("#" + hex, out Color c);
            return c;
        }

        // ─────────────────────────────────────────────────────────────────────
        // AURORA — Paladin (silver armor, gold trim, blonde hair, blue cape)
        // ─────────────────────────────────────────────────────────────────────

        static void GenerateAurora()
        {
            var cv = new Canvas(48, 80);
            Color skin=C("F4C89A"), hairD=C("D4A840"), hairL=C("FFE060");
            Color armM=C("D8DDE8"), armT=C("FFD700"), armDk=C("9AA4B4");
            Color capeB=C("3060C0"), capeDk=C("1A3A80");
            Color boot=C("705030"), eyeB=C("4488FF"), ol=C("1A1220");

            // Boots
            cv.Rect(14,0,10,10,boot); cv.HLine(13,9,12,C("503820"));
            // Legs
            cv.Rect(14,10,4,12,armDk); cv.Rect(30,10,4,12,armDk);
            // Cape behind
            cv.Rect(10,16,4,24,capeDk); cv.Rect(34,16,4,24,capeDk);
            cv.Rect(11,17,3,22,capeB);  cv.Rect(35,17,3,22,capeB);
            // Skirt
            cv.Rect(12,22,24,6,armM); cv.HLine(12,27,24,armT);
            // Chest armor
            cv.Rect(13,28,22,16,armM);
            cv.Rect(13,28,4,16,armDk); cv.Rect(31,28,4,16,armDk); // shading
            cv.VLine(23,30,12,armT); cv.HLine(16,36,16,armT);      // cross
            // Pauldrons
            cv.Rect(7,36,8,6,armM); cv.HLine(7,41,8,armT);
            cv.Rect(33,36,8,6,armM); cv.HLine(33,41,8,armT);
            // Arms
            cv.Rect(7,24,7,14,armM); cv.Rect(34,24,7,14,armM);
            cv.Rect(7,24,7,4,armT);  cv.Rect(34,24,7,4,armT); // gauntlets
            cv.Rect(8,20,6,5,skin);  cv.Rect(34,20,6,5,skin); // hands
            // Neck
            cv.Rect(20,44,8,4,skin);
            // Head
            cv.Rect(16,48,16,14,skin);
            // Hair
            cv.Rect(14,58,20,8,hairD); cv.Rect(16,60,16,6,hairL);
            cv.Rect(14,48,4,14,hairD); cv.Rect(30,48,4,14,hairD);
            cv.HLine(17,66,14,hairL); // highlight
            // Eyes
            cv.Rect(19,53,3,2,eyeB); cv.Rect(26,53,3,2,eyeB);
            cv.Set(19,52,ol); cv.Set(28,52,ol); // lash
            // Nose, mouth
            cv.Set(23,51,C("E0A070")); cv.Set(22,49,C("C07060")); cv.Set(25,49,C("C07060"));

            cv.Outline(ol);
            cv.Save("Assets/Art/Sprites/Characters/Aurora.png");
        }

        // ─────────────────────────────────────────────────────────────────────
        // KAEL — Hero / Divine Warrior (gold armor, dark spiky hair)
        // ─────────────────────────────────────────────────────────────────────

        static void GenerateKael()
        {
            var cv = new Canvas(48, 80);
            Color skin=C("E8B888"), hairD=C("1A1010"), hairH=C("3A2020");
            Color armG=C("FFD700"), armW=C("F0EEE8"), armDk=C("B89820");
            Color capeW=C("E8E0D0"), capeDk=C("A09080");
            Color boot=C("302820"), eyeA=C("CC8820"), ol=C("1A1220");

            cv.Rect(14,0,10,10,boot); cv.HLine(12,9,12,C("201810"));
            cv.Rect(13,10,10,12,armG); cv.VLine(23,10,12,armDk);
            // Cape
            cv.Rect(10,18,4,22,capeDk); cv.Rect(34,18,4,22,capeDk);
            cv.Rect(11,19,3,20,capeW);  cv.Rect(35,19,3,20,capeW);
            // Breastplate
            cv.Rect(13,22,22,18,armW);
            cv.Rect(13,22,4,18,armG); cv.Rect(31,22,4,18,armG);
            cv.HLine(13,32,22,armG);
            // Sun emblem
            cv.Circle(23,28,3,armG); cv.Circle(23,28,2,armW);
            // Pauldrons
            cv.Rect(5,34,10,8,armG); cv.HLine(5,41,10,armDk);
            cv.Rect(33,34,10,8,armG); cv.HLine(33,41,10,armDk);
            // Arms
            cv.Rect(5,24,9,14,armW); cv.Rect(34,24,9,14,armW);
            cv.Rect(5,38,9,3,armG);  cv.Rect(34,38,9,3,armG);
            cv.Rect(6,20,7,5,skin);  cv.Rect(35,20,7,5,skin);
            // Neck
            cv.Rect(20,40,8,4,skin);
            // Head
            cv.Rect(16,44,16,14,skin);
            // Dark spiky hair
            cv.Rect(14,54,20,10,hairD); cv.Rect(16,56,16,8,hairH);
            for (int i=0;i<5;i++) { int sx=13+i*5; cv.VLine(sx,54,4+i%2,hairD); }
            cv.Rect(14,44,4,14,hairD); cv.Rect(30,44,4,14,hairD);
            // Eyes — amber, intense
            cv.Rect(19,50,3,2,eyeA); cv.Rect(26,50,3,2,eyeA);
            cv.HLine(18,52,5,ol); cv.HLine(25,52,5,ol); // furrowed brows
            cv.Set(23,47,C("D09070")); cv.Set(21,45,C("B06050")); cv.Set(25,45,C("B06050"));

            cv.Outline(ol);
            cv.Save("Assets/Art/Sprites/Characters/Kael.png");
        }

        // ─────────────────────────────────────────────────────────────────────
        // SLIME ENEMY
        // ─────────────────────────────────────────────────────────────────────

        static void GenerateSlime()
        {
            var cv = new Canvas(64, 56);
            Color bM=C("40CC60"), bDk=C("20803A"), bHi=C("A0EEA8");
            Color eyW=Color.white, eyP=C("103020"), ol=C("0A2010");

            // Body ellipse
            for (int y=0;y<cv.H;y++) for (int x=0;x<cv.W;x++)
            {
                float dx=(x-32)/24f, dy=(y-26)/19f;
                if (dx*dx+dy*dy<1f) cv.Set(x,y,bM);
            }
            // Underside darker
            for (int y=0;y<18;y++) for (int x=0;x<cv.W;x++)
            {
                if (cv.Get(x,y).a>0.1f)
                { float f=(float)y/18; cv.Set(x,y,Color.Lerp(bDk,bM,f*0.5f)); }
            }
            // Top highlight
            cv.Circle(28,40,10,bHi);
            for (int y=0;y<cv.H;y++) for (int x=0;x<cv.W;x++)
                if (cv.Get(x,y)==bHi && cv.Get(x,y-1).a<0.1f) cv.Set(x,y,bM); // clip outside
            // Sheen
            cv.Circle(26,46,4,new Color(1,1,1,0.5f));
            // Drip
            cv.Rect(26,6,4,5,bM); cv.Rect(34,4,3,4,bM);
            // Eyes
            cv.Circle(22,30,6,eyW); cv.Circle(22,30,4,eyP); cv.Circle(23,31,2,C("204020"));
            cv.Circle(40,30,6,eyW); cv.Circle(40,30,4,eyP); cv.Circle(41,31,2,C("204020"));
            // Smile
            for (int x=24;x<=40;x++) cv.Set(x, 20-(int)(Mathf.Abs(x-32)*0.3f), eyP);

            cv.Outline(ol);
            cv.Save("Assets/Art/Sprites/Enemies/Slime.png");
        }

        // ─────────────────────────────────────────────────────────────────────
        // CRYSTAL GUARDIAN BOSS
        // ─────────────────────────────────────────────────────────────────────

        static void GenerateCrystalGuardian()
        {
            var cv = new Canvas(96, 112);
            Color cB=C("80C0FF"), cDk=C("2040A0"), cHi=C("C8E8FF"), cEd=C("4080D0");
            Color glow=new Color(0.8f,0.95f,1f,0.9f), ol=C("102060");

            // Legs
            cv.Rect(32,2,12,30,cDk); cv.Rect(52,2,12,30,cDk);
            cv.Rect(34,4,8,28,cB);   cv.Rect(54,4,8,28,cB);
            cv.VLine(38,4,28,cHi);   cv.VLine(58,4,28,cHi);
            // Lower body diamond
            cv.Diamond(48,32,28,24,cDk); cv.Diamond(48,32,24,20,cB); cv.Diamond(48,32,16,14,cHi);
            // Upper torso diamond
            cv.Diamond(48,58,20,20,cDk); cv.Diamond(48,58,16,16,cB); cv.Diamond(48,58,10,10,cHi);
            // Core glow
            cv.Circle(48,46,10,glow);
            // Left arm shards
            cv.Diamond(18,52,12,16,cDk); cv.Diamond(18,52,8,12,cB);
            cv.Diamond(8,42,8,10,cEd);
            // Right arm shards
            cv.Diamond(78,52,12,16,cDk); cv.Diamond(78,52,8,12,cB);
            cv.Diamond(88,42,8,10,cEd);
            // Shoulder connectors
            cv.Rect(26,46,8,10,cB); cv.Rect(62,46,8,10,cB);
            // Head diamond
            cv.Diamond(48,86,18,16,cDk); cv.Diamond(48,86,14,12,cB); cv.Diamond(48,86,9,8,cHi);
            // Crown spikes
            for (int i=-2;i<=2;i++)
            {
                int h=8-Mathf.Abs(i)*2, cx=48+i*8;
                for (int y=0;y<h;y++)
                {
                    int hw=Mathf.Max(1,(int)(2*(1f-(float)y/h)));
                    cv.HLine(cx-hw, 94+y, hw*2, i<0?cDk:cB);
                }
            }
            // Glowing cyan eyes
            cv.Circle(39,84,5,C("00EEFF")); cv.Circle(57,84,5,C("00EEFF"));
            cv.Circle(39,84,3,Color.white); cv.Circle(57,84,3,Color.white);
            cv.Circle(39,84,1,C("00FFFF")); cv.Circle(57,84,1,C("00FFFF"));

            cv.Outline(ol);
            cv.Save("Assets/Art/Sprites/Enemies/CrystalGuardian.png");
        }

        // ─────────────────────────────────────────────────────────────────────
        // TILES
        // ─────────────────────────────────────────────────────────────────────

        static void GenerateGrassTile()
        {
            var cv = new Canvas(32, 32);
            Color g1=C("4A8832"), g2=C("3D7228"), gL=C("6CAA46"), gD=C("2A5018");
            for (int y=0;y<32;y++) for (int x=0;x<32;x++)
                cv.Set(x,y,(x+y)%2==0?g1:g2);
            var rng = new System.Random(42);
            for (int i=0;i<14;i++)
            {
                int gx=rng.Next(2,30), gy=rng.Next(2,30);
                cv.Set(gx,gy,gL); cv.Set(gx+1,gy,gL); cv.Set(gx,gy+1,gD);
            }
            cv.Save("Assets/Art/Sprites/Tiles/Grass.png");
        }

        static void GenerateStoneTile()
        {
            var cv = new Canvas(32, 32);
            Color s1=C("888078"), s2=C("706860"), grout=C("484038");
            for (int y=0;y<32;y++) for (int x=0;x<32;x++) cv.Set(x,y,s1);
            // Grout lines
            cv.HLine(0,0,32,grout); cv.HLine(0,16,32,grout); cv.HLine(0,31,32,grout);
            for (int y=1;y<16;y++)  { cv.Set(0,y,grout); cv.Set(16,y,grout); cv.Set(31,y,grout); }
            for (int y=17;y<31;y++) { cv.Set(8,y,grout); cv.Set(24,y,grout); }
            var rng = new System.Random(7);
            for (int i=0;i<16;i++) cv.Set(rng.Next(1,31),rng.Next(1,31),s2);
            cv.Save("Assets/Art/Sprites/Tiles/Stone.png");
        }

        // ─────────────────────────────────────────────────────────────────────
        // NPC SPRITES
        // ─────────────────────────────────────────────────────────────────────

        static void GenerateBlacksmith()
        {
            var cv = new Canvas(48, 80);
            Color skin=C("C8905A"), hair=C("3A2010"), apron=C("705030");
            Color shirt=C("8B4513"), belt=C("2A1808"), pant=C("4A3020");
            Color boot=C("2A1808"), eye=C("3A2010"), ol=C("1A0E04");

            cv.Rect(14,0,10,10,boot);
            cv.Rect(13,10,10,14,pant);
            cv.HLine(13,24,22,belt); cv.Rect(13,25,22,3,belt);
            cv.Rect(12,28,24,16,shirt);
            cv.Rect(16,28,16,16,apron);
            cv.Rect(6,28,8,16,shirt); cv.Rect(34,28,8,16,shirt);
            cv.Rect(6,20,6,9,skin);   cv.Rect(36,20,6,9,skin);
            cv.Rect(20,44,8,4,skin);
            cv.Rect(16,48,16,14,skin);
            cv.Rect(14,58,20,8,hair);
            cv.Rect(12,48,6,16,hair); cv.Rect(30,48,6,16,hair);
            cv.Rect(14,48,20,6,hair); // full beard
            cv.Set(20,54,eye); cv.Set(27,54,eye);
            cv.Set(23,51,C("E0B090")); // nose
            // Eyebrows (thick)
            cv.HLine(19,56,4,hair); cv.HLine(25,56,4,hair);

            cv.Outline(ol);
            cv.Save("Assets/Art/Sprites/NPCs/Blacksmith.png");
        }

        static void GenerateElder()
        {
            var cv = new Canvas(48, 80);
            Color skin=C("D4B090"), hair=C("E8E4DC"), robe=C("4A3A6A");
            Color robL=C("6A5A8A"), staff=C("8B6030"), gem=C("8040FF");
            Color eye=C("4466AA"), ol=C("1A1228");

            cv.Rect(16,0,16,44,robe); cv.Rect(18,0,12,44,robL);
            cv.Rect(8,20,10,22,robe); cv.Rect(30,20,10,22,robe);
            // Staff (left of body)
            cv.VLine(4,0,52,staff); cv.VLine(5,0,52,C("A07840"));
            cv.Circle(4,50,3,gem);
            cv.Rect(20,44,8,4,skin);
            cv.Rect(16,48,16,14,skin);
            // Long white hair + beard
            cv.Rect(14,56,20,10,hair); cv.Rect(12,48,6,18,hair); cv.Rect(30,48,6,18,hair);
            cv.Rect(16,44,16,8,hair); // top hair
            cv.Rect(17,36,14,14,hair); // long beard
            // Eyes
            cv.Rect(19,52,3,2,eye); cv.Rect(26,52,3,2,eye);
            cv.Set(23,49,C("C09870")); // nose
            // Wise wrinkle lines
            cv.HLine(19,55,3,C("C09870")); cv.HLine(26,55,3,C("C09870"));

            cv.Outline(ol);
            cv.Save("Assets/Art/Sprites/NPCs/Elder.png");
        }

        static void GenerateMerchant()
        {
            var cv = new Canvas(48, 80);
            Color skin=C("E8C888"), hair=C("5A3010"), coat=C("C07020");
            Color coatL=C("E09030"), vest=C("802010"), pant=C("503818");
            Color boot=C("302010"), coin=C("FFD700"), eye=C("402010"), ol=C("1A0A04");

            cv.Rect(14,0,10,10,boot);
            cv.Rect(13,10,10,16,pant);
            cv.Rect(12,26,24,18,coat); cv.Rect(16,26,16,18,vest);
            cv.Rect(6,28,8,16,coat); cv.Rect(34,28,8,16,coat);
            cv.Rect(7,20,6,9,skin);  cv.Rect(35,20,6,9,skin);
            cv.Circle(38,22,4,coin); // coin bag
            // Lapels
            cv.Set(20,40,coatL); cv.Set(21,40,coatL);
            cv.Set(26,40,coatL); cv.Set(27,40,coatL);
            cv.Rect(20,44,8,4,skin);
            cv.Rect(16,48,16,14,skin);
            // Merchant hat
            cv.HLine(14,60,20,C("2A1808")); cv.Rect(17,61,14,10,C("2A1808"));
            cv.HLine(17,61,14,C("403020")); // hat band
            cv.Rect(14,48,5,12,hair); cv.Rect(29,48,5,12,hair); // side hair
            cv.Set(20,52,eye); cv.Set(27,52,eye);
            // Big merchant smile
            for (int x=20;x<=28;x++) cv.Set(x,47-(int)(Mathf.Sin((x-24)*0.4f)*2),C("902010"));
            cv.Set(23,49,C("D0A070")); // nose

            cv.Outline(ol);
            cv.Save("Assets/Art/Sprites/NPCs/Merchant.png");
        }

        // ─────────────────────────────────────────────────────────────────────
        // Folder setup
        // ─────────────────────────────────────────────────────────────────────

        static void EnsureFolders()
        {
            foreach (var path in new[]
            {
                "Assets/Art/Sprites/Characters",
                "Assets/Art/Sprites/Enemies",
                "Assets/Art/Sprites/Tiles",
                "Assets/Art/Sprites/NPCs"
            })
            {
                var parts = path.Split('/');
                var cur = parts[0];
                for (int i = 1; i < parts.Length; i++)
                {
                    var next = cur + "/" + parts[i];
                    if (!AssetDatabase.IsValidFolder(next))
                        AssetDatabase.CreateFolder(cur, parts[i]);
                    cur = next;
                }
            }
        }
    }
}
