# 3.1 LLM

本节介绍如何在 CIX P1 开发平台上运行本地大语言模型，主要包括 llama.cpp 和 MNN 两种推理路径。

本节使用 llama.cpp 和 MNN 社区版本进行部署。开发者可以从上游仓库获取当前最新源码，根据实际需要启用 CPU、KleidiAI、Vulkan 或 OpenCL 等能力。

由于 llama.cpp 和 MNN 均为持续更新的开源项目，不同版本的构建选项、程序名称、命令参数及后端支持可能发生变化。使用社区源码时，应记录实际使用的 Git Commit，并以当前版本的 README、构建说明和程序 --help 输出为准。

两种框架的主要区别如下：

| **路径**                 | **模型格式** | **适用场景**           | **使用建议**                |
|--------------------------|--------------|------------------------|-----------------------------|
| llama.cpp CPU / KleidiAI | GGUF         | 首次跑通和基础文本生成 | 推荐优先验证                |
| llama.cpp Vulkan         | GGUF         | Vulkan GPU 后端验证    | 可选，需确认 Vulkan Runtime |
| MNN CPU / KleidiAI       | MNN 模型目录 | MNN 模型加载和文本推理 | 使用经过验证的 MNN 模型     |
| MNN OpenCL               | MNN 模型目录 | OpenCL GPU 后端验证    | 可选，以板端实际结果为准    |

推荐验证顺序如下：

```text
llama.cpp CPU / KleidiAI
→ MNN CPU / KleidiAI
→ llama.cpp Vulkan
→ MNN OpenCL
```

建议先完成 CPU 路径验证，再验证 Vulkan 和 OpenCL。GPU 路径依赖 CIX GO 图形引擎、GPU 驱动及对应 Runtime，系统能够识别 GPU 并不代表推理框架一定已经成功使用 GPU。

## 3.1.1 llama.cpp

llama.cpp 是面向本地大语言模型推理的轻量级开源框架，主要用于运行 GGUF 格式模型。

本节介绍：

- llama.cpp 社区源码获取和编译；
- CPU / KleidiAI 推理；
- CPU 线程数和 taskset 绑核；
- Vulkan GPU 推理；
- CPU 与 Vulkan 性能测试。

KleidiAI 是面向 Arm CPU 的优化微内核库，属于 llama.cpp CPU 后端的性能优化能力，并不是独立的硬件推理后端。

Vulkan 用于将部分或全部模型层卸载至 GPU。

### 3.1.1.1 准备环境

开始前，请确认开发板已经启动至赛事指定的 Debian 12 系统，并具备网络连接和足够的磁盘空间。

建议预留：

- 模型存储空间：根据实际 GGUF 模型大小确定；
- 源码和编译空间：建议至少预留 5 GB；
- 运行内存：应大于模型文件、KV Cache 和运行时缓冲区所需空间之和。

安装基础依赖：

```bash
sudo apt update
sudo apt install -y \
git \
cmake \
build-essential \
wget \
ca-certificates \
util-linux
```

其中，util-linux 软件包提供后续绑核使用的 taskset 命令。

检查基础工具：

```bash
git --version
cmake --version
gcc --version
taskset --version
```

### 3.1.1.2 获取 llama.cpp 社区源码

创建工作目录：

```bash
mkdir -p ~/local-llm-test
cd ~/local-llm-test
```

获取社区源码：

```bash
git clone \
```

https://github.com/ggml-org/llama.cpp.git

进入源码目录：

```bash
cd ~/local-llm-test/llama.cpp
```

记录当前源码 Commit：

```bash
git rev-parse HEAD
```

建议将输出保存到文件：

```bash
git rev-parse HEAD \
| tee ~/local-llm-test/llama-cpp-commit.txt
```

如果源码目录已经存在，可更新至当前社区版本：

```bash
cd ~/local-llm-test/llama.cpp
git pull --ff-only
```

更新完成后再次记录 Commit，并重新执行编译。

### 3.1.1.3 编译 CPU / KleidiAI 版本

清理旧构建目录：

```bash
cd ~/local-llm-test/llama.cpp
rm -rf build-cpu
```

配置 Release 构建并启用 KleidiAI：

```text
cmake -S . -B build-cpu \
-DCMAKE_BUILD_TYPE=Release \
-DGGML_CPU_KLEIDIAI=ON
```

检查编译配置：

```bash
grep "GGML_CPU_KLEIDIAI" \
build-cpu/CMakeCache.txt
```

预期输出包含：

```text
GGML_CPU_KLEIDIAI:BOOL=ON
```

开始编译：

```bash
cmake --build build-cpu -j4
```

-j4 表示同时使用四个编译任务。

如果开发板内存充足，可以适当提高：

```bash
cmake --build build-cpu -j8
```

如果编译过程中出现进程被终止、Killed 或内存不足，应降低并行数：

```bash
cmake --build build-cpu -j2
```

检查主要编译产物：

```bash
ls -lh build-cpu/bin/llama-cli
ls -lh build-cpu/bin/llama-bench
```

查看程序版本和参数：

```bash
./build-cpu/bin/llama-cli --version
./build-cpu/bin/llama-cli --help
./build-cpu/bin/llama-bench --help
```

如果 llama-cli 和 llama-bench 均已生成，说明 CPU 版本编译完成。

### 3.1.1.4 准备 GGUF 模型

本节以 Qwen2.5-0.5B-Instruct-GGUF 的 Q4_K_M 量化模型作为基础验证模型。

该模型参数规模较小，适合优先验证模型下载、模型加载和文本生成链路。

创建模型目录：

```bash
mkdir -p ~/models/qwen2.5-0.5b
cd ~/models/qwen2.5-0.5b
```

模型页面：

https://modelscope.cn/models/Qwen/Qwen2.5-0.5B-Instruct-GGUF

下载 Q4_K_M 模型：

```bash
wget -c \
-O qwen2.5-0.5b-instruct-q4_k_m.gguf \
"https://modelscope.cn/models/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/master/qwen2.5-0.5b-instruct-q4_k_m.gguf"
```

