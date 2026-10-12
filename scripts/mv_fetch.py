#!/usr/bin/env python3
"""Fetch the Maldivian legislation database MVLaw (https://mvlaw.gov.mv, Attorney General's Office).

The site is an Inertia.js app: every HTML page embeds its data as JSON in <div id="app" data-page="...">.
1. /dv/legislations?page=N   -> list of all legislations (with latest consolidation URL)
2. latest consolidation page -> sections tree (number, title, content), metadata
Pages are cached under RAW (default ../../_raw/mv).
"""
import html, json, os, re, sys, time
import requests

UA = "LawCodex/1.0 (+https://github.com/LawCodex)"
BASE = "https://mvlaw.gov.mv"
RAW = os.environ.get("RAW", os.path.join(os.path.dirname(__file__), "..", "..", "_raw", "mv"))
S = requests.Session()
S.headers["User-Agent"] = UA


def get(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return open(path, encoding="utf-8").read()
    for attempt in range(5):
        try:
            r = S.get(url, timeout=120)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path + ".part", "w", encoding="utf-8") as f:
                f.write(r.text)
            os.replace(path + ".part", path)
            time.sleep(1.0)
            return r.text
        except Exception as e:
            print("retry", attempt, url, e, file=sys.stderr)
            time.sleep(5 * (attempt + 1))
    return None


def page_data(s):
    m = re.search(r'data-page="([^"]*)"', s)
    return json.loads(html.unescape(m.group(1))) if m else None


def main():
    items = []
    page = 1
    while True:
        s = get(f"{BASE}/dv/legislations?page={page}", f"{RAW}/index/page-{page}.html")
        d = page_data(s)["props"]["legislations"]
        items += d["data"]
        print("page", page, d["last_page"], file=sys.stderr)
        if page >= d["last_page"]:
            break
        page += 1
    json.dump(items, open(f"{RAW}/index.json", "w"), ensure_ascii=False, indent=1)
    for it in items:
        url = it.get("latest_consolidation_url") or it.get("permalink")
        if not url:
            continue
        get(url, f"{RAW}/law/{it['id']}.html")
    print("done", len(items), file=sys.stderr)


if __name__ == "__main__":
    main()
