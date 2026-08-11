# 5.1 接口选择

AnyInt 不同接入方式使用的接口如下。

| **使用方式**                  | **客户端配置 Base URL**         | **协议**                |
|-------------------------------|---------------------------------|-------------------------|
| Python、自研 Agent 或普通应用 | https://api.anyint.ai/openai/v1 | OpenAI Chat Completions |
| Claude Code                   | https://api.anyint.ai/anthropic | Anthropic Messages      |
| Codex CLI                     | https://api.anyint.ai/openai/v1 | OpenAI Responses        |

**说明：** Claude Code 的 ANTHROPIC_BASE_URL 使用 https://api.anyint.ai/anthropic；直接调用 Anthropic 兼容 API 时，版本化接口位于 https://api.anyint.ai/anthropic/v1。不要将客户端 Base URL 与完整请求路径混淆。

普通应用不需要直接调用 Responses API。只有 Codex CLI 等明确要求 wire_api = "responses" 的客户端才应使用 Responses 协议。
