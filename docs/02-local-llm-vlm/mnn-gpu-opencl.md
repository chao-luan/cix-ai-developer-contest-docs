# MNN GPU / OpenCL

本文档介绍如何在开发板上验证 MNN OpenCL 后端，包括 OpenCL Runtime 检查、MNN OpenCL 编译、OpenCL 产物确认、benchmark 后端验证，以及使用 MNN 格式小模型完成基础文本推理。

```{warning}
MNN OpenCL 后端是否能加速具体 LLM / VLM 模型，取决于模型结构、MNN Runtime 配置、算子覆盖、GPU 驱动和 OpenCL Runtime 状态。

本文档将验证分为两层：

1. OpenCL 后端可用性验证：通过 `clinfo`、`libMNN_CL.so` 和 `benchmark.out forwardtype=3` 确认 MNN OpenCL 后端可以执行 MNN 模型。
2. LLM 流程验证：通过 `Qwen2.5-0.5B-Instruct-MNN` 和 `backend_type=opencl` 验证 OpenCL build 下的 `llm_demo` 可以完成文本生成。

如果没有明确日志或性能对比，不建议直接写“所有 LLM 算子均已使用 OpenCL 加速”。
```

## 1. 适用场景

* 验证开发板 GPU / OpenCL Runtime 是否可用。
* 验证 MNN 是否能启用 OpenCL 后端编译。
* 验证 `benchmark.out` 是否可以通过 OpenCL 后端执行 MNN 模型。
* 验证 OpenCL build 下的 `llm_demo` 是否可以加载 MNN 文本模型。
* 为后续 MNN GPU 加速模型推理提供基础验证路径。

## 2. 前置条件

* 开发板已正常启动。
* 已完成网络配置。
* GPU 驱动正常。
* OpenCL Runtime 可用。
* 已安装基础编译工具。
* 已准备或可下载 MNN 格式模型。

```{note}
本文档使用 `Qwen2.5-0.5B-Instruct-MNN` 作为基础验证模型。该模型体积较小，适合用于验证 MNN 模型加载和文本推理流程。

MNN 不能直接加载 llama.cpp 使用的 GGUF 模型。`Qwen2.5-0.5B-Instruct-GGUF` 和 `Qwen2.5-0.5B-Instruct-MNN` 是不同格式，不能混用。
```

建议至少预留：

```text
MNN 源码和编译空间：5 GB+
Qwen2.5-0.5B-Instruct-MNN 模型空间：1 GB+
```

## 3. 安装基础依赖

安装基础编译工具：

```bash
sudo apt update
sudo apt install -y git build-essential gcc g++ cmake wget
```

安装 Git LFS：

```bash
sudo apt install -y git-lfs
git lfs install
```

安装 OpenCL 检查工具和开发依赖：

```bash
sudo apt install -y clinfo ocl-icd-opencl-dev opencl-headers
```

如果系统源中缺少相关包，请以当前 Release 提供的软件源和 GPU 驱动说明为准。

## 4. 检查 OpenCL Runtime

执行：

```bash
clinfo
```

如果可以看到 OpenCL Platform 和 Device 信息，说明系统层面可以识别 OpenCL Runtime。

可以进一步过滤关键信息：

```bash
clinfo | grep -E "Platform Name|Device Name|Device Version|Driver Version"
```

如果提示找不到 OpenCL platform / device，说明 OpenCL Runtime 或 GPU 驱动可能不可用，需要先检查系统镜像、GPU 驱动和 Release 基线。

## 5. 获取 MNN 源码

```bash
mkdir -p ~/mnn
cd ~/mnn

git clone https://github.com/alibaba/MNN.git
cd MNN
```

如果已经获取过源码，可以直接进入已有目录：

```bash
cd ~/mnn/MNN
```

## 6. 编译 MNN OpenCL + Benchmark + LLM

建议每次重新编译前先删除旧构建目录，避免沿用旧 CMake 配置：

```bash
cd ~/mnn/MNN

rm -rf build-opencl
mkdir -p build-opencl
cd build-opencl
```

配置并编译：

