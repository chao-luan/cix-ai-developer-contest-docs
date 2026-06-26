# MNN GPU / OpenCL

本文档记录如何在开发板上验证 MNN OpenCL 后端，包括 OpenCL Runtime 检查、MNN OpenCL 编译、OpenCL 产物确认、benchmark 后端验证，以及当前板端实测中遇到的 OpenCL backend fallback 问题。

```{important}
当前验证状态：MNN OpenCL 后端在本次板端测试中 **未验证通过**，本文档暂时作为问题记录与后续排查入口保留。

当前已确认现象：

- MNN CPU benchmark 可以正常运行。
- `build-opencl` 可以生成 `benchmark.out` 和 `llm_demo`。
- 指定 OpenCL 后端运行 benchmark 时，出现 `Can't Find type=3 backend, use 0 instead`。
- 该现象表示 MNN 收到了 OpenCL 后端请求，但未找到可用的 OpenCL backend，随后回退到 CPU 执行。

当前暂不确认是模型问题。该问题更可能与 OpenCL backend 注册、动态库加载、MNN 编译选项或板端 OpenCL Runtime 兼容性有关。后续需要继续定位。
```

```{warning}
MNN OpenCL 后端是否能加速具体 LLM / VLM 模型，取决于模型结构、MNN Runtime 配置、算子覆盖、GPU 驱动和 OpenCL Runtime 状态。

本文档将验证分为两层：

1. OpenCL 后端可用性验证：通过 `clinfo`、`libMNN_CL.so` 和 `benchmark.out forwardtype=3` 确认 MNN OpenCL 后端是否可以执行 MNN 模型。
2. LLM 流程验证：通过 `Qwen2.5-0.5B-Instruct-MNN` 和 `backend_type=opencl` 验证 OpenCL build 下的 `llm_demo` 是否可以完成文本生成。

在 OpenCL benchmark 出现 fallback 的情况下，不应直接写“LLM 已使用 OpenCL 加速”。
```

## 1. 适用场景

* 验证开发板 GPU / OpenCL Runtime 是否可用。
* 验证 MNN 是否能启用 OpenCL 后端编译。
* 验证 `benchmark.out` 是否可以通过 OpenCL 后端执行 MNN 模型。
* 验证 OpenCL build 下的 `llm_demo` 是否可以加载 MNN 文本模型。
* 记录当前 MNN OpenCL backend 未找到的问题，便于后续继续排查。

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
  -DMNN_SEP_BUILD=OFF \
  -DMNN_USE_SYSTEM_LIB=ON \
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
| `MNN_SEP_BUILD=OFF`        | 尝试将后端编入主构建，避免后端动态加载或注册问题                  |
| `MNN_USE_SYSTEM_LIB=ON`    | 使用系统库依赖                                   |
| `MNN_BUILD_BENCHMARK=ON`   | 编译 `benchmark.out`，用于明确验证 CPU / OpenCL 后端 |
| `MNN_BUILD_LLM=ON`         | 启用 LLM 支持，生成 `llm_demo`                   |
| `MNN_LOW_MEMORY=ON`        | 启用较低内存占用配置                                |
| `MNN_KLEIDIAI=ON`          | 启用 Arm KleidiAI 相关优化                      |

```{note}
如果 `MNN_KLEIDIAI=ON` 在当前 MNN 版本或系统环境下编译失败，可先去掉该选项，优先完成 OpenCL 编译验证。
```

编译完成后，确认 CMake 参数：

```bash
grep -E "MNN_OPENCL|MNN_SEP_BUILD|MNN_USE_SYSTEM_LIB|MNN_BUILD_BENCHMARK|MNN_BUILD_LLM" CMakeCache.txt
```

期望至少包含：

```text
MNN_OPENCL:BOOL=ON
MNN_SEP_BUILD:BOOL=OFF
MNN_BUILD_BENCHMARK:BOOL=ON
MNN_BUILD_LLM:BOOL=ON
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

重点关注是否存在类似文件：

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

