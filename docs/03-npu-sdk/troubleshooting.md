# NPU SDK Troubleshooting

本文档集中记录 CIX P1 / Radxa Orion O6 类开发板上 NPU SDK、NOE Runtime、NOE Compiler 和 AI ModelHub 示例的常见问题与排查方法。

```{note}
本页用于集中放置问题排查。  
其他页面只保留安装、编译和运行主流程，不再重复展开大量 FAQ。
```

## 1. 快速定位路径

遇到问题时，建议按以下顺序排查：

```text
System / Release
    |
    v
NPU Kernel Driver
    |
    v
/dev/aipu
    |
    v
NPU UMD / NOE UMD / AI Engine
    |
    v
Python libnoe
    |
    v
.cix Model
    |
    v
inference_npu.py
```

先确认底层，再排查模型和脚本。

## 2. 一键检查脚本

可以创建一个检查脚本：

```bash
cat > ~/check_npu_runtime.sh <<'EOF'
#!/usr/bin/env bash

echo "===== System ====="
uname -a
cat /etc/os-release | head -20

echo
echo "===== Architecture ====="
uname -m

echo
echo "===== NPU Device Node ====="
ls -l /dev/aipu || true

echo
echo "===== Kernel Module ====="
lsmod | grep aipu || true
modinfo aipu 2>/dev/null | head -40 || true

echo
echo "===== DKMS ====="
dkms status | grep aipu || true

echo
echo "===== Driver File ====="
find /lib/modules/$(uname -r) -name "aipu.ko*" 2>/dev/null || true

echo
echo "===== CIX Packages ====="
dpkg -l | grep -E "cix-npu-driver|cix-npu-umd|cix-noe-umd|cix-ai-engine" || true

echo
echo "===== CIX Libraries ====="
ls -l /usr/share/cix/lib/libnoe.so 2>/dev/null || true
ls -l /usr/share/cix/include/npu/cix_noe_standard_api.h 2>/dev/null || true

echo
echo "===== Python Packages ====="
python3 -m pip list | grep -E "libnoe|noe|cix" || true

echo
echo "===== dmesg ====="
dmesg | grep -iE "aipu|npu|noe" | tail -80 || true
EOF

chmod +x ~/check_npu_runtime.sh
```

运行：

```bash
~/check_npu_runtime.sh
```

## 3. `/dev/aipu` 不存在

### 3.1 现象

执行：

```bash
ls -l /dev/aipu
```

出现：

```text
No such file or directory
```

### 3.2 可能原因

* NPU KMD 未安装。
* NPU KMD 与当前 Kernel 不匹配。
* DKMS 编译失败。
* 驱动未成功加载。
* 安装 deb 后未重启。
* 当前系统镜像或 DTS 基线不包含 NPU 配置。
* 使用了不匹配的 AI SDK Release。

### 3.3 排查命令

```bash
uname -r
ls /usr/src | grep aipu
dkms status | grep aipu
find /lib/modules/$(uname -r) -name "aipu.ko*"
lsmod | grep aipu
dmesg | grep -iE "aipu|npu" | tail -80
```

### 3.4 处理建议

如果 `/usr/src` 下存在 `aipu-*` 目录，例如 `aipu-6.0.0`：

```bash
sudo dkms build -m aipu -v 6.0.0 --force
sudo dkms install -m aipu -v 6.0.0 --force
sudo reboot
```

```{note}
`6.0.0` 只是示例版本，请根据 `/usr/src/aipu-*` 的实际目录名修改。
```

如果 DKMS 成功但仍没有 `/dev/aipu`，检查 kernel log：

```bash
dmesg | grep -iE "aipu|npu|firmware|error|fail" | tail -100
```

## 4. `pip3 list | grep libnoe` 没有输出

### 4.1 现象

执行：

```bash
pip3 list | grep libnoe
```

没有任何输出。

### 4.2 可能原因

* `cix-noe-umd` 未安装。
* `cix-ai-engine` 未安装。
* 使用了虚拟环境，但包安装在系统 Python。
* `pip3` 和 `python3` 指向不同环境。
* 当前 Release 的 Python 包名发生变化。

### 4.3 排查命令

