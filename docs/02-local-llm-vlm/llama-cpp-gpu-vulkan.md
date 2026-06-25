# llama.cpp GPU / Vulkan

本文档介绍如何在开发板上使用 llama.cpp 的 Vulkan 后端运行本地 LLM / VLM 模型，并验证 GPU 后端是否可用。

> **Warning**
>
> Vulkan 后端依赖 GPU 驱动、Vulkan Runtime、Vulkan Headers、SPIR-V 工具链、模型类型、内存和 llama.cpp 版本。即使 Vulkan Runtime 可以识别 GPU，也不代表 llama.cpp 一定能成功使用 Vulkan 后端。实际效果需要以板端验证结果为准。

## 1. 适用场景

* 验证开发板 GPU / Vulkan Runtime 是否可用。
* 对比 llama.cpp CPU 与 Vulkan 后端运行差异。
* 尝试使用 GPU 后端运行 GGUF 模型。
* 为本地 LLM / VLM 推理提供 GPU 路径验证。

## 2. 前置条件

* 已完成系统启动和网络配置。
* 已安装基础编译工具。
* GPU 驱动和 Vulkan Runtime 可用。
* 已准备或可下载 GGUF 模型文件。
* 开发板可用磁盘空间充足。

建议至少预留：

```text
源码和编译空间：5 GB+
模型空间：根据模型大小决定
Qwen2.5-0.5B Q4_K_M GGUF：约 500 MB
```

## 3. 安装基础依赖

安装基础编译工具：

```bash
sudo apt update
sudo apt install -y git cmake build-essential wget htop
```

安装 Vulkan 相关依赖：

```bash
sudo apt install -y \
  vulkan-tools \
  libvulkan-dev \
  glslc \
  spirv-headers \
  spirv-tools \
  glslang-tools
```

各组件说明如下：

| 组件              | 说明                                             |
| --------------- | ---------------------------------------------- |
| `vulkan-tools`  | 提供 `vulkaninfo`，用于检查 Vulkan Runtime            |
| `libvulkan-dev` | 提供 Vulkan 开发头文件和库                              |
| `glslc`         | Vulkan shader compiler，llama.cpp Vulkan 后端编译需要 |
| `spirv-headers` | 提供 SPIR-V Headers                              |
| `spirv-tools`   | 提供 SPIR-V 工具链                                  |
| `glslang-tools` | 提供 `glslangValidator` 等工具                      |

> **Note**
>
> 部分 Debian 系统中可能没有名为 `shaderc` 的包。若 `sudo apt install shaderc` 提示找不到包，可以忽略，安装 `glslc`、`libshaderc1`、`spirv-headers`、`spirv-tools`、`glslang-tools` 即可。

## 4. 验证 Vulkan Runtime

执行：

```bash
vulkaninfo --summary
```

如果命令可用，并且输出中能看到 Vulkan device / GPU 信息，说明系统层面可以识别 Vulkan Runtime。

示例输出中应能看到类似信息：

```text
Vulkan Instance Version: 1.3.xxx

Devices:
GPU0:
    deviceType = PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU
    deviceName = Mali-G720-Immortalis
```

如果提示：

```text
vulkaninfo: command not found
```

说明 `vulkan-tools` 未安装。

如果提示找不到 Vulkan device、ICD、driver 或类似错误，说明 Vulkan Runtime 或 GPU 驱动可能不可用，需要先检查系统镜像、GPU 驱动和 Release 基线。

## 5. 获取 llama.cpp

```bash
mkdir -p ~/local-llm-test
cd ~/local-llm-test

git clone https://github.com/ggml-org/llama.cpp.git
cd llama.cpp
```

如果已经在 CPU 页面中获取过 llama.cpp，可以直接进入已有目录：

```bash
cd ~/local-llm-test/llama.cpp
```

## 6. 准备验证模型

llama.cpp 通常使用 GGUF 模型文件。为了快速验证 Vulkan 后端，建议优先使用小模型，避免模型过大导致下载慢、加载慢或内存不足。

