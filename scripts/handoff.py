from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import CASES, slug  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(prog="handoff.py")
    p.add_argument("--target", required=True)
    p.add_argument("--done", default="")
    p.add_argument("--next", dest="nxt", default="")
    p.add_argument("--block", default="")
    args = p.parse_args()
    d = CASES / slug(args.target)
    d.mkdir(parents=True, exist_ok=True)
    notes = []
    nf = d / "notes.jsonl"
    if nf.exists():
        for line in nf.read_text(encoding="utf-8").splitlines()[-12:]:
            try:
                notes.append(json.loads(line).get("text") or "")
            except Exception:
                continue
    body = "\n".join([
        f"# handoff {args.target}",
        f"ts: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## done",
        args.done or "(none)",
        "",
        "## next",
        args.nxt or "(none)",
        "",
        "## blocked",
        args.block or "(none)",
        "",
        "## recent notes",
        *(f"- {n}" for n in notes),
        "",
    ])
    path = d / "HANDOFF.md"
    path.write_text(body, encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
