# 5. 云端大模型接入

本次大赛支持通过 AnyInt 接入云端大模型。开发者可以根据作品需求，将云端模型用于任务规划、文本生成、文档理解、代码生成、多模态分析和工具调用等场景，并与此芯 P1 端侧模型组合形成端云协同应用。

本章提供两种接入方式：

| **接入方式**        | **适用场景**                                     | **建议**                                   |
|---------------------|--------------------------------------------------|--------------------------------------------|
| 应用程序 API 接入   | Python 后端、自研 Agent、RAG、网页应用和业务服务 | 推荐，作为参赛作品的主要云模型接入方式     |
| 现成 Agent 工具接入 | Claude Code、Codex CLI 等开发辅助工具            | 可选，用于辅助开发，不是参赛作品的必需组件 |

普通应用优先使用 OpenAI Chat Completions 兼容接口（Stable）。Claude Code 使用 Anthropic 兼容接口（Stable）；Codex CLI 需要使用 OpenAI Responses API（Beta）。

```{toctree}
:maxdepth: 2
:hidden:

api-selection
api-key
application
dev-tools
troubleshooting
security
```