```bash
dpkg -l | grep -E "cix-noe-umd|cix-ai-engine"
which python3
which pip3
python3 -m pip list | grep -E "libnoe|noe|cix"
```

检查 NOE 动态库：

```bash
ls -l /usr/share/cix/lib/libnoe.so
ls -l /usr/share/cix/include/npu/cix_noe_standard_api.h
```

### 4.4 处理建议

重新安装相关 deb 包：

```bash
cd ~/ai-sdk
sudo dpkg -i cix-noe-umd_*_arm64.deb
sudo dpkg -i cix-ai-engine_*_arm64.deb
sudo apt -f install
```

然后重新检查：

```bash
python3 -m pip list | grep -E "libnoe|noe|cix"
```

## 5. `dpkg -i` 依赖错误

### 5.1 现象

安装 deb 包时出现 dependency problems。

### 5.2 处理方式

执行：

```bash
sudo apt -f install
```

然后重新安装：

```bash
cd ~/ai-sdk
sudo dpkg -i *.deb
```

确认安装结果：

```bash
dpkg -l | grep -E "cix-npu-driver|cix-npu-umd|cix-noe-umd|cix-ai-engine"
```

## 6. DKMS 编译失败

### 6.1 现象

执行：

```bash
sudo dkms build -m aipu -v <VERSION> --force
```

失败。

### 6.2 可能原因

* 缺少当前 Kernel 对应的 headers。
* `build-essential` 或 `dkms` 未安装。
* `aipu-*` 版本号写错。
* 当前 KMD 源码与 Kernel 不匹配。
* AI SDK Release 与系统镜像不匹配。

### 6.3 排查命令

```bash
uname -r
ls /lib/modules/$(uname -r)/build
ls /usr/src | grep aipu
dkms status | grep aipu
```

### 6.4 处理建议

安装基础工具：

```bash
sudo apt update
sudo apt install -y dkms build-essential
```

如果缺少 kernel headers：

```bash
sudo apt install -y linux-headers-$(uname -r)
```

如果软件源中没有匹配 headers，需要向维护人员确认当前 Release 对应的 headers 或已编译 KMD 包。

## 7. `cixbuild` 找不到

### 7.1 现象

执行：

```bash
cixbuild -v
```

出现：

```text
command not found
```

### 7.2 可能原因

* 没有安装 `CixBuilder-xxx.whl`。
* Python 环境未激活。
* 安装到了用户目录，但 `~/.local/bin` 不在 `PATH`。
* 当前机器不是 NOE Compiler 安装环境。

### 7.3 排查命令

```bash
which cixbuild
python -m pip list | grep -i CixBuilder
echo $PATH
```

### 7.4 处理建议

激活环境后重新安装：

```bash
source ~/venvs/cix-noe/bin/activate
cd <NOE_COMPILER_PACKAGE_DIR>
pip install -r requirements.txt
pip install CixBuilder-xxx.whl
```

如果安装到了用户目录：

```bash
export PATH=$HOME/.local/bin:$PATH
```

再次检查：

```bash
cixbuild -v
```

## 8. Python 版本不匹配

### 8.1 现象

安装 `CixBuilder-xxx.whl` 失败，或导入依赖失败。

### 8.2 可能原因

* NOE Compiler 需要 Python 3.10。
* 当前系统默认 Python 不是 3.10。
* wheel 与 Python ABI 不匹配。

### 8.3 排查命令

```bash
python --version
pip --version
```

### 8.4 处理建议

创建 Python 3.10 环境：

```bash
conda create -n cix-noe python=3.10 -y
conda activate cix-noe
```

或：

```bash
python3.10 -m venv ~/venvs/cix-noe
source ~/venvs/cix-noe/bin/activate
```

重新安装：

```bash
pip install -r requirements.txt
pip install CixBuilder-xxx.whl
```

## 9. `cixbuild` 编译失败

### 9.1 现象

执行：

```bash
cixbuild cfg/onnx_resnet_v1_50build.cfg
```

失败，没有生成 `.cix` 文件。

### 9.2 常见原因

* 配置文件路径错误。
* 原始模型文件不存在。
* 输入节点名错误。
* 输入 shape 配置错误。
* 校准数据路径错误。
* `CIXLIB_PATH` / `CIXPLUGIN_PATH` 未设置。
* 当前模型存在不支持的算子。
* NOE Compiler 与 AI SDK Release 不匹配。

