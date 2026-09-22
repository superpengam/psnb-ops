from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"


def main() -> int:
    text = SKILL.read_text(encoding="utf-8")
    lines = text.count("\n") + (0 if text.endswith("\n") else 1)
    errs = []
    if lines > 160:
        errs.append(f"SKILL.md too long: {lines}")
    if "name: psnb-ops" not in text:
        errs.append("missing name")
    if "大风起兮云飞扬." not in text:
        errs.append("missing ping line")
    refs = {p.stem for p in (ROOT / "references").glob("*.md")}
    route = (ROOT / "scripts" / "route.py").read_text(encoding="utf-8")
    wanted = set(re.findall(r"references/([a-z0-9-]+)\.md", route))
    missing = sorted(wanted - refs)
    if missing:
        errs.append("route refs missing: " + ",".join(missing))
    secret = re.compile(r"(ghp_[A-Za-z0-9]{20,}|sk-ant-|AKIA[0-9A-Z]{16}|xox[baprs]-)")
    for p in ROOT.rglob("*"):
        if not p.is_file() or ".git" in p.parts or p.suffix in {".pyc"}:
            continue
        if p.name in {"check.py", "extract.py"}:
            continue
        blob = p.read_text(encoding="utf-8", errors="ignore")
        if secret.search(blob):
            errs.append(f"secret-like token in {p.relative_to(ROOT)}")
    if errs:
        print("FAIL")
        for e in errs:
            print(e)
        return 1
    print(f"ok lines={lines} refs={len(refs)} route={len(wanted)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
