from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", "hunt", "cases"}
CODE_EXT = {".py", ".js", ".ts", ".go", ".rs", ".java", ".c", ".cc", ".cpp", ".h", ".rb", ".php", ".cs"}
SINK_RE = re.compile(
    r"(eval|exec|pickle\.loads|yaml\.load|subprocess|os\.system|innerHTML|dangerouslySetInnerHTML|"
    r"copy\(|memcpy\(|strcpy\(|system\(|popen\(|Runtime\.getRuntime|"
    r"jwt\.decode|unserialize|deserialize|child_process)",
    re.I,
)
ENTRY_RE = re.compile(r"(app\.(get|post|put|delete)|router\.|@app\.|fastapi|express\(|flask|gin\.|http\.Handle)", re.I)


def main() -> int:
    p = argparse.ArgumentParser(prog="index.py")
    p.add_argument("root")
    p.add_argument("--out", default="")
    args = p.parse_args()
    root = Path(args.root).resolve()
    files = []
    sinks = []
    entries = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP for part in path.parts):
            continue
        if path.suffix.lower() not in CODE_EXT:
            continue
        if path.stat().st_size > 400_000:
            continue
        rel = str(path.relative_to(root)).replace("\\", "/")
        files.append(rel)
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if SINK_RE.search(line):
                sinks.append({"file": rel, "line": i, "text": line.strip()[:160]})
            if ENTRY_RE.search(line):
                entries.append({"file": rel, "line": i, "text": line.strip()[:160]})
    obj = {
        "root": str(root),
        "files": len(files),
        "sinks": sinks[:400],
        "entries": entries[:400],
        "sample_files": files[:200],
    }
    out = Path(args.out) if args.out else (root / "psnb-index.json")
    out.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"files": obj["files"], "sinks": len(sinks), "entries": len(entries), "out": str(out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
