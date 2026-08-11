# 5.5 接入验证与常见问题

推荐按照以下顺序进行验证：

1. 查询模型列表
2. 运行 Python 最小请求
3. 确认模型正常返回文本
4. 接入 Agent 框架或编码 Agent
5. 增加流式输出、工具调用和多模态能力

首次验证时不要同时加入工具调用、图片、长上下文、多轮记忆和复杂 Agent Workflow，否则出现错误后难以定位。

| **问题现象**                       | **处理建议**                                                                                                                                       |
|------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| Models API 返回 401                | 检查 API Key，以及 Authorization: Bearer 请求头                                                                                                    |
| 提示模型不存在                     | 重新查询 Models API，并使用准确的 data\[\].id                                                                                                      |
| 返回 404                           | 检查 Base URL；普通应用使用 /openai/v1，不要填写错误的完整路径                                                                                     |
| Python 可以调用，但 Agent 工具失败 | 检查工具要求的是 Chat Completions、Anthropic Messages 还是 Responses                                                                               |
| Claude Code 要求登录 Anthropic     | 检查 ANTHROPIC_BASE_URL 和 ANTHROPIC_AUTH_TOKEN 是否在当前终端生效                                                                                 |
| Codex 找不到 anyint Profile        | 检查 ~/.codex/config.toml 中是否存在 \[profiles.anyint\]，并检查 TOML 格式                                                                         |
| Codex 请求无法完成                 | Responses API 当前为 Beta。先使用第 5.3 节的 Chat Completions 示例验证 API Key 和模型，再检查 Codex 版本、目标模型、Responses 协议和流式响应兼容性 |
| 返回 429                           | 降低请求频率，并检查账号额度或并发限制                                                                                                             |
| 返回余额、额度或上游路由相关错误   | 更换已验证模型，并联系 AnyInt 技术支持确认账号和上游状态                                                                                           |
| API Key 已泄露                     | 立即在控制台撤销旧 Key，并创建新 Key                                                                                                               |
