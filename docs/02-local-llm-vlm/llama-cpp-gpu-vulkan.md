# llama.cpp GPU / Vulkan

本文档介绍如何在开发板上使用 llama.cpp 的 Vulkan 后端运行本地 LLM / VLM 模型，并验证 GPU 后端是否可用。

```{warning}
Vulkan 后端依赖 GPU 驱动、Vulkan Runtime、模型类型、内存和框架版本。即使 llama.cpp 能成功编译 Vulkan 后端，也不代表所有模型都能获得明显加速。实际效果需要以板端验证结果为准。
```

## 1. 适用场景

* 验证开发板 GPU / Vulkan Runtime 是否可用。
* 对比 llama.cpp CPU 与 Vulkan 后端运行差异。
* 尝试使用 GPU 后端运行 GGUF 模型。
* 为本地 LLM / VLM 推理提供 GPU 路径验证。

## 2. 前置条件

* 已完成系统启动和网络配置。
* 已安装基础编译工具。
* 已准备 GGUF 模型文件。
* GPU 驱动和 Vulkan Runtime 可用。
* 开发板可用磁盘空间充足。

建议至少预留：

```text
源码和编译空间：5 GB+
模型空间：根据模型大小决定
ERNIE Q4 模型：单个约 12 GB
```

## 3. 安装基础依赖

```bash
sudo apt update
sudo apt install -y git cmake build-essential python3 python3-pip htop libcurl4-openssl-dev
```

安装 Vulkan 检查工具：

```bash
sudo apt install -y vulkan-tools
```

## 4. 验证 Vulkan Runtime

执行：

```bash
vulkaninfo --summary
```

如果命令可用，并且输出中能看到 Vulkan device / GPU 信息，说明系统层面可以识别 Vulkan Runtime。

如果提示 `vulkaninfo: command not found`，说明工具未安装。

如果提示找不到 Vulkan device、ICD、driver 或类似错误，说明 Vulkan Runtime 或 GPU 驱动可能不可用，需要先检查系统镜像、GPU 驱动和 Release 基线。

## 5. 获取 llama.cpp

```bash
mkdir -p ~/local-llm-test
cd ~/local-llm-test

git clone https://github.com/ggml-org/llama.cpp.git
cd llama.cpp
```

## 6. 编译 Vulkan 后端

```bash
cmake -B build-vulkan -DGGML_VULKAN=ON
cmake --build build-vulkan -j$(nproc)
```

编译完成后检查：

```bash
ls build-vulkan/bin
```

确认存在：

```text
llama-cli
llama-bench
```

## 7. 准备验证模型

llama.cpp 通常使用 GGUF 模型文件。可使用 Arm Learning Path 中提供的 ERNIE-4.5 Q4 GGUF 模型进行验证。

```bash
mkdir -p ~/models/ernie-4.5
cd ~/models/ernie-4.5

wget https://modelscope.cn/models/unsloth/ERNIE-4.5-21B-A3B-PT-GGUF/resolve/master/ERNIE-4.5-21B-A3B-PT-Q4_0.gguf

wget https://modelscope.cn/models/unsloth/ERNIE-4.5-21B-A3B-Thinking-GGUF/resolve/master/ERNIE-4.5-21B-A3B-Thinking-Q4_0.gguf
```

```{note}
ERNIE-4.5 Q4 GGUF 模型体积较大，单个模型约 12 GB。下载前请确认磁盘空间和网络状态。
```

如果只是快速验证 llama.cpp Vulkan 编译和运行路径，也可以使用维护人员提供的小型 GGUF 模型，例如：

```text
Qwen2.5-0.5B-Instruct-Q4_0.gguf
Qwen2.5-1.5B-Instruct-Q4_0.gguf
TinyLlama Q4 GGUF
```

模型文件不建议提交到 GitHub 仓库。

## 8. 运行 Vulkan 推理

进入 llama.cpp 目录：

```bash
cd ~/local-llm-test/llama.cpp
```

使用 ERNIE Thinking 模型进行测试：

```bash
./build-vulkan/bin/llama-cli \
  --jinja \
  -m ~/models/ernie-4.5/ERNIE-4.5-21B-A3B-Thinking-Q4_0.gguf \
  -p "Please introduce Mixture of Experts in Chinese." \
  -c 4096 \
  -t 12 \
  -ngl 99
```