检查模型文件：

```bash
ls -lh \
~/models/qwen2.5-0.5b/qwen2.5-0.5b-instruct-q4_k_m.gguf
```

进一步检查文件大小：

```bash
stat -c "%n: %s bytes" \
~/models/qwen2.5-0.5b/qwen2.5-0.5b-instruct-q4_k_m.gguf
```

如果模型文件只有几 KB，通常表示下载到了错误页面、网络连接中断或模型未完整下载。

删除异常文件后重新下载：

```bash
rm -f \
~/models/qwen2.5-0.5b/qwen2.5-0.5b-instruct-q4_k_m.gguf
```

如果赛事资源包已经提供经过验证的 GGUF 模型，建议优先使用赛事资源包中的模型，并将后续命令中的模型路径替换为实际路径。

设置模型路径变量：

```text
MODEL=~/models/qwen2.5-0.5b/qwen2.5-0.5b-instruct-q4_k_m.gguf
```

确认变量指向有效文件：

```bash
ls -lh "$MODEL"
```

### 3.1.1.5 检查 CPU 拓扑并设置绑核范围

CIX P1 包含 8 个 Cortex-A720 核心和 4 个 Cortex-A520 小核。CPU 推理时建议绑定 Cortex-A720 核心，避免推理线程被调度到低性能核心，从而影响性能和测试稳定性。

查看 CPU 编号和最高频率：

```text
lscpu -e=CPU,CORE,ONLINE,MAXMHZ,MINMHZ
```

在赛事指定的 CIX P1 Debian 12 环境中，CPU 核心对应关系如下：

| **CPU 编号** | **核心类型**           | **最高频率** |
|--------------|------------------------|--------------|
| 0、1         | Cortex-A720 高性能核心 | 约 2.6 GHz   |
| 10、11       | Cortex-A720 高性能核心 | 约 2.5 GHz   |
| 6、7         | Cortex-A720 核心       | 约 2.3 GHz   |
| 8、9         | Cortex-A720 核心       | 约 2.2 GHz   |
| 2–5          | Cortex-A520 小核       | 约 1.8 GHz   |

推荐使用全部 8 个 Cortex-A720 核心进行 CPU / KleidiAI 推理：

```text
CPU_LIST=0,1,6-11
THREAD_NUM=8
```

如需测试 4 核配置，绑定当前频率最高的 4 个 Cortex-A720 核心：

```text
CPU_LIST=0,1,10,11
THREAD_NUM=4
```

检查当前设置：

```bash
echo "CPU_LIST=$CPU_LIST"
echo "THREAD_NUM=$THREAD_NUM"
taskset -c "$CPU_LIST" true
```

CPU_LIST 中的 CPU 数量应与 THREAD_NUM 保持一致。

-t 仅用于设置 llama.cpp 的 CPU 推理线程数，不能代替 taskset 的 CPU 亲和性设置。

### 3.1.1.6 运行 CPU / KleidiAI 推理

进入 llama.cpp 源码目录：

```bash
cd ~/local-llm-test/llama.cpp
```

推荐使用 taskset 固定 CPU 范围，并使线程数与绑定 CPU 数量保持一致：

```bash
taskset -c "$CPU_LIST" \
./build-cpu/bin/llama-cli \
-m "$MODEL" \
-p "请用一句话介绍你自己。" \
-t "$THREAD_NUM" \
-n 128
```

主要参数说明如下：

| **参数**   | **说明**                          |
|------------|-----------------------------------|
| taskset -c | 限制进程只能在指定逻辑 CPU 上运行 |
| -m         | GGUF 模型文件路径                 |
| -p         | 输入提示词                        |
| -t         | CPU 推理线程数                    |
| -n         | 最大生成 Token 数                 |

如果模型能够正常加载并输出文本，说明 llama.cpp CPU 推理链路基本可用。

不同 llama.cpp 版本在对话模板、交互模式和单轮运行参数方面可能存在差异。如果程序生成结束后进入交互状态，可输入：

```text
exit
```

或按：

Ctrl+C

退出程序。

如果当前版本提供单轮运行参数，可通过以下命令查询：

```bash
./build-cpu/bin/llama-cli --help \
| grep -Ei "single|conversation|interactive"
```

不要直接假设不同版本均支持完全相同的单轮参数。

如果输出内容异常、出现大量重复文本或未按照指令回答，应检查：

1.  模型是否完整；
2.  当前版本是否识别模型内置 Chat Template；
3.  是否启用了不合适的交互模式；
4.  模型量化格式是否与当前版本兼容；
5.  当前版本的 llama-cli --help 是否提供对应的对话参数。

### 3.1.1.7 验证 KleidiAI

保存完整运行日志：

```bash
taskset -c "$CPU_LIST" \
./build-cpu/bin/llama-cli \
-m "$MODEL" \
-p "请用一句话介绍你自己。" \
-t "$THREAD_NUM" \
-n 128 \
2>&1 | tee ~/local-llm-test/llama-cpu.log
```

检查日志中的 KleidiAI 信息：

```bash
grep -i "KLEIDIAI" \
~/local-llm-test/llama-cpu.log
```

启用 KleidiAI 后，日志中可能出现类似内容：

```text
CPU_KLEIDIAI
```

GGML_CPU_KLEIDIAI=ON 表示编译时已经集成 KleidiAI 支持。

运行日志中出现 CPU_KLEIDIAI 相关信息，可以进一步说明当前运行过程加载了 KleidiAI CPU 后端。

由于社区版本可能调整日志格式，如果未搜索到 KleidiAI 字符串，应同时检查：

```bash
grep "GGML_CPU_KLEIDIAI" \
build-cpu/CMakeCache.txt
./build-cpu/bin/llama-cli --version
```

日志中没有出现 KleidiAI 信息并不一定代表程序运行失败，但不能仅凭模型成功输出判断 KleidiAI 已经实际生效。

正式性能验证时，应结合以下信息综合判断：

- llama.cpp Commit；
- CMake 配置；
- 运行日志；
- CPU 指令能力；
- 相同模型和参数下的性能结果。

