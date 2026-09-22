from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import HUNT, http  # noqa: E402

PATTERNS = [
    ("aws_ak", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("github_pat", re.compile(r"ghp_[A-Za-z0-9]{20,}")),
    ("github_fine", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("gitlab_pat", re.compile(r"glpat-[A-Za-z0-9\-_]{20,}")),
    ("slack", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("openai", re.compile(r"sk-(?:proj-|live-)?[A-Za-z0-9]{20,}")),
    ("xai", re.compile(r"xai-[A-Za-z0-9]{20,}")),
    ("anthropic", re.compile(r"sk-ant-[A-Za-z0-9\-_]{20,}")),
    ("google_api", re.compile(r"AIza[0-9A-Za-z\-_]{32,}")),
    ("telegram", re.compile(r"\d{8,10}:[A-Za-z0-9_-]{30,}")),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----")),
    ("jwt", re.compile(r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")),
    ("password_assign", re.compile(r"(?i)(password|passwd|pwd|secret|token|api[_-]?key)\s*[:=]\s*['\"][^'\"]{4,}['\"]")),
]

DIR_HINTS = ("Index of /", "Directory listing for /", "Parent Directory", "<title>Index of")


def walk_text_files(root: Path) -> list[Path]:
    out = []
    if not root.exists():
        return out
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".json", ".jsonl", ".txt", ".html", ".md", ".env", ".yml", ".yaml", ".csv"}:
            if p.stat().st_size <= 8_000_000:
                out.append(p)
    return out


def extract_text(text: str, source: str) -> list[dict]:
    hits = []
    for name, rx in PATTERNS:
        for m in rx.finditer(text or ""):
            val = m.group(0)
            hits.append({"type": name, "value": val, "source": source})
    return hits


def probe_dirs(hosts: list[str], limit: int = 40) -> list[dict]:
    rows = []
    for host in hosts[:limit]:
        for scheme in ("https", "http"):
            url = f"{scheme}://{host}/"
            code, body = http(url, timeout=8)
            listing = any(h in (body or "") for h in DIR_HINTS)
            rows.append({"url": url, "status": code, "listing": listing, "len": len(body or "")})
            if code and code < 500:
                break
    return rows


def main() -> int:
    p = argparse.ArgumentParser(prog="extract.py")
    p.add_argument("root", nargs="?", default=str(HUNT))
    p.add_argument("--probe", action="store_true")
    args = p.parse_args()
    root = Path(args.root)
    hits: list[dict] = []
    for f in walk_text_files(root):
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        hits.extend(extract_text(text, str(f)))

    hosts_file = root / "unique_hosts.txt"
    hosts = hosts_file.read_text(encoding="utf-8").splitlines() if hosts_file.exists() else []
    listings = probe_dirs(hosts) if args.probe and hosts else []

    out_json = root / "found_keys.json"
    out_csv = root / "found_keys.csv"
    uniq = []
    seen = set()
    for h in hits:
        k = (h["type"], h["value"])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(h)
    out_json.write_text(json.dumps({"count": len(uniq), "items": uniq, "listings": listings}, ensure_ascii=False, indent=2), encoding="utf-8")
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["type", "value", "source"])
        w.writeheader()
        for row in uniq:
            w.writerow(row)
    print(json.dumps({"keys": len(uniq), "listings": sum(1 for x in listings if x.get("listing")), "out": str(out_json)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