```bash
cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DMNN_BUILD_SHARED=ON \
  -DMNN_OPENCL=ON \
  -DMNN_BUILD_BENCHMARK=ON \
  -DMNN_BUILD_LLM=ON \
  -DMNN_LOW_MEMORY=ON \
  -DMNN_KLEIDIAI=ON

make -j$(nproc)
```

参数说明：

| 参数                         | 说明                                        |
| -------------------------- | ----------------------------------------- |
| `CMAKE_BUILD_TYPE=Release` | 使用 Release 编译配置                           |
| `MNN_BUILD_SHARED=ON`      | 构建共享库                                     |
| `MNN_OPENCL=ON`            | 启用 OpenCL 后端                              |
| `MNN_BUILD_BENCHMARK=ON`   | 编译 `benchmark.out`，用于明确验证 CPU / OpenCL 后端 |
| `MNN_BUILD_LLM=ON`         | 启用 LLM 支持，生成 `llm_demo`                   |
| `MNN_LOW_MEMORY=ON`        | 启用较低内存占用配置                                |
| `MNN_KLEIDIAI=ON`          | 启用 Arm KleidiAI 相关优化                      |

```{note}
如果 `MNN_KLEIDIAI=ON` 在当前 MNN 版本或系统环境下编译失败，可先去掉该选项，优先完成 OpenCL 编译验证。
```

## 7. 验证编译产物

检查 MNN 库是否生成：

```bash
ls -lh ~/mnn/MNN/build-opencl/libMNN.so
```

检查 OpenCL 相关库是否生成：

```bash
find ~/mnn/MNN/build-opencl -iname "*CL*" | head -50
find ~/mnn/MNN/build-opencl -iname "*opencl*" | head -50
```

重点确认是否存在类似文件：

```text
libMNN_CL.so
```

检查 `benchmark.out` 是否生成：

```bash
ls -lh ~/mnn/MNN/build-opencl/benchmark.out
```

检查 `llm_demo` 是否生成：

```bash
ls -lh ~/mnn/MNN/build-opencl/llm_demo
```

如果 `libMNN_CL.so`、`benchmark.out` 和 `llm_demo` 都存在，说明 OpenCL + Benchmark + LLM 构建基本完成。

## 8. 配置运行时库路径

编译完成后，建议检查 `benchmark.out` 和 `llm_demo` 实际加载的 MNN 动态库：

```bash
cd ~/mnn/MNN/build-opencl

ldd ./benchmark.out | grep -E "libMNN|CL|OpenCL" || true
ldd ./llm_demo | grep -E "libMNN|Express|Audio|OpenCV|CL|Vulkan" || true
```

如果输出中的 MNN 库指向系统目录，例如：

```text
/usr/share/cix/lib/libMNN.so
/usr/share/cix/lib/libMNN_Express.so
/usr/share/cix/lib/libMNN_CL.so
```

说明当前运行时加载的是系统预装库，而不是本次源码编译生成的库。为避免版本不一致，建议设置 `LD_LIBRARY_PATH`：

```bash
export LD_LIBRARY_PATH=$HOME/mnn/MNN/build-opencl:$HOME/mnn/MNN/build-opencl/express:$HOME/mnn/MNN/build-opencl/tools/audio:$HOME/mnn/MNN/build-opencl/tools/cv:${LD_LIBRARY_PATH:-}
```

再次检查：

```bash
ldd ./benchmark.out | grep -E "libMNN|CL|OpenCL" || true
ldd ./llm_demo | grep -E "libMNN|Express|Audio|OpenCV|CL|Vulkan" || true
```

期望看到 MNN 相关库指向当前 build-opencl 目录，例如：

```text
libMNN.so => /home/cix/mnn/MNN/build-opencl/libMNN.so
libMNN_CL.so => /home/cix/mnn/MNN/build-opencl/libMNN_CL.so
```

## 9. OpenCL 后端 benchmark 验证

`benchmark.out` 可以显式指定 MNN 后端类型。本文使用相同 benchmark 模型分别跑 CPU 和 OpenCL，以验证 OpenCL 后端是否可以执行 MNN 模型。

进入 build 目录：