### 9.3 排查命令

```bash
pwd
ls -lh cfg/
ls -lh model/
ls -lh datasets/
grep -n "input_model\|input_shape\|calibration_data\|model_type\|model_domain" cfg/*.cfg
echo $CIXLIB_PATH
echo $CIXPLUGIN_PATH
```

提高日志级别：

```bash
export CIXBUILDER_LOG=1
cixbuild cfg/onnx_resnet_v1_50build.cfg 2>&1 | tee build.log
```

检查是否生成 `.cix`：

```bash
find . -name "*.cix" -print -exec ls -lh {} \;
```

## 10. `.cix` 模型不存在

### 10.1 现象

执行 NPU 推理时找不到模型文件：

```text
resnet_v1_50.cix not found
```

### 10.2 排查命令

```bash
pwd
find . -name "*.cix" -print
ls -lh
```

### 10.3 处理建议

如果模型未编译，回到主机侧执行：

```bash
cixbuild cfg/onnx_resnet_v1_50build.cfg
```

如果模型在主机侧，复制到开发板：

```bash
scp resnet_v1_50.cix cix@<BOARD_IP>:/home/cix/onnx_resnet_v1_50/
```

## 11. `python3 inference_npu.py` 加载模型失败

### 11.1 可能原因

* `.cix` 模型路径错误。
* `.cix` 与当前板端 NOE Runtime 版本不匹配。
* `/dev/aipu` 不存在。
* `libnoe` 没安装。
* 当前工作目录不对。
* 测试数据路径不对。

### 11.2 排查命令

```bash
pwd
ls -lh *.cix
ls -lh test_data
ls -l /dev/aipu
python3 -m pip list | grep -E "libnoe|noe|cix"
dmesg | grep -iE "aipu|npu|noe|error|fail" | tail -80
```

### 11.3 处理建议

进入正确模型目录运行：

```bash
cd ~/onnx_resnet_v1_50
python3 inference_npu.py
```

确认脚本中的模型路径：

```bash
grep -n "cix\|resnet\|test_data" inference_npu.py
```

## 12. NPU 初始化失败

### 12.1 现象

没有出现：

```text
npu: noe_init_context success
```

### 12.2 可能原因

* `/dev/aipu` 不存在。
* 当前用户没有访问 `/dev/aipu` 权限。
* KMD / UMD 版本不匹配。
* 驱动初始化失败。

### 12.3 排查命令

```bash
ls -l /dev/aipu
groups
dmesg | grep -iE "aipu|npu|noe|permission|denied|fail" | tail -100
```

### 12.4 处理建议

先用 sudo 验证是否是权限问题：

```bash
sudo python3 inference_npu.py
```

如果 sudo 可运行，说明普通用户权限不足，需要按当前 Release 的权限策略配置设备节点访问权限。

## 13. NPU 推理结果异常

### 13.1 现象

脚本能跑，但分类结果明显不对，或者输出全是异常值。

### 13.2 可能原因

* 预处理不匹配。
* 模型和脚本不匹配。
* `.cix` 不是当前 ONNX 编译出来的版本。
* 校准数据不合适。
* 量化配置不合适。
* 输入图片格式不符合预期。
* 使用了不同 Release 产物。

### 13.3 排查建议

先用 AI ModelHub 原始示例，不要改模型、图片、脚本：

```bash
cd ~/onnx_resnet_v1_50
python3 inference_npu.py
```

再对比 ONNX Runtime CPU 输出：

```bash
python3 inference_onnx.py
```

确认 NPU 和 ONNX Runtime 的输入图片、预处理、label 文件一致。

## 14. `import libnoe` 失败

### 14.1 现象

```bash
python3 - <<'PY'
import libnoe
PY
```

失败。

### 14.2 可能原因

* Python 包安装位置和当前 Python 不一致。
* 包名或导入方式在当前 Release 中不同。
* 缺少动态库路径。
* `cix-noe-umd` 或 `cix-ai-engine` 未正确安装。

### 14.3 排查命令

