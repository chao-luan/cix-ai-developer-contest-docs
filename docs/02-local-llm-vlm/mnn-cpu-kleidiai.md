# MNN CPU / KleidiAI

本文档介绍如何在 Armv9 开发板上使用 MNN 的 CPU 路径运行本地 LLM 模型，并尽可能利用 Arm CPU 优化能力。

本流程优先验证 MNN CPU 路径的基础可用性，包括 MNN 源码编译、`llm_demo` 生成、运行时库路径检查、MNN 格式模型加载和文本推理。

> **Note**
>
> 本文档使用 `Qwen2.5-0.5B-Instruct-MNN` 作为基础验证模型。该模型体积较小，适合用于验证 MNN CPU 路径。
>
> 如果需要验证图像、音频等多模态能力，应使用对应的 MNN 多模态模型，例如 Omni 系列模型。`Qwen2.5-0.5B-Instruct-MNN` 主要用于文本推理验证，不作为图像多模态验证模型。

## 1. 适用场景

* 在开发板本地运行 MNN 格式模型。
* 验证 MNN CPU 路径是否可用。
* 验证 `llm_demo` 是否可以加载 MNN 模型。
* 验证本地文本生成能力。
* 为后续 MNN OpenCL 或其他后端验证提供 CPU baseline。

## 2. 前置条件

* 开发板已正常启动。
* 已完成网络配置。
* 可访问 GitHub / ModelScope。
* 磁盘空间充足。

建议至少预留：

```text
MNN 源码和编译空间：5 GB+
Qwen2.5-0.5B-Instruct-MNN 模型空间：1 GB+
```

> **Warning**
>
> MNN 不能直接加载 GGUF 模型。
> llama.cpp 使用的 `*.gguf` 模型不能直接用于 MNN。MNN 需要使用 MNN 格式模型，例如包含 `config.json`、`llm.mnn`、`llm.mnn.weight` 等文件的模型目录。

## 3. 安装基础依赖

```bash
sudo apt update
sudo apt install -y git build-essential gcc g++ cmake wget
```

安装 Git LFS，用于下载模型权重：

```bash
sudo apt install -y git-lfs
git lfs install
```

## 4. 创建工作目录

```bash
mkdir -p ~/mnn
cd ~/mnn
```

## 5. 获取 MNN 源码

```bash
git clone https://github.com/alibaba/MNN.git
cd MNN
```

## 6. 编译 MNN CPU / KleidiAI 版本

建议每次重新编译前先删除旧构建目录，避免沿用旧 CMake 配置：

```bash
cd ~/mnn/MNN

rm -rf build
mkdir -p build
cd build
```

配置并编译：

```bash
cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DMNN_BUILD_SHARED=ON \
  -DMNN_BUILD_LLM=ON \
  -DMNN_LOW_MEMORY=ON \
  -DMNN_KLEIDIAI=ON

make -j$(nproc)
```

参数说明：

| 参数                         | 说明                          |
| -------------------------- | --------------------------- |
| `CMAKE_BUILD_TYPE=Release` | 使用 Release 编译配置             |
| `MNN_BUILD_SHARED=ON`      | 构建共享库                       |
| `MNN_BUILD_LLM=ON`         | 启用 LLM 支持，生成 `llm_demo` 等工具 |
| `MNN_LOW_MEMORY=ON`        | 启用较低内存占用配置                  |
| `MNN_KLEIDIAI=ON`          | 启用 Arm KleidiAI 相关优化        |

> **Note**
>
> 如果 `MNN_KLEIDIAI=ON` 在当前 MNN 版本或当前系统环境下编译失败，可先去掉该选项，使用基础 CPU 路径完成验证。

## 7. 验证编译产物

检查 `llm_demo` 是否生成：

```bash
ls -lh ~/mnn/MNN/build/llm_demo
```

如果存在 `llm_demo`，说明 MNN LLM Demo 编译成功。

也可以查看 build 目录中的相关产物：

```bash
ls -lh ~/mnn/MNN/build | grep MNN
```

## 8. 配置运行时库路径

编译完成后，建议检查 `llm_demo` 实际加载的 MNN 动态库：

