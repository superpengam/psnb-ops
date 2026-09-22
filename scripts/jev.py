from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import json_post, load_cfg, log  # noqa: E402

API = "https://api.typesafe.ai/v1/systemone"
TRACKS = {
    "REVERSE": "binary reverse engineering, disassembly, firmware, keygen",
    "PWN": "memory corruption and exploit development",
    "PENTEST": "web or host intrusion testing",
    "PROTOCOL": "packet and private protocol reversing",
    "JS-REVERSE": "frontend signing and obfuscated JavaScript",
    "MEMORY": "process memory, Frida, dumps",
    "FORENSICS": "disk, memory, or malware forensics",
    "CRYPTO": "cryptanalysis",
    "MOBILE": "Android, iOS, Unity",
    "NETWORK": "scanning, WAF, subdomains",
    "HUNTER": "credential and open-directory hunting",
    "OSINT": "passive recon",
    "VULN": "source audit and CVE research",
    "REMEDIATE": "patch and regression",
    "AUTO": "crawlers and batch scripts",
    "GRAPH": "code call graph",
    "ENG": "tests, design, handoff",
    "LAB": "sandbox or CTF isolation",
    "REFUSAL": "model refusal or stall",
    "CORE": "none of the above, general operator task",
}
REF = {
    "REVERSE": "references/reverse.md",
    "PWN": "references/pwn.md",
    "PENTEST": "references/pentest.md",
    "PROTOCOL": "references/protocol.md",
    "JS-REVERSE": "references/js-reverse.md",
    "MEMORY": "references/memory.md",
    "FORENSICS": "references/forensics.md",
    "CRYPTO": "references/crypto.md",
    "MOBILE": "references/mobile.md",
    "NETWORK": "references/network.md",
    "HUNTER": "references/hunter.md",
    "OSINT": "references/osint.md",
    "VULN": "references/vuln-research.md",
    "REMEDIATE": "references/remediation.md",
    "AUTO": "references/automation.md",
    "GRAPH": "references/graph.md",
    "ENG": "references/engineering.md",
    "LAB": "references/lab.md",
    "REFUSAL": "references/refusal.md",
    "CORE": "SKILL.md",
}


def api_key() -> str:
    cfg = load_cfg()
    return (os.environ.get("TYPESAFE_API_KEY") or os.environ.get("JEV_API_KEY") or cfg.get("typesafe") or "").strip()


def ask(key: str, state: str, questions: dict) -> dict:
    code, data, raw = json_post(
        API,
        {"state": state[:8000], "model": os.environ.get("JEV_MODEL") or "jev-latest", "questions": questions},
        headers={"Authorization": f"Bearer {key}"},
        timeout=30,
    )
    if code != 200 or not isinstance(data, dict):
        raise SystemExit(f"jev http {code} {raw[:180]}")
    return data


def cmd_ping(key: str) -> int:
    data = ask(key, "ping", {"up": {"type": "noul", "instructions": "The word ping is present."}})
    ans = (data.get("answers") or {}).get("up") or {}
    print(json.dumps({"ok": True, "model": data.get("model"), "noul": ans.get("noul")}, ensure_ascii=False))
    return 0


def cmd_route(key: str, text: str) -> int:
    data = ask(
        key,
        text,
        {
            "track": {
                "type": "choice",
                "instructions": "Which single operator track best fits this request",
                "criteria": TRACKS,
            }
        },
    )
    ans = (data.get("answers") or {}).get("track") or {}
    choice = str(ans.get("choice") or "CORE")
    conf = float(ans.get("confidence") or 0)
    if choice not in REF or conf < 0.4:
        log(f"jev abstain choice={choice} conf={conf:.2f}")
        choice = "CORE"
    print(f"PSNB-OPS TRACK={choice} REF={REF[choice]} SRC=jev CONF={conf:.2f}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(prog="jev.py")
    p.add_argument("--text", default="")
    p.add_argument("--ping", action="store_true")
    args = p.parse_args()
    key = api_key()
    if not key:
        print("NO_KEY set TYPESAFE_API_KEY or typesafe in config.yaml")
        return 3
    if args.ping:
        return cmd_ping(key)
    if not args.text:
        print("need --text or --ping")
        return 2
    return cmd_route(key, args.text)


if __name__ == "__main__":
    raise SystemExit(main())
