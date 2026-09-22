# TRACK=PWN

Triage：arch/ABI/端序/libc/缓解（ASLR/PIE/NX/RELRO/canary）/输入面。最小化崩溃。

原语：栈/堆/OOB/UAF/格式化/竞态。判定可控数据、泄露、任意读写、控制流。

Exploit：cyclic → 泄露 → 基址 → ROP/ret2libc/堆风水 → 验证。pwntools 脚本带 local/remote/GDB。

内核/驱动有材料再做 ioctl/对象生命周期。可靠性多次跑，写明环境。
