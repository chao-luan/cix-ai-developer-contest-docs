# 2.3 此芯P1 SDK

## 2.3.1 此芯 GO 图形引擎

此芯 GO 图形引擎是 CIX P1 Linux 平台的图形与 GPU 驱动软件栈，主要用于支持桌面显示、图形渲染、窗口系统兼容以及 GPU 加速应用运行。

GO 图形引擎向上支持 OpenGL、OpenGL ES、Vulkan 和 OpenCL 等接口，向下对接 Mali GPU 内核驱动、用户态驱动、GPU 固件、显示驱动及相关运行库。同时支持 Wayland 窗口系统，并通过 XWayland 兼容传统 X11 应用。

赛事提供的 Debian 12 系统镜像通常已经预装 GO 图形引擎及 GPU 运行环境，开发者一般无需重新安装。仅在系统恢复、驱动升级、环境异常或赛事组明确要求时，才需要执行本章节中的安装或更新步骤。

本章节仅介绍 GO 图形引擎的安装、基础验证和兼容配置。llama.cpp、MNN 等端侧 AI 推理框架的 GPU 后端使用方法见第 3 章。

### 2.3.1.1 GO 图形软件栈说明

CIX P1 Linux 图形软件栈主要支持以下能力：

| **类别**       | **支持内容**  | **说明**                           |
|----------------|---------------|------------------------------------|
| 图形 API       | OpenGL 4.0    | 用于传统桌面图形应用和部分 3D 应用 |
| 图形 API       | OpenGL ES 3.2 | 用于嵌入式图形应用                 |
| 图形 API       | Vulkan 1.3    | 用于低开销图形渲染和 Vulkan 应用   |
| 计算 API       | OpenCL        | 用于 GPU 通用计算                  |
| 窗口系统       | Wayland       | Linux 桌面环境使用的窗口系统       |
| 兼容层         | XWayland      | 用于兼容传统 X11 应用              |
| GPU 用户态驱动 | CIXGPU-Pro    | 此芯维护的 Mali Proprietary Driver |
| GPU 用户态驱动 | CIXGPU-Compat | 此芯维护的 Mesa Zink 兼容驱动      |

GO 图形引擎主要包含 CIXGPU-Pro 和 CIXGPU-Compat 两类 GPU 用户态驱动。

| **驱动路径**  | **主要能力**                            | **典型场景**                             |
|---------------|-----------------------------------------|------------------------------------------|
| CIXGPU-Pro    | OpenGL ES、Vulkan、OpenCL               | Wayland、GBM、Vulkan 应用及 GPU 通用计算 |
| CIXGPU-Compat | 通过 Mesa Zink 支持 OpenGL 和 OpenGL ES | X11、Wayland 及传统桌面 OpenGL 应用      |

GO 图形引擎通常会根据应用使用的图形接口和窗口系统自动选择驱动路径。一般情况下，开发者无需手动配置，仅在应用无法启动、渲染异常或需要调试时再调整兼容层配置。

### 2.3.1.2 安装包获取

GO 图形引擎安装包可通过此芯开发者中心或赛事资源包获取：

<https://developer.cixtech.com/>

请使用与赛事指定 Release 匹配的安装包。本次赛事统一使用 2026Q2 Release，不建议跨 Release 混装 GPU Kernel Driver、GPU 用户态驱动、Mesa、libglvnd 和 XWayland 等组件。

各组件说明如下：

| **文件或软件包**                            | **说明**                                |
|---------------------------------------------|-----------------------------------------|
| cix-gpu-dkms-src_1.0.0-cix-260624_arm64.deb | Mali GPU 内核态驱动 DKMS 包             |
| cix-gpu-umd_2.0.0-cix-260624_arm64.deb      | CIXGPU-Pro 用户态驱动                   |
| cix-libglvnd_1.7.0-cix-260624_arm64.deb     | OpenGL Vendor-Neutral Dispatch 相关组件 |
| cix-mesa_25.1.5-cix-260624_arm64.deb        | CIXGPU-Compat / Mesa Zink 驱动          |
| xwayland_24.1.6-1+cix-260624_arm64.deb      | 此芯适配的 XWayland 组件                |
| install.sh                                  | 安装脚本                                |
| uninstall.sh                                | 卸载脚本                                |
| README                                      | 安装方式、支持系统及版本说明            |

