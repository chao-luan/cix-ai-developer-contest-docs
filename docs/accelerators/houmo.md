# 4.2 后摩

本次大赛提供后摩 LQ50 M.2 卡和 LM5030 PCIe 智能加速卡，用于扩展 CIX P1 平台的本地模型推理能力。两款板卡均基于后摩 M50 平台，使用后摩大道和揽月软件栈，驱动、设备管理和推理框架的基本使用方式一致，主要区别在于硬件形态和赛事适配平台。

| **板卡** | **接口**                  | **赛事适配平台**        |
|----------|---------------------------|-------------------------|
| LQ50     | M.2 2280 M-Key，PCIe 通信 | 瑞莎星睿 O6N            |
| LM5030   | PCIe                      | 瑞莎星睿 O6、铭凡 MS-R1 |

后摩 M50 软件包通常使用 xh2 标识目标平台。CIX P1 为 ARM64 架构，下载驱动和揽月软件时，应选择：

关联芯片：M50

板级：LM5030/LQ50

平台架构：aarch64

本章按照以下流程介绍后摩加速卡的使用：

1. 检查硬件和已有驱动
2. 安装或恢复驱动
3. 选择揽月推理组件
4. 部署 HLIELlama
5. 下载并运行后摩适配模型
6. 启动 OpenAI 兼容接口
7. 接入 CIX P1 上的 Agent 应用

如果赛事设备已经预装驱动，且 hm_smi -a 检查正常，可以跳过驱动安装，直接进入 4.2.2 节。

## 4.2.1 驱动安装

### 4.2.1.1 检查硬件和现有驱动

安装驱动前，先安装 PCIe 检查工具：

```bash
sudo apt update
sudo apt install -y pciutils
```

检查 PCIe 设备：

```bash
lspci -nn | grep -i "1f6b:0c00"
```

也可以查看 PCIe 拓扑：

```bash
lspci -tv
```

如果能够看到 1f6b:0c00，说明操作系统已经识别到后摩 M50 设备，PCIe 硬件链路基本正常。

继续检查后摩设备管理工具：

```bash
command -v hm_smi
hm_smi -a
```

如果 hm_smi -a 能够显示以下信息，说明当前驱动环境基本可用：

- 后摩软件和 SMI 版本；
- 驱动版本；
- 固件版本；
- 板卡型号；
- PCIe BDF、速率和 Lane 数量；
- IPU 核心数量和利用率；
- 设备内存；
- 温度；
- 板卡功耗。

此时无需重新安装驱动，可以直接进入 4.2.2 节。

根据检查结果进行处理：

| **检查结果**                 | **处理方式**                                                |
|------------------------------|-------------------------------------------------------------|
| lspci 无输出                 | 检查板卡安装、供电、散热、BIOS 和 PCIe 通道，不继续安装驱动 |
| lspci 正常，hm_smi -a 正常   | 驱动已经可用，跳过安装                                      |
| lspci 正常，但 hm_smi 不存在 | 安装赛事提供的驱动包                                        |
| hm_smi 存在但无法识别设备    | 检查驱动、固件和 Runtime 版本，必要时重新安装               |
| 温度或功耗明显异常           | 停止模型任务并联系赛事维护人员                              |

lspci 无法识别设备属于硬件链路问题，不能通过反复安装驱动解决。

### 4.2.1.2 下载驱动安装包

