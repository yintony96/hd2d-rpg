"""
generate_assets.py  --  Shattered Realm full art pipeline
Generates portraits, map sprites, battle sprites and environment art
using Replicate Flux Dev (img2img with your reference images).
Background removal via 851-labs/background-removal.

Usage:
    python generate_assets.py YOUR_REPLICATE_TOKEN
"""

import sys, os, time, pathlib, base64
import httpx

# ---------------------------------------------------------------------------
# Token
# ---------------------------------------------------------------------------
TOKEN = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("REPLICATE_API_TOKEN", "")
if not TOKEN:
    print("Usage: python generate_assets.py r8_YOUR_TOKEN")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Reference images (your mood-board)
# ---------------------------------------------------------------------------
_REFS_DIR   = pathlib.Path(r"c:\Users\User\Downloads\Mood board FIRE EMBLEM")
REF_FE      = _REFS_DIR / "tumblr_dff96df58ebf5aa26317078d01686a78_208d8cba_1280.jpg"
REF_UO_MAP  = _REFS_DIR / "unicorn overlord map.jpg"
REF_UO_BTLR = _REFS_DIR / "unicorn overlord sprites in battle.jpeg"

# ---------------------------------------------------------------------------
# Output directories
# ---------------------------------------------------------------------------
BASE   = pathlib.Path(__file__).parent / "assets"
DIRS   = {
    "portrait":    BASE / "portraits",
    "map":         BASE / "sprites" / "map",
    "battle":      BASE / "sprites" / "battle",
    "environment": BASE / "sprites" / "environment",
}
for d in DIRS.values():
    d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------
HDR  = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json",
        "Prefer": "wait"}
BASE_URL = "https://api.replicate.com/v1"
CLIENT   = httpx.Client(timeout=180)


def _b64(path: pathlib.Path) -> str:
    ext = "jpeg" if path.suffix.lower() in (".jpg", ".jpeg") else "png"
    data = base64.b64encode(path.read_bytes()).decode()
    return f"data:image/{ext};base64,{data}"


def _post(endpoint: str, payload: dict) -> dict:
    r = CLIENT.post(f"{BASE_URL}{endpoint}", headers=HDR, json=payload)
    r.raise_for_status()
    return r.json()


def _poll(pred_id: str, timeout: int = 300) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = CLIENT.get(f"{BASE_URL}/predictions/{pred_id}", headers=HDR)
        r.raise_for_status()
        p = r.json()
        if p["status"] == "succeeded":
            return p
        if p["status"] in ("failed", "canceled"):
            raise RuntimeError(f"{p['status']}: {p.get('error')}")
        print(f"      [{p['status']}] ...", flush=True)
        time.sleep(5)
    raise TimeoutError("prediction timed out")


def _finish(pred: dict) -> dict:
    if pred.get("status") == "succeeded":
        return pred
    return _poll(pred["id"])


def _download(url: str, path: pathlib.Path):
    r = CLIENT.get(url, follow_redirects=True)
    r.raise_for_status()
    path.write_bytes(r.content)

# ---------------------------------------------------------------------------
# Generation functions
# ---------------------------------------------------------------------------

def flux_generate(prompt: str, ratio: str = "1:1",
                  ref: pathlib.Path = None, strength: float = 0.88) -> str:
    """Generate with Flux Dev (img2img when ref is given). Returns output URL."""
    inp = {
        "prompt":                 prompt,
        "aspect_ratio":           ratio,
        "output_format":          "png",
        "output_quality":         95,
        "num_outputs":            1,
        "guidance":               3.5,
        "num_inference_steps":    30,
        "disable_safety_checker": True,
    }
    if ref and ref.exists():
        inp["image"]           = _b64(ref)
        inp["prompt_strength"] = strength

    pred = _post("/models/black-forest-labs/flux-dev/predictions", {"input": inp})
    result = _finish(pred)
    out = result.get("output") or []
    return str(out[0] if isinstance(out, list) else out)


def remove_bg(image_url: str) -> str:
    """Remove background. Returns URL of transparent PNG.
    Tries two models; raises on both failing."""
    # Primary: cjwbw/rembg (version-based API)
    try:
        pred = _post("/predictions", {
            "version": "fb8af171cfa1616ddcf1242c093f9c46bcada9ad",
            "input": {"image": image_url}
        })
        result = _finish(pred)
        out = result.get("output") or []
        return str(out[0] if isinstance(out, list) else out)
    except Exception as e1:
        print(f"      rembg primary failed ({e1}), trying fallback ...", flush=True)

    # Fallback: 851-labs model via model-level predictions API
    pred = _post("/models/851-labs/background-removal/predictions",
                 {"input": {"image": image_url}})
    result = _finish(pred)
    out = result.get("output") or []
    return str(out[0] if isinstance(out, list) else out)