### 3.1.1.8 CPU 性能测试

使用 llama-bench 进行基础测试：

```bash
cd ~/local-llm-test/llama.cpp
```

先执行一次预热：

```bash
taskset -c "$CPU_LIST" \
./build-cpu/bin/llama-bench \
-m "$MODEL" \
-p 128 \
-n 32 \
-t "$THREAD_NUM" \
-r 1
```

正式测试：

```bash
taskset -c "$CPU_LIST" \
./build-cpu/bin/llama-bench \
-m "$MODEL" \
-p 512 \
-n 128 \
-t "$THREAD_NUM" \
-r 3 \
| tee ~/local-llm-test/llama-cpu-bench.log
```

主要参数说明：

| **参数** | **说明**                                    |
|----------|---------------------------------------------|
| -p 512   | Prompt Processing 测试使用 512 个输入 Token |
| -n 128   | Text Generation 测试生成 128 个 Token       |
| -t       | CPU 推理线程数                              |
| -r 3     | 每项重复测试三次                            |

重点记录：

- pp512；
- tg128；
- Token/s；
- 线程数；
- CPU affinity；
- 模型名称及量化方式；
- llama.cpp Commit；
- 系统温度和后台负载。

CPU 绑核通常用于减少操作系统调度带来的波动，提高多次性能测试结果的一致性。

进行正式性能对比时，应固定：

- 模型文件；
- CPU 线程数；
- CPU 绑定范围；
- Prompt Token 数；
- 生成 Token 数；
- 系统电源状态；
- 散热状态；
- 后台进程负载。

### 3.1.1.9 可选：编译 Vulkan 版本

llama.cpp Vulkan 后端依赖 CIX GO 图形引擎提供的 GPU 驱动和 Vulkan Runtime。

执行本节前，应先确认 GO 图形引擎已经正常安装。随后按照本节命令安装

vulkan-tools，并使用 vulkaninfo 检查 Vulkan Runtime 和板载 GPU。

安装 Vulkan 编译和检查工具：

```bash
sudo apt update
sudo apt install -y \
vulkan-tools \
libvulkan-dev \
glslc \
spirv-headers
```

检查 Vulkan Runtime：

```bash
vulkaninfo --summary
```

如果当前版本的 vulkaninfo 不支持 --summary，可以执行：

```bash
vulkaninfo | head -n 100
```

输出中能够识别板载 GPU，且未出现 Vulkan Loader、ICD 或设备初始化错误，说明 Vulkan Runtime 基本可用。

进入源码目录并清理旧构建目录：

```bash
cd ~/local-llm-test/llama.cpp
rm -rf build-vulkan
```

配置 Vulkan 构建，同时保留 KleidiAI CPU 支持：

```text
cmake -S . -B build-vulkan \
-DCMAKE_BUILD_TYPE=Release \
-DGGML_VULKAN=ON \
-DGGML_CPU_KLEIDIAI=ON
```

检查编译配置：

```bash
grep -E "GGML_VULKAN|GGML_CPU_KLEIDIAI" \
build-vulkan/CMakeCache.txt
```

预期输出包含：

```text
GGML_VULKAN:BOOL=ON
GGML_CPU_KLEIDIAI:BOOL=ON
```

开始编译：

```bash
cmake --build build-vulkan -j4
```

检查编译产物：

```bash
ls -lh build-vulkan/bin/llama-cli
ls -lh build-vulkan/bin/llama-bench
```

### 3.1.1.10 运行 Vulkan 推理

Vulkan 推理的主要计算由 GPU 承担，但 CPU 仍负责 Tokenizer、任务调度、内存管理以及部分未卸载至 GPU 的计算。

Vulkan 推理默认将宿主进程绑定至当前最高频的 4 个 Cortex-A720 核心：

```text
GPU_CPU_LIST=0,1,10,11
GPU_THREAD_NUM=4
```

检查设置：

```bash
echo "GPU_CPU_LIST=$GPU_CPU_LIST"
echo "GPU_THREAD_NUM=$GPU_THREAD_NUM"
taskset -c "$GPU_CPU_LIST" true
```

执行 Vulkan 推理：

```bash
cd ~/local-llm-test/llama.cpp
taskset -c "$GPU_CPU_LIST" \
./build-vulkan/bin/llama-cli \
-m "$MODEL" \
-p "请用一句话介绍你自己。" \
-t "$GPU_THREAD_NUM" \
-n 128 \
-ngl 99 \
2>&1 | tee ~/local-llm-test/llama-vulkan.log
```

其中：

- taskset -c "\$GPU_CPU_LIST" 将宿主进程绑定至 CPU 0、1、10、11；
- -t "\$GPU_THREAD_NUM" 将 llama.cpp CPU 线程数设置为 4；
- -ngl 99 表示尝试将尽可能多的模型层卸载至 GPU。

实际能够卸载的模型层数取决于：

- 模型结构和模型大小；
- 可用内存；
- GPU 驱动版本；
- Vulkan Runtime；
- llama.cpp Commit；
- Vulkan 后端算子支持情况。

运行时重点检查：

1.  vulkaninfo 能够识别板载 GPU；
2.  CMakeCache.txt 中显示 GGML_VULKAN=ON；
3.  执行的是 build-vulkan/bin/llama-cli；
4.  日志中出现 Vulkan 设备信息；
5.  日志中显示模型层被卸载至 GPU；
6.  模型能够正常生成文本；
7.  未出现 Vulkan 初始化失败或完全回退至 CPU。

检查关键日志：

```bash
grep -Ei \
"vulkan|gpu|offload|layer|fallback|error" \
~/local-llm-test/llama-vulkan.log
```

满足以下条件，可以认为 Vulkan 推理路径基本跑通：

- Vulkan Runtime 能够识别 GPU；
- llama.cpp 已启用 Vulkan 后端；
- 运行日志显示 Vulkan 设备和模型层卸载信息；
- 模型能够完成文本生成。

如果出现：

warning: no usable GPU found

或者：

```bash
--gpu-layers option will be ignored
```

依次检查：