```bash
cd ~/mnn/MNN/build-opencl

export LD_LIBRARY_PATH=$HOME/mnn/MNN/build-opencl:$HOME/mnn/MNN/build-opencl/express:$HOME/mnn/MNN/build-opencl/tools/audio:$HOME/mnn/MNN/build-opencl/tools/cv:${LD_LIBRARY_PATH:-}
```

确认 benchmark 模型目录存在：

```bash
ls ../benchmark/models
```

### 9.1 CPU benchmark

```bash
./benchmark.out ../benchmark/models 10 3 0 4 2
```

### 9.2 OpenCL benchmark

```bash
./benchmark.out ../benchmark/models 10 3 3 4 2
```

参数说明：

| 参数             |                   示例值 | 说明                       |
| -------------- | --------------------: | ------------------------ |
| `model_dir`    | `../benchmark/models` | benchmark 模型目录           |
| `loop_count`   |                  `10` | 循环次数                     |
| `warmup_count` |                   `3` | 预热次数                     |
| `forwardtype`  |             `0` / `3` | `0` 表示 CPU，`3` 表示 OpenCL |
| `thread_num`   |                   `4` | 线程数或执行配置                 |
| `precision`    |                   `2` | 低精度 / FP16 相关配置          |

如果 OpenCL benchmark 可以正常跑完，说明 MNN OpenCL 后端可以执行 MNN 模型推理。

如果出现类似：

```text
Can't Find type = 3 backend, use 0 instead
OpenCL init error
```

说明 OpenCL 后端没有真正可用，或当前运行时没有正确加载 `libMNN_CL.so`。

## 10. 下载验证模型

本文档使用 `Qwen2.5-0.5B-Instruct-MNN` 作为基础 LLM 验证模型。

如果已经在 MNN CPU 页面中下载过该模型，可以跳过本节。

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

```{warning}
如果 `llm.mnn` 或 `llm.mnn.weight` 只有几百字节或几 KB，说明 Git LFS 权重没有完整下载，需要重新执行 `git lfs pull`。
```

## 11. 创建 CPU / OpenCL 配置文件

MNN LLM 模型目录中包含默认 `config.json`。为了对比 CPU 与 OpenCL 后端，建议分别创建：

```text
config-cpu.json
config-opencl.json
```

进入模型目录：

```bash
cd ~/mnn/Qwen2.5-0.5B-Instruct-MNN
```

创建 CPU 配置：

```bash
cp config.json config-cpu.json

python3 - <<'PY'
import json

path = "config-cpu.json"
with open(path, "r", encoding="utf-8") as f:
    cfg = json.load(f)

cfg["backend_type"] = "cpu"
cfg["thread_num"] = 4
cfg["precision"] = "low"
cfg["memory"] = "low"

with open(path, "w", encoding="utf-8") as f:
    json.dump(cfg, f, indent=4, ensure_ascii=False)

print(json.dumps(cfg, indent=4, ensure_ascii=False))
PY
```

创建 OpenCL 配置：

```bash
cp config.json config-opencl.json

python3 - <<'PY'
import json

path = "config-opencl.json"
with open(path, "r", encoding="utf-8") as f:
    cfg = json.load(f)

cfg["backend_type"] = "opencl"
cfg["thread_num"] = 4
cfg["precision"] = "low"
cfg["memory"] = "low"

with open(path, "w", encoding="utf-8") as f:
    json.dump(cfg, f, indent=4, ensure_ascii=False)

print(json.dumps(cfg, indent=4, ensure_ascii=False))
PY
```

确认配置已修改：

```bash
grep -n "backend_type" ~/mnn/Qwen2.5-0.5B-Instruct-MNN/config-cpu.json
grep -n "backend_type" ~/mnn/Qwen2.5-0.5B-Instruct-MNN/config-opencl.json
```

期望输出：

```text
"backend_type": "cpu"
"backend_type": "opencl"
```

## 12. LLM 文本推理验证

创建 prompt 文件：

```bash
cat > ~/mnn/text_baseline_prompt.txt <<'EOF'
请用一句话介绍你自己。
EOF
```

### 12.1 CPU 配置验证

使用 OpenCL build 中的 `llm_demo` 加载 CPU 配置：

