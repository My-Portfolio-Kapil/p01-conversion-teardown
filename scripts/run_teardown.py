"""Run a CRO teardown on one screenshot with Gemini and prompt v2.

Usage: python scripts/run_teardown.py feasibility/test1.png
"""

import io
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.tiler import tile_image  # noqa: E402

PROMPT_PATH = ROOT / "prompts" / "v2-teardown.md"
OUTPUT_DIR = ROOT / "outputs"
REQUIRED_KEYS = {"page_type", "friction_points", "hypotheses"}


def load_prompt() -> str:
    # The prompt is everything after the first '---' line; above it are notes.
    text = PROMPT_PATH.read_text(encoding="utf-8")
    return text.split("\n---\n", 1)[1].strip()


def to_part(tile: Image.Image) -> types.Part:
    buf = io.BytesIO()
    tile.save(buf, format="JPEG", quality=90)
    return types.Part.from_bytes(data=buf.getvalue(), mime_type="image/jpeg")


def build_contents(prompt: str, tiles) -> list:
    contents = [prompt]
    for i, tile in enumerate(tiles, start=1):
        contents.append(f"Section {i} of {len(tiles)}")
        contents.append(to_part(tile))
    return contents


def parse(text: str):
    """Return the teardown dict, or None if the JSON is invalid."""
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(data, dict) or not REQUIRED_KEYS <= data.keys():
        return None
    return data


def add_ice_scores(teardown: dict) -> None:
    for h in teardown.get("hypotheses", []):
        try:
            h["ice_score"] = round((h["impact"] + h["confidence"] + h["ease"]) / 3, 1)
        except (KeyError, TypeError):
            h["ice_score"] = None
    teardown["hypotheses"].sort(
        key=lambda h: h["ice_score"] if h["ice_score"] is not None else -1,
        reverse=True,
    )


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: python scripts/run_teardown.py <screenshot.png>")
    image_path = Path(sys.argv[1])

    load_dotenv(ROOT / ".env")
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL")
    if not api_key or not model:
        sys.exit("Set GEMINI_API_KEY and GEMINI_MODEL in .env")

    start = time.perf_counter()
    tiles = tile_image(Image.open(image_path))
    contents = build_contents(load_prompt(), tiles)

    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(response_mime_type="application/json")

    teardown = None
    attempts = 0
    for attempts in (1, 2):  # retry once if the JSON is invalid
        response = client.models.generate_content(
            model=model, contents=contents, config=config
        )
        teardown = parse(response.text)
        if teardown is not None:
            break
        print(f"Attempt {attempts}: invalid JSON from the model.")
    if teardown is None:
        sys.exit("Model returned invalid JSON twice; nothing saved.")

    add_ice_scores(teardown)
    elapsed = time.perf_counter() - start

    teardown["_meta"] = {
        "image": str(image_path),
        "model": model,
        "prompt": PROMPT_PATH.name,
        "tiles": len(tiles),
        "attempts": attempts,
        "seconds": round(elapsed, 1),
    }
    OUTPUT_DIR.mkdir(exist_ok=True)
    out_path = OUTPUT_DIR / f"{image_path.stem}.json"
    out_path.write_text(json.dumps(teardown, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Tiles: {len(tiles)}")
    print(f"Time: {elapsed:.1f} s")
    print(f"Saved: {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
