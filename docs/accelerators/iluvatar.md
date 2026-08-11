# 4.1 天数智芯

本次大赛使用天数智芯 TY1100-NX 平台扩展本地 AI 推理能力。TY1100-NX 已集成天数智芯算力模块，开发者无需自行拆装加速设备。赛事设备默认运行 Debian 12，并预装与当前系统匹配的 CoreX 软件栈及 ARM64 大模型推理镜像。

| **项目**     | **赛事环境**              |
|--------------|---------------------------|
| 开发平台     | TY1100-NX                 |
| CPU 架构     | ARM64 / AArch64           |
| 操作系统     | Debian 12                 |
| 软件栈       | CoreX 4.4.0               |
| 默认安装目录 | /usr/local/corex          |
| 容器运行工具 | nerdctl + containerd      |
| 推荐推理方式 | 天数 ARM64 大模型推理容器 |
| 推荐推理框架 | 天数适配版 vLLM           |

本章以赛事设备中已经预置的 ARM64 大模型推理镜像为基础，介绍 CoreX 环境检查、推理容器启动、模型运行、OpenAI 兼容接口以及 Agent 应用接入方法。

参赛作品中，天数算力设备主要负责模型推理。Agent Workflow 编排、任务状态管理、工具调用、数据处理、记忆、RAG 和结果反馈等能力仍应由参赛作品实现。仅启动本地模型聊天服务，不等同于完成 Agentic AI 作品。

## 4.1.1 CoreX 和容器环境检查

赛事提供的 TY1100-NX 系统镜像已经预装与当前系统匹配的 CoreX 驱动、Runtime 和设备管理工具。开发者通常无需自行安装或升级驱动。

### 一、检查系统架构

执行：

```bash
uname -m
```

正常情况下应输出：

```text
aarch64
```

### 二、检查 CoreX 安装目录

执行：

```bash
ls -ld /usr/local/corex
当前赛事环境中，/usr/local/corex 通常为指向当前 CoreX 版本目录的软链接，例如：
/usr/local/corex -> /usr/local/corex-4.4.0/
```

如果 /usr/local/corex 不存在，说明当前系统环境可能不完整，应联系赛事技术支持恢复官方系统环境。

### 三、检查天数设备

执行：

```bash
command -v ixsmi
ixsmi
```

正常情况下，ixsmi 应能够识别天数算力设备，并显示以下信息：

- 驱动和 Runtime 版本；

- 设备内存及使用量；

- 设备利用率；

- 温度；

- 功耗；

- 当前运行进程；

- 设备错误状态。

如果当前终端无法找到 ixsmi，可以临时加载 CoreX 环境：

```bash
export PATH="/usr/local/corex/bin:$PATH"
export LD_LIBRARY_PATH="/usr/local/corex/lib64:${LD_LIBRARY_PATH:-}"
ixsmi
```

如果 ixsmi 能够执行但无法识别设备，可先重新启动系统：

```bash
sudo reboot
```

重新启动后仍无法识别设备时，应停止后续模型部署操作，并联系赛事技术支持。

开发者不要自行执行以下操作：

- 安装其他版本或其他平台的 CoreX 驱动；

- 升级系统内核；

- 强制卸载 CoreX 内核模块；

- 修改设备固件；

- 调整设备底层频率或功耗参数。

### 四、检查容器运行环境

当前 TY1100-NX 系统使用 nerdctl 和系统级 containerd 管理容器，不使用 Docker daemon 作为主要容器运行方式。

检查 nerdctl：

```bash
command -v nerdctl
nerdctl --version
```

检查系统级 containerd：

```bash
sudo nerdctl info
```

正常情况下，应能看到 Server Version、Storage Driver、Cgroup Driver、Architecture 等信息。

普通用户直接执行：

```bash
nerdctl info
```

可能出现 rootless containerd 未启动的提示。该现象不表示系统级 containerd 异常。本指南后续统一使用：

```bash
sudo nerdctl
```

不要将以下两种方式混用：

```bash
docker ...
sudo nerdctl ...
```

当前系统虽然可能安装 Docker CLI，但 Docker daemon 默认未运行，执行 docker images 或 docker run 可能出现：