```bash
cd ~/mnn/MNN/build
ldd ./llm_demo | grep -E "libMNN|Express|Audio|OpenCV|CL|Vulkan" || true
```

如果输出中的 MNN 库指向系统目录，例如：

```text
/usr/share/cix/lib/libMNN.so
/usr/share/cix/lib/libMNN_Express.so
```

说明当前运行时加载的是系统预装库，而不是本次源码编译生成的库。为避免版本不一致，建议设置 `LD_LIBRARY_PATH`：

```bash
export LD_LIBRARY_PATH=$HOME/mnn/MNN/build:$HOME/mnn/MNN/build/express:$HOME/mnn/MNN/build/tools/audio:$HOME/mnn/MNN/build/tools/cv:${LD_LIBRARY_PATH:-}
```

再次检查：

```bash
ldd ./llm_demo | grep -E "libMNN|Express|Audio|OpenCV|CL|Vulkan" || true
```

期望看到 MNN 相关库指向当前 build 目录，例如：

```text
libMNN.so => /home/cix/mnn/MNN/build/libMNN.so
libMNN_Express.so => /home/cix/mnn/MNN/build/express/libMNN_Express.so
```

如需长期生效，可写入 `~/.bashrc`：

```bash
echo 'export LD_LIBRARY_PATH=$HOME/mnn/MNN/build:$HOME/mnn/MNN/build/express:$HOME/mnn/MNN/build/tools/audio:$HOME/mnn/MNN/build/tools/cv:${LD_LIBRARY_PATH:-}' >> ~/.bashrc
source ~/.bashrc
```

## 9. 下载验证模型

本文档使用 `Qwen2.5-0.5B-Instruct-MNN` 作为基础验证模型。

下载模型：

```bash
cd ~/mnn

git clone https://www.modelscope.cn/MNN/Qwen2.5-0.5B-Instruct-MNN.git
```

如果 clone 后出现 `Filtering content`，说明 Git LFS 正在拉取模型权重。等待其完成即可。

如果下载中断，可进入模型目录继续拉取：

```bash
cd ~/mnn/Qwen2.5-0.5B-Instruct-MNN

git lfs install
git lfs pull
```

检查主要模型文件：

```bash
ls -lh ~/mnn/Qwen2.5-0.5B-Instruct-MNN/config.json
ls -lh ~/mnn/Qwen2.5-0.5B-Instruct-MNN/llm.mnn
ls -lh ~/mnn/Qwen2.5-0.5B-Instruct-MNN/llm.mnn.weight
```

> **Warning**
>
> 如果 `llm.mnn` 或 `llm.mnn.weight` 只有几百字节或几 KB，说明 Git LFS 权重没有完整下载，需要重新执行 `git lfs pull`。

## 10. 验证模型是否能加载

进入 MNN build 目录：

```bash
cd ~/mnn/MNN/build
```

设置运行时库路径：

```bash
export LD_LIBRARY_PATH=$HOME/mnn/MNN/build:$HOME/mnn/MNN/build/express:$HOME/mnn/MNN/build/tools/audio:$HOME/mnn/MNN/build/tools/cv:${LD_LIBRARY_PATH:-}
```

加载模型：

```bash
./llm_demo ~/mnn/Qwen2.5-0.5B-Instruct-MNN/config.json
```

如果进入交互模式，说明模型配置和运行时基本可用。

退出方式：

```text
Ctrl+C
```

或输入：

```text
exit
```

## 11. 文本推理验证

创建 prompt 文件：

```bash
cat > ~/mnn/text_baseline_prompt.txt <<'EOF'
请用一句话介绍你自己。
EOF
```

运行文本推理：

```bash
cd ~/mnn/MNN/build

export LD_LIBRARY_PATH=$HOME/mnn/MNN/build:$HOME/mnn/MNN/build/express:$HOME/mnn/MNN/build/tools/audio:$HOME/mnn/MNN/build/tools/cv:${LD_LIBRARY_PATH:-}

./llm_demo ~/mnn/Qwen2.5-0.5B-Instruct-MNN/config.json ~/mnn/text_baseline_prompt.txt
```