```bash
grep "GGML_VULKAN" \
~/local-llm-test/llama.cpp/build-vulkan/CMakeCache.txt
vulkaninfo --summary
ls -lh \
~/local-llm-test/llama.cpp/build-vulkan/bin/llama-cli
```

并确认实际执行的是：

```bash
./build-vulkan/bin/llama-cli
```

而不是：

```bash
./build-cpu/bin/llama-cli
```

如果 Vulkan 能够识别 GPU，但模型运行时因内存不足退出，可以降低卸载层数，例如：

```bash
taskset -c "$GPU_CPU_LIST" \
./build-vulkan/bin/llama-cli \
-m "$MODEL" \
-p "请用一句话介绍你自己。" \
-t "$GPU_THREAD_NUM" \
-n 128 \
-ngl 10
```

随后逐步提高 -ngl，观察内存占用、模型层卸载数量和运行结果。

### 3.1.1.11 CPU 与 Vulkan 性能对比

CPU / KleidiAI 测试使用全部 8 个 Cortex-A720 核心：

```text
CPU_LIST=0,1,6-11
THREAD_NUM=8
```

执行 CPU 测试：

```bash
taskset -c "$CPU_LIST" \
./build-cpu/bin/llama-bench \
-m "$MODEL" \
-p 512 \
-n 128 \
-t "$THREAD_NUM" \
-r 3 \
| tee ~/local-llm-test/llama-cpu-bench.log
```

Vulkan 测试将宿主进程绑定至当前最高频的 4 个 Cortex-A720 核心：

```text
GPU_CPU_LIST=0,1,10,11
GPU_THREAD_NUM=4
```

执行 Vulkan 测试：

```bash
taskset -c "$GPU_CPU_LIST" \
./build-vulkan/bin/llama-bench \
-m "$MODEL" \
-p 512 \
-n 128 \
-t "$GPU_THREAD_NUM" \
-ngl 99 \
-r 3 \
| tee ~/local-llm-test/llama-vulkan-bench.log
```

两次测试应使用相同的：

- 模型文件；
- 模型量化方式；
- Prompt Token 数；
- 生成 Token 数；
- 测试重复次数；
- 系统镜像；
- 系统电源状态；
- 散热状态；
- 后台进程负载。

CPU 和 Vulkan 使用不同的 CPU 绑定配置：

| **推理路径**   | **CPU 绑定范围** | **线程参数** |
|----------------|------------------|--------------|
| CPU / KleidiAI | 0,1,6-11         | -t 8         |
| Vulkan         | 0,1,10,11        | -t 4         |

该测试用于比较两条推荐部署路径的实际性能。由于两条路径承担主要计算的硬件不同，CPU 线程数和 CPU 绑定范围不要求完全一致，但必须在测试结果中分别记录。

如需严格控制 CPU 资源进行后端对比，可以额外将两条路径都绑定至相同的 4 个 Cortex-A720 核心：

```text
CPU_LIST=0,1,10,11
THREAD_NUM=4
```

但正式发布的默认测试配置仍建议使用：

- CPU / KleidiAI：8 个 Cortex-A720；
- Vulkan：4 个最高频 Cortex-A720。

llama-bench 的结果主要用于比较模型推理后端和参数配置，不等同于完整应用的端到端响应时间。

测试完成后，建议记录：

```bash
git rev-parse HEAD
uname -a
lscpu
vulkaninfo --summary
```

同时记录：

- 模型名称；
- 量化类型；
- CPU 推理线程数；
- CPU 绑定范围；
- -ngl 数值；
- Prompt Processing 性能；
- Text Generation 性能；
- 系统温度；
- 后台负载；
- 异常日志。

### 3.1.1.12 llama.cpp 常见问题

| **问题现象**            | **可能原因**                               | **建议处理方式**                   |
|-------------------------|--------------------------------------------|------------------------------------|
| 找不到 llama-cli        | 编译失败或构建路径错误                     | 检查编译日志及 build-cpu/bin       |
| 模型文件只有几 KB       | 模型未完整下载                             | 删除异常文件后重新下载             |
| 模型加载失败            | 模型路径错误、文件损坏或不是 GGUF          | 检查 -m、文件大小和模型格式        |
| 输出乱码或大量重复      | 模型不完整、Chat Template 不匹配或参数异常 | 检查模型、模板和当前版本帮助       |
| 日志中没有 CPU_KLEIDIAI | 未启用或日志格式变化                       | 检查 CMake 配置、Commit 和完整日志 |
| taskset 执行失败        | CPU 编号不存在或 CPU 不在线                | 使用 lscpu -e 检查 CPU 范围        |
| 线程数大于绑定核心数    | 配置不一致                                 | 调整 -t 或扩大 CPU_LIST            |
| vulkaninfo 找不到 GPU   | GPU 驱动或 Vulkan Runtime 异常             | 检查 GO 图形引擎和系统 Release     |
| -ngl 被忽略             | 未启用 Vulkan 或执行了错误二进制           | 检查构建参数和执行路径             |
| Vulkan 内存不足         | 模型或卸载层数过大                         | 使用更小模型或降低 -ngl            |
| 编译进程被终止          | 可用内存不足                               | 将编译并行数从 -j4 降至 -j2        |
| 多次测试波动较大        | 调度、温度或后台负载不同                   | 固定绑核、线程数和测试环境         |

## 3.1.2 MNN

MNN 是面向移动端、嵌入式设备和边缘设备的轻量级推理引擎，可运行经过转换的 MNN 大语言模型，并支持 CPU、OpenCL 等推理后端。

MNN LLM 使用包含模型结构、模型权重、Tokenizer 和运行配置的完整模型目录，不能直接加载 llama.cpp 使用的 GGUF 模型。

常见 MNN LLM 模型目录中可能包含：

```text
config.json
llm_config.json
llm.mnn
llm.mnn.weight
tokenizer.mtok
embeddings_bf16.bin
```

不同模型和不同 MNN 版本的文件组成可能存在差异，应以模型仓库中的 README 和 config.json 为准。

本节介绍：

