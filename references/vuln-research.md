# TRACK=VULN

威胁模型 <10% token。切片审计 60-80%。验证 20-30%。禁止「找所有漏洞」。

切片对应真实攻击面：认证/会话/上传/反序列化/沙箱/出站。要 PoC 不要评价。同一问题 2-5 个变体。

模型说有洞不算。单测/harness/grep 不变量走通才确认。先 `python scripts/index.py <repo>`。
