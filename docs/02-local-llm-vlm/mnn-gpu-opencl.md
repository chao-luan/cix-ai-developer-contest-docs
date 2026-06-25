# MNN GPU / OpenCL

本文档介绍如何在开发板上验证 MNN OpenCL 后端，包括 OpenCL Runtime 检查、MNN OpenCL 编译和基础验证方法。

```{warning}
Arm 官方 MNN Omni Learning Path 采用 CPU-first 路线。OpenCL 后端是否能加速具体 LLM / VLM / Omni 模型，取决于 MNN 后端支持、模型结构、算子覆盖、GPU 驱动和 Runtime 状态。本文档先用于验证 OpenCL 环境和 MNN OpenCL 编译路径，模型级加速效果需要板端实测。
```

## 1. 适用场景

* 验证开发板 GPU / OpenCL Runtime 是否可用。
* 验证 MNN 是否能启用 OpenCL 后端编译。
* 对比 MNN CPU 与 MNN OpenCL 后端的可用性。
* 为后续 GPU 加速模型推理提供基础环境检查。

## 2. 前置条件

* 开发板已正常启动。
* 已完成网络配置。
* GPU 驱动正常。
* OpenCL Runtime 可用。
* 已安装基础编译工具。
* 已准备 MNN 源码。

## 3. 安装基础依赖

```bash
sudo apt update
sudo apt install -y git build-essential gcc g++ cmake
```

安装 OpenCL 检查工具：

```bash
sudo apt install -y clinfo
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

## 6. 编译 MNN OpenCL 后端

```bash
mkdir -p build-opencl
cd build-opencl

cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DMNN_BUILD_SHARED=ON \
  -DMNN_OPENCL=ON

make -j$(nproc)
```

参数说明：

| 参数                         | 说明              |
| -------------------------- | --------------- |
| `MNN_BUILD_SHARED=ON`      | 构建共享库           |
| `MNN_OPENCL=ON`            | 启用 OpenCL 后端    |
| `CMAKE_BUILD_TYPE=Release` | 使用 Release 编译配置 |

## 7. 验证编译产物

检查 MNN 库是否生成：

```bash
ls -lh ~/mnn/MNN/build-opencl/libMNN.so
```

检查 OpenCL 相关构建输出：

```bash
find ~/mnn/MNN/build-opencl -iname "*opencl*" | head -50
```

## 8. 可选：同时启用 LLM / Omni 支持

如果需要在同一个构建目录中同时尝试 MNN LLM / Omni 和 OpenCL，可使用以下方式重新编译：

```bash
cd ~/mnn/MNN
mkdir -p build-opencl-llm
cd build-opencl-llm

cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DMNN_BUILD_SHARED=ON \
  -DMNN_OPENCL=ON \
  -DMNN_BUILD_LLM=ON \
  -DMNN_BUILD_AUDIO=ON \
  -DMNN_BUILD_LLM_OMNI=ON \
  -DMNN_LOW_MEMORY=ON \
  -DMNN_KLEIDIAI=ON

make -j$(nproc)
```

```{note}
即使编译时同时启用了 `MNN_OPENCL=ON` 和 LLM / Omni 相关选项，也不代表具体 LLM / VLM 模型一定会走 OpenCL 后端。是否使用 OpenCL 需要结合 MNN Runtime 配置、模型支持情况和运行日志确认。
```

## 9. 下载验证模型

可复用 MNN CPU / KleidiAI 页面中的 Qwen2.5 Omni MNN 模型包：

```bash
cd ~/mnn
git clone https://www.modelscope.cn/MNN/Qwen2.5-Omni-7B-MNN.git
cd ~/mnn/Qwen2.5-Omni-7B-MNN