- MNN 社区源码获取和编译；
- MNN 格式模型下载；
- CPU / KleidiAI 推理；
- taskset 绑核；
- OpenCL GPU 推理；
- CPU 与 OpenCL 性能测试。

### 3.1.2.1 准备环境并获取 MNN 源码

安装基础依赖：

```bash
sudo apt update
sudo apt install -y \
git \
git-lfs \
cmake \
build-essential \
wget \
ca-certificates \
clinfo \
ocl-icd-opencl-dev \
opencl-headers \
util-linux
```

初始化 Git LFS：

```bash
git lfs install
```

创建工作目录：

```bash
mkdir -p ~/mnn
cd ~/mnn
```

获取 MNN 社区源码：

```bash
git clone \
```

https://github.com/alibaba/MNN.git

进入源码目录：

```bash
cd ~/mnn/MNN
```

记录当前 Commit：

```bash
git rev-parse HEAD \
| tee ~/mnn/mnn-commit.txt
```

如果源码目录已经存在，可以更新：

```bash
cd ~/mnn/MNN
git pull --ff-only
```

更新后应重新记录 Commit，并重新编译。

### 3.1.2.2 编译 MNN CPU / KleidiAI 版本

清理旧构建目录：

```bash
cd ~/mnn/MNN
rm -rf build-cpu
```

配置 CPU、LLM 和 KleidiAI 构建：

```text
cmake -S . -B build-cpu \
-DCMAKE_BUILD_TYPE=Release \
-DMNN_BUILD_SHARED_LIBS=ON \
-DMNN_BUILD_LLM=ON \
-DMNN_LOW_MEMORY=ON \
-DMNN_SUPPORT_TRANSFORMER_FUSE=ON \
-DMNN_KLEIDIAI=ON \
-DMNN_KLEIDIAI_DEFAULT_ON=ON
```

主要构建选项如下：

| **构建选项**                    | **作用**                               |
|---------------------------------|----------------------------------------|
| MNN_BUILD_SHARED_LIBS=ON        | 构建动态库                             |
| MNN_BUILD_LLM=ON                | 构建 MNN LLM 引擎、llm_demo 和相关工具 |
| MNN_LOW_MEMORY=ON               | 启用低内存相关能力                     |
| MNN_SUPPORT_TRANSFORMER_FUSE=ON | 启用 Transformer 融合优化              |
| MNN_KLEIDIAI=ON                 | 集成 Arm KleidiAI                      |
| MNN_KLEIDIAI_DEFAULT_ON=ON      | 默认优先使用 KleidiAI Kernel           |

检查配置：

```bash
grep -E \
"^MNN_(BUILD_SHARED_LIBS|BUILD_LLM|LOW_MEMORY|SUPPORT_TRANSFORMER_FUSE|KLEIDIAI|KLEIDIAI_DEFAULT_ON):" \
build-cpu/CMakeCache.txt
```

开始编译：

```bash
cmake --build build-cpu -j4
```

如果编译时出现内存不足，可以降低并行数：

```bash
cmake --build build-cpu -j2
```

检查编译产物：

```bash
find ~/mnn/MNN/build-cpu \
-maxdepth 3 \
-type f \
\( -name "llm_demo" -o -name "llm_bench" \)
```

设置程序路径：

```bash
LLM_DEMO="$(find ~/mnn/MNN/build-cpu \
-type f -name llm_demo \
| head -n 1)"
LLM_BENCH="$(find ~/mnn/MNN/build-cpu \
-type f -name llm_bench \
| head -n 1)"
```

检查：

```bash
echo "$LLM_DEMO"
echo "$LLM_BENCH"
test -x "$LLM_DEMO"
test -x "$LLM_BENCH"
```

查看帮助：

```bash
"$LLM_DEMO" --help || true
"$LLM_BENCH" --help || true
```

### 3.1.2.3 检查动态库加载

如果系统中已经安装其他版本的 MNN，源码编译的 llm_demo 可能错误加载系统中的旧版 libMNN.so，从而出现：

- undefined symbol；
- 程序异常退出；
- 模型加载失败；
- OpenCL 后端缺失；
- 运行结果与构建配置不一致。

检查动态库：

```bash
ldd "$LLM_DEMO" \
| grep -E "libMNN|libllm|Express|not found"
```

MNN 相关动态库应优先指向当前 build-cpu 目录。

如果出现 not found，或者加载了系统中其他版本的 MNN 库，可以在当前终端设置：

```bash
export LD_LIBRARY_PATH="$HOME/mnn/MNN/build-cpu:$HOME/mnn/MNN/build-cpu/express:${LD_LIBRARY_PATH:-}"
```

再次检查：

```bash
ldd "$LLM_DEMO" \
| grep -E "libMNN|libllm|Express|not found"
```

不建议在没有确认影响范围的情况下永久写入 ~/.bashrc，避免影响系统中其他依赖 MNN 的程序。

### 3.1.2.4 准备 MNN 模型

本节以 Qwen2.5-0.5B-Instruct-MNN 作为基础验证模型。

如果赛事资源包已经提供经过验证的 MNN 模型，建议优先使用赛事模型，并将后续路径替换为实际路径。

创建工作目录并下载模型：

```bash
mkdir -p ~/mnn
cd ~/mnn
git clone \
```

https://www.modelscope.cn/MNN/Qwen2.5-0.5B-Instruct-MNN.git

进入模型目录并下载完整权重：

```bash
cd ~/mnn/Qwen2.5-0.5B-Instruct-MNN
git lfs pull
```

检查 Git LFS 文件：

```bash
git lfs ls-files
```

查看模型目录：

```bash
ls -lh
```

检查是否仍存在 Git LFS 指针文件：

```bash
grep -Il \
"^version https://git-lfs.github.com/spec/v1" \
./* 2>/dev/null
```

如果该命令输出了模型文件名称，说明实际权重没有完整下载，应重新执行：

```bash
git lfs pull
```

设置模型目录：

```text
MODEL_DIR=~/mnn/Qwen2.5-0.5B-Instruct-MNN
```

确认主要配置文件：

