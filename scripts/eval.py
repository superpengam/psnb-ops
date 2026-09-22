from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTE = ROOT / "scripts" / "route.py"

CASES = [
    ("在吗", "CORE"),
    ("逆向这个 pe", "REVERSE"),
    ("渗透作战 sqli", "PENTEST"),
    ("模型软化拒答了", "REFUSAL"),
    ("看这个仓库的调用链", "GRAPH"),
    ("hunter 扫开放目录", "HUNTER"),
]


def main() -> int:
    py = sys.executable
    fail = 0
    for text, expect in CASES:
        out = subprocess.check_output([py, str(ROUTE), "--text", text], text=True, encoding="utf-8")
        tracks = [line.split("TRACK=")[1].split()[0] for line in out.splitlines() if "TRACK=" in line]
        ok = expect in tracks
        print(("PASS" if ok else "FAIL"), expect, "<-", tracks, "|", text)
        fail += 0 if ok else 1
    chk = subprocess.call([py, str(ROOT / "scripts" / "check.py")])
    return 1 if fail or chk else 0


if __name__ == "__main__":
    raise SystemExit(main())