如果 `benchmark.out` 和 `llm_demo` 都存在，说明 Benchmark 和 LLM Demo 编译完成。

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
export LD_LIBRARY_PATH=$HOME/mnn/MNN/build-opencl:$HOME/mnn/MNN/build-opencl/source/backend/opencl:$HOME/mnn/MNN/build-opencl/express:$HOME/mnn/MNN/build-opencl/tools/audio:$HOME/mnn/MNN/build-opencl/tools/cv:${LD_LIBRARY_PATH:-}
```

再次检查：

```bash
ldd ./benchmark.out | grep -E "libMNN|CL|OpenCL" || true
ldd ./llm_demo | grep -E "libMNN|Express|Audio|OpenCV|CL|Vulkan" || true
```

期望 MNN 相关库优先指向当前 build-opencl 目录，例如：

```text
libMNN.so => /home/cix/mnn/MNN/build-opencl/libMNN.so
```

```{note}
本次实测中，设置 `LD_LIBRARY_PATH` 后，`benchmark.out` 已经可以加载本地 `build-opencl/libMNN.so`，但 OpenCL benchmark 仍然出现 `Can't Find type=3 backend, use 0 instead`。因此该问题不只是普通的 `libMNN.so` 路径指向错误，还需要继续检查 OpenCL backend 注册或加载机制。
```

## 9. OpenCL 后端 benchmark 验证

`benchmark.out` 可以显式指定 MNN 后端类型。本文使用相同 benchmark 模型分别跑 CPU 和 OpenCL，以验证 OpenCL 后端是否可以执行 MNN 模型。

进入 build 目录：

```bash
cd ~/mnn/MNN/build-opencl

export LD_LIBRARY_PATH=$HOME/mnn/MNN/build-opencl:$HOME/mnn/MNN/build-opencl/source/backend/opencl:$HOME/mnn/MNN/build-opencl/express:$HOME/mnn/MNN/build-opencl/tools/audio:$HOME/mnn/MNN/build-opencl/tools/cv:${LD_LIBRARY_PATH:-}
```

确认 benchmark 模型目录存在：

```bash
ls ../benchmark/models
```

### 9.1 CPU benchmark

```bash
./benchmark.out ../benchmark/models 10 3 0 4 2
```

参数中的 `0` 表示 CPU 后端。

当前实测结果：CPU benchmark 可以正常运行，能够输出各个模型的耗时结果。

### 9.2 OpenCL benchmark

```bash
./benchmark.out ../benchmark/models 10 3 3 4 2
```

参数中的 `3` 表示 OpenCL 后端。

当前实测中，该命令未能真正使用 OpenCL 后端，出现以下错误：

```text
Can't Find type=3 backend, use 0 instead
```

该错误表示 MNN 没有找到 `type=3` 对应的 OpenCL backend，随后回退到 `type=0` CPU backend 执行。

```{important}
当前板端实测中，MNN OpenCL benchmark 未验证通过。

虽然命令中指定了 OpenCL 后端，且终端会显示：

Forward type: OpenCL

但随后会出现：

Can't Find type=3 backend, use 0 instead

因此当前实际执行路径仍然回退到了 CPU，不能写作“OpenCL 推理已跑通”。
```

建议将错误截图保存到：

```text
docs/_static/images/mnn-opencl-backend-fallback.jpg
```

并在后续文档中引用：

```md
![MNN OpenCL backend fallback](../_static/images/mnn-opencl-backend-fallback.jpg)
```

### 9.3 benchmark 参数说明

| 参数             |                   示例值 | 说明                       |
| -------------- | --------------------: | ------------------------ |
| `model_dir`    | `../benchmark/models` | benchmark 模型目录           |
| `loop_count`   |                  `10` | 循环次数                     |
| `warmup_count` |                   `3` | 预热次数                     |
| `forwardtype`  |             `0` / `3` | `0` 表示 CPU，`3` 表示 OpenCL |
| `thread_num`   |                   `4` | 线程数或执行配置                 |
| `precision`    |                   `2` | 低精度 / FP16 相关配置          |

## 10. 下载验证模型

本文档原计划使用 `Qwen2.5-0.5B-Instruct-MNN` 作为基础 LLM 验证模型。

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

MNN LLM 模型目录中包含默认 `config.json`。为了对比 CPU 与 OpenCL 后端，可以分别创建：

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

```{warning}
由于当前 benchmark 已确认 OpenCL backend 未找到，LLM 的 `backend_type=opencl` 验证暂时不应作为 OpenCL 已跑通的证据。建议等 benchmark `forwardtype=3` 不再 fallback 后，再继续验证 LLM OpenCL 路径。
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

export LD_LIBRARY_PATH=$HOME/mnn/MNN/build-opencl:$HOME/mnn/MNN/build-opencl/source/backend/opencl:$HOME/mnn/MNN/build-opencl/express:$HOME/mnn/MNN/build-opencl/tools/audio:$HOME/mnn/MNN/build-opencl/tools/cv:${LD_LIBRARY_PATH:-}

./llm_demo ~/mnn/Qwen2.5-0.5B-Instruct-MNN/config-cpu.json ~/mnn/text_baseline_prompt.txt 2>&1 | tee ~/mnn/mnn-cpu-llm.log
```

如果能正常输出文本回复，说明当前 build 下的 LLM 文本流程可用。

### 12.2 OpenCL 配置验证

使用 OpenCL build 中的 `llm_demo` 加载 OpenCL 配置：

```bash
cd ~/mnn/MNN/build-opencl

