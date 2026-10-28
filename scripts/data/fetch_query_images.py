"""Download query photos for image search: a second, different photo of some places, from Wikimedia Commons.

The index already holds one photo per place (fetch_images.py). These are *other* photos of the same places, so
searching with them is a fair test: the model has never seen this exact picture. Each photo comes from the
place's Commons category (Wikidata P373), with the same free-license check and credits.

    uv run scripts/data/fetch_query_images.py            # skips photos that already exist
    uv run scripts/data/fetch_query_images.py --refresh

Writes data/query_images/<id>.jpg, data/query_images.jsonl and data/query_images/ATTRIBUTION.md.
"""

import argparse
import io
import json
import time
import urllib.parse
import urllib.request

from fetch_images import FREE, ROOT, UA, commons_info, get_json
from PIL import Image

OUT = ROOT / "data" / "query_images"
# Place id -> which free photo to take from its Commons category (0 = the first). Picked by eye from the first
# eight, skipping maps, old prints, distant hazy views and photos of something else.
PLACES = {
    "ayasofya": 3,
    "sultanahmet-camii": 5,
    "galata-kulesi": 4,
    "kiz-kulesi": 1,
    "dolmabahce": 0,
    "rumeli-hisari": 2,
    "yerebatan": 2,
    "kapalicarsi": 0,
    "misir-carsisi": 0,
    "suleymaniye": 0,
    "bogazici-koprusu": 4,
    "galata-koprusu": 0,
    "ortakoy": 4,
    "haydarpasa": 0,
    "bozdogan-kemeri": 0,
    "camlica-kulesi": 0,
    "theodosius-surlari": 1,
    "kediler": 0,
    "simit": 0,
    "baklava": 3,
    "doner": 5,
    "turk-kahvesi": 0,
    "midye-dolma": 0,
    "lokum": 0,
    "kumpir": 5,
    "cay": 0,
    "kunefe": 7,
}
SKIP_WORDS = (
    "map",
    "plan",
    "logo",
    "diagram",
    "drawing",
    "engraving",
    "painting",
    "stamp",
    "coin",
    "banknote",
    "panorama",
    "svg",
    "1890",
    "1900",
    "19th",
    "postcard",
    "interior detail",
)


def commons_category(title: str) -> str | None:
    q = urllib.parse.urlencode(
        {"action": "query", "prop": "pageprops", "titles": title, "redirects": 1, "format": "json"}
    )
    page = next(iter(get_json(f"https://en.wikipedia.org/w/api.php?{q}")["query"]["pages"].values()))
    item = page.get("pageprops", {}).get("wikibase_item")
    if not item:
        return None
    q = urllib.parse.urlencode({"action": "wbgetclaims", "entity": item, "property": "P373", "format": "json"})
    claims = get_json(f"https://www.wikidata.org/w/api.php?{q}").get("claims", {}).get("P373", [])
    return claims[0]["mainsnak"]["datavalue"]["value"] if claims else None


def category_files(category: str, limit: int = 60) -> list[str]:
    q = urllib.parse.urlencode(
        {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": f"Category:{category}",
            "cmtype": "file",
            "cmlimit": limit,
            "format": "json",
        }
    )
    members = get_json(f"https://commons.wikimedia.org/w/api.php?{q}")["query"]["categorymembers"]
    return [m["title"].removeprefix("File:") for m in members]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    places = {p["id"]: p for p in map(json.loads, (ROOT / "data/istanbul.jsonl").read_text().splitlines()) if p}
    indexed = {r["id"]: r for r in map(json.loads, (ROOT / "data/images.jsonl").read_text().splitlines()) if r}
    path = ROOT / "data/query_images.jsonl"
    old = {r["id"]: r for r in map(json.loads, path.read_text().splitlines()) if r} if path.exists() else {}

    records = []
    for pid, pick in PLACES.items():
        target = OUT / f"{pid}.jpg"
        if pid in old and target.exists() and not args.refresh:
            records.append(old[pid])
            continue
        category = commons_category(places[pid]["wiki_en"])
        if not category:
            print(f"skip  {pid:<20} no Commons category")
            continue
        candidates = [
            f
            for f in category_files(category)
            if f.lower().endswith((".jpg", ".jpeg")) and not any(w in f.lower() for w in SKIP_WORDS)
        ]
        found = 0
        for name in candidates:
            info = commons_info(name)
            if not info or not FREE.match(info["license"]) or not info["mime"].startswith("image/"):
                continue
            if found < pick:
                found += 1
                continue
            if info["source"] == indexed.get(pid, {}).get("source"):
                print(f"skip  {pid:<20} pick {pick} is the indexed photo itself, choose another")
                break
            req = urllib.request.Request(info["url"], headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                img = Image.open(io.BytesIO(r.read())).convert("RGB")
            img.thumbnail((800, 800))
            img.save(target, "JPEG", quality=80, optimize=True, progressive=True)
            records.append(
                {
                    "id": pid,
                    "file": target.name,
                    "title": places[pid]["title"],
                    "author": info["author"][:200],
                    "license": info["license"],
                    "license_url": info["license_url"],
                    "source": info["source"],
                }
            )
            print(f"ok    {pid:<20} {name[:60]}")
            break
        else:
            print(f"skip  {pid:<20} nothing free in Category:{category}")
        time.sleep(0.3)  # be polite to Wikimedia

    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8")
    rows = "\n".join(
        f"| {r['file']} | {r['title']} | {r['author']} | [{r['license']}]({r['license_url'] or r['source']}) "
        f"| [Commons]({r['source']}) |"
        for r in records
    )
    (OUT / "ATTRIBUTION.md").write_text(
        "# Query photo credits\n\nPhotos used as image-search queries. All come from Wikimedia Commons under the "
        "licenses below and were resized to 800 px.\n\n"
        "| File | Place | Author | License | Source |\n|---|---|---|---|---|\n" + rows + "\n",
        encoding="utf-8",
    )
    print(f"\n{len(records)} query photos")


if __name__ == "__main__":
    main()