```bash
ls -lh "$MODEL_DIR/config.json"
```

### 3.1.2.5 创建 MNN CPU 配置

MNN CPU / KleidiAI 推理默认绑定全部 8 个 Cortex-A720 核心：

```text
CPU_LIST=0,1,6-11
THREAD_NUM=8
```

其中，实际绑定的逻辑 CPU 为：

0,1,6,7,8,9,10,11

CPU 2、3、4、5 为 Cortex-A520 小核，不纳入默认 CPU / KleidiAI 推理的绑核范围。

如需测试 4 核配置，应绑定当前最高频的 4 个 Cortex-A720 核心：

```text
CPU_LIST=0,1,10,11
THREAD_NUM=4
```

检查当前设置：

```bash
echo "CPU_LIST=$CPU_LIST"
echo "THREAD_NUM=$THREAD_NUM"
taskset -c "$CPU_LIST" true
```

本节后续默认使用 8 个 Cortex-A720 核心：

```text
CPU_LIST=0,1,6-11
THREAD_NUM=8
```

为避免直接修改原始配置，复制 CPU 配置：

```bash
cd "$MODEL_DIR"
cp config.json config-cpu.json
```

根据 THREAD_NUM 修改配置：

```bash
python3 - "$THREAD_NUM" <<'PY'
import json
import sys
from pathlib import Path
thread_num = int(sys.argv[1])
path = Path("config-cpu.json")
with path.open("r", encoding="utf-8") as file:
config = json.load(file)
config["backend_type"] = "cpu"
config["thread_num"] = thread_num
config.setdefault("precision", "low")
config.setdefault("memory", "low")
with path.open("w", encoding="utf-8") as file:
json.dump(config, file, indent=4, ensure_ascii=False)
print(json.dumps(config, indent=4, ensure_ascii=False))
PY
```

检查配置：

```bash
grep -nE \
'"backend_type"|"thread_num"|"precision"|"memory"' \
"$MODEL_DIR/config-cpu.json"
```

使用默认 8 核配置时，预期包含：

```text
"backend_type": "cpu",
"thread_num": 8
```

创建测试 Prompt：

```bash
cat > ~/mnn/text_baseline_prompt.txt <<'EOF'
```

请用一句话介绍你自己。

EOF

进行 MNN CPU / KleidiAI 推理时，应确保以下三项一致：

- CPU_LIST 中包含的 CPU 数量；
- config-cpu.json 中的 thread_num；
- llm_bench 命令中的 -t 参数。

默认配置为：

```bash
taskset CPU 数量：8
config-cpu.json thread_num：8
llm_bench -t：8
```

### 3.1.2.6 运行 MNN CPU / KleidiAI 推理

设置当前构建目录的动态库路径：

```bash
export LD_LIBRARY_PATH="$HOME/mnn/MNN/build-cpu:$HOME/mnn/MNN/build-cpu/express:${LD_LIBRARY_PATH:-}"
```

执行绑核后的 CPU 推理：

```bash
taskset -c "$CPU_LIST" \
"$LLM_DEMO" \
"$MODEL_DIR/config-cpu.json" \
~/mnn/text_baseline_prompt.txt
```

保存完整日志：

```bash
taskset -c "$CPU_LIST" \
"$LLM_DEMO" \
"$MODEL_DIR/config-cpu.json" \
~/mnn/text_baseline_prompt.txt \
2>&1 | tee ~/mnn/mnn-cpu.log
```

如果模型能够正常加载并输出文本，说明 MNN CPU 推理链路基本可用。

检查 KleidiAI 信息：

```bash
grep -i "kleidiai" \
~/mnn/mnn-cpu.log
```

同时检查构建配置：

```bash
grep -E \
"^MNN_KLEIDIAI(:|_DEFAULT_ON:)" \
~/mnn/MNN/build-cpu/CMakeCache.txt
```

其中：

```text
MNN_KLEIDIAI=ON
```

表示构建时集成了 KleidiAI；

```text
MNN_KLEIDIAI_DEFAULT_ON=ON
```

表示运行时默认优先使用 KleidiAI Kernel。

但不能仅凭模型能够输出文本判断 KleidiAI 已经生效。正式测试时，应结合：

- MNN Commit；
- CMake 配置；
- 运行日志；
- CPU 指令能力；
- 线程数和绑核范围；
- 相同模型下的性能数据。

### 3.1.2.7 MNN CPU 性能测试

先查看当前版本参数：

```bash
"$LLM_BENCH" --help
```

使用相同 CPU 绑定范围执行测试：

```bash
taskset -c "$CPU_LIST" \
"$LLM_BENCH" \
-m "$MODEL_DIR/config-cpu.json" \
-a cpu \
-t "$THREAD_NUM" \
-p 32,128 \
-n 32 \
-rep 3 \
-kv true \
-fp ~/mnn/mnn-cpu-bench.md
```

主要参数说明如下：

| **参数** | **说明**                      |
|----------|-------------------------------|
| -m       | 模型目录中的 config.json 路径 |
| -a cpu   | 使用 CPU 后端                 |
| -t       | CPU 推理线程数                |
| -p       | Prompt 长度                   |
| -n       | 生成长度                      |
| -rep     | 每项重复测试次数              |
| -kv true | Decode 阶段考虑历史 KV Cache  |
| -fp      | 将结果写入指定文件            |

如果当前社区版本不支持其中某个参数，应删除该参数，并以：

"\$LLM_BENCH" --help

的实际输出为准。

正式测试时，config-cpu.json 中的 thread_num、llm_bench -t 和 taskset 绑定的 CPU 数量应保持一致。

### 3.1.2.8 可选：编译 MNN OpenCL 版本

MNN OpenCL 后端依赖 CIX GO 图形引擎提供的 GPU 驱动和 OpenCL Runtime。

检查 OpenCL Runtime：

```bash
clinfo
```

过滤关键信息：

```bash
clinfo | grep -E \
"Platform Name|Platform Version|Device Name|Device Version|Driver Version"
```

