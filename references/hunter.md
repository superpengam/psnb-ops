# TRACK=HUNTER

不要读外部猎取长文档。跑脚本：

```
python scripts/hunt.py --query "title=\"Directory listing for /\" && body=\".env\""
python scripts/hunt.py --target example.com
python scripts/extract.py hunt/
python scripts/report.py
```

顺序：密钥（无则跳过）→ 聚合（免费源优先）→ 归一化 unique_hosts → 目录探针 → 提取 → HTML。
Key 不明文回显。`hunt/` gitignore。FOFA 先 info/count 再拉，额度不够停。
