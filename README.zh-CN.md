# tg-ai-bot

你自己的 Telegram AI 聊天机器人。一个文件，一条命令，155+ 模型。

支持任何 OpenAI 兼容 API。实时流式输出。
发图片能看懂。聊天中随时切换模型。

## 部署

你需要两样东西：

1. **Telegram bot token** — 在 Telegram 找 [@BotFather](https://t.me/BotFather)，输入 `/newbot`，按步骤创建
2. **LLM API key** — 从 [TokenMix.ai](https://tokenmix.ai)（新用户送 $1，155+ 模型）或任何 OpenAI 兼容服务商

### Docker 部署（推荐）

```sh
git clone https://github.com/diaoyulao9657/tg-ai-bot
cd tg-ai-bot
cp .env.example .env
# 编辑 .env，填入 BOT_TOKEN 和 API_KEY
docker compose up -d
```

完事了。去 Telegram 跟你的 bot 说话吧。

### 直接运行

```sh
git clone https://github.com/diaoyulao9657/tg-ai-bot
cd tg-ai-bot
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env
python bot.py
```

## 功能

- **流式输出** — 逐字显示回复，不用干等
- **看图说话** — 发张图片问问题，bot 能理解
- **语音消息** — 发语音自动转文字并回复
- **Markdown** — 代码块、加粗等格式正确渲染
- **群聊支持** — 群里只有 @bot 或回复 bot 消息时才响应
- **切换模型** — `/model gpt-4o` 随时换
- **对话记忆** — 记住上下文（默认 20 条）
- **长回复拆分** — 超过 4096 字符自动分多条发送
- **权限控制** — 可以限制只允许特定用户使用

## 命令

```
/model <名称>  — 切换模型
/clear         — 清空对话
/help          — 帮助
```

## 配置

都在 `.env` 里：

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `BOT_TOKEN` | 是 | — | @BotFather 给的 token |
| `API_KEY` | 是 | — | API key |
| `BASE_URL` | 否 | `https://api.tokenmix.ai/v1` | API 地址 |
| `MODEL` | 否 | `gpt-4o-mini` | 默认模型 |
| `MAX_HISTORY` | 否 | `20` | 保留多少条上下文 |
| `ALLOWED_USERS` | 否 | *(所有人)* | 逗号分隔的用户 ID |
| `SYSTEM_PROMPT` | 否 | `You are a helpful assistant.` | 系统提示词 |

查你的 Telegram 用户 ID：给 [@userinfobot](https://t.me/userinfobot) 发消息。

## 许可证

MIT
