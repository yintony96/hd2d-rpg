# generate_portraits.py
# Usage: python generate_portraits.py YOUR_API_TOKEN

import sys, os, time, pathlib
import httpx

TOKEN = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("REPLICATE_API_TOKEN", "")
if not TOKEN:
    print("ERROR: No API token.\nUsage: python generate_portraits.py r8_YOUR_TOKEN")
    sys.exit(1)

OUT_DIR = pathlib.Path(__file__).parent / "assets" / "portraits"
OUT_DIR.mkdir(parents=True, exist_ok=True)

STYLE = (
    "fire emblem three houses art style, anime portrait, half body bust, "
    "cel-shaded illustration, clean black linework, soft dramatic lighting, "
    "highly detailed costume, game character portrait, professional quality"
)

CHARACTERS = [
    {
        "id":    "kairu",
        "label": "Kairu (Player)",
        "prompt": (
            "Young male hero protagonist, short spiky teal-blue hair with silver tips, "
            "bright glowing teal eyes, wearing elegant white and teal fantasy plate armor "
            "with gold trim and sapphire gems, confident determined expression, "
            f"dark atmospheric blue starlight background. {STYLE}"
        ),
    },
    {
        "id":    "elder_mira",
        "label": "Elder Mira",
        "prompt": (
            "Elderly female village sage, long silver-white hair pinned with golden moon ornaments, "
            "gentle wise violet eyes, deep wrinkles of wisdom, "
            "wearing dark indigo ceremonial robes with gold crescent moon embroidery, "
            f"serene knowing smile, warm candlelit background. {STYLE}"
        ),
    },
    {
        "id":    "blacksmith",
        "label": "Blacksmith",
        "prompt": (
            "Stocky middle-aged male blacksmith, short messy brown hair, "
            "amber eyes, neatly trimmed beard, strong jaw, "
            "wearing dark leather apron over rolled-sleeve shirt, "
            "muscular arms, gruff but good-natured expression, "
            f"warm orange forge-glow background. {STYLE}"
        ),
    },
    {
        "id":    "shadow_lurker",
        "label": "Shadow Lurker (Enemy)",
        "prompt": (
            "Dark shadow entity villain, swirling black and deep purple smoke body, "
            "malevolent glowing yellow slit eyes, dark spectral robes with purple energy tendrils, "
            "menacing sinister sneer, dark purple crackling aura, "
            f"ominous black void background with wisps of dark energy. {STYLE}"
        ),
    },
]

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type":  "application/json",
    "Prefer":        "wait",
}
BASE = "https://api.replicate.com/v1"


def create_prediction(prompt):
    r = httpx.post(
        f"{BASE}/models/black-forest-labs/flux-dev/predictions",
        headers=HEADERS,
        json={"input": {
            "prompt":                 prompt,
            "aspect_ratio":           "2:3",
            "output_format":          "png",
            "output_quality":         95,
            "num_outputs":            1,
            "guidance":               3.5,
            "num_inference_steps":    28,
            "disable_safety_checker": True,
        }},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


def poll(pred_id, timeout=300):
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = httpx.get(f"{BASE}/predictions/{pred_id}", headers=HEADERS, timeout=30)
        r.raise_for_status()
        pred = r.json()
        status = pred.get("status", "")
        if status == "succeeded":
            return pred
        if status in ("failed", "canceled"):
            raise RuntimeError(f"Prediction {status}: {pred.get('error')}")
        print(f"    status: {status} - waiting...", flush=True)
        time.sleep(4)
    raise TimeoutError(f"Timed out after {timeout}s")


def generate(char):
    out_path = OUT_DIR / f"{char['id']}.png"
    if out_path.exists():
        print(f"  [{char['label']}] already exists - skipping")
        return True

    print(f"  [{char['label']}] submitting...", flush=True)
    pred = None
    for attempt in range(5):
        try:
            pred = create_prediction(char["prompt"])
            break
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429 and attempt < 4:
                wait = 20 * (attempt + 1)
                print(f"    rate-limited, waiting {wait}s...", flush=True)
                time.sleep(wait)
            else:
                print(f"  [{char['label']}] FAILED: {e}")
                return False
        except Exception as e:
            print(f"  [{char['label']}] FAILED: {e}")
            return False

    if pred is None:
        print(f"  [{char['label']}] FAILED: all retries exhausted")
        return False

    try:
        if pred.get("status") == "succeeded":
            result = pred
        else:
            pred_id = pred["id"]
            print(f"    prediction id: {pred_id}", flush=True)
            result = poll(pred_id)

        output = result.get("output") or []
        if not output:
            raise ValueError("No output URL returned")

        url = output[0] if isinstance(output, list) else output
        print(f"    downloading...", flush=True)
        r = httpx.get(str(url), timeout=60, follow_redirects=True)
        r.raise_for_status()
        out_path.write_bytes(r.content)
        print(f"  [{char['label']}] SAVED -> {out_path.name}")
        return True

    except Exception as e:
        print(f"  [{char['label']}] FAILED: {e}")
        return False


if __name__ == "__main__":
    print(f"\nShattered Realm - Portrait Generator")
    print(f"Output: {OUT_DIR}\n")
    # Small delay between requests to avoid rate limits
    ok = 0
    for i, char in enumerate(CHARACTERS):
        if i > 0:
            time.sleep(5)
        if generate(char):
            ok += 1
    print(f"\n{ok}/{len(CHARACTERS)} portraits generated.")
    if ok == len(CHARACTERS):
        print("Launch the game - portraits will appear automatically.")
