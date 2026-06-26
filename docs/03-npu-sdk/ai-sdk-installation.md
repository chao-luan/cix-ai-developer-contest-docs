# AI SDK Installation

本文档介绍如何在 CIX P1 / Radxa Orion O6 类开发板上安装和验证 NPU 相关 AI SDK 组件，包括 NPU 内核态驱动、用户态运行时库、NOE 运行时和 Python 推理组件。

本页重点是 **板端运行环境安装与检查**。
模型编译、量化和 `.cix` 模型生成请参考后续 `noe-compiler.md` 和 `ai-modelhub-resnet50.md`。

```{warning}
本文档中的软件包版本、下载地址和 Release 名称需要以当前比赛提供的 Release 包或维护人员发布的信息为准。

不同 Release 之间的包名、版本号和依赖关系可能不同。不要混用不同 Release 的 NPU 驱动、NOE UMD、AI Engine 和系统镜像。
```

## 1. 适用场景

* 首次在开发板上安装 NPU / NOE 运行环境。
* 检查系统是否已经包含 NPU 驱动和 NOE 运行时。
* 验证 `/dev/aipu` 是否存在。
* 验证 Python 侧 `libnoe` 是否安装。
* 为后续 AI ModelHub 示例、YOLOX / OCR / NPU 推理 Demo 做准备。

## 2. 组件说明

AI SDK 通常包含以下几类组件：

| 组件                | 示例包名                           | 作用                           |
| ----------------- | ------------------------------ | ---------------------------- |
| NPU Kernel Driver | `cix-npu-driver_xxx_arm64.deb` | NPU 内核态驱动，安装后生成或更新 `aipu.ko` |
| NPU UMD           | `cix-npu-umd_xxx_arm64.deb`    | NPU 用户态运行时库                  |
| NOE UMD           | `cix-noe-umd_xxx_arm64.deb`    | NOE 统一用户态运行时接口               |
| AI Engine         | `cix-ai-engine_xxx_arm64.deb`  | Python 推理引擎和上层运行组件           |

示例版本如下，实际以当前 Release 为准：

```text
cix-npu-driver_3.0.3_arm64.deb
cix-npu-umd_3.0.2_arm64.deb
cix-noe-umd_3.1.2_arm64.deb
cix-ai-engine_1.1.0_arm64.deb
```

```{note}
NPU KMD 是 kernel mode driver，负责内核态设备管理。  
NPU UMD / NOE UMD 是 user mode driver，负责用户态 API、模型加载、任务创建和推理调度。
```

## 3. 前置条件

* 开发板已正常启动。
* 系统镜像版本与 AI SDK Release 匹配。
* 已完成网络配置。
* 已获得当前 Release 的 AI SDK 软件包。
* 当前用户具备 `sudo` 权限。

检查系统信息：

```bash
uname -a
cat /etc/os-release
```

检查架构：

```bash
uname -m
```

期望输出为：

```text
aarch64
```

## 4. 准备工作目录

建议统一放在 `~/ai-sdk`：

```bash
mkdir -p ~/ai-sdk
cd ~/ai-sdk
```

将当前 Release 提供的 deb 包放入该目录，例如：

```text
~/ai-sdk/
├── cix-npu-driver_3.0.3_arm64.deb
├── cix-npu-umd_3.0.2_arm64.deb
├── cix-noe-umd_3.1.2_arm64.deb
└── cix-ai-engine_1.1.0_arm64.deb
```

如果使用 `wget` 下载，请将 URL 替换为当前 Release 提供的实际地址：

```bash
cd ~/ai-sdk

wget <AI_SDK_RELEASE_URL>/cix-npu-driver_xxx_arm64.deb
wget <AI_SDK_RELEASE_URL>/cix-npu-umd_xxx_arm64.deb
wget <AI_SDK_RELEASE_URL>/cix-noe-umd_xxx_arm64.deb
wget <AI_SDK_RELEASE_URL>/cix-ai-engine_xxx_arm64.deb
```

```{warning}
不要直接复制旧文档中的历史下载地址。  
AI SDK 必须与系统镜像、Kernel、BIOS 和 Release 基线匹配。
```

## 5. 安装基础依赖

安装 `dkms` 和常用工具：

```bash
sudo apt update
sudo apt install -y dkms build-essential linux-headers-$(uname -r)
```

如果 `linux-headers-$(uname -r)` 无法安装，说明当前软件源可能没有匹配的 kernel headers。此时应优先确认当前 Release 是否已经内置可用的 NPU KMD，或者向维护人员确认对应 headers / driver 包。

## 6. 安装 NPU Kernel Driver

进入 AI SDK 目录：

```bash
cd ~/ai-sdk
```

安装 NPU 内核态驱动包：

```bash
sudo dpkg -i cix-npu-driver_*_arm64.deb
```

