from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import (  # noqa: E402
    HUNT,
    host_key,
    json_get,

    key_of,
    load_cfg,
    log,
    normalize_url,
    sleep_ok,
    write_json,
)

BODIES = [".env", ".git", ".ssh", ".npmrc", ".hermes", ".claude", ".opencode", "secret.json"]


def b64(s: str) -> str:
    return base64.b64encode(s.encode()).decode().replace("\n", "")


def collect(source: str, rows: list[dict]) -> None:
    raw = HUNT / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    write_json(raw / f"{source}.json", {"source": source, "count": len(rows), "rows": rows})
    log(f"[{source}] {len(rows)}")


def src_crtsh(domain: str) -> list[dict]:
    code, data, _ = json_get(f"https://crt.sh/?q=%25.{domain}&output=json", timeout=45)
    rows = []
    if code != 200 or not isinstance(data, list):
        return rows
    seen = set()
    for item in data:
        nv = item.get("name_value") or ""
        for part in nv.split("\n"):
            host = part.strip().lstrip("*.").lower()
            if host and host not in seen:
                seen.add(host)
                rows.append({"source": "crtsh", "host": host, "url": f"https://{host}"})
    return rows


def src_wayback(domain: str) -> list[dict]:
    url = f"https://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&fl=original&collapse=urlkey&limit=150"
    code, data, _ = json_get(url, timeout=45)
    rows = []
    if code != 200 or not isinstance(data, list):
        return rows
    for row in data[1:]:
        original = row[0] if isinstance(row, list) and row else ""
        if original:
            rows.append({"source": "wayback", "url": original, "host": host_key(original)})
    return rows


def src_leakix(cfg: dict, query: str) -> list[dict]:
    key = key_of(cfg, "leakix")
    headers = {"Accept": "application/json"}
    if key:
        headers["api-key"] = key
    code, data, _ = json_get(f"https://leakix.net/search?q={quote(query)}&scope=leak", headers=headers)
    rows = []
    if not isinstance(data, list):
        return rows
    for item in data[:100]:
        ip = item.get("ip") or ""
        host = item.get("host") or ip
        rows.append({"source": "leakix", "host": host, "ip": ip, "url": item.get("url") or host})
    return rows


def src_github(cfg: dict, query: str) -> list[dict]:
    token = key_of(cfg, "github")
    if not token:
        log("[github] skip no key")
        return []
    q = quote(f"{query} filename:.env")
    code, data, _ = json_get(
        f"https://api.github.com/search/code?q={q}&per_page=30",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
    )
    rows = []
    items = (data or {}).get("items") if isinstance(data, dict) else []
    for it in items or []:
        rows.append({
            "source": "github",
            "url": it.get("html_url"),
            "host": "github.com",
            "path": (it.get("repository") or {}).get("full_name"),
        })
    return rows


def src_fofa(cfg: dict, query: str) -> list[dict]:
    key = key_of(cfg, "fofa")
    if not key:
        log("[fofa] skip no key")
        return []
    info_code, info, _ = json_get(f"https://fofa.info/api/v1/info/my?key={key}")
    if info_code != 200:
        log(f"[fofa] info fail {info_code}")
        return []
    qb = b64(query)
    code, data, _ = json_get(
        f"https://fofa.info/api/v1/search/all?key={key}&qbase64={qb}&size=1&fields=host,ip,port,title"
    )
    total = 0
    if isinstance(data, dict):
        total = int(data.get("size") or 0)
    if total > 20000:
        log(f"[fofa] total={total} too large, skip pull")
        return []
    size = min(int(cfg.get("page_size") or 100), 100)
    pages = min(int(cfg.get("max_pages") or 5), 5)
    rows = []
    for page in range(1, pages + 1):
        code, data, _ = json_get(
            f"https://fofa.info/api/v1/search/all?key={key}&qbase64={qb}&size={size}&page={page}&fields=host,ip,port,title,link"
        )
        results = (data or {}).get("results") if isinstance(data, dict) else []
        if not results:
            break
        for r in results:
            if isinstance(r, list) and r:
                host = r[0]
                rows.append({"source": "fofa", "host": host, "ip": r[1] if len(r) > 1 else "", "url": r[-1] if r else host})
            elif isinstance(r, str):
                rows.append({"source": "fofa", "host": r, "url": r})
        if len(results) < size:
            break
        sleep_ok(1.2)
    return rows