如果能够识别 OpenCL Platform 和板载 GPU Device，且未出现 Loader 或设备初始化错误，说明 OpenCL Runtime 基本可用。

清理构建目录：

```bash
cd ~/mnn/MNN
rm -rf build-opencl
```

配置 OpenCL、LLM 和 KleidiAI 构建：

```text
cmake -S . -B build-opencl \
-DCMAKE_BUILD_TYPE=Release \
-DMNN_BUILD_SHARED_LIBS=ON \
-DMNN_BUILD_LLM=ON \
-DMNN_OPENCL=ON \
-DMNN_USE_SYSTEM_LIB=ON \
-DMNN_SEP_BUILD=OFF \
-DMNN_LOW_MEMORY=ON \
-DMNN_SUPPORT_TRANSFORMER_FUSE=ON \
-DMNN_KLEIDIAI=ON \
-DMNN_KLEIDIAI_DEFAULT_ON=ON
```

检查配置：

```bash
grep -E \
"^MNN_(BUILD_LLM|OPENCL|USE_SYSTEM_LIB|SEP_BUILD|KLEIDIAI|KLEIDIAI_DEFAULT_ON):" \
build-opencl/CMakeCache.txt
```

预期至少包含：

MNN_BUILD_LLM:BOOL=ON

MNN_OPENCL:BOOL=ON

MNN_USE_SYSTEM_LIB:BOOL=ON

MNN_SEP_BUILD:BOOL=OFF

开始编译：

```bash
cmake --build build-opencl -j4
```

如果内存不足：

```bash
cmake --build build-opencl -j2
```

查找程序：

```bash
LLM_DEMO_OPENCL="$(find ~/mnn/MNN/build-opencl \
-type f -name llm_demo \
| head -n 1)"
LLM_BENCH_OPENCL="$(find ~/mnn/MNN/build-opencl \
-type f -name llm_bench \
| head -n 1)"
```

检查：

```bash
echo "$LLM_DEMO_OPENCL"
echo "$LLM_BENCH_OPENCL"
test -x "$LLM_DEMO_OPENCL"
test -x "$LLM_BENCH_OPENCL"
```

设置动态库路径：

```bash
export LD_LIBRARY_PATH="$HOME/mnn/MNN/build-opencl:$HOME/mnn/MNN/build-opencl/express:${LD_LIBRARY_PATH:-}"
```

检查动态库：

```bash
ldd "$LLM_DEMO_OPENCL" \
| grep -E "libMNN|libllm|OpenCL|not found"
```

### 3.1.2.9 创建 OpenCL 配置

复制原始模型配置：

```bash
cd "$MODEL_DIR"
cp config.json config-opencl.json
```

修改 OpenCL 配置：

```bash
python3 - <<'PY'
import json
from pathlib import Path
path = Path("config-opencl.json")
with path.open("r", encoding="utf-8") as file:
config = json.load(file)
config["backend_type"] = "opencl"
config["thread_num"] = 4
config.setdefault("precision", "low")
config.setdefault("memory", "low")
with path.open("w", encoding="utf-8") as file:
json.dump(config, file, indent=4, ensure_ascii=False)
print(json.dumps(config, indent=4, ensure_ascii=False))
PY
```

检查配置：

```bash
grep -nE \
'"backend_type"|"thread_num"|"precision"|"memory"' \
"$MODEL_DIR/config-opencl.json"
```

预期包含：

```text
"backend_type": "opencl"
```

需要注意：

在 MNN OpenCL LLM 测试中，thread_num=4 或 llm_bench -t 4 不应简单理解为使用四个 CPU 线程。对于 OpenCL 后端，该参数与 GPU Mode 有关，当前社区版本通常推荐使用 4，但应以当前版本文档和 llm_bench --help 为准。

### 3.1.2.10 运行 MNN OpenCL 推理

OpenCL 推理的主要计算由 GPU 承担，但 CPU 仍可能负责：

- Tokenizer；
- 模型调度；
- 内存管理；
- 数据搬运；
- 部分 OpenCL 不支持的算子。

OpenCL 推理默认将宿主进程绑定至当前最高频的 4 个 Cortex-A720 核心：

```text
GPU_CPU_LIST=0,1,10,11
```

检查绑定范围：

```bash
echo "GPU_CPU_LIST=$GPU_CPU_LIST"
taskset -c "$GPU_CPU_LIST" true
```

执行 OpenCL 推理并保存日志：

```bash
taskset -c "$GPU_CPU_LIST" \
"$LLM_DEMO_OPENCL" \
"$MODEL_DIR/config-opencl.json" \
~/mnn/text_baseline_prompt.txt \
2>&1 | tee ~/mnn/mnn-opencl.log
```

检查日志：

```bash
grep -Ei \
"opencl|backend|device|fallback|error" \
~/mnn/mnn-opencl.log
```

模型能够输出文本，只能说明推理流程能够运行，不能单独证明 OpenCL 已实际参与计算。

满足以下条件，可以认为 MNN OpenCL 推理路径基本跑通：

1.  clinfo 能够识别 OpenCL Platform 和 GPU Device；
2.  构建配置中显示 MNN_OPENCL=ON；
3.  使用的是 build-opencl 中编译的程序；
4.  config-opencl.json 中设置了 backend_type=opencl；
5.  运行日志显示 OpenCL 后端或 GPU Device 已初始化；
6.  未出现 OpenCL 初始化失败或完全回退至 CPU；
7.  模型能够正常生成文本。

OpenCL 推理过程中，日志中出现 CPU 信息不一定表示 OpenCL 失败。重点应确认是否出现 OpenCL 初始化失败，或者整个模型完全回退至 CPU。

需要注意：

```text
"thread_num": 4
```

以及 llm_bench 命令中的：

```text
-t 4
```

在当前 MNN OpenCL LLM 路径中与 OpenCL GPU Mode 有关，不能简单理解为使用 4 个 CPU 推理线程。

真正限制宿主进程 CPU 运行范围的是：

```bash
taskset -c "$GPU_CPU_LIST"
```

即：

```bash
taskset -c 0,1,10,11
```

