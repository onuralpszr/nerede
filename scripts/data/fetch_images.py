"""Download one freely licensed photo per place from Wikimedia Commons, with attribution.

Takes the lead image of each place's Wikipedia article (wiki_en, else wiki_tr), checks the
Commons license (CC0, CC BY, CC BY-SA, Free Art License or public domain only), resizes to 800 px wide and writes
data/images/<id>.jpg, data/images.jsonl and data/images/ATTRIBUTION.md.

    uv run scripts/data/fetch_images.py            # skips photos that already exist
    uv run scripts/data/fetch_images.py --refresh
"""

import argparse
import html
import io
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "images"
UA = "nerede-workshop/0.1 (GDG DevFest Istanbul 2026 workshop; thunderbirdtr@gmail.com)"
# Where the article's lead image is a logo, use a real photo instead.
OVERRIDES = {
    "pera-muzesi": "Osman Hamdi Bey - The Tortoise Trainer - Google Art Project.jpg",
    "marmaray": "Marmaray-TCDD E32000 @ Sirkeci, Istanbul Turkey 2024 (1).jpg",
}
FREE = re.compile(r"^(cc0|cc[ -]by(-sa)?([ -][\d.]+)?|public domain|pd(-\w+)*|fal|free art licen[cs]e)", re.I)


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def lead_image(title: str, lang: str) -> str | None:
    q = urllib.parse.urlencode({"action": "query", "prop": "pageimages", "piprop": "name", "pilicense": "free",
                                "titles": title, "redirects": 1, "format": "json"})
    pages = get_json(f"https://{lang}.wikipedia.org/w/api.php?{q}")["query"]["pages"]
    return next(iter(pages.values())).get("pageimage")


def commons_info(name: str) -> dict | None:
    q = urllib.parse.urlencode({"action": "query", "titles": f"File:{name}", "prop": "imageinfo",
                                "iiprop": "url|extmetadata|mime", "iiurlwidth": 800, "format": "json"})
    page = next(iter(get_json(f"https://commons.wikimedia.org/w/api.php?{q}")["query"]["pages"].values()))
    if "imageinfo" not in page:
        return None  # file lives on a local wiki only, usually non-free
    info = page["imageinfo"][0]
    meta = {k: v.get("value", "") for k, v in info.get("extmetadata", {}).items()}
    plain = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()  # noqa: E731
    return {"url": info.get("thumburl") or info["url"], "mime": info.get("mime", ""),
            "source": info["descriptionurl"], "license": plain(meta.get("LicenseShortName")),
            "license_url": meta.get("LicenseUrl", ""), "author": plain(meta.get("Artist")) or "unknown"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    places = [json.loads(line) for line in (ROOT / "data/istanbul.jsonl").read_text().splitlines() if line]
    old = {}
    if (ROOT / "data/images.jsonl").exists():
        old = {r["id"]: r for r in map(json.loads, (ROOT / "data/images.jsonl").read_text().splitlines()) if r}

    records, skipped = [], []
    for p in places:
        target = OUT / f"{p['id']}.jpg"
        if p["id"] in old and target.exists() and not args.refresh:
            records.append(old[p["id"]])
            continue
        name = OVERRIDES.get(p["id"])
        for lang in ("en", "tr") if not name else ():
            title = p.get(f"wiki_{lang}")
            if title and (name := lead_image(title, lang)):
                break
        info = commons_info(name) if name else None
        if not info or not FREE.match(info["license"]) or not info["mime"].startswith("image/"):
            skipped.append((p["id"], name, info and info["license"]))
            continue
        req = urllib.request.Request(info["url"], headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            img = Image.open(io.BytesIO(r.read())).convert("RGB")
        img.thumbnail((800, 800))
        img.save(target, "JPEG", quality=80, optimize=True, progressive=True)
        records.append({"id": p["id"], "file": target.name, "title": p["title"], "author": info["author"][:200],
                        "license": info["license"], "license_url": info["license_url"], "source": info["source"]})
        print(f"ok    {p['id']:<24} {info['license']:<14} {target.stat().st_size // 1024} KB")
        time.sleep(0.3)  # be polite to Wikimedia

    (ROOT / "data/images.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8")
    rows = "\n".join(f"| {r['file']} | {r['title']} | {r['author']} | [{r['license']}]({r['license_url'] or r['source']}) "
                     f"| [Commons]({r['source']}) |" for r in records)
    (OUT / "ATTRIBUTION.md").write_text(
        "# Photo credits\n\nAll photos come from Wikimedia Commons under the licenses below and were resized "
        "to 800 px. Click through to the file page for full details.\n\n"
        "| File | Place | Author | License | Source |\n|---|---|---|---|---|\n" + rows + "\n", encoding="utf-8")
    for pid, name, lic in skipped:
        print(f"skip  {pid:<24} {name or 'no lead image'} {lic or ''}")
    print(f"\n{len(records)} photos, {len(skipped)} skipped")


if __name__ == "__main__":
    main()