```text
Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

此时应使用 sudo nerdctl，不要为完成本章操作自行启动或重新配置 Docker daemon。

## 4.1.2 检查赛事推理镜像

### 一、查看已有镜像

执行：

```bash
sudo nerdctl images
```

当前赛事设备中已经预置与 CoreX 4.4.0 匹配的 ARM64 大模型推理镜像。本章使用以下镜像：

```text
harbor.iluvatar.com.cn:10443/saas/mr-bi150-4.4.0-aarch64-ubuntu20.04-py3.10-poc-llm-infer:v1.2.4-202605280001-ty1100-4.4.0
```

该镜像与以下环境匹配：

- ARM64 / AArch64；

- TY1100-NX；

- CoreX 4.4.0；

- Python 3.10；

- 天数适配版大模型推理环境。

设备中可能同时存在旧版 CoreX 4.3.x 镜像或其他应用镜像。使用时应优先选择与当前 CoreX 4.4.0 环境匹配的镜像，不要使用旧版 4.3.x 镜像作为赛事默认环境。

### 二、设置镜像变量

执行：

```bash
export TIANSHU_IMAGE="harbor.iluvatar.com.cn:10443/saas/mr-bi150-4.4.0-aarch64-ubuntu20.04-py3.10-poc-llm-infer:v1.2.4-202605280001-ty1100-4.4.0"
```

检查变量：

```bash
echo "$TIANSHU_IMAGE"
```

检查镜像是否存在：

```bash
sudo nerdctl image inspect "$TIANSHU_IMAGE" \
>/dev/null 2>&1 \
&& echo "推理镜像检查通过"
```

如果没有显示“推理镜像检查通过”，再次执行：

```bash
sudo nerdctl images
```

确认镜像完整名称和 Tag 是否正确。

赛事设备已经预置该镜像时，无需重复拉取。若重新烧录系统后镜像缺失，应通过赛事资源包或赛事技术支持恢复，不建议自行使用其他 CoreX Release 的镜像替代。

### 三、检查已有容器

执行：

```bash
sudo nerdctl ps -a
```

部分赛事设备中可能已经创建 vllm_test、vllm_embed 等测试容器。

如果存在 vllm_test，可以直接进入：

```bash
sudo nerdctl start -ai vllm_test
```

如果容器状态为 Created，表示容器已经创建但尚未运行，可以通过上述命令启动。

已有测试容器的挂载目录和启动参数可能不同。进入容器后应先检查其 README、模型目录和软件版本，不要直接假定模型已经准备完成。

## 4.1.3 创建并进入推理容器

如果设备中没有可直接使用的测试容器，可以按照本节新建容器。

### 一、准备模型目录

在宿主机创建模型目录：

```bash
sudo mkdir -p /opt/models
sudo chown -R "$USER":"$USER" /opt/models
```

检查存储空间：

```text
df -h /opt/models
```

将完整模型目录放入：

```bash
/opt/models
```

例如：

```bash
/opt/models/Qwen2.5-7B-Instruct
```

模型目录通常应包括：

```text
config.json
tokenizer.json
tokenizer_config.json
generation_config.json
model*.safetensors
model.safetensors.index.json
```

不同模型的文件组成可能不同，应以模型仓库中的 README 为准。模型权重、Tokenizer 和配置文件必须属于同一个模型版本。

### 二、创建容器

删除可能存在的同名旧容器：

```bash
sudo nerdctl rm -f ty1100-llm 2>/dev/null || true
```

创建并进入推理容器：

```bash
sudo nerdctl run -it \
--name ty1100-llm \
--privileged \
--net host \
--shm-size 8g \
-v /opt/models:/models \
"$TIANSHU_IMAGE" \
/bin/bash
```

主要参数说明如下：

| **参数**               | **说明**                           |
|------------------------|------------------------------------|
| --name ty1100-llm      | 设置容器名称                       |
| --privileged           | 允许容器访问天数算力设备和相关驱动 |
| --net host             | 容器与宿主机共用网络               |
| --shm-size 8g          | 设置容器共享内存                   |
| -v /opt/models:/models | 将宿主机模型目录挂载至容器         |
| "\$TIANSHU_IMAGE"      | 使用赛事指定推理镜像               |
| /bin/bash              | 进入容器终端                       |

当前 TY1100-NX 系统内存约为 16 GB，不建议将 --shm-size 直接设置为 16 GB。模型规模、并发数和上下文较小时，也可以适当降低共享内存。

### 三、重新进入已有容器

退出容器后，如需再次进入，执行：

```bash
sudo nerdctl start ty1100-llm
sudo nerdctl exec -it ty1100-llm /bin/bash
```

查看容器状态：

```bash
sudo nerdctl ps -a
```

停止容器：

```bash
sudo nerdctl stop ty1100-llm
```

## 4.1.4 检查容器推理环境

进入容器后，首先执行以下检查。

### 一、检查设备

```bash
ixsmi
```

容器内应能正常识别天数算力设备。

### 二、检查 PyTorch 和 vLLM

执行：

```bash
python3 - <<'PY'
import torch
print("torch version:", torch.__version__)
print("cuda available:", torch.cuda.is_available())
print("device count:", torch.cuda.device_count())
PY
```

正常情况下：

- torch.cuda.is_available() 返回 True；

- torch.cuda.device_count() 大于 0。

为避免公开输出具体算力芯片型号，不建议在公开日志中执行：

```text
torch.cuda.get_device_name(0)
```

检查 vLLM：

```bash
python3 - <<'PY'
import vllm
print("vllm version:", vllm.__version__)
PY
```

检查主要 Python 软件包：

```bash
python3 -m pip list \
| grep -Ei \
"torch|vllm|transformers|corex"
```

不要在赛事推理容器中直接执行：

```bash
pip install --upgrade torch
pip install --upgrade vllm
pip install --upgrade transformers
```

普通 PyPI 软件包可能覆盖天数适配版本，导致：

- 无法识别算力设备；

- 天数定制算子缺失；

- 动态库版本冲突；

- vLLM 启动失败；

- 模型回退到 CPU；

- 原有容器环境损坏。

### 三、查看镜像说明

查找 README：

```bash
find /root /workspace /opt \
-maxdepth 3 \
-iname "README*" \
2>/dev/null
```

如果找到镜像说明，应优先阅读：

cat /root/README.md

如果文件位于其他位置，应将路径替换为实际路径。

不同镜像构建版本中的 vLLM 启动入口、参数、模型支持范围和已知问题可能不同，应以镜像内 README 和当前命令帮助为准。

### 四、检查模型目录

执行：

```bash
ls -lah /models
```

查看模型关键文件：

```bash
find /models \
-maxdepth 2 \
-type f \
\( \
-name "config.json" \
-o -name "tokenizer.json" \
-o -name "*.safetensors" \
\) \
| head -n 30
如果 /models 为空，应检查：
```

- 宿主机 /opt/models 中是否存在模型；

- -v /opt/models:/models 参数是否正确；

- 模型目录和文件权限是否正常。

## 4.1.5 运行最小离线推理

进入容器后，先查看实际模型目录：

```bash
ls -lah /models
```

根据实际模型目录名称设置变量。以下示例中的 your-model-directory 必须修改为真实目录名称：

```bash
MODEL_DIR_NAME="your-model-directory"
export MODEL_PATH="/models/$MODEL_DIR_NAME"
```

检查模型配置：

```bash
test -f "$MODEL_PATH/config.json" \
&& echo "模型目录检查通过" \
|| echo "未找到模型配置，请检查 MODEL_PATH"
```

创建测试程序：

```bash
cat > /tmp/ty_vllm_test.py <<'PY'
import os
import sys
from vllm import LLM, SamplingParams
model_path = os.getenv("MODEL_PATH")
if not model_path:
print("缺少环境变量 MODEL_PATH", file=sys.stderr)
raise SystemExit(1)
sampling_params = SamplingParams(
max_tokens=128,
temperature=0.7,
top_p=0.9,
)
llm = LLM(
model=model_path,
tensor_parallel_size=1,
max_model_len=2048,
gpu_memory_utilization=0.85,
dtype="auto",
)
outputs = llm.generate(
["请用一句话介绍你自己。"],
sampling_params,
)
if not outputs or not outputs[0].outputs:
print("模型未返回有效结果", file=sys.stderr)
raise SystemExit(2)
print(outputs[0].outputs[0].text)
PY
```

运行：

```bash
MODEL_PATH="$MODEL_PATH" \
python3 /tmp/ty_vllm_test.py
```

主要参数说明如下：

| **参数**                    | **说明**                         |
|-----------------------------|----------------------------------|
| tensor_parallel_size=1      | 使用单个算力设备                 |
| max_model_len=2048          | 首次验证使用较短上下文           |
| gpu_memory_utilization=0.85 | 为系统预留部分设备内存           |
| dtype="auto"                | 由框架根据模型和环境选择数据类型 |
| max_tokens=128              | 最多生成 128 个 Token            |

如果模型要求执行远程模型代码，应先检查模型来源和相关代码，再根据模型 README 决定是否增加：

```text
trust_remote_code=True
```

不要对来源不明的模型直接启用该选项。

如果上述 Python 接口与镜像版本不兼容，应以镜像 README 和当前 vLLM 版本说明为准，不要直接升级 vLLM。

## 4.1.6 启动 OpenAI 兼容服务

### 一、查看当前 vLLM 启动入口

先执行：

```bash
python3 -m \
vllm.entrypoints.openai.api_server \
--help
```

如果当前版本不支持该入口，再检查：

```bash
vllm serve --help
```

实际使用的启动入口和参数应以当前镜像帮助信息为准。

### 二、仅供当前设备访问

当 Agent 应用和 vLLM 服务均运行在同一台 TY1100-NX 上时，可以仅监听本机地址：

```bash
python3 -m \
vllm.entrypoints.openai.api_server \
--model "$MODEL_PATH" \
--served-model-name local-model \
--host 127.0.0.1 \
--port 12345 \
--tensor-parallel-size 1 \
--max-model-len 2048 \
--gpu-memory-utilization 0.85
```

### 三、供局域网其他设备访问

如果 Agent 应用运行在另一台 CIX P1 设备上，应让服务监听所有网络接口：

```bash
python3 -m \
vllm.entrypoints.openai.api_server \
--model "$MODEL_PATH" \
--served-model-name local-model \
--host 0.0.0.0 \
--port 12345 \
--tensor-parallel-size 1 \
--max-model-len 2048 \
--gpu-memory-utilization 0.85
```

主要参数说明如下：

| **参数**                      | **说明**                  |
|-------------------------------|---------------------------|
| --model                       | 模型目录                  |
| --served-model-name           | OpenAI 接口使用的模型名称 |
| --host 127.0.0.1              | 仅允许当前设备访问        |
| --host 0.0.0.0                | 允许局域网其他设备访问    |
| --port 12345                  | 服务端口                  |
| --tensor-parallel-size 1      | 使用单个算力设备          |
| --max-model-len 2048          | 最大上下文长度            |
| --gpu-memory-utilization 0.85 | 设备内存利用比例          |

使用 --host 0.0.0.0 时，服务会监听所有网络接口。该方式仅适用于可信的赛事局域网，应通过防火墙和网络隔离限制访问来源，不要将模型服务直接暴露至公网。

## 4.1.7 验证 OpenAI 兼容接口

在模型服务所在设备上另开一个终端。

查询模型列表：

```bash
curl -sS \
http://127.0.0.1:12345/v1/models \
| python3 -m json.tool
```

发送 Chat Completions 请求：

```bash
curl -sS \
http://127.0.0.1:12345/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{
"model": "local-model",
"messages": [
{
"role": "user",
"content": "请只回复：天数本地模型接入成功"
}
],
"max_tokens": 64,
"stream": false
}' \
| python3 -m json.tool
```

如果能够正常返回文本，说明：

1.  vLLM 服务已经启动；

2.  模型已经成功加载；

3.  OpenAI 兼容接口可以访问；

4.  天数算力设备可以作为本地模型 Provider 使用。

本地模型服务通常不要求真实 API Key。部分客户端强制要求填写 API Key 时，可以使用无敏感含义的占位值：

```text
EMPTY
```

## 4.1.8 接入 CIX P1 Agent 应用

根据 Agent 应用和模型服务的部署位置选择 Base URL。

**情况一：Agent 和 vLLM 运行在同一台 TY1100-NX 上**

Base URL 使用：

http://127.0.0.1:12345/v1

127.0.0.1 表示当前设备自身，适用于 Agent 应用和模型服务部署在同一台设备上的场景。

**情况二：Agent 运行在另一台 CIX P1 设备上**

先在 TY1100-NX 上查询局域网 IP：

```text
hostname -I
```

假设 TY1100-NX 的局域网 IP 为：

```text
192.168.1.105
```

则 Agent 应使用：

http://192.168.1.105:12345/v1

跨设备访问时，应确保：

- vLLM 服务使用 --host 0.0.0.0 启动；

- 两台设备位于可以互相访问的网络中；

- 服务端口没有被防火墙阻断；

- Base URL 使用 TY1100-NX 的实际局域网 IP，而不是访问端设备自身的 127.0.0.1。

对于支持 OpenAI 兼容接口的 Agent 框架，通常配置：

| **配置项** | **配置值**           |
|------------|----------------------|
| Base URL   | 根据上述部署方式填写 |
| API Key    | EMPTY                |
| Model      | local-model          |

建议在 Agent 项目的独立虚拟环境中安装 OpenAI SDK：

```bash
python3 -m venv ~/agent-venv
source ~/agent-venv/bin/activate
python3 -m pip install "openai>=1,<2"
```

Python 示例：

```python
from openai import OpenAI
client = OpenAI(
    base_url="http://127.0.0.1:12345/v1",
    api_key="EMPTY",
    timeout=120.0,
)
response = client.chat.completions.create(
    model="local-model",
    messages=[
        {
            "role": "user",
            "content": "请只回复：天数本地模型接入成功",
        }
    ],
    max_tokens=64,
    stream=False,
)
content = response.choices[0].message.content
if not content:
    raise RuntimeError("模型未返回文本内容")
