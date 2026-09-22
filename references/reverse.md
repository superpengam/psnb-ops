# TRACK=REVERSE

Pipeline: hash → file → strings → r2/Ghidra → arch/protect/entry → 关键函数（偏移+字节）。

工具：r2 (`r2 -A`/`pdf`/`izz`/`/R`/`radiff2`)、binwalk、jadx/apktool、ilspycmd、Il2CppDumper、capstone。

授权校验（自有/CTF/已授权）：搜 expired/invalid/注册码 → patch jz/nop，或 hook 返回真，算法可逆才写 keygen。

固件：`binwalk -Me` → squashfs → strings telnet/httpd/passwd。多版本 `radiff2`。

每个判断必须有偏移或反汇编。无证据不写结论。

代码面大时先 `python scripts/index.py <dir>` 拿薄索引，再只读命中文件。
