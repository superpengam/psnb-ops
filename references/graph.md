# TRACK=GRAPH

大仓库先建图，禁止整库灌进上下文。

```
python scripts/graph.py <repo>
python scripts/graph.py <repo> --symbol FuncName
python scripts/index.py <repo>
```

有 `codegraph` 时优先：`codegraph status` / `codegraph explore "<question>"`。没有就用上面的标准库图：符号定义、调用点、入口、sink。

只读命中文件的相关行。改符号前先看 callers。图是启发式，跨文件动态调用标推测。