print(content)
```

如果 Agent 运行在另一台设备上，应将示例中的 127.0.0.1 替换为 TY1100-NX 的实际局域网 IP。

推荐按照以下顺序完成接入：

1.  在 TY1100-NX 本机通过 curl 验证模型接口；

2.  从 Agent 所在设备验证网络和接口访问；

3.  使用 OpenAI Python SDK 验证调用；

4.  接入 Agent 框架；

5.  增加工具调用；

6.  增加记忆或 RAG；

7.  最后增加流式输出、多模态和并发能力。

Agent 应限制：

- 最大任务步骤数；

- 单次任务模型调用次数；

- 最大输入长度；

- 最大生成长度；

- 工具调用超时时间；

- 模型请求超时时间；

- 模型和工具重试次数。

避免模型或工具异常时进入无限循环。

## 4.1.9 性能测试和设备监控

### 一、监控设备状态

模型加载和推理期间，可以执行：

```text
watch -n 1 ixsmi
```

重点观察：

- 设备内存占用；

- 设备利用率；

- 温度；

- 功耗；

- 当前推理进程；

- 设备错误状态。

在公开文档、截图和测试报告中，应隐藏或裁剪具体芯片型号、内部代号以及不需要公开的设备标识。

### 二、服务预热

正式测试前，先执行一次预热请求：

```bash
curl -sS \
http://127.0.0.1:12345/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{
"model": "local-model",
"messages": [
{
"role": "user",
"content": "请用一句话介绍你自己。"
}
],
"max_tokens": 64,
"stream": false
}' \
>/dev/null
```

### 三、测试端到端时间

执行：

```text
time curl -sS \
http://127.0.0.1:12345/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{
"model": "local-model",
"messages": [
{
"role": "user",
"content": "请说明端侧智能体的三个主要特点。"
}
],
"max_tokens": 128,
"stream": false
}' \
>/tmp/ty-response.json
```

查看响应：

```bash
python3 -m json.tool \
/tmp/ty-response.json
```

如果当前 vLLM 版本提供 Benchmark 工具，可以先查看：

```bash
vllm bench serve --help
```

不同 vLLM 版本的 Benchmark 参数可能不同，正式测试前应以当前镜像帮助信息为准。

### 四、建议记录的指标

| **指标**         | **说明**                           |
|------------------|------------------------------------|
| 模型加载时间     | 从启动服务到模型能够接受请求的时间 |
| TTFT             | 从发送请求到收到首个 Token 的时间  |
| Prefill Tokens/s | 输入 Token 处理速度                |
| Decode Tokens/s  | 输出 Token 生成速度                |
| E2E Latency      | 完整请求端到端延迟                 |
| E2E Throughput   | 多请求场景整体吞吐                 |
| 设备内存占用     | 模型加载和推理期间的设备内存       |
| 设备利用率       | 模型推理期间的计算负载             |
| 功耗             | 模型推理期间的设备功耗             |
| 温度             | 模型推理期间的设备温度             |
| 并发数           | 同时处理的请求数量                 |
| 稳定性           | 连续运行期间是否出现错误或退出     |

正式比较时，应固定：

- CoreX 和推理镜像版本；

- 模型名称和版本；

- 模型权重格式；

- 上下文长度；

- 输入 Token 数；

- 生成 Token 数；

- 并发数；

- 服务参数；

- 系统负载；

- 散热和环境温度。

不同模型、不同镜像和不同参数下的结果不能直接横向比较。

## 4.1.10 常见问题

| **问题现象**                                 | **处理建议**                                                                           |
|----------------------------------------------|----------------------------------------------------------------------------------------|
| uname -m 不是 aarch64                        | 当前不是 TY1100-NX ARM64 环境，检查设备和系统镜像                                      |
| /usr/local/corex 不存在                      | 当前系统环境可能不完整，联系赛事技术支持恢复                                           |
| ixsmi 不存在                                 | 检查 /usr/local/corex/bin 和 PATH                                                      |
| ixsmi 可以执行但无法识别设备                 | 重新启动系统；仍失败时保存输出并联系赛事技术支持                                       |
| nerdctl info 提示 rootless containerd 未运行 | 使用 sudo nerdctl info 访问系统级 containerd                                           |
| docker images 无法连接 Docker daemon         | 当前系统不使用 Docker daemon，改用 sudo nerdctl images                                 |
| sudo nerdctl images 输出两次相同结果         | sudo nerdctl images 默认查询 default namespace，与 sudo nerdctl -n default images 相同 |
| 推理镜像不存在                               | 检查完整镜像名称和 Tag；必要时联系赛事技术支持恢复                                     |
| 容器状态为 Created                           | 使用 sudo nerdctl start -ai 容器名称 启动                                              |
| 提示容器名称已存在                           | 删除旧容器或更换名称                                                                   |
| 容器内无法执行 ixsmi                         | 确认宿主机正常，并使用 --privileged 创建容器                                           |
| 容器内看不到模型目录                         | 检查 /opt/models、挂载参数和文件权限                                                   |
| torch.cuda.is_available() 返回 False         | 检查是否使用赛事指定镜像及 CoreX 4.4.0 环境                                            |
| 无法导入 vLLM                                | 确认使用赛事 LLM 推理镜像，不要安装普通 PyPI vLLM 覆盖环境                             |
| 模型目录缺少 config.json                     | 模型下载或复制不完整                                                                   |
| 模型加载提示 trust_remote_code               | 检查模型来源和代码后，再决定是否开启                                                   |
| 模型加载时设备内存不足                       | 使用更小模型，降低上下文、并发数或设备内存利用率                                       |
| 服务启动后长时间无响应                       | 模型可能仍在加载，检查服务日志、ixsmi 和设备内存                                       |
| /v1/models 返回 404                          | 检查 vLLM 启动入口、端口和当前版本支持的接口                                           |
| Chat Completions 提示模型不存在              | 使用 /v1/models 返回的模型名称，或检查 --served-model-name                             |
| TY1100-NX 本机可访问，其他设备无法访问       | 使用 --host 0.0.0.0，并检查 IP、端口、防火墙和网络                                     |
| 模型有输出但设备利用率没有变化               | 检查模型是否实际使用天数算力设备或是否回退到 CPU                                       |
| 输出乱码或质量异常                           | 检查 Tokenizer、Prompt Template、模型版本和权重完整性                                  |
| 性能结果波动较大                             | 固定模型、输入、并发、软件版本、温度和后台负载                                         |
| 温度、功耗或设备状态异常                     | 立即停止压力任务并联系赛事技术支持                                                     |
| 公开截图中出现具体设备型号                   | 发布前裁剪或隐藏设备名称和内部标识                                                     |

天数智芯开发者社区：

https://developer.iluvatar.com/

天数智芯官方文档中心：

https://developer.iluvatar.com/docs

完整的 CoreX、ixsmi、vLLM、模型迁移和性能分析方法，应以赛事提供的推理镜像 README、天数智芯官方文档和赛事技术支持说明为准。