如果出现依赖错误，执行：

```bash
sudo apt -f install
```

检查 `/usr/src` 中是否出现 `aipu` 源码目录：

```bash
ls /usr/src | grep aipu
```

常见目录形式：

```text
aipu-6.0.0
```

如果 Release 要求手动通过 DKMS 编译和安装 NPU 模块，可以执行：

```bash
sudo dkms build -m aipu -v 6.0.0 --force
sudo dkms install -m aipu -v 6.0.0 --force
```

```{note}
上面的 `6.0.0` 只是示例版本。请根据 `/usr/src/` 中实际出现的 `aipu-*` 目录调整版本号。
```

查看 DKMS 状态：

```bash
dkms status | grep aipu
```

## 7. 安装 NPU UMD、NOE UMD 和 AI Engine

继续在 `~/ai-sdk` 目录执行：

```bash
cd ~/ai-sdk
```

安装 NPU 用户态运行时库：

```bash
sudo dpkg -i cix-npu-umd_*_arm64.deb
```

安装 NOE 用户态运行时库：

```bash
sudo dpkg -i cix-noe-umd_*_arm64.deb
```

安装 AI Engine：

```bash
sudo dpkg -i cix-ai-engine_*_arm64.deb
```

如出现依赖错误，执行：

```bash
sudo apt -f install
```

建议安装完成后重启系统：

```bash
sudo reboot
```

## 8. 验证 NPU 设备节点

重启后，检查 NPU 设备节点：

```bash
ls -l /dev/aipu
```

如果正常，应能看到类似输出：

```text
crw------- 1 root root ... /dev/aipu
```

检查内核模块：

```bash
lsmod | grep aipu
```

检查模块信息：

```bash
modinfo aipu
```

如果 `/dev/aipu` 不存在，可以先查看 kernel log：

```bash
dmesg | grep -iE "aipu|npu|noe"
```

也可以检查驱动文件是否存在：

```bash
find /lib/modules/$(uname -r) -name "aipu.ko*"
```

```{warning}
如果 `/dev/aipu` 不存在，后续 NPU 推理一般无法正常运行。  
需要先确认 NPU KMD 是否安装、是否与当前 Kernel 匹配、是否成功加载。
```

## 9. 验证 NOE 用户态库

检查 NOE 动态库：

```bash
ls -l /usr/share/cix/lib/libnoe.so
```

检查 NOE 头文件：

```bash
ls -l /usr/share/cix/include/npu/cix_noe_standard_api.h
```

检查 Python 扩展模块：

```bash
pip3 list | grep libnoe
```

如果可以看到 `libnoe`，说明 Python 侧 NOE 组件已安装。

也可以尝试 Python import：

```bash
python3 - <<'PY'
try:
    import libnoe
    print("libnoe import ok")
except Exception as e:
    print("libnoe import failed:", e)
PY
```

```{note}
不同 Release 的 Python 包名和模块导入方式可能存在差异。  
如果 `pip3 list | grep libnoe` 能看到版本，但 `import libnoe` 失败，请以当前 Release 的 user guide 或示例代码为准。
```

## 10. 验证 AI Engine 安装

检查 AI Engine 相关包：

```bash
dpkg -l | grep -E "cix-ai-engine|cix-noe-umd|cix-npu-umd|cix-npu-driver"
```

检查 Python 包：

```bash
pip3 list | grep -E "cix|noe|libnoe"
```

如果 AI Engine 安装后提供命令行工具，可通过以下方式搜索：

```bash
which cixbuild || true
which noe_benchmark || true
which noe_profiler || true
```

```{note}
`cixbuild` 通常属于 NOE 编译器，主要安装在 x86_64 Linux 主机侧，不一定出现在开发板侧。开发板侧重点是运行时、`/dev/aipu`、`libnoe` 和推理脚本。
```

## 11. 快速检查脚本

可以创建一个快速检查脚本：

```bash
cat > ~/ai-sdk/check_npu_runtime.sh <<'EOF'
#!/usr/bin/env bash
set -e

echo "===== System ====="
uname -a
cat /etc/os-release | head

echo
echo "===== Device Node ====="
ls -l /dev/aipu || true

echo
echo "===== Kernel Module ====="
lsmod | grep aipu || true
modinfo aipu 2>/dev/null | head || true

echo
echo "===== DKMS ====="
dkms status | grep aipu || true

echo
echo "===== CIX Libraries ====="
ls -l /usr/share/cix/lib/libnoe.so 2>/dev/null || true
ls -l /usr/share/cix/include/npu/cix_noe_standard_api.h 2>/dev/null || true

echo
echo "===== Python Packages ====="
pip3 list | grep -E "libnoe|cix|noe" || true

echo
echo "===== dmesg ====="
dmesg | grep -iE "aipu|npu|noe" | tail -50 || true
EOF

chmod +x ~/ai-sdk/check_npu_runtime.sh
```