```bash
cd ~/mnn/MNN/build-opencl

export LD_LIBRARY_PATH=$HOME/mnn/MNN/build-opencl:$HOME/mnn/MNN/build-opencl/express:$HOME/mnn/MNN/build-opencl/tools/audio:$HOME/mnn/MNN/build-opencl/tools/cv:${LD_LIBRARY_PATH:-}

./llm_demo ~/mnn/Qwen2.5-0.5B-Instruct-MNN/config-cpu.json ~/mnn/text_baseline_prompt.txt 2>&1 | tee ~/mnn/mnn-cpu-llm.log
```

### 12.2 OpenCL 配置验证

使用 OpenCL build 中的 `llm_demo` 加载 OpenCL 配置：

```bash
cd ~/mnn/MNN/build-opencl

export LD_LIBRARY_PATH=$HOME/mnn/MNN/build-opencl:$HOME/mnn/MNN/build-opencl/express:$HOME/mnn/MNN/build-opencl/tools/audio:$HOME/mnn/MNN/build-opencl/tools/cv:${LD_LIBRARY_PATH:-}

./llm_demo ~/mnn/Qwen2.5-0.5B-Instruct-MNN/config-opencl.json ~/mnn/text_baseline_prompt.txt 2>&1 | tee ~/mnn/mnn-opencl-llm.log
```

如果能正常输出文本回复，说明当前 OpenCL build 可以完成模型加载和文本生成流程。

```{warning}
LLM 文本生成成功不等于所有算子都已确认使用 OpenCL。是否真正走 OpenCL，需要结合 `backend_type=opencl` 配置、运行日志、benchmark 结果以及 CPU / OpenCL 性能对比综合判断。
```

## 13. 对比 CPU / OpenCL 日志

查看 CPU 日志：

```bash
grep -E "backend|OpenCL|CPU|prefill|decode|speed|time" ~/mnn/mnn-cpu-llm.log
```

查看 OpenCL 日志：

```bash
grep -E "backend|OpenCL|CPU|prefill|decode|speed|time" ~/mnn/mnn-opencl-llm.log
```

如果 OpenCL 日志中出现 OpenCL 初始化、OpenCL backend、kernel、device 等信息，同时 benchmark `forwardtype=3` 可以正常执行，则可以说明当前 OpenCL 后端具备基础可用性。

## 14. 验证结果记录

如果完成以下项目，可以认为 MNN OpenCL 后端基础验证通过：

| 验证层级      | 验证项                                           | 结果  |
| --------- | --------------------------------------------- | --- |
| 系统级       | `clinfo` 可识别 OpenCL device                    | 待补充 |
| 编译级       | `MNN_OPENCL=ON` 编译成功                          | 待补充 |
| 产物级       | `libMNN_CL.so` 生成                             | 待补充 |
| Benchmark | `benchmark.out` 使用 `forwardtype=3` 可执行        | 待补充 |
| LLM 流程    | `config-opencl.json` 设置 `backend_type=opencl` | 待补充 |
| LLM 流程    | `llm_demo` 可加载模型并生成文本                         | 待补充 |
| 结论        | 是否确认 OpenCL 后端基础可用                            | 待补充 |

建议保存运行截图到：

```text
docs/_static/images/mnn-opencl-qwen2.5-0.5b-result.jpg
```

并在验证通过后添加图片：

```md
![MNN OpenCL Qwen2.5 0.5B result](../_static/images/mnn-opencl-qwen2.5-0.5b-result.jpg)
```

## 15. 常见问题

### 15.1 `clinfo` 找不到 OpenCL device

可能原因：

* GPU 驱动未安装或未加载。
* OpenCL Runtime 缺失。
* 当前系统镜像未包含 OpenCL 支持。
* OpenCL ICD 配置异常。

检查：

```bash
clinfo
ls /etc/OpenCL/vendors/
```

### 15.2 编译 MNN OpenCL 失败

检查：

* `cmake` 是否安装。
* `gcc/g++` 是否安装。
* 是否缺少 OpenCL 相关开发包。
* 当前系统是否提供 OpenCL headers / libraries。

可尝试重新安装依赖：

```bash
sudo apt install -y clinfo ocl-icd-opencl-dev opencl-headers
```

