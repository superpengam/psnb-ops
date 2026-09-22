# Jev

TypeSafe 的判断模型，不写正文。只在有 `TYPESAFE_API_KEY` 时用。

```
python scripts/jev.py --ping
python scripts/jev.py --text "<用户原话>"
```

输出一行 `PSNB-OPS TRACK=... REF=... SRC=jev CONF=0.xx`。`CONF < 0.4` 时脚本改打 `CORE` / `SKILL.md`，再跑原来的 `route.py`。

密钥不进 git、不进回复。接口 `POST https://api.typesafe.ai/v1/systemone`。没 key 就当没这层。
