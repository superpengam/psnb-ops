# Runtime

先判环境再干活，不问操作员。

- 手持 iSH：`/var/minis` 或 `MINIS_ROOT` 或 `uname` 含 iSH → apk + pathlib。
- 电脑：Win/mac/Linux。Win 用 `python` 与 PowerShell；POSIX 用 `python3`。
- 自检：`python scripts/case.py doctor`
- 交付脚本只用 pathlib + utf-8，禁止写死 `/tmp` 或 `C:\`。
- 重型工具（r2/Ghidra/Frida/nmap）缺则装；装不上给可在 PC 跑的等价脚本。