运行：

```bash
~/ai-sdk/check_npu_runtime.sh
```

## 12. 使用 AI ModelHub 进行 NPU 推理验证

安装 AI SDK 后，建议通过 AI ModelHub 中的预置示例进行 NPU 推理验证。

典型流程如下：

1. 在 x86_64 Linux 主机侧安装 NOE 编译器。
2. 使用 `cixbuild` 将 ONNX / TensorFlow / TFLite / Caffe 模型编译为 `.cix` 模型。
3. 将 `.cix` 模型和推理脚本复制到开发板。
4. 在开发板上执行 NPU 推理脚本。

以 ResNet50 示例为例，AI ModelHub 中常见目录如下：

```text
models/
└── ComputeVision/
    └── Image_Classification/
        └── onnx_resnet_v1_50/
            ├── cfg/
            ├── datasets/
            ├── test_data/
            ├── graph.json
            ├── model/
            ├── resnet_v1_50.cix
            ├── inference_npu.py
            ├── inference_onnx.py
            └── ReadMe.md
```

如果目录中已经包含编译好的 `.cix` 模型，可以直接在开发板上运行：

```bash
cd <AI_MODEL_HUB_ROOT>/models/ComputeVision/Image_Classification/onnx_resnet_v1_50

python3 inference_npu.py
```

正常情况下，日志中应看到类似内容：

```text
npu: noe_init_context success
npu: noe_load_graph success
Input tensor count is 1.
Output tensor count is 1.
npu: noe_create_job success
...
npu: noe_clean_job success
npu: noe_unload_graph success
npu: noe_deinit_context success
```

如果能看到模型分类结果和上述 `success` 日志，说明 NPU 运行时、NOE UMD、模型加载和推理流程基本可用。

## 13. 与 NOE Compiler 的关系

AI SDK 安装完成后，开发板只具备运行 `.cix` 模型的基础环境。
如果需要将原始模型转换为 NPU 可执行模型，还需要在 x86_64 Linux 主机上安装 NOE 编译器。

NOE 编译器安装流程通常如下：

```bash
pip3 install -r requirements.txt
pip3 install CixBuilder-xxx.whl
cixbuild -v
```

模型编译示例：

```bash
cixbuild cfg/onnx_resnet_v1_50build.cfg
```

编译成功后会生成类似：

```text
resnet_v1_50.cix
```

这部分详细流程请参考 `noe-compiler.md`。

## 14. 常见问题

### 14.1 `/dev/aipu` 不存在

可能原因：

* NPU KMD 未安装。
* 当前 Kernel 与 KMD 不匹配。
* DKMS 未编译成功。
* 驱动未加载。
* 当前系统镜像不包含 NPU DTS / driver 基线。
* 安装 deb 后未重启。

检查：

```bash
ls /usr/src | grep aipu
dkms status | grep aipu
find /lib/modules/$(uname -r) -name "aipu.ko*"
lsmod | grep aipu
dmesg | grep -iE "aipu|npu"
```

可尝试重启：

```bash
sudo reboot
```

### 14.2 `pip3 list | grep libnoe` 没有输出

可能原因：

* `cix-noe-umd` 未安装。
* `cix-ai-engine` 未安装。
* Python 环境不一致。
* 使用了虚拟环境，但包安装在系统 Python 中。
* 当前 Release 的 Python 包名发生变化。

检查：

```bash
dpkg -l | grep -E "cix-noe-umd|cix-ai-engine"
python3 -m pip list | grep -E "libnoe|noe|cix"
which python3
which pip3
```

### 14.3 `dpkg -i` 报依赖错误

执行：

```bash
sudo apt -f install
```

然后重新安装：

```bash
sudo dpkg -i *.deb
```

### 14.4 DKMS 编译失败

检查 kernel headers：

```bash
uname -r
ls /lib/modules/$(uname -r)/build
```

如果 `/lib/modules/$(uname -r)/build` 不存在，说明缺少当前 Kernel 对应的 headers，需要安装匹配 headers 或使用当前 Release 已编译好的 KMD。

### 14.5 NPU 推理脚本报模型加载失败

检查：

* `.cix` 模型是否存在。
* 模型是否由匹配版本的 NOE 编译器生成。
* 模型路径是否正确。
* `libnoe` 是否安装。
* `/dev/aipu` 是否存在。
* 当前脚本是否在正确目录运行。

常用检查命令：

```bash
ls -lh *.cix
ls -l /dev/aipu
pip3 list | grep libnoe
dmesg | grep -iE "aipu|npu|noe" | tail -50
```

## 15. 参考资料

* Radxa Orion O6 Artificial Intelligence Documentation
* CIX P1 NPU 开发指导手册
* CIX P1 NOE SDK 和 AI ModelHub 开发指导手册
