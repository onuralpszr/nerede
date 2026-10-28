"""Build the docs in English and Turkish (and optionally the static demo) into site/.

uv run --group docs scripts/docs/build_docs.py                     # site/en, site/tr, site/index.html
uv run --group docs scripts/docs/build_docs.py --with-demo         # + site/demo (browser-only search, no server)
uv run --group docs scripts/docs/build_docs.py --base /nerede/     # for GitHub project pages: user.github.io/nerede/
uv run --group docs scripts/docs/build_docs.py --serve             # build, then serve site/ on http://127.0.0.1:8001 (the app uses 8000)
"""

import argparse
import functools
import hashlib
import http.server
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
LANGS = {"en": "zensical.toml", "tr": "zensical.tr.toml"}

REDIRECT = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Nerede?</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>location.replace((navigator.language || "en").toLowerCase().startsWith("tr") ? "tr/" : "en/");</script>
<style>body{{font:18px system-ui;background:#f1f1ee;color:#14213d;display:grid;place-items:center;min-height:90vh}}
a{{color:#2257b5;margin:0 .6em}}</style></head>
<body><p><a href="en/">English</a> · <a href="tr/">Türkçe</a>{demo}</p></body></html>
"""


def build(lang: str, config: str, base: str, site_url: str | None) -> None:
    text = (ROOT / config).read_text(encoding="utf-8")
    text = re.sub(r'link = "/(en|tr)/"', lambda m: f'link = "{base}{m.group(1)}/"', text)
    text = text.replace('= "/demo/"', f'= "{base}demo/"')  # nav link to the browser demo
    if site_url:
        text = re.sub(r'^site_url = ".*"$', f'site_url = "{site_url.rstrip("/")}/{lang}/"', text, flags=re.M)
    tmp = ROOT / f".zensical.{lang}.build.toml"  # must sit next to the real config: paths are relative to it
    tmp.write_text(text, encoding="utf-8")
    try:
        subprocess.run([sys.executable, "-m", "zensical", "build", "--clean", "-f", str(tmp)], cwd=ROOT, check=True)
    finally:
        tmp.unlink()


def stamp(demo: Path) -> None:
    """Add a content hash to the CSS and JS links (style.css?v=1a2b3c4d). GitHub Pages lets browsers cache every
    file for 10 minutes, so without it a fresh page can run with last deploy's CSS and look broken."""
    page = demo / "index.html"
    html = page.read_text(encoding="utf-8")
    for name in ("style.css", "app.js"):
        digest = hashlib.sha256((demo / name).read_bytes()).hexdigest()[:8]
        html = html.replace(f'"{name}"', f'"{name}?v={digest}"')
    page.write_text(html, encoding="utf-8")


def copy_demo() -> None:
    demo = SITE / "demo"
    shutil.copytree(ROOT / "app" / "static", demo, dirs_exist_ok=True)
    if not (demo / "index.json").exists():
        sys.exit("app/static/index.json is missing: run workshop/02_build_index.py first")
    shutil.copytree(ROOT / "data" / "images", demo / "images", dirs_exist_ok=True)
    stamp(demo)
    print(f"demo -> {demo.relative_to(ROOT)} (browser-only: it has no /api, so the page runs the model itself)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8001, help="port for --serve; the app uses 8000")
    parser.add_argument("--base", default="/", help="URL path the site is served from, e.g. /nerede/")
    parser.add_argument("--site-url", default=None, help="full URL, e.g. https://you.github.io/nerede")
    parser.add_argument("--with-demo", action="store_true")
    parser.add_argument("--serve", action="store_true")
    args = parser.parse_args()
    base = "/" + args.base.strip("/") + "/" if args.base.strip("/") else "/"

    if SITE.exists():
        shutil.rmtree(SITE)
    for lang, config in LANGS.items():
        build(lang, config, base, args.site_url)
    if args.with_demo:
        copy_demo()
    demo_link = ' · <a href="demo/">Demo</a>' if args.with_demo else ""
    (SITE / "index.html").write_text(REDIRECT.format(demo=demo_link), encoding="utf-8")
    (SITE / ".nojekyll").touch()
    print(f"site -> {SITE.relative_to(ROOT)}/ (en, tr{', demo' if args.with_demo else ''})")

    if args.serve:
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=SITE)
        print(f"serving on http://127.0.0.1:{args.port}")
        http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler).serve_forever()


if __name__ == "__main__":
    main()