本文档推荐复用 CPU 页面中的 `Qwen2.5-0.5B-Instruct-GGUF Q4_K_M` 模型。

模型仓库：

| 平台           | 链接                                                                                              |
| ------------ | ----------------------------------------------------------------------------------------------- |
| ModelScope   | [Qwen/Qwen2.5-0.5B-Instruct-GGUF](https://modelscope.cn/models/Qwen/Qwen2.5-0.5B-Instruct-GGUF) |
| Hugging Face | [Qwen/Qwen2.5-0.5B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF)       |

在开发板上执行：

```bash
mkdir -p ~/models/qwen2.5-0.5b
cd ~/models/qwen2.5-0.5b

wget -O qwen2.5-0.5b-instruct-q4_k_m.gguf \
https://modelscope.cn/models/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/master/qwen2.5-0.5b-instruct-q4_k_m.gguf
```

下载完成后检查：

```bash
ls -lh ~/models/qwen2.5-0.5b/
```

正常情况下可以看到类似文件：

```text
qwen2.5-0.5b-instruct-q4_k_m.gguf
```

> **Warning**
>
> 如果文件大小明显异常，例如只有几 KB，说明模型没有完整下载。请删除该文件后重新下载。

## 7. 编译 Vulkan 后端

进入 llama.cpp 源码目录：

```bash
cd ~/local-llm-test/llama.cpp
```

每次重新编译 Vulkan 后端前，建议先删除旧的构建目录，避免沿用旧 CMake 配置：

```bash
rm -rf build-vulkan
```

配置 Vulkan 后端：

```bash
cmake -S . -B build-vulkan \
  -DGGML_VULKAN=ON \
  -DGGML_BACKEND_DL=OFF
```

检查 `GGML_VULKAN` 是否已打开：

```bash
grep -i "GGML_VULKAN" build-vulkan/CMakeCache.txt
```

必须看到：

```text
GGML_VULKAN:BOOL=ON
```

如果仍然是：

```text
GGML_VULKAN:BOOL=OFF
```

说明 Vulkan 后端没有启用，后续即使运行时加了 `-ngl 99`，也仍然会走 CPU。

确认 Vulkan 后端打开后，开始编译：

```bash
cmake --build build-vulkan -j$(nproc)
```

编译完成后检查：

```bash
ls -lh build-vulkan/bin/llama-cli
```

## 8. 处理 Vulkan-Headers 版本不匹配问题

在部分 Debian / Bookworm 系统中，系统自带的 Vulkan-Headers / Vulkan-Hpp 版本可能与最新 llama.cpp 的 Vulkan 后端不匹配。

典型报错如下：

```text
error: 'LayerSettingEXT' is not a member of 'vk'
error: 'LayerSettingTypeEXT' has not been declared
error: 'LayerSettingsCreateInfoEXT' is not a member of 'vk'
```

如果遇到上述错误，可以将新版 Vulkan-Headers 安装到用户本地目录，不修改系统文件。

执行：

```bash
cd ~/local-llm-test

git clone https://github.com/KhronosGroup/Vulkan-Headers.git
cd Vulkan-Headers

cmake -B build -DCMAKE_INSTALL_PREFIX=$HOME/local-vulkan
cmake --build build -j$(nproc)
cmake --install build
```

然后重新编译 llama.cpp Vulkan 后端，并通过 `CMAKE_PREFIX_PATH` 指定本地 Vulkan-Headers：

```bash
cd ~/local-llm-test/llama.cpp

rm -rf build-vulkan

cmake -S . -B build-vulkan \
  -DGGML_VULKAN=ON \
  -DGGML_BACKEND_DL=OFF \
  -DCMAKE_PREFIX_PATH=$HOME/local-vulkan

grep -i "GGML_VULKAN" build-vulkan/CMakeCache.txt

cmake --build build-vulkan -j$(nproc)
```

如果仍然出现旧 Vulkan-Headers 相关错误，可以增加 include 搜索路径：

```bash
export CPLUS_INCLUDE_PATH=$HOME/local-vulkan/include:$CPLUS_INCLUDE_PATH
```

然后重新执行：

```bash
cd ~/local-llm-test/llama.cpp

rm -rf build-vulkan

cmake -S . -B build-vulkan \
  -DGGML_VULKAN=ON \
  -DGGML_BACKEND_DL=OFF \
  -DCMAKE_PREFIX_PATH=$HOME/local-vulkan

cmake --build build-vulkan -j$(nproc)
```

> **Note**
>
> 如果系统 Vulkan Runtime 可以识别 GPU，但 llama.cpp Vulkan 编译失败，通常不是模型问题，而是 Vulkan 开发头文件、SPIR-V 工具链或 llama.cpp 当前 commit 与系统环境不匹配。

## 9. 运行 Vulkan 推理

进入 llama.cpp 目录：

```bash
cd ~/local-llm-test/llama.cpp
```

使用本地 GGUF 文件运行：

```bash
./build-vulkan/bin/llama-cli \
  -m ~/models/qwen2.5-0.5b/qwen2.5-0.5b-instruct-q4_k_m.gguf \
  -p "请用一句话介绍你自己。" \
  -t 8 \
  -n 128 \
  -ngl 99
```

参数说明：

| 参数     | 说明                   |
| ------ | -------------------- |
| `-m`   | 本地 GGUF 模型路径         |
| `-p`   | 输入 prompt            |
| `-t`   | CPU 线程数              |
| `-n`   | 最大生成 token 数         |
| `-ngl` | 尝试 offload 到 GPU 的层数 |

> **Note**
>
> `-ngl 99` 表示尽可能将更多层 offload 到 GPU。实际能 offload 多少层取决于模型、后端、显存/内存、驱动和 llama.cpp 支持情况。

如果运行时出现：

```text
warning: no usable GPU found, --gpu-layers option will be ignored
warning: one possible reason is that llama.cpp was compiled without GPU support
```

说明当前运行没有成功使用 Vulkan 后端。请检查：

```bash
grep -i "GGML_VULKAN" build-vulkan/CMakeCache.txt
vulkaninfo --summary
```

并确认运行的是：

```bash
./build-vulkan/bin/llama-cli
```

而不是：

```bash
./build/bin/llama-cli
```

## 10. 可选：使用 llama-bench 验证

可以使用 `llama-bench` 做基础性能验证：

```bash
./build-vulkan/bin/llama-bench \
  -m ~/models/qwen2.5-0.5b/qwen2.5-0.5b-instruct-q4_k_m.gguf \
  -t 8 \
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

## 11. 验证结果

如果模型能够正常加载并生成回复，说明 llama.cpp Vulkan 路径基本跑通。

本次验证中，Vulkan 后端已成功编译，`GGML_VULKAN` 为 `ON`，并使用本地 `Qwen2.5-0.5B-Instruct-GGUF Q4_K_M` 模型完成文本生成。

![llama.cpp GPU Vulkan Qwen2.5 0.5B result](../_static/images/llama-cpp-gpu-qwen2.5-0.5b-result.jpg)

本次验证结果如下：

| 项目                  | 结果                                                        |
| ------------------- | --------------------------------------------------------- |
| Vulkan Runtime      | 可用，`vulkaninfo --summary` 可识别 GPU                         |
| GPU                 | Mali-G720-Immortalis                                      |
| llama.cpp Vulkan 编译 | 成功                                                        |
| `GGML_VULKAN`       | `ON`                                                      |
| 验证模型                | `Qwen2.5-0.5B-Instruct-GGUF Q4_K_M`                       |
| 模型路径                | `~/models/qwen2.5-0.5b/qwen2.5-0.5b-instruct-q4_k_m.gguf` |
| CPU 线程数             | `-t 8`                                                    |
| 最大生成 token 数        | `-n 128`                                                  |
| GPU offload 参数      | `-ngl 99`                                                 |
| 文本生成                | 成功                                                        |
| Prompt 速度           | 约 17.5 t/s                                                |
| Generation 速度       | 约 35.5 t/s                                                |

> **Note**
>
> 本次验证中，Vulkan 后端可以完成模型加载和文本生成，但在 `Qwen2.5-0.5B` 小模型上未体现明显加速。GPU 后端性能与模型规模、量化格式、offload 层数、驱动实现和数据搬运开销有关，建议与 CPU 路径进行实测对比。

## 12. 常见问题

### 12.1 `vulkaninfo` 找不到设备

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

### 12.2 `glslc` 缺失

如果 CMake 报错：

```text
Could NOT find Vulkan (missing: glslc)
```

说明缺少 Vulkan shader compiler。安装：

```bash
sudo apt install -y glslc
```

然后删除旧构建目录并重新配置：

```bash
rm -rf build-vulkan

cmake -S . -B build-vulkan \
  -DGGML_VULKAN=ON \
  -DGGML_BACKEND_DL=OFF
```

### 12.3 `SPIRV-Headers` 缺失

如果 CMake 报错：

```text
Could not find a package configuration file provided by "SPIRV-Headers"
```

安装：

```bash
sudo apt install -y spirv-headers spirv-tools glslang-tools
```

然后删除旧构建目录并重新配置：

```bash
rm -rf build-vulkan

cmake -S . -B build-vulkan \
  -DGGML_VULKAN=ON \
  -DGGML_BACKEND_DL=OFF
```

### 12.4 `GGML_VULKAN` 仍然是 `OFF`

检查：

```bash
grep -i "GGML_VULKAN" build-vulkan/CMakeCache.txt
```

如果显示：

```text
GGML_VULKAN:BOOL=OFF
```

说明 Vulkan 后端没有启用。请删除旧构建目录后重新执行：

```bash
rm -rf build-vulkan

cmake -S . -B build-vulkan \
  -DGGML_VULKAN=ON \
  -DGGML_BACKEND_DL=OFF
```

注意不要把 `cmake` 写成 `make`。下面是错误写法：

```bash
make -S . -B build-vulkan -DGGML_VULKAN=ON
```

正确写法是：

```bash
cmake -S . -B build-vulkan -DGGML_VULKAN=ON
```

### 12.5 Vulkan-Headers 版本不匹配

如果编译时报：

```text
LayerSettingEXT is not a member of vk
LayerSettingsCreateInfoEXT is not a member of vk
```

说明当前系统 Vulkan-Headers / Vulkan-Hpp 版本与当前 llama.cpp 源码不匹配。

可参考本文档第 8 节，将新版 Vulkan-Headers 安装到 `$HOME/local-vulkan`，并在配置 llama.cpp 时加入：

```bash
-DCMAKE_PREFIX_PATH=$HOME/local-vulkan
```

### 12.6 运行后仍提示 `no usable GPU found`

如果运行时提示：

```text
warning: no usable GPU found, --gpu-layers option will be ignored
```

检查以下几点：

* 是否运行的是 `./build-vulkan/bin/llama-cli`。
* `GGML_VULKAN` 是否为 `ON`。
* `vulkaninfo --summary` 是否可以识别 GPU。
* 是否加了 `-ngl 99`。
* 是否误用了 CPU 版本 `./build/bin/llama-cli`。

### 12.7 Vulkan 后端没有明显加速

可能原因：

* 模型较小，GPU 调度和数据搬运开销抵消收益。
* 模型层没有全部 offload 到 GPU。
* `-ngl` 设置不合适。
* GPU 驱动或 Runtime 支持有限。
* 当前模型结构或量化格式不适合该后端。

建议同时记录 CPU 路径和 Vulkan 路径的实测结果，而不要默认认为 Vulkan 一定更快。

## 13. 参考资料

* [Arm Learning Path: Run ERNIE-4.5 MoE on Armv9 with llama.cpp](https://learn.arm.com/learning-paths/cross-platform/ernie_moe_v9/)
* [llama.cpp GitHub Repository](https://github.com/ggml-org/llama.cpp)
* [llama.cpp Build Documentation](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)
* [Qwen2.5-0.5B-Instruct-GGUF on ModelScope](https://modelscope.cn/models/Qwen/Qwen2.5-0.5B-Instruct-GGUF)