export LD_LIBRARY_PATH=$HOME/mnn/MNN/build-opencl:$HOME/mnn/MNN/build-opencl/source/backend/opencl:$HOME/mnn/MNN/build-opencl/express:$HOME/mnn/MNN/build-opencl/tools/audio:$HOME/mnn/MNN/build-opencl/tools/cv:${LD_LIBRARY_PATH:-}

./llm_demo ~/mnn/Qwen2.5-0.5B-Instruct-MNN/config-opencl.json ~/mnn/text_baseline_prompt.txt 2>&1 | tee ~/mnn/mnn-opencl-llm.log
```

```{warning}
当前 OpenCL benchmark 已出现 fallback 到 CPU 的问题，因此即使 `config-opencl.json` 能够启动文本生成，也不能直接说明 LLM 已经使用 OpenCL 后端。需要先解决 `Can't Find type=3 backend, use 0 instead` 问题。
```

## 13. 当前实测结果记录

当前板端实测状态如下：

| 验证层级   | 验证项                                        | 当前状态        | 说明                             |
| ------ | ------------------------------------------ | ----------- | ------------------------------ |
| 系统级    | `clinfo` 可识别 OpenCL device                 | 待补充         | 需要根据实际 `clinfo` 输出确认           |
| 编译级    | `MNN_OPENCL=ON` 编译                         | 已执行         | `build-opencl` 可以完成编译          |
| 产物级    | `benchmark.out`                            | 通过          | 已生成                            |
| 产物级    | `llm_demo`                                 | 通过          | 已生成                            |
| 运行级    | CPU benchmark                              | 通过          | `forwardtype=0` 可以正常运行         |
| 运行级    | OpenCL benchmark                           | 未通过         | `forwardtype=3` fallback 到 CPU |
| 错误信息   | `Can't Find type=3 backend, use 0 instead` | 已复现         | 表示未找到 OpenCL backend           |
| LLM 流程 | 0.5B MNN 文本模型                              | 暂不作为 GPU 证据 | 需要先解决 OpenCL backend fallback  |

当前结论：

```text
MNN CPU 路径已验证可用。
MNN OpenCL 编译路径和 benchmark 工具已生成。
但 MNN OpenCL benchmark 当前未验证通过，指定 forwardtype=3 后 fallback 到 CPU。
因此当前不能写作 MNN GPU/OpenCL 推理已跑通。
```

## 14. 后续排查方向

后续可以从以下方向继续定位：

### 14.1 检查 OpenCL Runtime

```bash
clinfo
clinfo | grep -E "Platform Name|Device Name|Device Version|Driver Version"
ls /etc/OpenCL/vendors/
```

确认系统是否存在 OpenCL platform 和 device。

### 14.2 检查 OpenCL backend 产物

```bash
cd ~/mnn/MNN/build-opencl

find . -type f \( -name "libMNN_CL.so*" -o -name "*MNN_CL*.so*" -o -name "*OpenCL*.so*" \) -print -exec ls -lh {} \;
```

确认本地 build 中是否真的生成了 OpenCL backend 动态库。

### 14.3 检查动态库加载路径

```bash
cd ~/mnn/MNN/build-opencl

ldd ./benchmark.out | grep -E "libMNN|CL|OpenCL" || true
ldd ./llm_demo | grep -E "libMNN|Express|Audio|OpenCV|CL|Vulkan" || true
```

确认是否加载了本地构建产物，而不是系统预装库。

### 14.4 尝试强制预加载 OpenCL backend

如果本地能找到 `libMNN_CL.so`，可尝试：

```bash
cd ~/mnn/MNN/build-opencl

CL_SO=$(find . -name "libMNN_CL.so*" | head -1)
echo "$CL_SO"

LD_PRELOAD="$CL_SO" ./benchmark.out ../benchmark/models 10 3 3 4 2
```

如果仍然出现：

```text
Can't Find type=3 backend, use 0 instead
```

说明问题可能不只是动态库搜索路径，而是 OpenCL backend 注册或编译方式问题。

### 14.5 尝试不同 MNN 编译选项

可尝试重新编译：

```bash
cd ~/mnn/MNN

rm -rf build-opencl
mkdir -p build-opencl
cd build-opencl

cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DMNN_BUILD_SHARED=ON \
  -DMNN_OPENCL=ON \
  -DMNN_SEP_BUILD=OFF \
  -DMNN_USE_SYSTEM_LIB=ON \
  -DMNN_BUILD_BENCHMARK=ON \
  -DMNN_BUILD_LLM=ON \
  -DMNN_LOW_MEMORY=ON

make -j$(nproc)
```

