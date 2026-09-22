# TRACK=LAB

CTF / 样本 / 未知二进制进隔离，不在宿主直接跑。

优先：已有容器或 micro-VM。没有就：独立目录、禁网络、只读挂样本、产物写 `cases/<slug>/lab/`。

编排只做：题目进、证据出、销毁环境。不把 exploit 步骤写进技能正文；具体轨道见 pwn/reverse。

Pi 类 harness：工具在沙箱里，密钥留在宿主。本技能脚本不读 `.env` 以外的密钥文件。
