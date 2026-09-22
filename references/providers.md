# TRACK=PROVIDERS

多模型切换是配置问题，不是破甲问题。

一个供应商一条 profile：base_url、api_key_env、协议（openai / anthropic）。切换只改当前 profile，密钥留在环境变量或本机 config，不进仓库、不进回复。

失败切换：超时/5xx/429 换下一条，熔断后不再打满。本地代理若已有（cc-switch / 网关）就用它，不在技能里再写一套服务。

技能正文保持短。供应商名单不写进 SKILL.md。