### 2.3.1.3 安装前检查

开始安装或更新前，确认设备已经启动至赛事指定的系统。

检查系统中是否已经安装 GO 图形引擎相关软件包：

```bash
dpkg -l | grep -E "cix-gpu|cix-mesa|cix-libglvnd|xwayland"
```

如果能够看到 cix-gpu-dkms、cix-gpu-umd、cix-libglvnd、cix-mesa 或 xwayland 等软件包，说明系统中已经安装 GO 图形引擎相关组件。更新时应按照安装包说明先卸载旧版本，再安装赛事指定版本。

如果没有任何输出，说明当前系统可能未安装 GO 图形引擎，或者当前 Release 使用了不同的软件包名称。

仅安装普通 xwayland 软件包不能说明系统已经安装完整的 GO 图形引擎，应结合软件包版本和当前 Release 判断是否为此芯适配版本。

### 2.3.1.4 安装与更新

#### 2.3.1.4.1 获取并解压安装包

通过浏览器登录此芯开发者中心[CIX Technology](https://developer.cixtech.com/)，下载与赛事 Release 匹配的 GO 图形引擎安装包并解压。进入解压目录后执行 ls，确认其中包含 README.md、ReleaseNotes.md、install.sh、uninstall.sh 及相关 .deb 软件包。

#### 2.3.1.4.2 全新安装

如果当前系统未安装其他版本的 GO 图形引擎，按照安装包 README 执行：

```bash
sudo ./install.sh
sudo reboot
```

#### 2.3.1.4.3 更新已安装版本

如果系统已经安装其他版本的 GO 图形引擎，应先卸载旧版本，再安装当前版本：

```bash
sudo ./uninstall.sh
sudo ./install.sh
sudo reboot
```

不建议直接覆盖安装不同 Release 的软件包。

#### 2.3.1.4.4 可选：DKMS 模式安装

DKMS 模式用于根据当前 Linux 内核重新编译 GPU 内核驱动，主要适用于以下场景：

1.  使用了自定义内核或升级过内核；
2.  普通安装后出现 GPU 内核模块无法加载、版本不匹配等问题；
3.  安装包 README 或赛事维护人员明确要求使用 DKMS。

使用 DKMS 前，应确认系统已安装当前内核对应的 Linux Headers，并且 GCC 版本不低于 12。

执行：

```bash
sudo ./uninstall.sh
sudo ./install.sh --dkms
sudo reboot
```

普通开发者使用赛事指定系统镜像和 2026Q2 GO 图形引擎安装包时，通常不需要使用 DKMS，直接执行 sudo ./install.sh 即可。当前 2026Q2 Orange Pi 系统镜像缺少对应的 Linux Headers，不支持 DKMS 安装。

### 2.3.1.5 基础环境验证

安装或更新完成并重启后，应验证 GPU 驱动、设备节点和图形应用是否能够正常工作。

#### 2.3.1.5.1 再次检查软件包

执行：

```bash
dpkg -l | grep -E "cix-gpu|cix-mesa|cix-libglvnd|xwayland"
```

确认 cix-gpu-dkms、cix-gpu-umd、cix-libglvnd 和 cix-mesa 等相关软件包已经安装，并且版本与当前 GO 图形引擎安装包一致。

#### 2.3.1.5.2 检查 GPU 设备节点

执行：

```bash
ls /dev/dri
```

正常情况下应能看到 card\* 和 renderD\* 节点。

#### 2.3.1.5.3 安装图形测试工具

执行：

```bash
sudo apt update
sudo apt install -y glmark2-x11
```

如果当前赛事镜像已经预装该工具，则无需重复安装。

#### 2.3.1.5.4 运行图形测试

进入桌面环境后执行：

```bash
glmark2
```

如果测试窗口能够正常打开，各测试场景能够正常渲染，并在结束后输出测试结果，说明基础 OpenGL 图形路径基本可用。

如果需要确认应用是否实际使用 GPU，可以在应用运行期间另开一个终端，执行：

```bash
cix-go-manager monitor gpu --refresh 1
```

该命令可实时查看 Mali GPU 的运行状态。部分利用率、频率、功耗策略和进程信息需要 root 权限，如数据不完整，可以执行：

```bash
sudo cix-go-manager monitor gpu --refresh 1
```

如果系统提示 cix-go-manager: command not found，请确认当前安装包是否已完整安装，并以安装包 README 中列出的工具为准。

如果运行应用时 GPU 利用率或频率发生变化，或者监控结果中出现对应进程，说明应用正在使用 GPU。更详细的性能分析、驱动调试和 GPU 配置方法请参考《CIX P1 Linux GPU 开发指导手册》。

### 2.3.1.6 卸载 GO 图形引擎

如果需要卸载当前 GO 图形引擎，进入对应安装包目录后执行：

```bash
sudo ./uninstall.sh
sudo reboot
```

```{warning}
卸载后如果未安装新的 CIX GPU 驱动，系统桌面可能无法正常启动。除非赛事维护人员明确要求，否则不建议普通开发者单独卸载。
```

### 2.3.1.7 应用兼容配置

个别图形应用可能需要指定使用 CIXGPU-Pro 或 CIXGPU-Compat 驱动。相关配置文件位于：

```bash
/opt/cixgpu-compat/app.json
```

开发者仅在应用出现无法启动、渲染异常或驱动兼容问题时，才需自行调整配置，正常情况下无需修改该文件。

如果系统出现黑屏、无法进入桌面或 GPU 设备无法识别等问题，请恢复赛事指定版本的 GO 图形引擎，或联系赛事维护人员。

## 2.3.2 此芯 NOE AI SDK

此芯 NeuralONE（NOE）AI SDK 是面向 CIX P1 NPU 的模型编译与推理工具链。开发者可以在 x86_64 Linux 宿主机上使用 NOE 编译器，将 TensorFlow、TFLite、PyTorch、ONNX 等格式的神经网络模型解析、量化并编译为 .cix 文件，再通过 CIX P1 设备端的 NOE Runtime 和 NOE Engine 执行 NPU 推理。

NOE AI SDK 分为宿主机和设备端两部分：

| **运行位置**        | **主要组件**                              | **作用**                                 |
|---------------------|-------------------------------------------|------------------------------------------|
| x86_64 Linux 宿主机 | NOE 编译器、cixbuild                      | 完成模型解析、量化、优化及 .cix 文件生成 |
| CIX P1 设备端       | NPU KMD、NPU UMD、NOE Runtime、NOE Engine | 加载 .cix 文件并调度 NPU 执行推理        |

赛事设备通常已经预装设备端 NPU 驱动、运行时和推理引擎。普通开发者一般只需检查现有环境并运行基础示例，不需要重新安装设备端组件。

本节仅介绍 NOE AI SDK 的获取、安装和基础验证。模型编译配置、量化参数以及 CV、Audio、LLM、VLM 等具体部署方法见第 3 章。

### 2.3.2.1 获取 NOE AI SDK

NOE AI SDK 可通过此芯开发者中心或赛事资源包获取：

<https://developer.cixtech.com/>

请使用与赛事指定 Release 和系统镜像匹配的软件包。本次赛事以 2026Q2 Release 为软件基线。

主要交付组件如下：

| **组件**            | **作用**                                                        |
|---------------------|-----------------------------------------------------------------|
| CixBuilder          | 宿主机侧 NOE 模型编译工具，用于将支持的模型编译转换为 .cix 模型 |
| cix-npu-driver-dkms | 设备端 NPU 内核态驱动，即 NPU KMD                               |
| cix-npu-umd         | 设备端 NPU 用户态驱动，即 NPU UMD                               |
| cix-noe-umd         | NOE 用户态运行时，负责加载和执行 .cix 模型                      |
| cix-ai-engine       | NOE Python 推理引擎，对 NOE Python API 进行高层封装             |
| cix-ai-test         | NPU 测试工具，用于基础功能和稳定性验证                          |

实际文件名可能包含操作系统标识、构建日期等后缀，应以当前赛事安装包中的文件为准。26Q2 Release 同时交付了 cix-llama-cpp 和 cix-mnn，其用途和安装方法见第 3 章，不在本节展开。

```{warning}
linux_x86_64.whl 用于 x86_64 Linux 宿主机；\_arm64.deb 用于 CIX P1 设备端，不要将 ARM64 软件包安装到 x86_64 宿主机，不要跨 Release 混装 NPU Driver、NPU UMD、NOE Runtime、NOE Engine 和系统镜像。
```

### 2.3.2.2 宿主机安装 NOE 编译器

NOE 编译器用于将原始神经网络模型编译为 .cix 文件。

编译器环境要求如下：

| **项目** | **要求**                     |
|----------|------------------------------|
| CPU 架构 | x86_64                       |
| 操作系统 | Ubuntu 20.04 或 Ubuntu 22.04 |
| Python   | Python 3.10.2                |

检查宿主机环境：

```bash
uname -m
python3 -V
```

预期输出：

```bash
x86_64
Python 3.10.x
```

如果系统默认 Python 不是 3.10，建议创建独立的 Python 3.10 虚拟环境后再安装。

进入 NOE SDK 安装包目录，执行：

```bash
python3 -m pip install ./cixbuilder-*.whl
```

实际安装时应以目录中的 WHL 文件名为准。例如：

```bash
python3 -m pip install \
./cixbuilder-6.1.3753.3-cp310-none-linux_x86_64.whl
```

当前版本 WHL 已声明所需的 Python 软件包依赖，安装时会由 pip 自动处理。

安装前应确认当前 Python 版本和主机架构与 WHL 文件匹配：

```bash
python3 --version
uname -m
```

例如，文件名中的：

```text
cp310
```

表示该 WHL 适用于 CPython 3.10；

```text
linux_x86_64
```

表示该 WHL 应安装在 x86_64 Linux 编译主机上，不能直接安装在 ARM64 架构的 CIX P1 设备中。

安装完成后执行：

```text
cixbuild -v
cixbuild -h
```

能够正常输出版本信息和命令帮助，说明 NOE 编译器安装成功。

如果安装过程中仍提示缺少 Python 软件包，可以根据当前安装包的 README、Release Note 或实际报错补充依赖。

### 2.3.2.3 检查设备端 NPU 环境

开发板启动至赛事指定系统后，首先检查 NPU 设备节点：

```bash
ls -l /dev/aipu
```

NPU 内核驱动正常加载后，应存在：

```bash
/dev/aipu
```

检查设备端软件包：

```bash
dpkg -l | grep -E "cix-npu|cix-noe|cix-ai"
```

正常情况下可以看到以下相关组件：

```text
cix-npu-driver-dkms
cix-npu-umd
cix-noe-umd
cix-ai-engine
```

检查 NOE UMD Python 扩展和 NOE Engine：

```bash
python3 -m pip list | grep -E "libnoe|noe_engine"
```

正常情况下应能看到：

libnoe

```text
noe_engine
```

其中：

- noe_engine 是对 NOE Python API 的高级封装；
- CIX AI ModelHub 中的 Python NPU 推理示例通常基于 noe_engine 编写。

如果 /dev/aipu、相关软件包和 Python 模块均存在，无需重新安装设备端组件。

### 2.3.2.4 设备端组件恢复安装

仅在以下情况下执行本节操作：

1.  系统恢复后缺少 NPU 组件；
2.  当前组件版本与赛事指定 Release 不一致；
3.  NPU 环境已经损坏；
4.  赛事维护人员明确要求重新安装。

官方 SDK 提供 install.sh 和 uninstall.sh，普通开发者应优先使用一键安装脚本，不建议手动逐个安装 .deb 软件包。使用官方安装脚本可以避免遗漏必要组件，或因手动安装操作不当导致环境异常。

进入设备端 SDK 安装目录，执行：

```bash
sudo ./install.sh
```

如果安装成功，执行以下命令重启设备：

```bash
sudo reboot
```

如果安装脚本检测到系统中已安装 cix-ai-engine 或其他旧版本组件，并提示需要先卸载，应在确认需要升级或重新安装后执行：

```bash
sudo ./uninstall.sh
sudo ./install.sh
sudo reboot
```

重启后，重新检查设备节点、相关软件包和 Python 模块：

```bash
ls -l /dev/aipu
dpkg -l | grep -E "cix-npu|cix-noe|cix-ai"
python3 -m pip list | grep -E "libnoe|noe_engine"
```

### 2.3.2.5 运行基础 NPU 推理示例

CIX AI ModelHub 提供已经完成量化编译和环境验证的模型、配置文件、测试数据和推理示例。建议使用其中已经包含 .cix 文件的模型验证设备端 NPU 推理链路，无需在本节重新编译模型。

CIX AI ModelHub 地址：

[ai_model_hub_26_Q2 · 模型库](https://modelscope.cn/models/cix/ai_model_hub_26_Q2)

ModelHub 中的推理脚本依赖既定的目录结构，并可能引用根目录中的 utils 模块、配置文件及测试数据。因此，**下载后必须保留完整的 AI ModelHub 目录结构，不要仅复制单个模型目录、推理脚本或 .cix 文件到其他位置运行**。

下文使用 AI_MODEL_HUB_DIR 表示下载到本地的 AI Model Hub 根目录。假设 AI Model Hub 位于当前用户主目录下的 ai_model_hub 目录，执行：

```bash
export AI_MODEL_HUB_DIR="$HOME/ai_model_hub"
```

如果实际存放目录不同，请将上述路径替换为真实路径。

检查目录是否正确：

```bash
test -d "$AI_MODEL_HUB_DIR/models" && \
echo "AI Model Hub 目录检查通过"
```

进入 AI Model Hub 根目录：

```bash
cd "$AI_MODEL_HUB_DIR"
```

进入根目录后，应先阅读根目录中的 ReadMe.md 或

ReadMe_EN.md，并按照其中“二、环境与依赖”的说明安装当前版本所需依赖。

不同模型和不同任务所需的 Python 依赖可能不同，不要默认直接执行根目录中的

requirements.txt，也不要仅根据脚本导入内容自行升级系统已有软件包。

以 onnx_resnet_v1_50 为例，进入模型目录：

```bash
cd "$AI_MODEL_HUB_DIR/models/ComputeVision/Image_Classification/onnx_resnet_v1_50"
```

确认基础文件存在：

```bash
ls -lh resnet_v1_50.cix inference_npu.py test_data
```

该示例目录通常还包含：

cfg/

datasets/

model/

```text
graph.json
inference_onnx.py
ReadMe.md
Tutorials.ipynb
```

运行 NPU 推理：

```bash
python3 inference_npu.py
```

推理正常时，终端应出现类似信息：

npu: noe_init_context success

npu: noe_load_graph success

Input tensor count is 1.

Output tensor count is 1.

npu: noe_create_job success

随后输出测试图片路径和分类结果，并在结束时显示：

```text
npu: noe_clean_job success
npu: noe_unload_graph success
npu: noe_deinit_context success
```

出现上下文初始化、模型加载、任务创建、推理结果输出和资源释放成功信息，说明 NPU Driver、NOE Runtime、NOE Engine 和 .cix 模型的基础推理链路已经正常运行。官方 ModelHub 的 onnx_resnet_v1_50 示例即采用该流程。

如果只复制单个模型目录到开发板，还需要同时保留推理脚本依赖的 utils 目录及相关 Python 依赖，否则可能出现：

ModuleNotFoundError: No module named 'utils'

### 2.3.2.6 基础问题排查

| **问题现象**                | **检查与处理**                                                                                     |
|-----------------------------|----------------------------------------------------------------------------------------------------|
| cixbuild: command not found | 确认已经进入安装 CixBuilder 的 Python 3.10 环境，并重新安装 WHL                                    |
| /dev/aipu 不存在            | NPU 内核驱动未正常加载，不要继续运行模型；检查设备端安装状态并重启                                 |
| 提示找不到 libnoe           | 检查 cix-noe-umd、NOE Runtime 及动态库搜索路径是否正常                                             |
| 提示找不到 noe_engine       | 检查 cix-ai-engine 是否安装，并确认当前 Python 环境正确                                            |
| noe_init_context 失败       | 检查 /dev/aipu、NPU Driver、UMD 和 Runtime 是否属于同一 Release                                    |
| noe_load_graph 失败         | 确认 .cix 模型与当前 NOE Runtime 和 SDK Release 匹配                                               |
| 提示找不到 utils            | 使用完整 AI ModelHub 目录，或同时复制根目录中的 utils                                              |
| 推理脚本缺少 Python 依赖    | 阅读 AI Model Hub 根目录中的 ReadMe.md 或 ReadMe_EN.md，并按照“二、环境与依赖”补齐当前版本所需依赖 |

如果通过赛事指定安装包恢复环境后仍无法运行，应保留具体问题信息并联系赛事维护人员。

## 2.3.3 此芯多媒体 SDK

此芯多媒体 SDK 是 CIX P1 平台的音视频处理软件栈，主要用于视频解码、视频编码、播放、转码、摄像头取流以及实时视频 AI Pipeline 构建。

对于端侧 AI 应用，多媒体 SDK 主要负责从摄像头或视频文件中获取、解码和处理图像帧，再将处理后的数据交给 NOE Runtime 等推理后端。多媒体 SDK 本身不负责模型编译。

CIX P1 Debian 12 多媒体环境主要包括以下组件：

| **组件**                 | **作用**                                                                |
|--------------------------|-------------------------------------------------------------------------|
| GStreamer                | 构建视频解码、编码、播放、转码和摄像头 Pipeline                         |
| NNStreamer               | 在 GStreamer Pipeline 中完成张量转换、前后处理和 NPU 推理接入           |
| FFmpeg                   | 通过命令行完成视频编解码、转码和码流分析                                |
| VPU 驱动及 V4L2 M2M 接口 | 为视频和 JPEG/MJPEG 编解码提供硬件加速，并对接 GStreamer、FFmpeg 等框架 |

如需进行缩放、颜色转换、归一化、仿射变换等 2D 图像预处理，可使用 CIX Media Engine（CME）；本节不展开 CME API 的具体开发方法。

本章节仅介绍多媒体基础环境检查和简单验证。视频编码、转码、多路处理、摄像头录像以及完整 AI 视频 Pipeline，请参考第3章。

### 2.3.3.1 安装与更新说明

赛事提供的 Debian 12系统镜像通常已经预装与当前 Release 匹配的 GStreamer、FFmpeg、VPU 插件及相关多媒体组件，开发者一般无需自行安装。

仅在系统恢复后组件缺失、版本与赛事 Release 不一致，或赛事维护人员明确要求时，才需要恢复或更新多媒体组件。

更新时应使用赛事提供的 Multimedia SDK 安装包，并按照对应 Release Notes 执行。不同 Release 的具体软件包名称和安装方式可能不同，本章节不提供统一的覆盖安装命令。

```{warning}
不建议通过系统软件源自行升级或覆盖 GStreamer、FFmpeg、V4L2 插件及相关多媒体组件，以免用户态组件、VPU 驱动和系统镜像版本不匹配。
```

### 2.3.3.2 基础环境检查

检查 GStreamer：

```bash
gst-launch-1.0 --version
gst-inspect-1.0 --version
```

如果能够正常输出版本信息，说明 GStreamer 基础环境已经安装。

检查常用 VPU 编解码插件：

```text
gst-inspect-1.0 v4l2h264dec
gst-inspect-1.0 v4l2h265dec
gst-inspect-1.0 v4l2h264enc
gst-inspect-1.0 v4l2h265enc
```

如果能够正常输出对应插件的属性和能力信息，说明相关 GStreamer V4L2 插件已经加载。

检查 FFmpeg：

```bash
ffmpeg -version
```

检查 FFmpeg 中的V4L2 M2M 编解码器：

```bash
ffmpeg -decoders | grep v4l2m2m
ffmpeg -encoders | grep v4l2m2m
```

正常情况下可能看到以下部分条目：

```text
h264_v4l2m2m
hevc_v4l2m2m
av1_v4l2m2m
vp9_v4l2m2m
vp8_v4l2m2m
mjpeg_v4l2m2m
```

不同格式可能仅支持解码或编码，具体支持范围以当前系统实际输出为准。

### 2.3.3.3 准备测试视频

安装依赖：

```bash
sudo apt update
sudo apt install -y wget unzip
```

新建并进入测试目录：

```bash
mkdir -p ~/multimedia-test
cd ~/multimedia-test
```

下载测试视频：

```bash
wget -c \ https://download.blender.org/peach/bigbuckbunny_movies/big_buck_bunny_1080p_h264.mov.zip
```

下载后解压缩得到测试视频.mov文件

```bash
unzip \ big_buck_bunny_1080p_h264.mov.zip
ls -lh \ big_buck_bunny_1080p_h264.mov
```

### 2.3.3.4 GStreamer 基础验证

#### 2.3.3.4.1 视频播放验证

执行：

```bash
gst-launch-1.0 playbin \
uri=file://$HOME/multimedia-test/big_buck_bunny_1080p_h264.mov
```

如果桌面和显示环境正常，应能打开播放窗口并正常播放视频。该步骤仅用于验证视频播放、音视频同步和显示链路，不作为 VPU 硬件解码是否启用的判断依据。

#### 2.3.3.4.2 VPU 硬件解码验证

执行：

```bash
gst-launch-1.0 \
filesrc location="$HOME/multimedia-test/big_buck_bunny_1080p_h264.mov" ! \
qtdemux ! \
h264parse ! \
v4l2h264dec ! \
fakesink sync=true
```

该 Pipeline 显式使用 v4l2h264dec，不会显示画面，而是调用 CIX P1 VPU 完成 H.264 硬件解码。Pipeline 能够正常运行，说明 GStreamer 已找到并调用 V4L2 M2M 硬件解码插件。

#### 2.3.3.4.3 确认 VPU 硬件加速已启用

在运行硬件解码 Pipeline 前，另开一个终端，执行：

```bash
sudo sh -c \
'echo 1 > /sys/kernel/debug/amvx/log/group/perf/enable'
```

实时查看 VPU 使用率：

```bash
sudo watch -n 1 \
cat /sys/kernel/debug/amvx/log/group/perf/utilization
```

然后在原终端运行：

```bash
gst-launch-1.0 \
filesrc location="$HOME/multimedia-test/big_buck_bunny_1080p_h264.mov" ! \
qtdemux ! \
h264parse ! \
v4l2h264dec ! \
fakesink sync=true
```

如果解码期间 utilization 显示非零占用，并随视频解码过程发生变化，说明 VPU 硬件解码已经实际启用。

验证完成后关闭统计：

```bash
sudo sh -c \
'echo 0 > /sys/kernel/debug/amvx/log/group/perf/enable'
```

VPU 使用率是确认硬件解码是否实际运行的直接依据，CPU 占用率仅可作为辅助判断。

如果当前系统中不存在对应的 debugfs 节点，可以退化为两种判断：

1.  Pipeline 中显式使用了 v4l2h264dec；
2.  开启 VPU 驱动日志后，解码期间持续产生 VPU 日志。

FFmpeg 显式使用 h264_v4l2m2m，且运行期间出现持续的 VPU 驱动日志，可以确认硬件解码生效。

#### 2.3.3.4.4 可选：摄像头预览验证

如果应用需要使用摄像头，先检查视频设备节点：

```bash
ls /dev/video*
假设摄像头设备为 /dev/video0，可以执行：
gst-launch-1.0 \
v4l2src device=/dev/video0 ! \
glupload ! \
glcolorconvert ! \
glcolorbalance ! \
gtkglsink
```

如果能够正常显示摄像头画面，说明摄像头取流、GStreamer 数据传输和基础显示链路可用。该步骤不涉及视频解码，因此不能用于验证 VPU 解码能力。

实际设备节点和摄像头输出格式可能不同。如命令无法运行，应先使用 v4l2-ctl 或摄像头说明文档确认设备节点、分辨率和像素格式，使用前应先安装对应工具：sudo apt install -y v4l-utils

### 2.3.3.5 FFmpeg 基础验证

使用 FFmpeg 显式指定 H.264 V4L2 M2M 解码器：

```bash
ffmpeg \
-c:v h264_v4l2m2m \
-i "$HOME/multimedia-test/big_buck_bunny_1080p_h264.mov" \
-f null -
```

该命令会完成视频解码并丢弃输出数据，不会生成大容量 YUV 文件。

-c:v h264_v4l2m2m 显式指定使用 CIX V4L2 M2M H.264 硬件解码器。执行期间可以使用前述 VPU 使用率监测命令确认 VPU 是否产生实际占用。

若删除 -c:v h264_v4l2m2m，FFmpeg 将选择默认解码器，可能转为软件解码。

### 2.3.3.6 NNStreamer 基础检查

NNStreamer 用于将 GStreamer 数据流接入 AI 推理链路，常用插件包括：

| **插件**         | **作用**                                                         |
|------------------|------------------------------------------------------------------|
| tensor_converter | 将视频帧、音频或其他数据转换为张量                               |
| tensor_filter    | 调用 Python 脚本或其他框架完成张量前处理、后处理及自定义数据处理 |
| tensor_noe       | 加载 .cix 模型并调用 CIX P1 NPU 推理                             |
| tensor_decoder   | 将推理结果转换为可显示或继续处理的数据                           |

检查相关插件：

```text
gst-inspect-1.0 tensor_converter
gst-inspect-1.0 tensor_filter
gst-inspect-1.0 tensor_noe
gst-inspect-1.0 tensor_decoder
```

如果能够正常显示插件信息，说明 NNStreamer 相关组件已经安装。

注意：

NNStreamer 当前主要用于 Demo 和功能评估，稳定性、性能及支持能力仍有限。搭建完整 AI 视频 Pipeline 前，建议先分别验证视频解码、模型推理和前后处理，再逐步串接完整链路。

### 2.3.3.7 常见问题

| **问题现象**                         | **处理建议**                                                                |
|--------------------------------------|-----------------------------------------------------------------------------|
| 找不到 v4l2h264dec 等插件            | 使用 gst-inspect-1.0 检查插件，并确认系统镜像与 Multimedia SDK Release 匹配 |
| Pipeline 能运行但 VPU 使用率始终为 0 | 确认 Pipeline 显式使用 v4l2h264dec，或 FFmpeg 显式使用 h264_v4l2m2m         |
| 视频可以解码但无法显示               | 先用 fakesink 验证解码，再检查 GO 图形引擎和桌面显示环境                    |
| 摄像头无法预览                       | 使用 v4l2-ctl 检查设备节点、分辨率和像素格式                                |

如果问题仍未解决，请保留具体问题信息并联系赛事维护人员。