如果 `MNN_KLEIDIAI=ON` 干扰 OpenCL 构建，可先去掉 `MNN_KLEIDIAI=ON`，优先验证 OpenCL backend 是否可以注册。

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
  -DMNN_SEP_BUILD=OFF \
  -DMNN_USE_SYSTEM_LIB=ON \
  -DMNN_BUILD_BENCHMARK=ON \
  -DMNN_BUILD_LLM=ON \
  -DMNN_LOW_MEMORY=ON

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
export LD_LIBRARY_PATH=$HOME/mnn/MNN/build-opencl:$HOME/mnn/MNN/build-opencl/source/backend/opencl:$HOME/mnn/MNN/build-opencl/express:$HOME/mnn/MNN/build-opencl/tools/audio:$HOME/mnn/MNN/build-opencl/tools/cv:${LD_LIBRARY_PATH:-}
```

### 15.6 benchmark OpenCL 失败

如果执行：

```bash
./benchmark.out ../benchmark/models 10 3 3 4 2
```

出现：

```text
Can't Find type=3 backend, use 0 instead
```

说明 MNN 未找到 OpenCL backend，并回退到 CPU。

可能原因：

* `libMNN_CL.so` 未生成。
* `libMNN_CL.so` 未被正确加载。
* OpenCL backend 没有注册到 MNN Runtime。
* `MNN_SEP_BUILD` / 动态后端加载策略与当前 Linux 环境不匹配。
* 系统 OpenCL Runtime 与 MNN OpenCL 后端存在兼容问题。
* 当前构建加载了系统旧版 MNN 库，导致本地 OpenCL backend 未生效。

当前处理建议：

```bash
cd ~/mnn/MNN/build-opencl

find . -type f \( -name "libMNN_CL.so*" -o -name "*MNN_CL*.so*" -o -name "*OpenCL*.so*" \) -print -exec ls -lh {} \;

ldd ./benchmark.out | grep -E "libMNN|CL|OpenCL" || true

export LD_LIBRARY_PATH=$HOME/mnn/MNN/build-opencl:$HOME/mnn/MNN/build-opencl/source/backend/opencl:$HOME/mnn/MNN/build-opencl/express:$HOME/mnn/MNN/build-opencl/tools/audio:$HOME/mnn/MNN/build-opencl/tools/cv:${LD_LIBRARY_PATH:-}

./benchmark.out ../benchmark/models 10 3 3 4 2
```

如果仍然失败，建议保留该问题，后续结合 MNN 版本、Release 基线和 GPU OpenCL Runtime 继续排查。

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

在当前 benchmark 已经出现 fallback 的情况下，不建议使用 LLM 文本生成结果作为 GPU 推理成功证据。

### 15.9 OpenCL 路径反而更慢

可能原因：

* 模型算子不适合 GPU。
* OpenCL backend 算子覆盖不足。
* 数据搬运开销较大。
* 小模型或短输入下 GPU 启动开销占比高。
* 驱动实现差异。

建议保留 CPU 路径作为稳定 baseline。

## 16. 当前文档结论

当前文档结论如下：

```text
MNN CPU 路径已验证可用。
MNN OpenCL 相关编译流程已尝试，benchmark.out 与 llm_demo 可以生成。
但在当前板端环境下，benchmark 指定 forwardtype=3 后出现 Can't Find type=3 backend, use 0 instead，并回退到 CPU。
因此，当前 MNN GPU / OpenCL 推理未验证通过，暂作为已知问题保留。
```

后续若需要继续推进，应优先解决 OpenCL backend 注册或加载问题，而不是继续更换 LLM 模型。

## 17. 参考资料

* [MNN GitHub Repository](https://github.com/alibaba/MNN)
* [MNN Build Documentation](https://mnn-docs.readthedocs.io/en/2.6.1/compile/engine.html)
* [MNN Benchmark Documentation](https://mnn-docs.readthedocs.io/en/latest/tools/benchmark.html)
* [MNN LLM Documentation](https://mnn-docs.readthedocs.io/en/latest/transformers/llm.html)
* [Arm Learning Path: Build a Multimodal Retail Restocking Assistant on Armv9 With MNN](https://learn.arm.com/learning-paths/cross-platform/multimodel_mnn_v9/)
* [Qwen2.5-0.5B-Instruct-MNN ModelScope Repository](https://www.modelscope.cn/MNN/Qwen2.5-0.5B-Instruct-MNN)
* [OpenCL Overview](https://www.khronos.org/opencl/)
