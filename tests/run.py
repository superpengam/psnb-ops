from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from lib import host_key, normalize_url  # noqa: E402
from extract import extract_text  # noqa: E402


def main() -> None:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    lines = text.count("\n")
    assert lines < 160, lines
    assert "name: psnb-ops" in text
    assert "scripts/route.py" in text
    refs = ROOT / "references"
    needed = [
        "reverse", "pwn", "pentest", "protocol", "js-reverse", "memory",
        "forensics", "crypto", "mobile", "network", "hunter", "osint",
        "vuln-research", "remediation", "automation", "constitution",
        "graph", "engineering", "lab", "providers", "catalog", "refusal", "jev",
    ]
    for name in needed:
        assert (refs / f"{name}.md").exists(), name
    assert host_key("https://A.Example.com:443/x") == "a.example.com"
    assert normalize_url("Example.com/a/") == "http://example.com/a"
    hits = extract_text("token=sk-live-abcdefghijklmnopqrstuvwxyz password='hunter2x'", "t")
    kinds = {h["type"] for h in hits}
    assert "openai" in kinds or "password_assign" in kinds, kinds
    print("ok", "lines", lines, "refs", len(needed), "hits", sorted(kinds))


if __name__ == "__main__":
    main()