def src_shodan(cfg: dict, query: str) -> list[dict]:
    key = key_of(cfg, "shodan") or key_of(cfg, "shodan2")
    if not key:
        log("[shodan] skip no key")
        return []
    q = quote(query)
    code, data, _ = json_get(f"https://api.shodan.io/shodan/host/search?key={key}&query={q}&page=1")
    rows = []
    matches = (data or {}).get("matches") if isinstance(data, dict) else []
    for m in matches or []:
        ip = m.get("ip_str") or ""
        port = m.get("port")
        host = ip if not port else f"{ip}:{port}"
        rows.append({"source": "shodan", "host": host, "ip": ip, "url": f"http://{host}"})
    return rows


def src_hunter(cfg: dict, query: str) -> list[dict]:
    key = key_of(cfg, "hunter")
    if not key:
        log("[hunter] skip no key")
        return []
    search = quote(b64(query))
    code, data, _ = json_get(
        f"https://hunter.qianxin.com/openApi/search?api-key={key}&search={search}&is_web=1&page=1&page_size=20"
    )
    rows = []
    arr = ((data or {}).get("data") or {}).get("arr") if isinstance(data, dict) else []
    for it in arr or []:
        url = it.get("url") or it.get("ip")
        rows.append({"source": "hunter", "host": host_key(url or ""), "url": url, "ip": it.get("ip")})
    return rows


def merge(all_rows: list[dict]) -> list[str]:
    seen = set()
    hosts = []
    for row in all_rows:
        url = normalize_url(row.get("url") or row.get("host") or "")
        k = host_key(url)
        if not k or k in seen:
            continue
        seen.add(k)
        hosts.append(k)
    (HUNT / "unique_hosts.txt").write_text("\n".join(hosts) + "\n", encoding="utf-8")
    write_json(HUNT / "merged.json", {"count": len(hosts), "hosts": hosts})
    return hosts


def main() -> int:
    p = argparse.ArgumentParser(prog="hunt.py")
    p.add_argument("--query", default='title="Directory listing for /" && body=".env"')
    p.add_argument("--target", default="")
    p.add_argument("--sources", default="crtsh,wayback,leakix,github,fofa,shodan,hunter")
    args = p.parse_args()
    cfg = load_cfg()
    HUNT.mkdir(parents=True, exist_ok=True)
    wanted = {s.strip() for s in args.sources.split(",") if s.strip()}
    rows: list[dict] = []
    domain = args.target.strip()

    if domain and "crtsh" in wanted:
        rows += src_crtsh(domain)
        collect("crtsh", [r for r in rows if r["source"] == "crtsh"])
    if domain and "wayback" in wanted:
        w = src_wayback(domain)
        rows += w
        collect("wayback", w)
    if "leakix" in wanted:
        q = domain or args.query
        lx = src_leakix(cfg, q)
        rows += lx
        collect("leakix", lx)
    if "github" in wanted:
        gh = src_github(cfg, domain or ".env")
        rows += gh
        collect("github", gh)
    if "fofa" in wanted:
        ff = src_fofa(cfg, args.query)
        rows += ff
        collect("fofa", ff)
    if "shodan" in wanted:
        sh = src_shodan(cfg, args.query.replace("&&", " ").replace("title=", "http.title:"))
        rows += sh
        collect("shodan", sh)
    if "hunter" in wanted:
        ht = src_hunter(cfg, args.query)
        rows += ht
        collect("hunter", ht)

    hosts = merge(rows)
    print(json.dumps({"rows": len(rows), "unique_hosts": len(hosts), "out": str(HUNT)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
