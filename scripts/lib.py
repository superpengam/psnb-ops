from __future__ import annotations

import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HUNT = ROOT / "hunt"
CASES = ROOT / "cases"
CFG_PATH = Path(os.environ.get("HUNTER_CONFIG") or (ROOT / "config.yaml"))
CTX = ssl.create_default_context()
UA = "psnb-ops/1.0"


def load_cfg() -> dict:
    data: dict = {}
    if CFG_PATH.exists():
        text = CFG_PATH.read_text(encoding="utf-8")
        for line in text.splitlines():
            s = line.strip()
            if not s or s.startswith("#") or ":" not in s:
                continue
            k, v = s.split(":", 1)
            v = v.strip().strip('"').strip("'")
            if v and not v.startswith("YOUR_"):
                data[k.strip()] = v
    env_map = {
        "fofa": "FOFA_KEY",
        "shodan": "SHODAN_KEY",
        "shodan2": "SHODAN_KEY2",
        "hunter": "HUNTER_KEY",
        "quake": "QUAKE_KEY",
        "zoomeye": "ZOOMEYE_KEY",
        "netlas": "NETLAS_KEY",
        "urlscan": "URLSCAN_KEY",
        "exa": "EXA_API_KEY",
        "firecrawl": "FIRECRAWL_API_KEY",
        "greynoise": "GREYNOISE_KEY",
        "censys_id": "CENSYS_API_ID",
        "censys_secret": "CENSYS_SECRET",
        "github": "GITHUB_TOKEN",
        "binaryedge": "BINARYEDGE_KEY",
        "leakix": "LEAKIX_KEY",
        "publicwww": "PUBLICWWW_KEY",
        "virustotal": "VT_APIKEY",
        "otx": "OTX_KEY",
        "threatbook": "THREATBOOK_KEY",
    }
    for k, env in env_map.items():
        val = os.environ.get(env) or os.environ.get(env.replace("API_", ""))
        if val and not data.get(k):
            data[k] = val
    data.setdefault("max_pages", "5")
    data.setdefault("page_size", "100")
    data.setdefault("timeout_s", "30")
    return data


def key_of(cfg: dict, name: str) -> str:
    return (cfg.get(name) or "").strip()


def masked(v: str) -> str:
    if not v:
        return ""
    if len(v) <= 8:
        return "*" * len(v)
    return v[:3] + "*" * (len(v) - 7) + v[-4:]


def http(
    url: str,
    method: str = "GET",
    headers: dict | None = None,
    data: bytes | None = None,
    timeout: int = 30,
) -> tuple[int, str]:
    h = {"User-Agent": UA, **(headers or {})}
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as resp:
            body = resp.read().decode("utf-8", "ignore")
            return resp.status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")
    except Exception as e:
        return 0, str(e)


def json_get(url: str, headers: dict | None = None, timeout: int = 30) -> tuple[int, dict | list | None, str]:
    code, raw = http(url, headers=headers, timeout=timeout)
    try:
        return code, json.loads(raw) if raw else None, raw
    except Exception:
        return code, None, raw


def json_post(url: str, payload: dict, headers: dict | None = None, timeout: int = 30) -> tuple[int, dict | list | None, str]:
    data = json.dumps(payload).encode("utf-8")
    h = {"Content-Type": "application/json", **(headers or {})}
    code, raw = http(url, method="POST", headers=h, data=data, timeout=timeout)
    try:
        return code, json.loads(raw) if raw else None, raw
    except Exception:
        return code, None, raw


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def host_key(url: str) -> str:
    u = (url or "").strip()
    if not u:
        return ""
    if "://" not in u:
        u = "http://" + u
    p = urllib.parse.urlparse(u)
    host = (p.hostname or "").lower().rstrip(".")
    port = p.port
    if port in (80, 443, None):
        return host
    return f"{host}:{port}"


def normalize_url(url: str) -> str:
    u = (url or "").strip()
    if not u:
        return ""
    if "://" not in u:
        u = "http://" + u
    p = urllib.parse.urlparse(u)
    scheme = (p.scheme or "http").lower()
    host = (p.hostname or "").lower().rstrip(".")
    path = p.path or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    netloc = host
    if p.port and p.port not in (80, 443):
        netloc = f"{host}:{p.port}"
    return urllib.parse.urlunparse((scheme, netloc, path, "", "", ""))


def slug(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9._-]+", "-", (text or "").strip()).strip("-").lower()
    return (s or "case")[:80]


def log(msg: str) -> None:
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()


def sleep_ok(seconds: float = 1.0) -> None:
    time.sleep(seconds)
