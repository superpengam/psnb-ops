from __future__ import annotations

import fnmatch
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"


def load_ignores() -> list[str]:
    """读 .gitignore，返回模式列表（忽略注释与空行）。"""
    gi = ROOT / ".gitignore"
    if not gi.exists():
        return []
    pats = []
    for line in gi.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("!"):
            continue
        pats.append(line)
    return pats


def is_ignored(rel: str, name: str, pats: list[str]) -> bool:
    """判断相对路径是否被 .gitignore 覆盖（支持目录名与 glob）。"""
    for pat in pats:
        p = pat.rstrip("/")
        if pat.endswith("/"):
            # 目录模式：任一路径段命中即忽略
            if any(fnmatch.fnmatch(seg, p) for seg in Path(rel).parts[:-1]):
                return True
        if fnmatch.fnmatch(name, p) or fnmatch.fnmatch(rel, p):
            return True
    return False


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
    ignores = load_ignores()
    for p in ROOT.rglob("*"):
        if not p.is_file() or ".git" in p.parts or p.suffix in {".pyc"}:
            continue
        if p.name in {"check.py", "extract.py"}:
            continue
        rel = p.relative_to(ROOT).as_posix()
        # 已 gitignore 的本地文件（config.yaml / .env / hunt/ 等）不参与扫描
        if is_ignored(rel, p.name, ignores):
            continue
        blob = p.read_text(encoding="utf-8", errors="ignore")
        if secret.search(blob):
            errs.append(f"secret-like token in {rel}")
    if errs:
        print("FAIL")
        for e in errs:
            print(e)
        return 1
    print(f"ok lines={lines} refs={len(refs)} route={len(wanted)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
