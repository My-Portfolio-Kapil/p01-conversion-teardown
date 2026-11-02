"""Capture full-page screenshots for the eval set.

Reads evals/urls.csv (id,url,device) and writes evals/screenshots/<id>.png.

Usage:
    python scripts/capture_screenshots.py                 # all rows
    python scripts/capture_screenshots.py E03 E04         # only these ids
    python scripts/capture_screenshots.py --headed E09    # visible browser
"""

import argparse
import csv
import re
import sys
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
URLS_CSV = ROOT / "evals" / "urls.csv"
OUT_DIR = ROOT / "evals" / "screenshots"

DESKTOP_VIEWPORT = {"width": 1440, "height": 900}
MOBILE_DEVICE = "iPhone 13"
MOBILE_SCALE = 2  # the device default of 3 pushes tall pages past Chromium's 16384 px limit
LOCALE = "de-DE"
TIMEZONE = "Europe/Berlin"

# Matches "Alle akzeptieren", "Alle annehmen", "Alle Cookies und Tracking akzeptieren", "Zustimmen", "OK", ...
# but not "Nur notwendige akzeptieren" or "Ablehnen".
COOKIE_BUTTONS = re.compile(
    r"^(?!.*(nur|notwendig|ablehn|nicht|reject|necessary))"
    r"(.*(akzeptieren|annehmen|zulassen|zustimmen|accept all).*|\s*ok\s*)$",
    re.IGNORECASE | re.DOTALL,
)
MAX_SCROLL = 20000  # stop scrolling on endless feeds


def accept_cookies(page, wait_ms: int = 6000) -> bool:
    """Click the first cookie-consent button found in the page or its iframes.

    Banners often render a few seconds after load, so keep looking for wait_ms.
    """
    waited = 0
    while True:
        for frame in page.frames:
            # match on the accessible name (aria-label) and on the visible text
            for locator in (
                frame.get_by_role("button", name=COOKIE_BUTTONS),
                frame.locator("button", has_text=COOKIE_BUTTONS),
            ):
                try:
                    for i in range(locator.count()):
                        button = locator.nth(i)
                        if button.is_visible():
                            button.click(timeout=3000)
                            return True
                except PlaywrightError:
                    continue
        if waited >= wait_ms:
            return False
        page.wait_for_timeout(500)
        waited += 500


def scroll_through(page) -> None:
    """Scroll to the bottom in steps (so lazy images load), then back up."""
    height = page.evaluate("window.innerHeight")
    y = 0
    while y < MAX_SCROLL:
        y += height
        page.evaluate(f"window.scrollTo(0, {y})")
        page.wait_for_timeout(300)
        if y >= page.evaluate("document.documentElement.scrollHeight"):
            break
    page.wait_for_timeout(500)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(500)


def context_options(playwright, device: str) -> dict:
    if device == "mobile":
        options = dict(playwright.devices[MOBILE_DEVICE])
        options["device_scale_factor"] = MOBILE_SCALE
    else:
        options = {"viewport": DESKTOP_VIEWPORT}
    options.update(locale=LOCALE, timezone_id=TIMEZONE)
    return options


def capture(playwright, row: dict, headless: bool) -> Path:
    browser = playwright.chromium.launch(headless=headless)
    try:
        context = browser.new_context(**context_options(playwright, row["device"]))
        page = context.new_page()
        response = page.goto(row["url"], wait_until="domcontentloaded", timeout=45000)
        try:
            page.wait_for_load_state("load", timeout=15000)
        except PlaywrightError:
            pass  # ad-heavy pages may never fire "load"; carry on with what is there
        # Cloudflare-style interstitials clear themselves after a few seconds (if at all)
        for _ in range(10):
            if not re.search(r"einen moment|just a moment", page.title(), re.IGNORECASE):
                break
            page.wait_for_timeout(1500)
        if response is not None and response.status >= 400:
            raise RuntimeError(f"HTTP {response.status}")
        accept_cookies(page)
        page.wait_for_timeout(2000)
        scroll_through(page)
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUT_DIR / f"{row['id']}.png"
        page.screenshot(path=str(path), full_page=True)
        return path
    finally:
        browser.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ids", nargs="*", help="only capture these ids (default: all)")
    parser.add_argument("--headed", action="store_true", help="show the browser window")
    args = parser.parse_args()

    with URLS_CSV.open(newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if not args.ids or r["id"] in args.ids]

    failed = 0
    with sync_playwright() as playwright:
        for row in rows:
            try:
                path = capture(playwright, row, headless=not args.headed)
                print(f"OK    {row['id']} {row['device']:7} {path.relative_to(ROOT)}")
            except Exception as exc:  # keep going on any error
                failed += 1
                print(f"FAIL  {row['id']} {row['device']:7} {row['url']} ({str(exc).splitlines()[0]})")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
