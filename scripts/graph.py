from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", "hunt", "cases", "target"}
CODE_EXT = {".py", ".js", ".ts", ".tsx", ".go", ".rs", ".java", ".c", ".cc", ".cpp", ".h", ".rb", ".php", ".cs", ".vue", ".svelte"}
DEF_RE = re.compile(r"^\s*(?:export\s+)?(?:async\s+)?(?:def|fn|func|function|class|pub\s+fn|pub\s+struct|interface)\s+([A-Za-z_][\w]*)", re.M)
SINK_RE = re.compile(
    r"(eval|exec|pickle\.loads|yaml\.load|subprocess|os\.system|innerHTML|dangerouslySetInnerHTML|"
    r"strcpy\(|system\(|popen\(|Runtime\.getRuntime|jwt\.decode|unserialize|deserialize|child_process)",
    re.I,
)
ENTRY_RE = re.compile(r"(app\.(get|post|put|delete)|router\.|@app\.|fastapi|express\(|flask|gin\.|http\.Handle|@(Get|Post)Mapping)", re.I)


def files_of(root: Path) -> list[Path]:
    out = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in CODE_EXT:
            continue
        if any(part in SKIP for part in path.parts):
            continue
        if path.stat().st_size > 400_000:
            continue
        out.append(path)
    return out


def main() -> int:
    p = argparse.ArgumentParser(prog="graph.py")
    p.add_argument("root")
    p.add_argument("--symbol", default="")
    p.add_argument("--out", default="")
    args = p.parse_args()
    root = Path(args.root).resolve()
    defs: dict[str, list[dict]] = defaultdict(list)
    sinks, entries, edges = [], [], []
    texts: dict[str, str] = {}
    for path in files_of(root):
        rel = str(path.relative_to(root)).replace("\\", "/")
        text = path.read_text(encoding="utf-8", errors="ignore")
        texts[rel] = text
        for m in DEF_RE.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            defs[m.group(1)].append({"file": rel, "line": line})
        for i, line in enumerate(text.splitlines(), 1):
            if SINK_RE.search(line):
                sinks.append({"file": rel, "line": i, "text": line.strip()[:160]})
            if ENTRY_RE.search(line):
                entries.append({"file": rel, "line": i, "text": line.strip()[:160]})
    if args.symbol:
        name = args.symbol
        callers = []
        rx = re.compile(r"\b" + re.escape(name) + r"\b")
        for rel, text in texts.items():
            for i, line in enumerate(text.splitlines(), 1):
                if rx.search(line):
                    callers.append({"file": rel, "line": i, "text": line.strip()[:160]})
        obj = {"symbol": name, "defs": defs.get(name, [])[:40], "callers": callers[:80]}
    else:
        for name, places in defs.items():
            if len(name) < 3:
                continue
            rx = re.compile(r"\b" + re.escape(name) + r"\s*\(")
            hits = 0
            for rel, text in texts.items():
                hits += len(rx.findall(text))
            if hits:
                edges.append({"symbol": name, "defs": len(places), "call_sites": hits})
        edges.sort(key=lambda x: x["call_sites"], reverse=True)
        obj = {
            "root": str(root),
            "files": len(texts),
            "symbols": len(defs),
            "sinks": sinks[:300],
            "entries": entries[:300],
            "hot": edges[:80],
        }
    out = Path(args.out) if args.out else (root / "psnb-graph.json")
    out.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out), "keys": list(obj)[:6]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