然后重新编译：

```bash
cd ~/mnn/MNN

rm -rf build-opencl
mkdir build-opencl
cd build-opencl

cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DMNN_BUILD_SHARED=ON \
  -DMNN_OPENCL=ON \
  -DMNN_BUILD_BENCHMARK=ON \
  -DMNN_BUILD_LLM=ON \
  -DMNN_LOW_MEMORY=ON \
  -DMNN_KLEIDIAI=ON

make -j$(nproc)
```

### 15.3 找不到 `benchmark.out`

检查是否启用了：

```text
-DMNN_BUILD_BENCHMARK=ON
```

如果没有启用，重新编译。

### 15.4 找不到 `llm_demo`

检查是否启用了：

```text
-DMNN_BUILD_LLM=ON
```

如果只编译了基础 OpenCL 库，而没有启用 `MNN_BUILD_LLM=ON`，可能不会生成 `llm_demo`。

### 15.5 运行时加载了系统预装 MNN 库

如果执行：

```bash
ldd ./llm_demo | grep -E "libMNN|Express|Audio|OpenCV|CL|Vulkan"
```

发现输出指向：

```text
/usr/share/cix/lib/
```

说明当前运行时加载的是系统预装库，不是当前 build-opencl 目录下的库。请设置：

```bash
export LD_LIBRARY_PATH=$HOME/mnn/MNN/build-opencl:$HOME/mnn/MNN/build-opencl/express:$HOME/mnn/MNN/build-opencl/tools/audio:$HOME/mnn/MNN/build-opencl/tools/cv:${LD_LIBRARY_PATH:-}
```

### 15.6 benchmark OpenCL 失败

如果执行：

```bash
./benchmark.out ../benchmark/models 10 3 3 4 2
```

出现 OpenCL 初始化失败或 fallback 到 CPU，需要检查：

* `clinfo` 是否能识别 OpenCL device。
* `libMNN_CL.so` 是否生成。
* `LD_LIBRARY_PATH` 是否指向当前 build-opencl。
* 是否加载了系统旧版 MNN 库。
* 当前 GPU OpenCL Runtime 是否与 MNN OpenCL 后端兼容。

### 15.7 模型文件没有完整下载

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

### 15.8 模型能跑但不确定是否用了 OpenCL

这是正常情况。模型能跑不等于一定使用了 OpenCL。

需要进一步确认：

* `config-opencl.json` 中是否设置了 `"backend_type": "opencl"`。
* 运行日志中是否有 OpenCL / GPU / kernel 相关信息。
* benchmark `forwardtype=3` 是否能正常执行。
* CPU / OpenCL 的性能是否存在差异。
* 是否存在 fallback 到 CPU 的日志。

在无法确认 OpenCL 实际参与推理前，建议表述为：

```text
MNN OpenCL build 可完成模型加载和文本推理流程，但是否所有算子均实际使用 OpenCL 后端仍需进一步确认。
```

### 15.9 OpenCL 路径反而更慢

可能原因：

* 模型算子不适合 GPU。
* OpenCL backend 算子覆盖不足。
* 数据搬运开销较大。
* 小模型或短输入下 GPU 启动开销占比高。
* 驱动实现差异。

建议保留 CPU 路径作为稳定 baseline。

## 16. 参考资料

* [MNN GitHub Repository](https://github.com/alibaba/MNN)
* [MNN Build Documentation](https://mnn-docs.readthedocs.io/en/2.6.1/compile/engine.html)
* [MNN Benchmark Documentation](https://mnn-docs.readthedocs.io/en/latest/tools/benchmark.html)
* [MNN LLM Documentation](https://mnn-docs.readthedocs.io/en/latest/transformers/llm.html)
* [Arm Learning Path: Build a Multimodal Retail Restocking Assistant on Armv9 With MNN](https://learn.arm.com/learning-paths/cross-platform/multimodel_mnn_v9/)
* [Qwen2.5-0.5B-Instruct-MNN ModelScope Repository](https://www.modelscope.cn/MNN/Qwen2.5-0.5B-Instruct-MNN)
* [OpenCL Overview](https://www.khronos.org/opencl/)
