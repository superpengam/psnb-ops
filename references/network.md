# TRACK=NETWORK

URL/HAR/JS → 还原签名 → 枚举端点 → schema → round-trip client。

火力：httpx 并发、TLS 指纹、子域→存活→爬取→nuclei。绕过：编码矩阵/分块/HPP/XFF。无 nmap 时 `python scripts/recon.py --ports`。
