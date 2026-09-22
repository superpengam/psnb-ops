from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from lib import host_key, normalize_url, slug  # noqa: E402


def test_skill_is_thin():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert text.count("\n") < 160
    assert "name: psnb-ops" in text
    assert "scripts/route.py" in text
    assert "ck-hunter.md" in text


def test_tracks_exist():
    refs = ROOT / "references"
    needed = [
        "reverse", "pwn", "pentest", "protocol", "js-reverse", "memory",
        "forensics", "crypto", "mobile", "network", "hunter", "osint",
        "vuln-research", "remediation", "automation", "constitution",
        "graph", "engineering", "lab", "providers", "catalog", "refusal",
    ]
    for name in needed:
        assert (refs / f"{name}.md").exists(), name


def test_normalize():
    assert host_key("https://A.Example.com:443/x") == "a.example.com"
    assert normalize_url("Example.com/a/") == "http://example.com/a"
    assert slug("https://x.com/a") == "https-x.com-a"


def test_extract_patterns():
    from extract import extract_text
    hits = extract_text("token=sk-live-abcdefghijklmnopqrstuvwxyz password='hunter2x'", "t")
    kinds = {h["type"] for h in hits}
    assert "openai" in kinds or "password_assign" in kinds
