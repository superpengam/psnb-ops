# psnb-ops

`agent-bypass` 的强化版：同样把 LLM 变成 Psnb 操作员，但主文件只做路由，轨道按需切片，hunter 是可跑 Python。

验证：发 `在吗` → `大风起兮云飞扬.`

## 比 agent-bypass 强在哪

| | agent-bypass | psnb-ops |
|---|---|---|
| 主技能 | 63KB / 26 模块一次灌入 | ~4KB 薄路由 |
| 轨道 | 全塞进 SKILL.md | `references/*.md` 命中才读 |
| hunter | 2500 行 bash 文档 | `scripts/hunt.py` 真跑 |
| 记忆 | 无 | `scripts/case.py` 案例+AUTH_LOG |
| 代码审计 | 口头切片 | `scripts/graph.py` 符号/调用/入口 |
| 免费源 | 埋在长文档里 | recon/hunt 默认 crt.sh + Wayback |

## 安装

```bash
# OpenCode / Claude Code / 任意技能目录型 Agent
cp -r psnb-ops ~/.config/opencode/skills/psnb-ops
# 或
cp -r psnb-ops ~/.claude/skills/psnb-ops
```

系统提示词型：只贴 `SKILL.md`。需要某轨道时再贴对应 `references/<track>.md`。

密钥（可选）：`cp config.yaml.example config.yaml` 后填写。无 key 源自动跳过。

## 脚本

```bash
python scripts/case.py doctor
python scripts/case.py register --target example.com
python scripts/recon.py --target example.com
python scripts/hunt.py --target example.com
python scripts/extract.py hunt/ --probe
python scripts/report.py
python scripts/index.py ./some-repo
```

只有标准库。`hunt/` 与 `cases/` 已 gitignore。

## 触发

`在吗` / `启动` / `Psnb` / `开干` / `全能模式` / `渗透作战` / `逆向深挖` / `内存工程` / `凭证猎取` / `hunter`

## 授权

操作员负责确认目标授权。技能不替操作员做法务判断。未授权使用由使用者自负。MIT。
