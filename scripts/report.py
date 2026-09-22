from __future__ import annotations

import argparse
import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import HUNT  # noqa: E402


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def main() -> int:
    p = argparse.ArgumentParser(prog="report.py")
    p.add_argument("--out", default=str(HUNT / "hunt_report.html"))
    args = p.parse_args()
    hosts = []
    uf = HUNT / "unique_hosts.txt"
    if uf.exists():
        hosts = [x for x in uf.read_text(encoding="utf-8").splitlines() if x.strip()]
    keys = load_json(HUNT / "found_keys.json", {"count": 0, "items": [], "listings": []})
    merged = load_json(HUNT / "merged.json", {})
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    key_rows = "".join(
        f"<tr><td>{html.escape(i.get('type',''))}</td><td><code>{html.escape((i.get('value') or '')[:24])}…</code></td><td>{html.escape(str(i.get('source','')))}</td></tr>"
        for i in (keys.get("items") or [])[:200]
    )
    host_rows = "".join(f"<li>{html.escape(h)}</li>" for h in hosts[:300])
    listing_n = sum(1 for x in (keys.get("listings") or []) if x.get("listing"))
    page = f"""<!doctype html><html lang="zh"><meta charset="utf-8">
<title>psnb-ops hunt report</title>
<style>
body{{font:14px/1.45 system-ui,sans-serif;max-width:960px;margin:32px auto;color:#111}}
h1{{font-size:22px}} table{{border-collapse:collapse;width:100%}}
td,th{{border-bottom:1px solid #ddd;text-align:left;padding:6px}}
.k{{display:flex;gap:16px}} .card{{border:1px solid #eee;padding:12px 16px;border-radius:8px}}
code{{font-size:12px}}
</style>
<h1>psnb-ops hunt</h1>
<p>{html.escape(ts)}</p>
<div class="k">
<div class="card">hosts {len(hosts)}</div>
<div class="card">keys {keys.get('count') or 0}</div>
<div class="card">listings {listing_n}</div>
<div class="card">merged {merged.get('count') or 0}</div>
</div>
<h2>hosts</h2><ul>{host_rows or '<li>none</li>'}</ul>
<h2>extracted (masked)</h2>
<table><tr><th>type</th><th>value</th><th>source</th></tr>{key_rows or '<tr><td colspan=3>none</td></tr>'}</table>
</html>"""
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