如果可以看到模型输出文本，说明 MNN CPU 文本推理路径已跑通。

## 12. 验证结果

如果终端可以正常加载模型并输出文本回复，说明 MNN CPU 路径已跑通。

运行成功后，终端通常会显示 CPU Group、设备特性、模型加载信息、prompt 文件路径、模型输出以及 prefill / decode 速度统计。

![MNN CPU Qwen2.5 0.5B result](../_static/images/mnn-cpu-qwen2.5-0.5b-result.jpg)

> **Note**
>
> 本次验证使用的是文本模型，主要用于确认 MNN CPU 路径、`llm_demo`、模型加载和文本生成能力。
> 若需要验证图像/音频等多模态输入能力，需要使用对应的 MNN 多模态模型，并确认 `vision time`、`pixels_mp` 等指标不为 0。

## 13. 常见问题

### 13.1 编译失败

检查：

* `cmake` 是否安装。
* `gcc/g++` 是否安装。
* 磁盘空间是否充足。
* 是否缺少 MNN 编译依赖。
* 是否使用了不支持当前平台的编译选项。

### 13.2 找不到 `llm_demo`

检查是否启用了：

```text
-DMNN_BUILD_LLM=ON
```

重新编译：

```bash
cd ~/mnn/MNN

rm -rf build
mkdir build
cd build

cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DMNN_BUILD_SHARED=ON \
  -DMNN_BUILD_LLM=ON \
  -DMNN_LOW_MEMORY=ON \
  -DMNN_KLEIDIAI=ON

make -j$(nproc)
```

### 13.3 运行时报 `undefined symbol`

通常是动态库路径混乱导致 `llm_demo` 加载了系统里的旧版 `libMNN.so`。

执行：

```bash
cd ~/mnn/MNN/build
ldd ./llm_demo | grep -E "libMNN|Express|Audio|OpenCV|CL|Vulkan" || true
```

然后设置：

```bash
export LD_LIBRARY_PATH=$HOME/mnn/MNN/build:$HOME/mnn/MNN/build/express:$HOME/mnn/MNN/build/tools/audio:$HOME/mnn/MNN/build/tools/cv:${LD_LIBRARY_PATH:-}
```

再次检查：

```bash
ldd ./llm_demo | grep -E "libMNN|Express|Audio|OpenCV|CL|Vulkan" || true
```

### 13.4 模型文件没有完整下载

检查：

```bash
ls -lh ~/mnn/Qwen2.5-0.5B-Instruct-MNN/llm.mnn
ls -lh ~/mnn/Qwen2.5-0.5B-Instruct-MNN/llm.mnn.weight
```

如果文件很小，重新执行：

```bash
cd ~/mnn/Qwen2.5-0.5B-Instruct-MNN
git lfs pull
```

### 13.5 `Filtering content` 长时间不动

`Filtering content` 通常表示 Git LFS 正在下载模型权重。如果网络较慢，可能需要等待一段时间。

可在另一个终端观察目录大小是否变化：

```bash
watch -n 2 "du -sh ~/mnn/Qwen2.5-0.5B-Instruct-MNN"
```

如果长时间无变化，可中断后进入模型目录重新执行：

```bash
cd ~/mnn/Qwen2.5-0.5B-Instruct-MNN
git lfs pull
```

### 13.6 图像推理结果异常

如果使用文本模型执行图像 prompt，可能出现以下现象：

```text
vision time = 0.00 s
pixels_mp = 0.00 MP
```

这说明图像没有被有效处理。`Qwen2.5-0.5B-Instruct-MNN` 不应作为图像多模态验证模型。

如需验证图像多模态能力，应使用对应的 MNN 多模态模型，例如 Omni 系列模型。

## 14. 参考资料

* [Arm Learning Path: Build a Multimodal Retail Restocking Assistant on Armv9 With MNN](https://learn.arm.com/learning-paths/cross-platform/multimodel_mnn_v9/)
* [MNN GitHub Repository](https://github.com/alibaba/MNN)
* [Qwen2.5-0.5B-Instruct-MNN ModelScope Repository](https://www.modelscope.cn/MNN/Qwen2.5-0.5B-Instruct-MNN)