```bash
python3 -m pip list | grep -E "libnoe|noe|cix"
python3 -c "import sys; print(sys.path)"
dpkg -l | grep -E "cix-noe-umd|cix-ai-engine"
ls -l /usr/local/lib/python3.*/dist-packages/ | grep -i noe || true
```

### 14.4 处理建议

优先使用 AI ModelHub 示例脚本验证，因为不同 Release 的导入方式可能不同：

```bash
python3 inference_npu.py
```

如果示例脚本也失败，再检查安装包和 Python 环境。

## 15. `noe_benchmark` / `noe_profiler` 找不到

### 15.1 现象

执行：

```bash
which noe_benchmark
which noe_profiler
```

没有输出。

### 15.2 可能原因

* 当前 Release 没有安装调试工具。
* 工具不在 `PATH` 中。
* 相关 deb 包未安装。
* 工具名称或安装路径发生变化。

### 15.3 搜索工具

```bash
sudo find / -name "noe_benchmark" 2>/dev/null
sudo find / -name "noe_profiler" 2>/dev/null
```

如果找到工具目录，可以临时加入 `PATH`：

```bash
export PATH=<TOOL_DIR>:$PATH
```

## 16. `noe_benchmark` 使用方式

`noe_benchmark` 用于测试 NPU 长时间推理稳定性，一般需要：

```text
noe.cix
input.bin
output.bin
```

示例：

```bash
noe_benchmark -b noe.cix -i input.bin -c output.bin
```

如果当前模型目录没有 `input.bin` / `output.bin`，需要根据模型和示例生成对应输入输出二进制文件，或者优先使用 AI ModelHub 已经提供完整数据的示例。

## 17. `noe_profiler` 使用方式

`noe_profiler` 用于性能分析。通常需要模型在编译时开启 profile 相关配置。

如果没有生成 profile 数据，检查模型编译配置中的 `GBuilder` 段是否开启：

```ini
profile = True
```

然后重新编译模型：

```bash
cixbuild cfg/xxx.cfg
```

再运行 profiler。

## 18. 端到端检查清单

遇到问题时，可以按下面表格逐项确认：

| 层级     | 检查项        | 命令                                                        |                |     |       |
| ------ | ---------- | --------------------------------------------------------- | -------------- | --- | ----- |
| 系统     | 架构         | `uname -m`                                                |                |     |       |
| 系统     | Kernel     | `uname -r`                                                |                |     |       |
| KMD    | DKMS 状态    | `dkms status                                              | grep aipu`     |     |       |
| KMD    | 模块文件       | `find /lib/modules/$(uname -r) -name "aipu.ko*"`          |                |     |       |
| KMD    | 设备节点       | `ls -l /dev/aipu`                                         |                |     |       |
| UMD    | NOE 动态库    | `ls -l /usr/share/cix/lib/libnoe.so`                      |                |     |       |
| UMD    | NOE 头文件    | `ls -l /usr/share/cix/include/npu/cix_noe_standard_api.h` |                |     |       |
| Python | libnoe     | `python3 -m pip list                                      | grep libnoe`   |     |       |
| 编译器    | cixbuild   | `cixbuild -v`                                             |                |     |       |
| 模型     | `.cix` 文件  | `ls -lh *.cix`                                            |                |     |       |
| 示例     | NPU 推理     | `python3 inference_npu.py`                                |                |     |       |
| 日志     | Kernel log | `dmesg                                                    | grep -iE "aipu | npu | noe"` |

## 19. 最小可交付结论

如果需要在文档或报告中记录当前状态，可以按下面口径写：

```text
AI SDK 安装完成后，板端可通过 /dev/aipu、libnoe 和 dpkg 包版本确认 NPU Runtime 基础环境。
AI ModelHub 中 onnx_resnet_v1_50 示例可用于端到端验证：cixbuild 生成 .cix 模型后，在开发板上执行 inference_npu.py，若出现 noe_init_context、noe_load_graph、noe_create_job、noe_clean_job 等 success 日志，并输出图片分类结果，则说明 NPU 推理链路基本可用。
```

## 20. 参考资料

* CIX P1 NPU 开发指导手册
* CIX P1 NOE SDK 和 AI ModelHub 开发指导手册
