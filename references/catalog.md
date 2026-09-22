# 参考清单（只学结构，不搬正文）

已吸收进本技能的做法：

- mattpocock/skills：小技能、可组合、交接、TDD、先对齐再写码 → `engineering.md` + `handoff.py`
- colbymchenry/codegraph：先查图再读文件 → `graph.py` / `graph.md`
- farion1231/cc-switch、Wei-Shaw/sub2api：供应商配置与故障切换，密钥不进技能 → `providers.md`
- earendil-works/pi、vastsa/PI-Desktop：工具进沙箱，密钥留宿主 → `lab.md`
- GALIAIS/CTF-Sandbox-Orchestrator：题目隔离运行 → `lab.md`
- OpenMinis/OpenMinis：手持/电脑分流 → `runtime.md`
- Pa55w0rd/secknowledge-skill、elementalsouls/Claude-OSINT：知识卡与被动源 → `osint.md` `vuln-research.md`
- unclecode/crawl4ai：要抓页面时用现成爬虫，不把爬虫内核写进技能
- fastapi/fastapi：脚本保持小，HTTP 用标准库即可
- LING71671/open-reverselab：逆向先索引再切片 → `reverse.md` + `graph.py`
- baiqi-redteam-lab / attack-graph-rag：案例与证据链落盘 → `case.py`，不内置攻击图数据
- guchangan1/All-Defense-Tool、stablyai/orca：工具按轨道调用，不把工具清单塞进主文件

越狱仓库只收结构，不收正文 → `refusal.md`：

- EasyJailbreak：mutate→evaluate 循环变成拒答分类，不装 11 套 recipe
- L1B3RT4S / togg53192-cmd/jailbreaks：一厂商一文件 → 只换 injection 槽，不贴 GROK-MEGA 长包
- hermes-seagull：profile 叠加、探针激活；密钥留宿主 config
- gpt-instruct：候选指令 ≤8KB、失败归因（模型拒 vs 网/账号）、隔离评测；不写别人的 `model_instructions_file`
- Spiritual-Spell：第一人称锁 + 不列清单；不复制其注入正文

明确不收进技能正文：

- 上述仓库的提示词/ZIP/会话补丁原文
- funnycups/Toolify：不生成伪造工具调用协议。
- ryfineZ/codex-session-patcher：不改其它产品的会话完整性。
- baiqi-register-template、baiqi-cf-worker-mihomo、LoseNine/ruyipage、DietrichGebert/ponytail：与操作员技能无关，不并入。
