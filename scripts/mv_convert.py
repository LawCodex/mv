#!/usr/bin/env python3
"""Convert cached MVLaw consolidation pages (see mv_fetch.py) into Markdown.

Usage: mv_convert.py [REPO_DIR]
"""
import datetime, html, json, os, re, sys

RAW = os.environ.get("RAW", os.path.join(os.path.dirname(__file__), "..", "..", "_raw", "mv"))
REPO = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..")
RETRIEVED = os.environ.get("RETRIEVED", datetime.date.today().isoformat())


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def clean(s):
    if not s:
        return ""
    s = re.sub(r"\s*\n\s*", " ", s)  # plain newlines are line wraps (rendered as HTML whitespace)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</(p|div|li)>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\xa0", " ")
    lines = [" ".join(l.split()) for l in s.split("\n")]
    return "\n\n".join(l for l in lines if l)


def esc(s):
    s = re.sub(r"([*_`\\])", r"\\\1", s)
    if s.startswith(("#", ">", "- ", "+ ")):
        s = "\\" + s
    return s


def render(nodes, out, depth=0):
    for x in nodes:
        num = clean(x.get("number") or "")
        title = clean(x.get("title") or "")
        content = clean(x.get("content") or "") or clean(x.get("html") or "")
        if title:
            lvl = min(6, 2 + depth)
            out.append("#" * lvl + " " + " ".join(t for t in [num, title] if t))
            if content:
                out.append(esc(content))
        elif content:
            paras = content.split("\n\n")
            first = (num + " " if num else "") + paras[0]
            out.append(esc(first))
            out += [esc(p) for p in paras[1:]]
        elif num:
            out.append(esc(num))
        note = clean(x.get("amendment_note") or "")
        if note:
            out.append("> " + note.replace("\n\n", "\n>\n> "))
        render(x.get("children") or [], out, depth + 1)


def date(s):
    if not s:
        return None
    try:
        # timestamps are UTC midnight-ish values of a Maldives (UTC+5) date
        d = datetime.datetime.fromisoformat(s.replace("Z", "+00:00")) + datetime.timedelta(hours=5)
        return d.date().isoformat()
    except ValueError:
        return None


def main():
    idx = json.load(open(f"{RAW}/index.json"))
    stats = {"written": 0, "no_text": [], "by_kind": {}}
    for it in idx:
        p = f"{RAW}/law/{it['id']}.html"
        if not os.path.exists(p):
            continue
        s = open(p, encoding="utf-8").read()
        m = re.search(r'data-page="([^"]*)"', s)
        if not m:
            continue
        props = json.loads(html.unescape(m.group(1)))["props"]
        leg = props["legislation"]
        out = []
        render(props.get("sections") or [], out)
        cats = [c.get("name", "") for c in leg.get("categories") or []]
        cat_ids = [c.get("id") for c in leg.get("categories") or []]
        if 9 in cat_ids:
            kind, typ = "constitution", "constitution"
        elif 2 in cat_ids or any("ގަވާއިދު" in c for c in cats):
            kind, typ = "regulations", "regulation"
        elif 1 in cat_ids or any(c.startswith("ވޮލިއުމް") for c in cats):
            kind, typ = "laws", "act"
        else:
            kind, typ = "other", "other"
        title = clean(leg.get("title") or "")
        impl = date(leg.get("implemented_at"))
        pub = date(leg.get("published_at"))
        abol = date(leg.get("abolished_at"))
        body = "\n\n".join(out).strip()
        if len(body) < 40:
            stats["no_text"].append({"id": it["id"], "title": title, "pdf": props.get("original_document_url")})
            continue
        year = (impl or pub or "0000")[:4]
        slug = re.sub(r"[^a-z0-9]+", "-", (leg.get("slug") or "").lower()).strip("-")[:80].rstrip("-")
        name = f"{leg['id']}-{slug}" if slug else str(leg["id"])
        rel = f"{kind}/{name}.md" if kind in ("constitution", "other") else f"{kind}/{year}/{name}.md"
        fm = ["---", f"title: {q(title)}"]
        if leg.get("legislation_no"):
            fm.append(f"identifier: {q(clean(leg['legislation_no']))}")
        fm.append(f"mvlaw_id: {leg['id']}")
        fm += [f"type: {typ}", "jurisdiction: mv", "language: dv"]
        if impl:
            fm.append(f"date: {impl}")
        if pub:
            fm.append(f"published: {pub}")
        cons = props.get("consolidation_name") or (leg.get("latest_consolidation") or {}).get("title")
        if cons:
            fm.append(f"consolidation: {q(clean(cons))}")
        fm.append("status: " + ("repealed" if abol else "in_force"))
        if abol:
            fm.append(f"abolished: {abol}")
        if cats:
            fm.append("categories: [" + ", ".join(q(clean(c)) for c in cats) + "]")
        fm.append(f"source: {q(leg.get('latest_consolidation_url') or leg.get('permalink'))}")
        if props.get("original_document_url"):
            fm.append(f"source_pdf: {q(props['original_document_url'])}")
        fm.append(f"retrieved: {RETRIEVED}")
        fm.append("---")
        md = "\n".join(fm) + "\n\n# " + title + "\n\n" + body + "\n"
        path = os.path.join(REPO, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(md)
        stats["written"] += 1
        stats["by_kind"][kind] = stats["by_kind"].get(kind, 0) + 1
    json.dump(stats, open(f"{RAW}/convert-stats.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps({k: (v if not isinstance(v, list) else len(v)) for k, v in stats.items()}))


if __name__ == "__main__":
    main()
