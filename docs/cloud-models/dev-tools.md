# 5.4 可选：开发辅助工具接入

Claude Code 和 Codex CLI 可通过 AnyInt 使用云端模型，主要用于辅助开发者阅读代码、修改工程文件和排查问题。使用此类工具辅助完成开发，不计入参赛作品本身的多步骤规划、工具调用和状态管理能力，也不能替代作品需要实现的 Agent Workflow。

本节只介绍 AnyInt Provider 配置，不展开客户端安装、权限管理、MCP、Skill 和代码执行策略。客户端安装与更新方法应以各自官方文档为准。

## 5.4.1 Claude Code

AnyInt 的 Claude Code 接入使用 Anthropic 兼容接口。

首先查询 Anthropic 兼容模型：

```bash
curl -sS https://api.anyint.ai/anthropic/v1/models \
-H "x-api-key: ${ANYINT_API_KEY}" \
-H "anthropic-version: 2023-06-01" \
| python3 -m json.tool
```

从结果中选择准确的模型 ID，然后设置环境变量：

```bash
export ANTHROPIC_BASE_URL="https://api.anyint.ai/anthropic"
export ANTHROPIC_AUTH_TOKEN="${ANYINT_API_KEY}"
export ANTHROPIC_MODEL="<ANTHROPIC_MODEL_ID>"
export ANTHROPIC_DEFAULT_SONNET_MODEL="${ANTHROPIC_MODEL}"
export CLAUDE_CODE_SUBAGENT_MODEL="${ANTHROPIC_MODEL}"
```

启动 Claude Code：

```text
claude
```

输入：

```text
请只回复：AnyInt connected
```

如果能够正常返回指定文本，并且没有要求重新登录 Anthropic 或切换 Provider，说明 Claude Code 基础接入成功。

注意：

1.  ANTHROPIC_AUTH_TOKEN 只填写 API Key，不要添加 Bearer ；
2.  模型 ID 应来自 /anthropic/v1/models；
3.  当前终端关闭后，临时环境变量会失效；
4.  不要把包含 API Key 的配置文件提交到代码仓库。

Claude Code 官方支持通过 ANTHROPIC_BASE_URL 接入 LLM Gateway，用户级配置文件通常位于 ~/.claude/settings.json。本指南优先使用临时环境变量，避免将 API Key 直接写入文件。

## 5.4.2 Codex CLI

Codex CLI 通过 OpenAI Responses API 接入 AnyInt。AnyInt 当前将 Responses API 标记为 Beta，使用前应验证目标模型、账号、流式响应和当前 Codex 版本是否兼容。

查看 Codex 版本：

```bash
codex --version
```

创建配置目录：

```bash
mkdir -p ~/.codex
```

打开 Codex 配置文件：

```bash
nano ~/.codex/config.toml
```

在配置文件中添加：

```toml
[profiles.anyint]
model_provider = "anyint"
model = "<MODEL_ID>"
[model_providers.anyint]
name = "AnyInt"
base_url = "https://api.anyint.ai/openai/v1"
env_key = "ANYINT_API_KEY"
wire_api = "responses"
```

其中，\<MODEL_ID\> 应替换为 /openai/v1/models 返回的准确模型 ID。

设置 API Key：

```bash
export ANYINT_API_KEY="your-anyint-api-key"
```

执行最小验证：

```bash
codex exec --profile anyint "请只回复：AnyInt connected"
```

base_url 必须设置为：

https://api.anyint.ai/openai/v1

不要在后面追加 /responses 或 /chat/completions，Codex 会根据 wire_api = "responses" 自动调用 Responses 路径。

由于 Responses API 当前仍为 Beta，出现以下情况时，应先验证客户端、模型和接口组合，而不能直接判断为本地配置错误：

- 模型在 Models API 中可见，但 Responses 请求不可用；
- 请求开始后流式响应无法完成；
- Codex 无法获取或识别模型信息；
- 返回临时上游路由或额度异常。

应先使用第 5.3 节的 Chat Completions 示例验证 API Key 和模型，再更换模型或联系 AnyInt 技术支持。
