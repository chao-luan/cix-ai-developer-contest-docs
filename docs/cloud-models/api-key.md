# 5.2 创建 API Key 并查询模型

登录 AnyInt 控制台，进入 API Key 管理页面创建 API Key。

在系统中设置环境变量：

```bash
export ANYINT_API_KEY="your-anyint-api-key"
```

不要通过以下命令输出完整 API Key：

```bash
echo "$ANYINT_API_KEY"
```

查询当前 API Key 可访问的模型：

```bash
curl -sS https://api.anyint.ai/openai/v1/models \
-H "Authorization: Bearer ${ANYINT_API_KEY}" \
| python3 -m json.tool
```

响应通常包含以下结构：

```json
{
"data": [
{
"id": "<MODEL_ID>",
"display_name": "<MODEL_DISPLAY_NAME>"
}
]
}
```

后续请求中的模型名称必须使用 data\[\].id，不能使用 display_name，也不要根据模型宣传名称自行猜测。

选择模型后设置环境变量：

```bash
export ANYINT_MODEL_ID="<MODEL_ID>"
```

Models API 是当前账号模型 ID 的查询入口，但正式开发前仍应使用目标接口完成一次最小请求，确认所选模型在当前协议下能够正常调用。