def with_retry(fn, label: str, max_tries: int = 5):
    for attempt in range(max_tries):
        try:
            return fn()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429 and attempt < max_tries - 1:
                wait = 25 * (attempt + 1)
                print(f"      rate-limited, waiting {wait}s ...", flush=True)
                time.sleep(wait)
            else:
                raise
        except Exception as e:
            if attempt < max_tries - 1:
                print(f"      error ({e}), retrying ...", flush=True)
                time.sleep(10)
            else:
                raise
    raise RuntimeError(f"{label}: all retries exhausted")

# ---------------------------------------------------------------------------
# Style strings
# ---------------------------------------------------------------------------

_FE = (
    "fire emblem fates art style, anime game character portrait, half body bust, "
    "cel-shaded illustration with clean precise black linework, "
    "large expressive anime eyes with multi-tone iris and bright catchlight, "
    "richly detailed fantasy costume, smooth colour gradients, "
    "professional game character portrait, vibrant colours"
)

_UO_S = (
    "unicorn overlord art style, japanese tactical RPG, painterly anime sprite, "
    "rich vibrant medieval fantasy, detailed armour and costume, "
    "full body character, isolated on solid white background, "
    "clean cut-out edges, professional game asset, no background"
)

_UO_E = (
    "unicorn overlord map asset, tactical RPG, painterly medieval fantasy, "
    "rich vibrant colours, detailed, isolated on solid white background, "
    "clean edges, professional game environment asset, no background"
)

# ---------------------------------------------------------------------------
# Asset manifest
# ---------------------------------------------------------------------------

ASSETS = [

    # ── Portraits  (regen with FE style reference) ──────────────────────────
    dict(
        id="kairu",    dir="portrait", regen=True,
        label="Portrait — Kairu",
        prompt=f"Young male hero, short spiky teal-blue hair with silver tips, "
               f"bright glowing teal eyes, white and teal fantasy plate armour with gold ornaments, "
               f"determined heroic expression, dark starlit background. {_FE}",
        ref=REF_FE, strength=0.80, ratio="2:3", removebg=False,
    ),
    dict(
        id="elder_mira",  dir="portrait", regen=True,
        label="Portrait — Elder Mira",
        prompt=f"Elderly female sage, long silver-white hair with golden moon pins, "
               f"wise violet eyes, deep kind wrinkles, dark indigo ceremonial robes "
               f"with gold crescent-moon embroidery, serene expression, warm candlelit interior. {_FE}",
        ref=REF_FE, strength=0.80, ratio="2:3", removebg=False,
    ),
    dict(
        id="blacksmith",  dir="portrait", regen=True,
        label="Portrait — Blacksmith",
        prompt=f"Stocky middle-aged male blacksmith, short messy brown hair, amber eyes, "
               f"neatly trimmed beard, dark leather apron over rolled-sleeve linen shirt, "
               f"muscular forearms, gruff friendly expression, warm forge-light background. {_FE}",
        ref=REF_FE, strength=0.80, ratio="2:3", removebg=False,
    ),
    dict(
        id="shadow_lurker", dir="portrait", regen=True,
        label="Portrait — Shadow Lurker",
        prompt=f"Dark shadow demon villain, swirling black and deep-purple smoke body, "
               f"malevolent glowing yellow slit eyes, dark spectral robes with purple tendrils, "
               f"sinister sneer, ominous void background. {_FE}",
        ref=REF_FE, strength=0.80, ratio="2:3", removebg=False,
    ),

    # ── Map sprites  (UO map reference) ────────────────────────────────────
    dict(
        id="kairu",     dir="map", regen=False,
        label="Map Sprite — Kairu",
        prompt=f"Young male hero in white and teal fantasy plate armour, sword at side, "
               f"neutral standing pose, full body visible from head to feet. {_UO_S}",
        ref=REF_UO_MAP, strength=0.90, ratio="1:1", removebg=True,
    ),
    dict(
        id="elder_mira", dir="map", regen=False,
        label="Map Sprite — Elder Mira",
        prompt=f"Elderly female mage in dark indigo robes, holding ornate staff, "
               f"gentle standing pose, full body from head to feet. {_UO_S}",
        ref=REF_UO_MAP, strength=0.90, ratio="1:1", removebg=True,
    ),
    dict(
        id="blacksmith", dir="map", regen=False,
        label="Map Sprite — Blacksmith",
        prompt=f"Stocky male blacksmith in leather apron, hammer at side, "
               f"neutral standing pose, full body from head to feet. {_UO_S}",
        ref=REF_UO_MAP, strength=0.90, ratio="1:1", removebg=True,
    ),
    dict(
        id="shadow_lurker", dir="map", regen=False,
        label="Map Sprite — Shadow Lurker",
        prompt=f"Dark shadow enemy creature, glowing yellow eyes, purple energy tendrils, "
               f"menacing standing pose, full body visible from head to feet. {_UO_S}",
        ref=REF_UO_MAP, strength=0.90, ratio="1:1", removebg=True,
    ),

    # ── Battle sprites  (UO battle reference) ──────────────────────────────
    dict(
        id="kairu",     dir="battle", regen=False,
        label="Battle Sprite — Kairu",
        prompt=f"Young hero in white teal armour, side-facing left, sword raised mid-swing, "
               f"dynamic combat stance, full body from head to feet. {_UO_S}",
        ref=REF_UO_BTLR, strength=0.88, ratio="2:3", removebg=True,
    ),
    dict(
        id="shadow_lurker", dir="battle", regen=False,
        label="Battle Sprite — Shadow Lurker",
        prompt=f"Dark shadow creature, side-facing right, claws lunging forward, "
               f"glowing yellow eyes, purple energy, dynamic attack pose, full body. {_UO_S}",
        ref=REF_UO_BTLR, strength=0.88, ratio="2:3", removebg=True,
    ),

    # ── Environment  (UO map reference) ────────────────────────────────────
    dict(
        id="oak_tree", dir="environment", regen=False,
        label="Environment — Oak Tree",
        prompt=f"Single large lush oak tree, full round green canopy, "
               f"thick brown trunk, painterly medieval fantasy style. {_UO_E}",
        ref=REF_UO_MAP, strength=0.88, ratio="1:1", removebg=True,
    ),
    dict(
        id="pine_cluster", dir="environment", regen=False,
        label="Environment — Pine Cluster",
        prompt=f"Cluster of three dark-green pine trees, tall pointed conifers, "
               f"dense foliage, forest edge. {_UO_E}",
        ref=REF_UO_MAP, strength=0.88, ratio="1:1", removebg=True,
    ),
    dict(
        id="village_house", dir="environment", regen=False,
        label="Environment — Village House",
        prompt=f"Medieval fantasy village house, stone walls, warm orange tiled roof, "
               f"arched wooden door, cozy quaint architecture, slightly elevated front view. {_UO_E}",
        ref=REF_UO_MAP, strength=0.88, ratio="1:1", removebg=True,
    ),
    dict(
        id="castle_tower", dir="environment", regen=False,
        label="Environment — Castle Tower",
        prompt=f"Medieval stone castle tower with battlements, "
               f"red-tiled conical roof, narrow windows, imposing fortress architecture. {_UO_E}",
        ref=REF_UO_MAP, strength=0.88, ratio="1:1", removebg=True,
    ),
    dict(
        id="blacksmith_forge", dir="environment", regen=False,
        label="Environment — Blacksmith Forge",
        prompt=f"Medieval blacksmith forge building, stone and timber construction, "
               f"chimney with wisps of smoke, warm orange glow from forge fire, "
               f"tools hanging outside, workshop aesthetic. {_UO_E}",
        ref=REF_UO_MAP, strength=0.88, ratio="1:1", removebg=True,
    ),
]

# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_asset(a: dict) -> bool:
    out_path = DIRS[a["dir"]] / f"{a['id']}.png"

    # Skip existing unless forced regen
    if out_path.exists() and not a.get("regen", False):
        print(f"  [{a['label']}] exists - skipping")
        return True

    print(f"  [{a['label']}] generating ...", flush=True)

    try:
        # 1. Generate
        gen_url = with_retry(
            lambda: flux_generate(a["prompt"], a["ratio"], a.get("ref"), a.get("strength", 0.88)),
            a["label"]
        )
        print(f"      generated OK", flush=True)

        # 2. Remove background (sprites/env only)
        if a.get("removebg"):
            print(f"      removing background ...", flush=True)
            try:
                final_url = with_retry(lambda: remove_bg(gen_url), a["label"] + " rembg")
                print(f"      bg removed OK", flush=True)
            except Exception as rmbg_err:
                print(f"      bg removal failed ({rmbg_err}), saving without bg removal", flush=True)
                final_url = gen_url
        else:
            final_url = gen_url

        # 3. Download
        _download(final_url, out_path)
        print(f"  [{a['label']}] SAVED -> {out_path.relative_to(BASE)}")
        return True

    except Exception as e:
        print(f"  [{a['label']}] FAILED: {e}")
        return False


if __name__ == "__main__":
    print(f"\nShattered Realm - Full Asset Generator")
    print(f"Total assets: {len(ASSETS)}\n")

    ok = 0
    for i, asset in enumerate(ASSETS):
        if i > 0:
            time.sleep(6)   # gentle pacing between requests
        if run_asset(asset):
            ok += 1

    print(f"\n{ok}/{len(ASSETS)} assets generated.")
    if ok == len(ASSETS):
        print("All done. Launch the game - new art loads automatically.")
    else:
        print("Some assets failed. Run again to retry (existing files are skipped).")
