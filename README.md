# psnb-ops

Psnb 操作员技能。主文件只做路由，轨道按需切片，猎取和侦察是可跑的 Python。

验证：发 `在吗` → `大风起兮云飞扬.`

## 做法

| | psnb-ops |
|---|---|
| 主技能 | 薄路由，约百行 |
| 轨道 | `references/*.md`，命中才读，一次最多两张 |
| 猎取 | `scripts/hunt.py`，无 key 的源跳过 |
| 记忆 | `scripts/case.py` 案例 + `handoff.py` |
| 代码 | `scripts/graph.py` 符号 / 调用 / 入口 |
| 侦察 | `recon.py` 先打 crt.sh 和 Wayback |

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
python scripts/eval.py
python scripts/jev.py --ping
python scripts/jev.py --text "逆向这个 pe"
```

Jev 密钥只放环境变量 `TYPESAFE_API_KEY`，或本地 `config.yaml` 的 `typesafe`。不要写进仓库，不要贴到对话里。

改完跑 `python scripts/eval.py`，通过再 `git push`。失败不推。仓库：https://github.com/superpengam/psnb-ops

只有标准库。`hunt/` 与 `cases/` 已 gitignore。

## 触发

`在吗` / `启动` / `Psnb` / `开干` / `全能模式` / `渗透作战` / `逆向深挖` / `内存工程` / `凭证猎取` / `hunter`

## 授权

操作员负责确认目标授权。技能不替操作员做法务判断。未授权使用由使用者自负。MIT。