后摩开发者社区：[点击此处跳转](https://developer.houmoai.com/) 

后摩资源中心：[点击此处跳转](https://developer.houmoai.com/resources_v2) 

在资源中心下载驱动时，应确认以下条件：

| **筛选项** | **选择要求**            |
|------------|-------------------------|
| 板级产品   | LQ50或LM5030            |
| 平台架构   | ARM / ARM64 / aarch64   |
| 操作系统   | Linux，若没有选择ubuntu |
| 资源类型   | 芯片驱动                |

驱动文件名通常类似：

houmo-drv-xh2\_\<release\>\_\<distro\>\_aarch64.run

其中：

- xh2 表示 M50 平台；
- \<release\> 表示后摩软件 Release；
- \<distro\> 表示适配的操作系统；
- aarch64 表示 ARM64 架构。

后摩官方驱动文档主要覆盖 Ubuntu、Kylin、UOS 等系统。赛事使用 Debian 12 时，应优先使用赛事技术团队已经在当前系统和内核上验证过的驱动包，不要自行选择其他发行版的软件包混装。

### 4.2.1.3 安装前准备

创建安装目录：

```bash
mkdir -p ~/houmo-install
cd ~/houmo-install
```

将赛事提供的驱动安装包复制到该目录。

安装基础依赖：

```bash
sudo apt update
sudo apt install -y \
pciutils \
python3 \
python3-dev \
python3-pip
```

检查 Python 和 pip：

```bash
python3 --version
python3 -m pip --version
```

后摩驱动文档要求 Python 3.9 及以上，并推荐 Python 3.9。赛事 Debian 12 系统如果已经使用更高版本的 Python，且赛事驱动已完成验证，不需要主动降级系统 Python。

网络访问 PyPI 较慢时，可以选择配置 pip 镜像源：

```bash
python3 -m pip config set \
global.index-url \
```

https://pypi.tuna.tsinghua.edu.cn/simple

检查配置：

```bash
python3 -m pip config list
```

如果仅使用命令行安装驱动，不需要安装 GUI 和 XCB 图形依赖。只有在明确使用图形化升级工具时，才按照后摩对应文档安装图形组件。

安装前还应确认：

- 主机网络连接正常；
- 系统剩余空间充足；
- 没有正在运行的驱动安装或卸载任务；
- 当前使用的驱动包文件完整；
- 板卡供电和散热正常。

### 4.2.1.4 卸载旧版本驱动

首次安装可以跳过本步骤。

如果设备已经安装其他版本的后摩驱动，或者需要升级到赛事指定版本，应先使用原驱动安装包卸载旧版本：

```bash
sudo bash \
./houmo-drv-xh2_<old_release>_<distro>_aarch64.run \
uninstall all
```

卸载过程中：

1.  不得使用 Ctrl+C 中断；
2.  不得关闭主机电源；
3.  不得复位或拔插后摩设备；
4.  不得同时执行新版本驱动安装。

不要直接删除：

```bash
/usr/local/houmo-sdk
```

直接删除目录可能残留内核模块、环境变量、系统服务或配置文件，应通过原安装包执行完整卸载。

卸载完成后，根据安装程序提示重新启动系统：

```bash
sudo reboot
```

### 4.2.1.5 安装驱动和 SDK

进入驱动安装包目录：

```bash
cd ~/houmo-install
```

增加执行权限：

```bash
chmod a+x \
houmo-drv-xh2_<release>_<distro>_aarch64.run
```

安装驱动和全部相关组件：

```bash
sudo bash \
./houmo-drv-xh2_<release>_<distro>_aarch64.run \
install all
```

后摩官方建议使用：

```text
install all
```

该方式会安装驱动、SDK、SMI 管理工具及 HmUpdateTool 等相关组件。

上述install成功后，需要重启加速卡设备

```bash
hm_smi -rd <device_id>
<device_id>为当前设备上后摩加速卡设备描述符，若只有一张卡则默认为0
```

如果需要指定安装目录，可以执行：

```bash
sudo bash \
./houmo-drv-xh2_<release>_<distro>_aarch64.run \
install all \
--path /usr/local/houmo-sdk
```

不指定 --path 时，默认安装目录通常为：

```bash
/usr/local/houmo-sdk
```

安装过程中如果提示旧目录非空，例如：

```text
the /usr/local/houmo-drv-xh2_<release> directory is not empty,
do you want to clean the files in this directory
```

确认该目录属于需要替换的旧版本后，输入：

```text
yes
```

安装过程中必须遵守以下要求：

1.  不得断电或复位主机；
2.  不得拔插后摩板卡；
3.  不得使用 Ctrl+C 中断；
4.  不得同时启动其他安装或卸载程序；
5.  不得混装不同 Release 的驱动、固件和 Runtime。

### 4.2.1.6 加载环境变量并验证

安装程序可能提示执行：

```bash
source /etc/profile.d/houmo-sdk.sh
```

可以使用以下命令判断文件是否存在并加载：

```bash
test -f /etc/profile.d/houmo-sdk.sh && \
source /etc/profile.d/houmo-sdk.sh
```

检查 SDK 目录：

```bash
ls -ld /usr/local/houmo-sdk
```

检查管理工具：

```bash
command -v hm_smi
```

验证设备：

```bash
hm_smi -a
```

重点检查以下字段：

| **字段**         | **判断标准**                   |
|------------------|--------------------------------|
| Driver_Version   | 能够显示驱动版本               |
| Firmware_Version | 能够显示固件版本               |
| Model            | 能够识别当前板卡型号           |
| BDF              | 能够显示 PCIe 地址             |
| Cur_BandWidth    | 能够显示 PCIe 速率和 Lane 数量 |
| Core_Num         | 能够识别 IPU 核心              |
| DDR_Memory_Total | 能够识别板载内存               |
| Temperature      | 温度信息正常                   |
| Board_Power      | 能够读取功耗                   |

再次检查 PCIe：

```bash
lspci -nn | grep -i "1f6b:0c00"
```

如果安装后 hm_smi -a 没有返回设备信息，可以重新启动系统：

```bash
sudo reboot
```

重新登录后执行：

```bash
source /etc/profile.d/houmo-sdk.sh
hm_smi -a
```

同时满足以下条件，可认为驱动环境基本正常：

1.  lspci 能够识别 1f6b:0c00；
2.  hm_smi -a 能够显示后摩设备；
3.  驱动和固件版本能够读取；
4.  IPU、板载内存、温度和功耗信息正常；
5.  没有设备初始化或 PCIe 通信错误。

### 4.2.1.7 固件异常处理

如果驱动安装程序提示固件版本过低，或者 hm_smi -a 显示驱动与固件版本不匹配，不应继续反复安装驱动。

HmUpdateTool 用于后摩设备固件升级，但固件刷写存在设备不可用风险。赛事环境下，应由后摩或赛事技术团队确认以下内容后再执行：

- 板卡型号；
- 固件包版本；
- 驱动与固件的对应关系；
- 供电和散热状态；
- 升级失败后的恢复方案。

参赛者不要自行执行：

- 固件升级；
- DDR Training；
- 设备频率调整；
- 功耗策略调整；
- 底层设备复位。

## 4.2.2 揽月推理组件选择

后摩揽月软件栈提供从底层推理引擎到上层服务封装的多层组件。M.2 和 PCIe 板卡的软件选型方式基本一致，选择时应重点考虑模型格式、调用接口、并发需求、开发语言和交付复杂度。

### 4.2.2.1 组件定位

| **组件**   | **核心定位**                | **典型能力**                                        | **大赛使用建议**            |
|------------|-----------------------------|-----------------------------------------------------|-----------------------------|
| HLIELlama  | 后摩定制 llama.cpp 运行环境 | GGUF、命令行推理、Benchmark、WebUI、OpenAI 兼容接口 | **推荐优先使用**            |
| HLIECpp    | C++ 工程化推理服务          | HTTP 服务、模型加载与卸载、多实例、系统服务         | 可选                        |
| HLIEvLLM   | 后摩定制 vLLM 推理引擎      | 高吞吐、长上下文、批处理、Prompt Cache、多芯调优    | 高级可选                    |
| HLIEPython | Python 服务封装与模型调度层 | 多模型管理、HTTP、OpenAI SDK、WebSocket             | 高级可选，通常依赖 HLIEvLLM |

HLIELlama 基于开源 llama.cpp 集成后摩大道推理能力，提供 llama-cli、llama-server、llama-bench、llama-gguf 和 model-cli 等工具，适合在 ARM64 Linux 环境中完成模型验证、性能测试和本地 Agent 接入。

### 4.2.2.2 选择建议

根据作品需求选择：

1.  需要快速运行 GGUF 模型并接入 Agent：选择 HLIELlama；
2.  需要工程化 OpenAI 兼容服务和模型动态管理：选择 HLIECpp；
3.  需要高并发、长上下文或 vLLM 参数调优：选择 HLIEvLLM；
4.  Python 后端需要统一管理文本、多模态、ASR、TTS 或 Embedding 模型：选择 HLIEPython 和 HLIEvLLM。

本指南后续以 HLIELlama 为主要示例。

后摩资源中心还提供 HLChatDesktop、HLChat、揽月 AI 助手等应用。这些应用可以用于模型能力体验和环境验证，但不替代参赛作品自身需要实现的多步骤规划、工具调用和任务状态管理能力。

### 4.2.2.3 版本选择原则

HLIELlama、后摩大道 Runtime 和模型包之间存在版本对应关系。不同版本可能出现以下变化：

- 支持的模型架构不同；
- 模型包可能不向前兼容；
- llama-server 参数可能变化；
- Qwen 思考模式参数可能变化；
- Prompt Cache、并发和多模态能力可能变化；
- 模型使用的后摩大道 BUILD 版本不同。

赛事使用时应遵循：

1. 赛事驱动版本
2. 赛事大道 Runtime 版本
3. 赛事 HLIELlama 版本
4. 与该版本匹配的模型 BUILD

应优先使用赛事指定的正式版本，不建议使用未经验证的 Preview 软件包。

## 4.2.3 HLIELlama 部署和使用

### 4.2.3.1 下载 HLIELlama

进入后摩资源中心，选择：

后摩揽月

类别：推理框架

软件系统：HLIELlama

CPU 架构：arm

操作系统：Linux

版本：最新正式版

创建工作目录：

```bash
mkdir -p ~/houmo
cd ~/houmo
```

将软件包复制到该目录，根据实际格式解压。例如：

```bash
tar -xf <HLIELLAMA_ARM_LINUX_PACKAGE>.tar.gz
```

或者：

```bash
unzip <HLIELLAMA_ARM_LINUX_PACKAGE>.zip
```

进入解压目录：

```bash
cd houmo-application-software-llama.cpp-xh2*
```

查看目录结构：

```bash
find . -maxdepth 2 -type d | sort
```

正常情况下应包含：

bin/

include/

lib/

models/

scripts/

service/

```text
version.txt
```

其中：

| **目录**    | **作用**                              |
|-------------|---------------------------------------|
| bin         | HLIELlama 命令行和服务程序            |
| include     | llama.cpp 头文件，用于 C/C++ 二次开发 |
| lib         | llama.cpp 和后摩大道依赖库            |
| models      | 默认模型存放目录                      |
| scripts     | HMM 到 GGUF 的转换工具                |
| service     | llama-server 系统服务脚本             |
| version.txt | 当前软件版本                          |

查看版本：

```text
cat version.txt
```

检查主要程序：

```bash
ls -lh bin
```

通常包括：

```text
llama-cli
llama-server
llama-bench
llama-gguf
llama-gguf-split
model-cli
```

确保程序具有执行权限：

```bash
chmod +x bin/*
```

### 4.2.3.2 检查运行环境

加载后摩 SDK 环境：

```bash
test -f /etc/profile.d/houmo-sdk.sh && \
source /etc/profile.d/houmo-sdk.sh
```

检查程序架构：

```text
file bin/llama-server
```

输出中应包含 ARM 或 AArch64，而不是 x86-64。

检查动态库：

```bash
ldd bin/llama-server | grep "not found"
```

如果没有输出，说明没有发现明显缺失的动态库。

仅在确实存在软件包内部动态库加载问题时，可在当前终端临时执行：

```bash
export LD_LIBRARY_PATH="$PWD/lib:${LD_LIBRARY_PATH:-}"
```

不要在未确认影响范围时，将该路径永久写入系统环境。

检查 HLIELlama 是否能够识别后摩设备：

```bash
./bin/llama-server --list-devices
```

正常情况下应看到类似：

Available devices:

0: HoumoNPU LQ50

同时执行：

```bash
hm_smi -a
```

如果 llama-server --list-devices 和 hm_smi -a 均能识别设备，说明 HLIELlama 已经能够访问后摩加速卡。

单卡赛事设备通常默认使用设备 0。如需显式指定：

```bash
export HOUMO_DEVICE_ID=0
```

### 4.2.3.3 查询并下载适配模型

HLIELlama 的 model-cli 可以查询和下载后摩已经完成量化、编译和 GGUF 封装的模型。

查询 M50 模型：

```bash
./bin/model-cli query target=xh2
```

筛选单卡模型：

```bash
./bin/model-cli query target=xh2 device=1
```

也可以根据模型规模继续筛选：

```bash
./bin/model-cli query \
target=xh2 \
device=1 \
size=4b
```

模型列表中的主要字段如下：

| **字段** | **说明**                                  |
|----------|-------------------------------------------|
| ID       | 模型下载标识                              |
| NAME     | 模型名称                                  |
| SIZE     | 模型参数规模                              |
| BUILD    | 模型使用的后摩大道构建版本                |
| CTX      | 最大上下文长度                            |
| BATCH    | 是否为多 Batch 模型                       |
| DEVICE   | 模型所需板卡或芯片数量                    |
| TARGET   | 目标平台，M50 应为 xh2                    |
| CORES    | 使用的 IPU 核心数量                       |
| FILES    | GGUF 文件数量，多模态模型通常包含多个文件 |

单卡赛事设备应优先选择：

```text
TARGET = xh2
DEVICE = 1
```

首次验证建议优先使用赛事指定的 Qwen3 4B、Qwen3 8B 或其他较小模型，不建议一开始选择需要双卡、多卡或超长上下文的大模型。

下载模型：

```bash
./bin/model-cli \
-model-path "$PWD/models" \
pull <MODEL_ID>
```

其中，\<MODEL_ID\> 应替换为当前 query 返回的实际 ID，不建议把文档中的历史 ID 写死。

查看本地模型：

```bash
./bin/model-cli \
-model-path "$PWD/models" \
list
```

检查下载结果：

```bash
find "$PWD/models" \
-type f \
-name "*.gguf" \
-ls
```

查看 GGUF 信息：

```bash
./bin/llama-gguf <MODEL_GGUF> r
```

如果模型包含多个 GGUF 文件，应按照模型说明选择入口文件。分片模型通常使用第一个 GGUF 文件作为 -m 参数，例如：

```text
model_00001-of-00003.gguf
```

后摩发布的 GGUF 模型已经根据 M50 和后摩大道工具链完成适配。普通上游 GGUF 不一定能够直接运行，应优先使用 model-cli 下载或赛事提供的模型。

### 4.2.3.4 运行命令行推理

1.  查看已下载的 GGUF 模型文件

```bash
find "$PWD/models" -type f -name "*.gguf"
```

根据模型 README、下载说明或 model-cli list 输出，确认需要加载的入口模型文件。

2.  设置模型路径

将 MODEL_PATH 设置为入口模型文件的绝对路径：

```text
MODEL_PATH="<MODEL_GGUF绝对路径>"
```

例如：

```text
MODEL_PATH="$PWD/models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"
```

注意：不要自动选择搜索结果中的第一个 .gguf 文件。在多模态、多模型或分片模型目录中，第一个文件可能是 mmproj.gguf、Embedding 模型或非入口分片，无法作为主模型直接加载。具体入口文件应以模型 README、下载说明或 model-cli list 的结果为准。

3.  检查模型路径

```bash
echo "$MODEL_PATH"
ls -lh "$MODEL_PATH"
```

如果文件路径正确，ls 命令将输出模型文件的大小、权限和修改时间等信息。

4.  查看 llama-cli 参数

```bash
./bin/llama-cli --help
```

5.  执行基础文本推理

```bash
./bin/llama-cli \
-m "$MODEL_PATH" \
-p "请用一句话介绍你自己。" \
-n 128
```

6.  观察设备运行状态

推理过程中，在另一个终端执行：

```text
watch -n 1 hm_smi -a
```

如果模型能够正常加载并生成文本，同时设备内存、功耗或 IPU 利用率发生变化，说明基础推理链路基本可用。

### 4.2.3.5 启动 OpenAI 兼容服务

HLIELlama 推荐直接运行 llama-server。新版本不再建议使用 run_llama-server.sh，该脚本后续可能被移除。官方指南同时提供预加载模型、动态加载模型和系统服务三种方式。

查看支持的参数：

```bash
./bin/llama-server --help
```

使用预加载模型方式启动。

仅供当前设备上的 Agent 或客户端访问时，建议服务只监听本机地址。先查看当前

版本支持的参数：

```bash
./bin/llama-server --help
```

如果当前版本支持 --host 参数，可以执行：

```bash
./bin/llama-server \
-m "$MODEL_PATH" \
-a local-model \
--host 127.0.0.1 \
--port 17701 \
--cache-ram 0
如果当前版本不支持 --host 参数，应以 ./bin/llama-server --help 的实际输出和
```

赛事指定版本的 HLIELlama 使用指南为准。

需要供局域网中的其他设备访问时，应将服务监听地址设置为 0.0.0.0。确认当前

版本支持 --host 参数后，执行：

```bash
./bin/llama-server \
-m "$MODEL_PATH" \
-a local-model \
--host 0.0.0.0 \
--port 17701 \
--cache-ram 0
```

主要参数如下：

| **参数**         | **说明**                             |
|------------------|--------------------------------------|
| -m               | 后摩适配 GGUF 模型路径               |
| -a               | 模型别名，用于 OpenAI 兼容请求       |
| --host 127.0.0.1 | 仅监听本机，只允许当前设备访问       |
| --host 0.0.0.0   | 监听所有网络接口，允许局域网设备访问 |
| --port 17701     | 服务端口，默认通常为 17701           |
| --cache-ram 0    | 关闭会话 Prompt 的 RAM 缓存          |

HLIELlama 默认可能启用 Prompt Cache，用于复用历史 KV Cache、降低多轮对话的首 Token 延迟。长期运行时，缓存可能导致主机内存逐渐增加，因此基础长稳测试建议增加：

```bash
--cache-ram 0
```

如果模型加载阶段因系统内存不足退出，可尝试：

```bash
--no-mmap
```

使用该参数后，模型加载速度可能下降。

### 4.2.3.6 验证 OpenAI 兼容接口

在模型服务所在设备上查询模型列表：

```bash
curl -sS \
http://127.0.0.1:17701/v1/models \
| python3 -m json.tool
如果从局域网中的其他设备验证，应将 127.0.0.1 替换为模型服务所在设备的实际 局域网 IP，例如： curl -sS \ http://192.168.1.100:17701/v1/models \ | python3 -m json.tool
```

发送最小文本请求：

```bash
curl -sS \
http://127.0.0.1:17701/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{
"model": "local-model",
"messages": [
{
"role": "user",
"content": "请只回复：后摩本地模型接入成功"
}
],
"stream": false
}' \
| python3 -m json.tool
```

如果能够正常返回文本，说明：

1.  llama-server 已经启动；
2.  模型已经正确加载；
3.  OpenAI 兼容接口可以访问；
4.  后摩加速卡可以作为本地模型 Provider 使用。

本地服务通常不需要真实 API Key。部分 OpenAI SDK 客户端强制要求填写 api_key 时，可以使用无敏感含义的占位值：

```text
no-key
```

Python 示例：

```python
from openai import OpenAI
client = OpenAI(
    base_url="http://127.0.0.1:17701/v1",
    api_key="no-key",
    timeout=60.0,
)
response = client.chat.completions.create(
    model="local-model",
    messages=[
        {
            "role": "user",
            "content": "请只回复：后摩本地模型接入成功",
        }
    ],
    stream=False,
)
content = response.choices[0].message.content
print(content)
```

安装 Python SDK：

```bash
python3 -m venv ~/anyint-venv
source ~/anyint-venv/bin/activate
python3 -m pip install "openai>=1,<2"
```

### 4.2.3.7 动态模型管理

如果需要在服务启动后加载和卸载不同模型，可以使用动态模型目录。

启动服务：

```bash
./bin/llama-server \
--models-dir "$PWD/models" \
--port 17701 \
--cache-ram 0
```

列出模型：

```bash
./bin/model-cli list
```

加载模型：

```bash
./bin/model-cli run <MODEL_NAME>
```

查看加载状态：

```bash
./bin/model-cli ps
```

卸载模型：

```bash
./bin/model-cli stop <MODEL_NAME>
```

删除本地模型：

```bash
./bin/model-cli rm <MODEL_NAME>
```

model-cli run 返回通常只表示服务已经接收到加载请求，模型加载需要一定时间，应继续执行：

```bash
./bin/model-cli ps
```

确认模型已经完成加载。

当前版本通常只在 llama-server 启动时扫描 --models-dir。服务启动后新增模型时，应重新启动服务以刷新模型列表。

### 4.2.3.8 安装为系统服务

开发调试阶段建议直接运行 llama-server，便于查看日志。模型和参数验证完成后，可以安装为后台服务。

安装：

```bash
sudo bash service/install_llama-server.sh
```

查看状态：

```bash
sudo systemctl status llama-server.service
```

启动、停止和重启：

```bash
sudo systemctl start llama-server.service
sudo systemctl stop llama-server.service
sudo systemctl restart llama-server.service
```

查看实时日志：

```bash
sudo journalctl \
-u llama-server.service \
-f
```

卸载服务：

```bash
sudo bash service/uninstall_llama-server.sh
```

安装服务前，应先检查安装脚本中的模型目录、端口、设备和启动参数是否符合当前赛事环境。

### 4.2.3.9 可选功能

#### 4.2.3.9.1 多模态模型

多模态模型通常包含语言主模型和视觉模型：

```text
main-model.gguf
mmproj.gguf
```

启动：

```bash
./bin/llama-server \
-m <MAIN_MODEL_GGUF> \
--mmproj <MMPROJ_GGUF> \
-a local-vlm \
--port 17701 \
--cache-ram 0
```

主模型和 mmproj 必须来自同一模型版本和同一构建版本。

后摩部分视觉模型采用固定输入分辨率。图片会按照模型要求 Resize 和 Padding。目标检测等任务返回的坐标可能基于处理后的图片，应用端需要根据 Resize 和 Padding 过程映射回原图。

#### 4.2.3.9.2 Embedding 模型

```bash
./bin/llama-server \
-m <EMBEDDING_MODEL_GGUF> \
--embedding \
--pooling last \
-b <CONTEXT_LENGTH> \
-ub <CONTEXT_LENGTH> \
--port 17701
```

Embedding 模型可用于：

- 本地知识库；
- RAG；
- 文档向量化；
- 语义检索；
- Agent 长期记忆检索。

#### 4.2.3.9.3 Rerank 模型

```bash
./bin/llama-server \
-m <RERANK_MODEL_GGUF> \
--rerank \
--port 17701
```

Rerank 模型可对向量检索结果进行重新排序。

#### 4.2.3.9.4 并发访问

多用户访问时，可以根据模型类型使用：

```bash
--np 2
```

当前版本通常最大支持 4。只有多 Batch 模型能够实现真正并发，单 Batch 模型通常采用请求交替执行。

应先完成单请求验证，再逐步提高并发数。

#### 4.2.3.9.5 Qwen 思考模式

不同版本关闭 Qwen 思考模式的参数可能不同：

| **HLIELlama 版本** | **常见参数**         |
|--------------------|----------------------|
| 2.1.0 之前         | --reasoning-budget 0 |
| 2.1.0              | -rea off             |

OpenAI 兼容请求还可通过请求体控制：

```json
{
"chat_template_kwargs": {
"enable_thinking": false
}
}
```

部分模型支持设置推理等级：

```json
{
"reasoning": {
"effort": "low"
}
}
```

具体能力应以模型和赛事 HLIELlama 版本为准。基础连通性测试不建议加入这些可选参数。

更多模型转换、多卡调度、投机解码、ASR、OCR、C/C++ 二次开发和底层模型调试方法，应参见赛事指定版本的《HLIELlama 部署及使用指南》。

## 4.2.4 性能测试

### 4.2.4.1 基础性能测试

HLIELlama 提供 llama-bench 用于模型性能测试。

查看参数：

```bash
./bin/llama-bench --help
```

执行基础测试：

```bash
./bin/llama-bench \
-m "$MODEL_PATH" \
-p 512 \
-n 128
```

其中：

| **参数** | **说明**                          |
|----------|-----------------------------------|
| -m       | 模型路径                          |
| -p 512   | Prompt/Prefill 测试输入 512 Token |
| -n 128   | Decode 测试生成 128 Token         |

如果赛事指定版本的参数格式不同，应以：

```bash
./bin/llama-bench --help
```

为准。

### 4.2.4.2 观察设备状态

性能测试期间，在另一个终端执行：

```text
watch -n 1 hm_smi -a
```

重点观察：

- IPU 利用率；
- Core 利用率；
- 设备内存；
- 板卡功耗；
- 芯片和内存温度；
- PCIe 链路状态。

如果模型有输出但 IPU 利用率、设备内存和功耗始终没有变化，应检查模型是否实际使用后摩设备。

### 4.2.4.3 记录性能指标

建议记录：

| **指标**     | **说明**                  |
|--------------|---------------------------|
| Prefill 速度 | 输入 Token 处理速度       |
| Decode 速度  | 输出 Token 生成速度       |
| TTFT         | 首 Token 延迟             |
| TOPT         | 相邻输出 Token 的时间间隔 |
| E2E Latency  | 端到端响应时间            |
| E2E TPS      | 端到端整体吞吐            |
| Vision 时间  | 多模态模型的图片编码耗时  |
| 设备内存     | 模型加载和推理内存占用    |
| 主机内存     | 模型服务占用的系统内存    |
| IPU 利用率   | 推理期间的加速卡负载      |
| 温度         | 芯片和设备内存温度        |
| 功耗         | 板卡运行功耗              |

HLIELlama 默认启用 Prompt Cache 时，Prefill 统计可能排除已经复用的历史前缀。正式对比时，应保证两次测试采用相同的 Cache 配置；需要观察完整 Prefill 时，可根据当前版本帮助关闭 Prompt Cache。官方指南将 TTFT、TOPT、E2E Latency、E2E TPS、Prefill 和 Decode 作为主要统计指标。

### 4.2.4.4 测试要求

不同配置的性能结果不能直接比较。正式测试时应保持以下条件一致：

- 板卡型号和内存容量；
- 驱动、固件和大道 Runtime 版本；
- HLIELlama 版本；
- 模型名称和模型 BUILD；
- 模型量化方式；
- 上下文长度；
- Prompt Token 数；
- 生成 Token 数；
- Batch 和并发数；
- Prompt Cache 配置；
- 多模态图片尺寸；
- 后台系统负载；
- 散热和环境温度。

建议模型启动后先完成一次预热，再连续执行多次测试，记录稳定结果。性能数据只用于当前硬件和软件环境下的对比，不作为不同模型、不同设备和不同版本之间的统一结论。

### 4.2.4.5 基础验收条件

同时满足以下条件，可认为后摩推理链路基本跑通：

1.  lspci 能够识别 1f6b:0c00；
2.  hm_smi -a 能够显示设备状态；
3.  llama-server --list-devices 能够识别 HoumoNPU；
4.  后摩适配 GGUF 模型能够加载；
5.  llama-cli 或 llama-server 能够生成有效结果；
6.  OpenAI 兼容接口能够正常返回；
7.  推理期间设备内存、功耗或 IPU 利用率发生变化；
8.  日志中没有模型加载失败或完全回退至 CPU 的异常；
9.  多次请求能够稳定完成；

## 4.2.5 常见问题

| **问题现象**                      | **处理建议**                                                |
|-----------------------------------|-------------------------------------------------------------|
| lspci 找不到 1f6b:0c00            | 检查板卡安装、供电、散热、BIOS 和 PCIe 通道，不继续安装驱动 |
| lspci 正常但 hm_smi 不存在        | 检查是否安装驱动并使用了 install all                        |
| hm_smi 能执行但无设备             | 检查驱动、固件和 PCIe 状态，按照要求重启设备                |
| 驱动包无法执行                    | 检查执行权限和 CPU 架构，确认使用 AArch64 包                |
| 驱动提示架构不匹配                | 误用了 x86_64、AMD64、Windows 或 M30 软件包                 |
| 驱动依赖下载失败                  | 检查网络、DNS 和 pip 源，或使用赛事提供的离线依赖           |
| 驱动目录已存在                    | 先使用旧版本安装包执行 uninstall all                        |
| 驱动安装被中断                    | 不要直接重复覆盖安装，先联系赛事技术支持确认残留状态        |
| Debian 12 安装失败                | 使用赛事验证的驱动包，不要自行更换其他发行版驱动反复尝试    |
| 驱动与固件不匹配                  | 联系后摩或赛事维护人员，不要自行刷写固件                    |
| HLIELlama 无法启动                | 检查是否下载了 M50、xh2、ARM Linux 版本                     |
| file bin/llama-server 显示 x86-64 | 下载了错误 CPU 架构的软件包                                 |
| 提示动态库缺失                    | 使用 ldd 检查，必要时临时设置 LD_LIBRARY_PATH               |
| --list-devices 找不到 NPU         | 检查 hm_smi、SDK 环境变量和动态库                           |
| model-cli query 失败              | 检查网络和后摩模型服务访问状态                              |
| 模型下载失败                      | 检查网络、磁盘空间和模型访问权限                            |
| 模型加载失败                      | 检查 BUILD、TARGET、DEVICE 和 HLIELlama 版本                |
| 单卡设备加载了双卡模型            | 重新选择 DEVICE=1 的模型                                    |
| 普通 GGUF 无法运行                | 使用后摩已经适配并发布的 GGUF 模型                          |
| 多文件模型无法加载                | 按模型说明指定主文件或第一个 GGUF 分片                      |
| 新下载模型未出现在动态列表        | 重启 llama-server，重新扫描 --models-dir                    |
| model-cli run 后模型不可用        | 使用 model-cli ps 检查是否仍在加载                          |
| OpenAI 接口返回 404               | 检查服务端口、接口路径和 llama-server 状态                  |
| 服务可以输出但 NPU 无负载         | 检查模型是否使用后摩适配版本，以及是否发生 CPU 回退         |
| 运行一段时间后内存增长            | 启动服务时增加 --cache-ram 0                                |
| 模型加载阶段内存不足              | 使用更小模型，或尝试增加 --no-mmap                          |
| 多并发效果不明显                  | 检查模型是否为多 Batch 模型                                 |
| 提高 --np 后内存不足              | 降低并发数，使用更小上下文或更小模型                        |
| 多模态模型只能文本对话            | 检查主模型、mmproj、图片输入和模型版本                      |
| 多模态结果与图片无关              | 检查图片是否成功读取，主模型和视觉模型是否匹配              |
| 检测框位置不准确                  | 检查图片 Resize、Padding 和坐标映射                         |
| Qwen 无法关闭思考模式             | 根据 HLIELlama 版本选择对应参数                             |
| llama-bench 执行失败              | 检查模型和 HLIELlama 版本，优先使用赛事验证版本             |
| 性能结果波动较大                  | 固定模型、参数、Cache、并发、温度和系统负载                 |
| 温度或功耗异常                    | 立即停止压力任务并联系赛事维护人员                          |

后摩开发者社区：

https://developer.houmoai.com/

后摩资源中心：

https://developer.houmoai.com/resources_v2

后摩文档中心：

https://developer.houmoai.com/document

HLIELlama、HLIECpp、HLIEPython 和 HLIEvLLM 的完整模型支持范围、多芯调度、投机解码、模型转换、C/C++ API 和深度性能调优方法，以后摩官方部署及使用指南为准。