OpenCL 首次运行时可能执行 Kernel Tuning 并生成缓存，因此首次运行结果通常不适合作为正式性能数据。建议先运行一次预热，再执行正式测试。

### 3.1.2.11 CPU 与 OpenCL 性能对比

MNN CPU / KleidiAI 测试使用全部 8 个 Cortex-A720 核心：

```text
CPU_LIST=0,1,6-11
THREAD_NUM=8
```

执行 CPU 测试：

```bash
taskset -c "$CPU_LIST" \
"$LLM_BENCH" \
-m "$MODEL_DIR/config-cpu.json" \
-a cpu \
-t "$THREAD_NUM" \
-p 32,128 \
-n 32 \
-rep 3 \
-kv true \
-fp ~/mnn/mnn-cpu-bench.md
```

OpenCL 测试将宿主进程绑定至当前最高频的 4 个 Cortex-A720 核心：

```text
GPU_CPU_LIST=0,1,10,11
```

OpenCL 预热：

```bash
taskset -c "$GPU_CPU_LIST" \
"$LLM_BENCH_OPENCL" \
-m "$MODEL_DIR/config-opencl.json" \
-a opencl \
-t 4 \
-p 32 \
-n 16 \
-rep 1 \
-kv true
```

OpenCL 正式测试：

```bash
taskset -c "$GPU_CPU_LIST" \
"$LLM_BENCH_OPENCL" \
-m "$MODEL_DIR/config-opencl.json" \
-a opencl \
-t 4 \
-p 32,128 \
-n 32 \
-rep 3 \
-kv true \
-fp ~/mnn/mnn-opencl-bench.md
```

正式对比时，应固定：

- 模型及量化配置；
- Prompt 长度；
- 生成长度；
- 测试重复次数；
- MNN Commit；
- 系统镜像；
- GPU Runtime；
- 系统电源状态；
- 系统温度和散热状态；
- 后台进程负载。

CPU 和 OpenCL 使用不同的 CPU 绑定配置：

| **推理路径**   | **CPU 绑定范围** | **线程或模式参数** |
|----------------|------------------|--------------------|
| CPU / KleidiAI | 0,1,6-11         | thread_num=8、-t 8 |
| OpenCL         | 0,1,10,11        | thread_num=4、-t 4 |

CPU 测试中的 -t 表示 CPU 推理线程数，应与以下两项保持一致：

- config-cpu.json 中的 thread_num；
- taskset 绑定的 CPU 数量。

即默认 CPU 配置为：

```text
CPU_LIST=0,1,6-11
THREAD_NUM=8
config-cpu.json thread_num=8
llm_bench -t 8
```

OpenCL 测试中的 -t 4 与 OpenCL GPU Mode 有关，不能直接与 CPU 测试中的 4 个或 8 个 CPU 推理线程作等价解释。

OpenCL 宿主进程实际绑定的 CPU 范围由以下命令决定：

```bash
taskset -c "$GPU_CPU_LIST"
```

默认对应：

CPU 0、1、10、11

该测试用于比较两条推荐部署路径的实际性能。由于 CPU 和 OpenCL 路径承担主要计算的硬件不同，CPU 线程数和 CPU 绑定范围不要求完全一致，但必须分别记录。

如需严格控制 CPU 资源进行后端对比，可以额外将 CPU 和 OpenCL 路径都绑定至相同的 4 个 Cortex-A720 核心：

```text
CPU_LIST=0,1,10,11
THREAD_NUM=4
GPU_CPU_LIST=0,1,10,11
```

此时还需要将 config-cpu.json 中的：

```text
"thread_num": 8
```

修改为：

```text
"thread_num": 4
```

并将 CPU Benchmark 命令中的：

```text
-t 8
```

修改为：

-t 4

正式发布的默认测试配置仍建议使用：

- MNN CPU / KleidiAI：全部 8 个 Cortex-A720；
- MNN OpenCL：4 个最高频 Cortex-A720。

测试结果用于比较当前设备和当前环境下不同后端的相对性能，不应直接作为不同开发板、不同模型或不同软件版本之间的统一性能基准。

### 3.1.2.12 MNN 常见问题

| **问题现象**                    | **可能原因**                     | **处理建议**                   |
|---------------------------------|----------------------------------|--------------------------------|
| 找不到 llm_demo                 | 未启用 MNN_BUILD_LLM 或编译失败  | 检查 CMake 配置和编译日志      |
| 找不到 llm_bench                | 当前版本未生成或构建失败         | 使用 find 查找并检查编译日志   |
| 模型文件只有几百字节            | 下载到 Git LFS 指针              | 在模型目录执行 git lfs pull    |
| MNN 无法加载 GGUF               | 模型格式不兼容                   | 使用完整 MNN 模型目录          |
| 找不到配置或权重                | 模型目录不完整或相对路径失效     | 保持配置文件位于模型原目录     |
| 动态库显示 not found            | 当前构建库不在搜索路径           | 临时设置 LD_LIBRARY_PATH       |
| 出现 undefined symbol           | 程序与 libMNN.so 版本不一致      | 使用 ldd 检查实际库路径        |
| CPU 可以运行但无法确认 KleidiAI | 仅编译了支持，日志未说明实际使用 | 检查构建配置、日志和性能       |
| taskset 失败                    | CPU 编号不存在或 CPU 不在线      | 使用 lscpu -e 检查范围         |
| CPU 配置线程数不一致            | thread_num、-t 和绑核数量不同    | 统一三者配置                   |
| clinfo 找不到设备               | OpenCL Runtime、ICD 或驱动异常   | 检查 GO 图形引擎和系统版本     |
| OpenCL 初始化失败               | 未构建 OpenCL 或 Runtime 异常    | 检查 MNN_OPENCL、clinfo 和日志 |
| OpenCL 回退至 CPU               | 后端初始化失败或算子不支持       | 检查完整日志和后端信息         |
| OpenCL 首次运行较慢             | 正在执行 Kernel Tuning           | 预热一次后重新测试             |
| 性能波动较大                    | 温度、调度、绑核或负载不同       | 固定测试条件并重复测试         |