参数说明：

| 参数        | 说明                   |
| --------- | -------------------- |
| `--jinja` | 启用 Jinja prompt 模板   |
| `-m`      | GGUF 模型路径            |
| `-p`      | 输入 prompt            |
| `-c`      | 上下文长度                |
| `-t`      | CPU 线程数              |
| `-ngl`    | 尝试 offload 到 GPU 的层数 |

```{note}
`-ngl 99` 表示尽可能将更多层 offload 到 GPU。实际能 offload 多少层取决于模型、后端、显存/内存、驱动和 llama.cpp 支持情况。
```

## 9. 使用 llama-bench 验证

可以使用 `llama-bench` 做基础性能验证：

```bash
./build-vulkan/bin/llama-bench \
  -m ~/models/ernie-4.5/ERNIE-4.5-21B-A3B-Thinking-Q4_0.gguf \
  -t 12 \
  -ngl 99
```

建议记录：

* 模型名称。
* 量化格式。
* 是否启用 Vulkan。
* `-ngl` 数值。
* 线程数。
* prompt eval 性能。
* decode 性能。
* 内存占用。
* 是否出现 Vulkan device 相关日志。

## 10. 验证结果

如果模型能够正常加载并生成回复，说明 llama.cpp Vulkan 路径基本跑通。

建议记录以下环境信息：

```bash
uname -a
cat /etc/os-release
lscpu
free -h
vulkaninfo --summary
```

建议在文档中补充实测结果：

| 项目               | 结果  |
| ---------------- | --- |
| 开发板型号            | 待补充 |
| OS / Kernel      | 待补充 |
| llama.cpp commit | 待补充 |
| 模型               | 待补充 |
| Vulkan Runtime   | 待补充 |
| 是否成功加载模型         | 待补充 |
| 是否成功生成输出         | 待补充 |
| tokens/s         | 待补充 |
| 备注               | 待补充 |

## 11. 常见问题

### 11.1 `vulkaninfo` 找不到设备

可能原因：

* GPU 驱动未安装或未加载。
* Vulkan Runtime 缺失。
* Vulkan ICD 配置异常。
* 当前系统镜像不包含 Vulkan 支持。

处理建议：

```bash
vulkaninfo --summary
ls /usr/share/vulkan/icd.d/
```

如果仍无法识别，请确认当前系统镜像和 GPU 驱动版本是否符合 Release 基线。

### 11.2 编译时报 Vulkan 相关错误

检查：

* 是否安装 `vulkan-tools`。
* 是否安装 Vulkan 相关开发包。
* 当前 llama.cpp 版本是否支持目标平台。
* CMake 选项是否正确。

可尝试安装：

```bash
sudo apt install -y libvulkan-dev
```

然后重新编译：

```bash
rm -rf build-vulkan
cmake -B build-vulkan -DGGML_VULKAN=ON
cmake --build build-vulkan -j$(nproc)
```

### 11.3 模型加载失败

检查：

* 模型路径是否正确。
* 模型文件是否完整下载。
* 磁盘空间是否足够。
* 内存是否足够。
* 模型格式是否为 GGUF。

检查模型文件大小：

```bash
ls -lh ~/models/ernie-4.5/
```

### 11.4 Vulkan 后端没有明显加速

可能原因：

* 模型层没有成功 offload 到 GPU。
* `-ngl` 设置不合适。
* GPU 驱动或 Runtime 支持有限。
* 数据搬运开销抵消了加速收益。
* 当前模型结构或量化格式不适合该后端。

建议同时跑 CPU 路径和 Vulkan 路径进行对比。

## 12. 参考资料

* [Arm Learning Path: Run ERNIE-4.5 MoE on Armv9 with llama.cpp](https://learn.arm.com/learning-paths/cross-platform/ernie_moe_v9/)
* [Arm Learning Path: Set up llama.cpp on an Armv9 development board](https://learn.arm.com/learning-paths/cross-platform/ernie_moe_v9/2_llamacpp_installation/)
* [llama.cpp GitHub Repository](https://github.com/ggml-org/llama.cpp)
* [llama.cpp Build Documentation](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)
