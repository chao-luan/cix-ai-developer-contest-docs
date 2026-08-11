# 5.3 在应用程序中调用云端模型

## 5.3.1 安装 Python SDK

执行：

```bash
python3 -m venv ~/anyint-venv
source ~/anyint-venv/bin/activate
python3 -m pip install "openai>=1,<2"
```

确认已经设置以下环境变量：

```bash
export ANYINT_API_KEY="your-anyint-api-key"
export ANYINT_MODEL_ID="<MODEL_ID>"
```

## 5.3.2 创建测试程序

创建文件：

```bash
nano anyint_chat.py
```

写入以下内容：

```python
import os
import sys
from openai import OpenAI
def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        print(f"缺少环境变量：{name}", file=sys.stderr)
        raise SystemExit(1)
    return value
api_key = get_required_env("ANYINT_API_KEY")
model_id = get_required_env("ANYINT_MODEL_ID")
client = OpenAI(
    base_url="https://api.anyint.ai/openai/v1",
    api_key=api_key,
    timeout=60.0,
)
try:
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant.",
            },
            {
                "role": "user",
                "content": "请只回复：AnyInt 接入成功",
            },
        ],
        stream=False,
    )
except Exception as exc:
    print(f"AnyInt 请求失败：{exc}", file=sys.stderr)
    raise SystemExit(2) from exc
content = response.choices[0].message.content
if not content:
    print("模型未返回文本内容", file=sys.stderr)
    raise SystemExit(3)
print(content)
```

运行程序：

```bash
python3 anyint_chat.py
```

如果程序能够正常返回文本，说明以下基础链路已经跑通：

1.  开发板可以访问 AnyInt；

2.  API Key 有效；

3.  模型 ID 正确；

4.  OpenAI SDK 配置正确；

5.  Chat Completions 接口可以正常返回结果。

AnyInt 的 OpenAI 兼容接口支持通过标准 OpenAI SDK 调用，普通文本聊天应优先使用 chat.completions.create()，而不是 Responses API。

## 5.3.3 接入自研 Agent

对于支持 OpenAI 兼容接口的 Agent 框架或 LLM 客户端，通常只需要配置以下三项：

| **配置项** | **配置值**                      |
|------------|---------------------------------|
| Base URL   | https://api.anyint.ai/openai/v1 |
| API Key    | 环境变量 ANYINT_API_KEY         |
| Model      | 环境变量 ANYINT_MODEL_ID        |

典型调用链路如下：

用户输入

↓

此芯 P1 上的 Agent 应用

↓

任务规划、记忆、RAG 或工具调用

↓

AnyInt OpenAI 兼容接口

↓

云端大模型

↓

结果返回 Agent

不同 Agent 框架的参数名称可能不同，但应确保最终请求使用正确的 Base URL、API Key 和模型 ID。建议先运行 anyint_chat.py，确认基础 API 正常后，再接入完整 Agent Workflow。
