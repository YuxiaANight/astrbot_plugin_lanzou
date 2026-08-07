# astrbot_plugin_lanzou

[![Visitors](https://visitor-badge.laobi.icu/badge?page_id=YuxiaANight/astrbot_plugin_lanzou)](https://visitor-badge.laobi.icu/badge?page_id=YuxiaANight/astrbot_plugin_lanzou)

![Latest Version](https://img.shields.io/badge/LATEST%20VERSION-v1.0.8-7ec8e3?style=for-the-badge&labelColor=EDFFEC)

![AstrBot Plugin](https://img.shields.io/badge/ASTRBOT-PLUGIN-ff69b4?style=for-the-badge&labelColor=EDFFEC)

蓝奏云直链解析 AstrBot 插件，兼容全平台。
**注意蓝奏云的链接有时效，过期请重新解析！**

## 功能

- 指令解析：`/lanzou <链接> [密码]`
- 密码识别：消息中带 `密码:xxxx` 或 `密码：xxxx` 时自动带入
- LLM 工具：开启后 AI 可自动调用解析，对话更自然
- 返回文件名、文件大小、直链地址

## 指令列表

| 指令 | 别名 | 用法 |
| --- | --- | --- |
| /lanzou | 蓝奏 / 蓝奏云 / lz | 解析蓝奏云链接，可附带密码 |

## 使用示例

指令方式：

```
/lanzou https://www.lanzouf.com/xxxxx
/lanzou https://www.lanzouf.com/xxxxx abcd
```

LLM 工具方式（开启 `enable_llm_tool` 后，对话中提及蓝奏云链接，AI 会自动调用工具）：

```
帮我解析这个蓝奏云链接 https://www.lanzouf.com/xxxxx 密码是 abcd
```

## 配置

在 AstrBot WebUI 插件配置页可调整以下项：

| 配置项 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| enable_llm_tool | bool | true | 是否将蓝奏云解析注册为 LLM 工具 |
| request_timeout | int | 20 | 请求超时时间（秒） |

## 安装

1. 将插件目录放入 `AstrBot/data/plugins/astrbot_plugin_lanzou/`
2. 安装依赖：`pip install -r requirements.txt`
3. 重启 AstrBot 或在 WebUI 重新加载插件

## 致谢

解析逻辑参考 Filmy / hanximeng (**https://github.com/hanximeng/LanzouAPI**) 的开源版本。
