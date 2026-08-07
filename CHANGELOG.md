# 更新日志

## 1.0.8 - 2026-08-06

- 优化兼容性

## 1.0.7 - 2026-08-06

- 修复 aiohttp 被 TLS 指纹拦截问题：自动求解 `acw_sc__v2` 反爬虫挑战
- 从 PHP 源码移植 `acw_sc_v2_simple` 算法，遇到挑战页自动解出 cookie 并重试
- `_http_get` 和 `_http_post` 均支持自动挑战求解
- 修复 X-Forwarded-For 和 Client-IP 不一致问题（同一请求使用同一 IP）

## 1.0.6 - 2026-08-06

- 修复无密码链接解析失败：所有 HTTP 请求补上 `acw_sc__v2=` cookie，与 PHP 原版一致
- 新增反爬虫检测：被蓝奏云 JS 挑战拦截时返回明确提示
- 修复 iframe 正则匹配：补上无 `\n` 前缀的回退匹配

## 1.0.5 - 2026-08-06

- 修复已知bug

## 1.0.4 - 2026-08-06

- 修复普通文件解析时 `提取参数失败` 的问题：ajaxm 路径拼接缺少 `ajaxm.php?file=` 前缀

## 1.0.3 - 2026-08-06

- 修复 `_empty() takes no arguments` 报错：移除 command handler 的 `*args`，改从 `event.message_str` 提取链接
- 移除 `from __future__ import annotations`，避免框架 `inspect.signature(eval_str=True)` 边界问题

## 1.0.2 - 2026-08-06

- 配置文件改为标准 `_conf_schema.json`，可在 WebUI 配置页直接控制
- 配置项 `enable_llm_tool` 控制 LLM 工具是否注册
- 配置项 `auto_parse` 控制自动解析开关
- 配置项 `command_name` 自定义指令名
- 配置项 `request_timeout` 自定义请求超时

## 1.0.1 - 2026-08-06

- 新增可视化配置，可控制 LLM 工具、自动解析、指令名、超时时间
- 新增 LLM 工具 `parse_lanzou`，开启后 AI 可自动调用解析能力，交互更自然

## 1.0.0 - 2026-08-06

- 没啥好说的