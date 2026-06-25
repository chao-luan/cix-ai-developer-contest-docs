# llama.cpp CPU / KleidiAI

本文档介绍如何在开发板上使用 llama.cpp 的 CPU 路径运行本地 LLM / VLM 模型。

当前页面优先用于验证 llama.cpp 在开发板上的基础可用性。KleidiAI 相关优化以当前框架支持情况和实际编译选项为准。

## 1. 适用场景

* 快速验证本地 LLM / VLM 推理。
* 不依赖 GPU / NPU 的基础模型运行。
* 对比不同 CPU 线程数下的推理性能。
* 验证 GGUF 模型在开发板上的可运行性。

## 2. 前置条件

* 已完成系统启动和网络配置。
* 已安装基础编译工具。
* 已准备 GGUF 模型文件。
* 开发板可用磁盘空间满足模型和编译需求。

## 3. 安装依赖

```bash
sudo apt update
sudo apt install -y git cmake build-essential
```

## 4. 获取 llama.cpp

```bash
mkdir -p ~/local-llm-test
cd ~/local-llm-test

git clone https://github.com/ggml-org/llama.cpp.git
cd llama.cpp
```

## 5. 编译 CPU 版本

```bash
cmake -B build
cmake --build build -j$(nproc)
```

编译完成后检查：

```bash
ls build/bin
```

确认存在：

```text
llama-cli
```

## 6. 准备验证模型

llama.cpp 通常使用 GGUF 模型文件。建议优先使用小模型验证基础运行路径，避免模型过大导致下载慢、加载慢或内存不足。

本文档推荐使用 `Qwen2.5-0.5B-Instruct-GGUF` 作为基础验证模型。

模型仓库：

| 平台           | 链接                                                                                              |
| ------------ | ----------------------------------------------------------------------------------------------- |
| Hugging Face | [Qwen/Qwen2.5-0.5B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF)       |
| ModelScope   | [qwen/Qwen2.5-0.5B-Instruct-GGUF](https://modelscope.cn/models/qwen/Qwen2.5-0.5B-Instruct-GGUF) |

```{note} id="s4dt6z"
模型文件不建议提交到 GitHub 仓库。请将模型下载到开发板本地目录，例如 `~/models/`。
```

### 6.1 方式一：使用 llama.cpp 自动拉取模型

如果网络可以访问 Hugging Face，可以直接使用 llama.cpp 的 `-hf` 参数拉取并运行模型：

```bash
./build/bin/llama-cli \
  -hf Qwen/Qwen2.5-0.5B-Instruct-GGUF:Q4_K_M \
  -p "请用一句话介绍你自己。" \
  -t 8 \
  -n 128
```

该方式最简单，适合快速验证 llama.cpp 是否可以正常运行。

### 6.2 方式二：手动下载模型文件

也可以手动下载 GGUF 文件到本地目录：

```bash
mkdir -p ~/models/qwen2.5-0.5b
cd ~/models/qwen2.5-0.5b
```

使用 Hugging Face CLI 下载：

```bash
pip3 install -U huggingface_hub

huggingface-cli download \
  Qwen/Qwen2.5-0.5B-Instruct-GGUF \
  qwen2.5-0.5b-instruct-q4_k_m.gguf \
  --local-dir . \
  --local-dir-use-symlinks False
```

如果 Hugging Face 访问较慢，可打开 ModelScope 页面下载对应 GGUF 文件：

```text
https://modelscope.cn/models/qwen/Qwen2.5-0.5B-Instruct-GGUF
```

下载完成后，确认模型文件存在：

```bash
ls -lh ~/models/qwen2.5-0.5b/
```

## 7. 运行模型

如果使用 `-hf` 自动拉取模型，执行：

```bash
./build/bin/llama-cli \
  -hf Qwen/Qwen2.5-0.5B-Instruct-GGUF:Q4_K_M \
  -p "请用一句话介绍你自己。" \
  -t 8 \
  -n 128
```

如果使用本地 GGUF 文件，执行：

```bash
./build/bin/llama-cli \
  -m ~/models/qwen2.5-0.5b/qwen2.5-0.5b-instruct-q4_k_m.gguf \
  -p "请用一句话介绍你自己。" \
  -t 8 \
  -n 128
```

参数说明：

| 参数    | 说明                          |
| ----- | --------------------------- |
| `-hf` | 从 Hugging Face 仓库自动拉取指定量化模型 |
| `-m`  | 本地 GGUF 模型路径                |
| `-p`  | 输入 prompt                   |
| `-t`  | CPU 线程数                     |
| `-n`  | 最大生成 token 数                |

## 8. 验证结果

如果终端可以正常输出模型回复，说明 llama.cpp CPU 路径已跑通。

建议记录以下信息：

```bash
uname -a
cat /etc/os-release
lscpu
free -h
```

并记录模型运行输出中的：

* 模型名称。
* 量化格式。
* CPU 线程数。
* 加载耗时。
* 首 token 延迟。
* tokens/s。
* 内存占用。

## 9. 当前验证状态

| 项目             | 状态  | 备注 |
| -------------- | --- | -- |
| llama.cpp 源码拉取 | 待验证 |    |
| CPU 编译         | 待验证 |    |
| GGUF 模型加载      | 待验证 |    |
| 文本生成           | 待验证 |    |
| 性能数据记录         | 待补充 |    |

## 10. 常见问题

### 10.1 编译失败

检查：

* CMake 是否安装。
* GCC / G++ 是否安装。
* 磁盘空间是否充足。
* 当前 llama.cpp 分支是否支持目标平台。

### 10.2 模型加载失败

检查：

* 模型文件路径是否正确。
* 模型文件是否完整。
* 模型格式是否为 GGUF。
* 内存是否足够。

## 11. 参考资料

* [Arm Learning Path: llama.cpp on Armv9](https://learn.arm.com/learning-paths/cross-platform/ernie_moe_v9/)
* [llama.cpp GitHub Repository](https://github.com/ggml-org/llama.cpp)