sudo apt install -y git-lfs
git lfs install
git lfs pull
```

检查模型文件：

```bash
ls -lh ~/mnn/Qwen2.5-Omni-7B-MNN/config.json
ls -lh ~/mnn/Qwen2.5-Omni-7B-MNN/llm.mnn
ls -lh ~/mnn/Qwen2.5-Omni-7B-MNN/llm.mnn.weight
```

也可以下载图像测试资产：

```bash
mkdir -p ~/mnn/assets
wget -P ~/mnn/assets https://upload.wikimedia.org/wikipedia/commons/e/e6/Pet_Food_Aisle.jpg
file ~/mnn/assets/Pet_Food_Aisle.jpg
```

## 10. 基础模型加载验证

如果已编译 `build-opencl-llm`：

```bash
cd ~/mnn/MNN/build-opencl-llm
```

设置动态库路径：

```bash
export LD_LIBRARY_PATH=$HOME/mnn/MNN/build-opencl-llm:$HOME/mnn/MNN/build-opencl-llm/express:$HOME/mnn/MNN/build-opencl-llm/tools/audio:$HOME/mnn/MNN/build-opencl-llm/tools/cv:${LD_LIBRARY_PATH:-}
```

运行：

```bash
./llm_demo ~/mnn/Qwen2.5-Omni-7B-MNN/config.json
```

如果可以进入交互模式，说明当前构建的 MNN LLM Demo 能加载模型配置。

## 11. 文本推理验证

创建 prompt 文件：

```bash
cat > ~/mnn/text_baseline_prompt.txt <<'EOF'
You are an on-device inference assistant. In one short sentence, describe the benefits of multimodal on-device inference.
EOF
```

运行：

```bash
cd ~/mnn/MNN/build-opencl-llm
./llm_demo ~/mnn/Qwen2.5-Omni-7B-MNN/config.json ~/mnn/text_baseline_prompt.txt
```

如果能正常输出文本回复，说明模型加载和推理流程可用。

```{warning}
这一步只能说明当前 MNN 构建可以运行该模型，并不能直接证明推理实际使用了 OpenCL 后端。是否真正走 OpenCL，需要进一步查看 MNN Runtime 配置、日志或性能差异。
```

## 12. OpenCL 后端验证建议

建议采用分级验证：

### 12.1 系统级验证

```bash
clinfo
```

确认系统能识别 OpenCL 平台和设备。

### 12.2 编译级验证

```bash
cmake .. -DMNN_OPENCL=ON
make -j$(nproc)
```

确认 MNN 能启用 OpenCL 后端编译。

### 12.3 运行级验证

运行 MNN 模型，观察是否存在 OpenCL 初始化、设备选择、kernel 编译或 GPU 相关日志。

### 12.4 性能级验证

对同一个模型分别测试 CPU 构建和 OpenCL 构建：

```text
MNN CPU build
MNN OpenCL build
```

记录：

* 首次加载耗时。
* 推理耗时。
* CPU 使用率。
* GPU 使用率。
* 内存占用。
* 输出是否一致。

## 13. 验证结果记录

建议记录以下信息：

```bash
uname -a
cat /etc/os-release
lscpu
free -h
clinfo | grep -E "Platform Name|Device Name|Device Version|Driver Version"
```

表格记录：

| 项目                   | 结果  |
| -------------------- | --- |
| 开发板型号                | 待补充 |
| OS / Kernel          | 待补充 |
| GPU / OpenCL Runtime | 待补充 |
| `clinfo` 是否可用        | 待补充 |
| MNN OpenCL 是否编译成功    | 待补充 |
| 是否启用 LLM / Omni 支持   | 待补充 |
| 模型是否下载完整             | 待补充 |
| `llm_demo` 是否可运行     | 待补充 |
| 是否确认使用 OpenCL        | 待补充 |
| CPU / OpenCL 性能差异    | 待补充 |

## 14. 常见问题

### 14.1 `clinfo` 找不到 OpenCL device

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

### 14.2 编译 MNN OpenCL 失败

检查：

* `cmake` 是否安装。
* `gcc/g++` 是否安装。
* 是否缺少 OpenCL 相关开发包。
* 当前系统是否提供 OpenCL headers / libraries。

可尝试安装：

```bash
sudo apt install -y ocl-icd-opencl-dev opencl-headers
```

然后重新编译：

```bash
cd ~/mnn/MNN
rm -rf build-opencl
mkdir build-opencl && cd build-opencl

cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DMNN_BUILD_SHARED=ON \
  -DMNN_OPENCL=ON

make -j$(nproc)
```

### 14.3 模型能跑但不确定是否用了 OpenCL

这是正常情况。模型能跑不等于一定使用了 OpenCL。

需要进一步确认：

* MNN Runtime 配置。
* 运行日志。
* 是否有 OpenCL kernel 初始化信息。
* CPU / OpenCL 构建的性能差异。
* GPU 使用率。

### 14.4 OpenCL 路径反而更慢

可能原因：

* 模型算子不适合 GPU。
* OpenCL backend 算子覆盖不足。
* 数据搬运开销较大。
* 小模型或短输入下 GPU 启动开销占比高。
* 驱动实现差异。

建议保留 CPU 路径作为稳定基线。

## 15. 当前验证状态

| 项目                     | 状态  | 备注                     |
| ---------------------- | --- | ---------------------- |
| OpenCL Runtime 检查      | 待验证 | 通过 `clinfo`            |
| MNN OpenCL 编译          | 待验证 | `MNN_OPENCL=ON`        |
| LLM / Omni + OpenCL 构建 | 待验证 | 可选                     |
| Qwen2.5-Omni 模型下载      | 待验证 | ModelScope + Git LFS   |
| 模型加载                   | 待验证 | `llm_demo config.json` |
| 是否实际走 OpenCL           | 待确认 | 需日志或性能对比               |

## 16. 参考资料

* [MNN GitHub Repository](https://github.com/alibaba/MNN)
* [MNN Build Documentation](https://mnn-docs.readthedocs.io/en/2.6.1/compile/engine.html)
* [Arm Learning Path: Build a Multimodal Retail Restocking Assistant on Armv9 With MNN](https://learn.arm.com/learning-paths/cross-platform/multimodel_mnn_v9/)
* [Qwen2.5-Omni-7B-MNN ModelScope Repository](https://www.modelscope.cn/MNN/Qwen2.5-Omni-7B-MNN)
* [OpenCL Overview](https://www.khronos.org/opencl/)
