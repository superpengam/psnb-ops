from __future__ import annotations

import argparse
import json
import socket
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import HUNT, host_key, http, json_get, log, write_json, write_jsonl  # noqa: E402

DEFAULT_PORTS = [80, 443, 8080, 8443, 8000, 22, 21, 3306, 6379, 27017, 9200, 2375, 8848]
PATHS = [
    "/", "/.env", "/.git/HEAD", "/.git/config", "/robots.txt", "/sitemap.xml",
    "/admin", "/login", "/api", "/swagger/index.html", "/favicon.ico",
    "/.DS_Store", "/backup.zip", "/wp-login.php", "/console",
]


def crtsh(domain: str) -> list[str]:
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    code, data, _ = json_get(url, timeout=45)
    names: set[str] = set()
    if code != 200 or not isinstance(data, list):
        log(f"[crt.sh] skip status={code}")
        return []
    for row in data:
        nv = (row.get("name_value") or "") if isinstance(row, dict) else ""
        for part in nv.split("\n"):
            host = part.strip().lstrip("*.").lower()
            if host and " " not in host:
                names.add(host)
    return sorted(names)


def wayback(domain: str) -> list[str]:
    url = (
        "https://web.archive.org/cdx/search/cdx"
        f"?url={domain}/*&output=json&fl=original&collapse=urlkey&limit=200"
    )
    code, data, _ = json_get(url, timeout=45)
    out: list[str] = []
    if code != 200 or not isinstance(data, list):
        log(f"[wayback] skip status={code}")
        return out
    for row in data[1:]:
        if isinstance(row, list) and row:
            out.append(row[0])
        elif isinstance(row, str):
            out.append(row)
    return out


def probe_ports(host: str, ports: list[int], timeout: float = 0.8) -> list[dict]:
    found = []
    for port in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            banner = ""
            try:
                banner = s.recv(128).decode("latin-1", "ignore")
            except Exception:
                pass
            found.append({"host": host, "port": port, "open": True, "banner": banner[:80]})
        except Exception:
            pass
        finally:
            s.close()
    return found


def probe_http(base: str) -> list[dict]:
    rows = []
    for path in PATHS:
        url = base.rstrip("/") + path
        code, body = http(url, timeout=8)
        rows.append({
            "url": url,
            "status": code,
            "len": len(body or ""),
            "title": _title(body),
            "hit": code in (200, 301, 302, 401, 403) and path != "/",
        })
    return rows


def _title(html: str) -> str:
    low = (html or "")[:4000].lower()
    i = low.find("<title>")
    if i < 0:
        return ""
    j = low.find("</title>", i)
    return (html[i + 7:j] if j > i else "")[:80].strip()


def main() -> int:
    p = argparse.ArgumentParser(prog="recon.py")
    p.add_argument("--target", required=True, help="domain or host")
    p.add_argument("--ports", default="", help="comma ports, empty=default")
    p.add_argument("--no-http", action="store_true")
    args = p.parse_args()
    target = args.target.strip().split("://")[-1].split("/")[0]
    out_dir = HUNT / "recon"
    out_dir.mkdir(parents=True, exist_ok=True)

    subs = crtsh(target)
    wb = wayback(target)
    write_json(out_dir / "crtsh.json", {"target": target, "hosts": subs, "count": len(subs)})
    write_json(out_dir / "wayback.json", {"target": target, "urls": wb[:200], "count": len(wb)})

    hosts = [target] + [h for h in subs if h.endswith(target)][:40]
    unique = []
    seen = set()
    for h in hosts:
        k = host_key(h)
        if k and k not in seen:
            seen.add(k)
            unique.append(k)
    (HUNT / "unique_hosts.txt").write_text("\n".join(unique) + "\n", encoding="utf-8")

    ports = [int(x) for x in args.ports.split(",") if x.strip().isdigit()] or DEFAULT_PORTS
    port_rows = []
    for h in unique[:15]:
        port_rows.extend(probe_ports(h.split(":")[0], ports))
    write_json(out_dir / "ports.json", port_rows)

    http_rows = []
    if not args.no_http:
        for h in unique[:8]:
            for scheme in ("https", "http"):
                http_rows.extend(probe_http(f"{scheme}://{h}"))
                if any(r["status"] and r["status"] < 500 for r in http_rows[-len(PATHS):]):
                    break
        write_jsonl(out_dir / "http.jsonl", http_rows)

    print(json.dumps({
        "target": target,
        "subdomains": len(subs),
        "wayback": len(wb),
        "hosts": len(unique),
        "open_ports": len(port_rows),
        "http_hits": sum(1 for r in http_rows if r.get("hit")),
        "out": str(out_dir),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
