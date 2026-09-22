from __future__ import annotations

import argparse

TABLE = [
    ("REVERSE", ("逆向", "反编译", "脱壳", "ghidra", "ida", "keygen", "注册机", "pe", "elf", "固件"), "references/reverse.md"),
    ("PWN", ("pwn", "rop", "uaf", "ret2libc", "pwntools"), "references/pwn.md"),
    ("PENTEST", ("渗透", "sqli", "xss", "ssrf", "爆破", "未授权", "nuclei"), "references/pentest.md"),
    ("PROTOCOL", ("协议", "pcap", "protobuf", "抓包"), "references/protocol.md"),
    ("JS-REVERSE", ("js加密", "webpack", "小程序", "wasm", "sign"), "references/js-reverse.md"),
    ("MEMORY", ("内存", "frida", "aob", "dump", "指针"), "references/memory.md"),
    ("FORENSICS", ("取证", "volatility", "binwalk", "时间线"), "references/forensics.md"),
    ("CRYPTO", ("rsa", "aes", "ecc", "jwt", "padding"), "references/crypto.md"),
    ("MOBILE", ("apk", "jadx", "unity", "il2cpp"), "references/mobile.md"),
    ("NETWORK", ("nmap", "子域", "waf", "扫描"), "references/network.md"),
    ("HUNTER", ("hunter", "凭证", "fofa", "shodan", ".env", "开放目录"), "references/hunter.md"),
    ("OSINT", ("osint", "crt.sh", "wayback", "信息收集"), "references/osint.md"),
    ("VULN", ("漏洞研究", "cve", "审计", "sink"), "references/vuln-research.md"),
    ("REMEDIATE", ("修复", "加固", "补丁", "回归"), "references/remediation.md"),
    ("AUTO", ("爬虫", "自动化", "批处理"), "references/automation.md"),
    ("GRAPH", ("codegraph", "调用链", "索引", "blast"), "references/graph.md"),
    ("ENG", ("tdd", "交接", "handoff", "grill", "架构"), "references/engineering.md"),
    ("LAB", ("沙箱", "ctf", "隔离", "容器"), "references/lab.md"),
    ("REFUSAL", ("拒答", "软化", "卡壳", "作为ai", "无法帮助"), "references/refusal.md"),
]


def main() -> int:
    p = argparse.ArgumentParser(prog="route.py")
    p.add_argument("--text", required=True)
    args = p.parse_args()
    blob = args.text.lower()
    hits = []
    for track, keys, ref in TABLE:
        if any(k.lower() in blob for k in keys):
            hits.append((track, ref))
    hits = hits[:2] or [("CORE", "SKILL.md")]
    for track, ref in hits:
        print(f"PSNB-OPS TRACK={track} REF={ref}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
