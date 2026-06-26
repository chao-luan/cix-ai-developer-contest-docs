# NOE Compiler

本文档介绍如何在 x86_64 Linux 主机上安装和使用 NOE Compiler，并通过 `cixbuild` 将第三方模型编译为 CIX P1 NPU 可执行的 `.cix` 模型文件。

```{warning}
NOE Compiler 通常运行在 x86_64 Linux 主机环境中，不建议直接在开发板上执行完整模型编译流程。

开发板侧主要负责运行已经编译好的 `.cix` 模型；模型解析、量化、优化和生成通常在主机侧完成。
```

## 1. 适用场景

* 在 x86_64 Linux 主机上安装 NOE Compiler。
* 使用 `cixbuild` 编译 ONNX / TensorFlow / TFLite / Caffe 模型。
* 将模型转换为 CIX P1 NPU 可执行的 `.cix` 文件。
* 为后续 AI ModelHub ResNet50 示例准备编译环境。

## 2. 工作流程

NOE Compiler 的典型工作流程如下：

```text
Original Model
    |
    |  ONNX / TensorFlow / TFLite / Caffe
    v
NOE Compiler / cixbuild
    |
    |  parse / quantize / optimize / generate
    v
CIX NPU Executable Model
    |
    |  .cix
    v
Run on CIX P1 NPU
```

简化理解：

| 阶段        | 作用           |
| --------- | ------------ |
| Parser    | 解析第三方模型      |
| Optimizer | 量化和图优化       |
| GBuilder  | 生成 NPU 可执行模型 |
| Profiler  | 分析模型性能       |

## 3. 前置条件

* x86_64 Linux 主机。
* Python 3.10 环境。
* 已获取当前 Release 对应的 NOE SDK。
* 已获取 `CixBuilder-xxx.whl`。
* 已获取对应的依赖文件，例如 `requirements.txt` 或 `lib_dependency.txt`。
* 已获取 AI ModelHub 示例工程。

```{warning}
NOE Compiler、AI SDK、AI ModelHub、系统镜像需要保持 Release 基线一致。不同版本混用可能导致模型编译成功但板端加载失败，或者板端推理结果异常。
```

## 4. 创建 Python 环境

建议使用 Conda 或 venv 创建独立 Python 3.10 环境。

### 4.1 Conda 方式

```bash
conda create -n cix-noe python=3.10 -y
conda activate cix-noe
```

### 4.2 venv 方式

```bash
python3.10 -m venv ~/venvs/cix-noe
source ~/venvs/cix-noe/bin/activate
```

确认 Python 版本：

```bash
python --version
```

期望类似：

```text
Python 3.10.x
```

## 5. 安装 NOE Compiler

进入 NOE Compiler 安装包目录：

```bash
cd <NOE_COMPILER_PACKAGE_DIR>
```

安装依赖：

```bash
pip install -r requirements.txt
```

如果 Release 包中使用的是 `lib_dependency.txt`，则执行：

```bash
pip install -r lib_dependency.txt
```

安装 `CixBuilder`：

```bash
pip install CixBuilder-xxx.whl
```

```{note}
请将 `CixBuilder-xxx.whl` 替换为当前 Release 提供的实际 wheel 文件名。
```

验证安装：

```bash
cixbuild -v
```

如果可以输出版本号，说明 NOE Compiler 安装成功。

也可以查看帮助：

```bash
cixbuild -h
```

## 6. 环境变量

使用 `cixbuild` 前，可能需要根据当前 Release 设置以下环境变量。

```bash
export CIXLIB_PATH=<NOE_SDK_LIB_PATH>
export CIXPLUGIN_PATH=<NOE_SDK_PLUGIN_PATH>
export CIXBUILDER_LOG=2
```

参数说明：

| 环境变量             | 说明                    |
| ---------------- | --------------------- |
| `CIXLIB_PATH`    | NPU C 库搜索路径，多个路径用冒号分隔 |
| `CIXPLUGIN_PATH` | NPU 插件搜索路径，多个路径用冒号分隔  |
| `CIXBUILDER_LOG` | 编译器日志级别               |

`CIXBUILDER_LOG` 常用值：

|    值 | 说明                    |
| ---: | --------------------- |
|  `1` | 显示 DEBUG 及以上日志        |
|  `2` | 显示 WARN、INFO、ERROR 日志 |
|  `3` | 仅显示 INFO、ERROR 日志     |
|  `6` | 仅显示 ERROR 日志          |
| `10` | 不显示日志                 |

如需长期生效，可以写入 `~/.bashrc`：

```bash
echo 'export CIXLIB_PATH=<NOE_SDK_LIB_PATH>' >> ~/.bashrc
echo 'export CIXPLUGIN_PATH=<NOE_SDK_PLUGIN_PATH>' >> ~/.bashrc
echo 'export CIXBUILDER_LOG=2' >> ~/.bashrc
source ~/.bashrc
```

## 7. cixbuild 配置文件结构

`cixbuild` 使用 INI 格式配置文件。一个典型配置文件包含以下段落：

```ini
[Common]
mode = build

[Parser]
model_type = ONNX
model_name = resnet_v1_50
model_domain = image_classification
input_model = model/resnet50-v1-12-sim.onnx
input = data
input_shape = [1,224,224,3]

[Optimizer]
calibration_data = datasets/calib_data.npy
calibration_batch_size = 1
weight_bits = 8
activation_bits = 8

[GBuilder]
target = npu
```

```{note}
不同模型的输入节点名、输入 shape、量化配置、后处理配置不同。实际配置请优先参考 AI ModelHub 中对应模型目录下的 `cfg/*.cfg` 文件。
```

## 8. 编译 ResNet50 示例模型

以 AI ModelHub 中的 `onnx_resnet_v1_50` 为例。

进入模型目录：

```bash
cd <AI_MODEL_HUB_ROOT>/models/ComputeVision/Image_Classification/onnx_resnet_v1_50
```

查看目录：

```bash
ls
```

常见目录结构：

```text
cfg/
datasets/
test_data/
graph.json
model/
resnet_v1_50.cix
inference_npu.py
inference_onnx.py
ReadMe.md
```

如果模型目录中已经有编译配置：

```bash
ls cfg
```

编译模型：

```bash
cixbuild cfg/onnx_resnet_v1_50build.cfg
```

编译过程中会看到模型解析、图优化、量化和生成相关日志。

编译成功后，通常会生成：

```text
resnet_v1_50.cix
```

检查输出文件：

```bash
ls -lh resnet_v1_50.cix
```

## 9. 可选：ONNX 模型简化

部分 ONNX 模型可以先用 `onnxsim` 简化，再进行 NPU 编译。

安装：

```bash
pip install onnxsim
```

执行简化：

```bash
onnxsim model/resnet50-v1-12.onnx model/resnet50-v1-12-sim.onnx
```

```{note}
是否需要执行 ONNX 简化取决于模型本身和当前 Release 的编译器支持情况。若 AI ModelHub 已经提供 `*-sim.onnx`，可以直接使用。
```

## 10. 将编译产物复制到开发板

如果编译在主机侧完成，需要将 `.cix` 模型和推理脚本复制到开发板：

```bash
scp -r onnx_resnet_v1_50 cix@<BOARD_IP>:/home/cix/
```

或者只复制必要文件：

```bash
scp resnet_v1_50.cix cix@<BOARD_IP>:/home/cix/onnx_resnet_v1_50/
scp inference_npu.py cix@<BOARD_IP>:/home/cix/onnx_resnet_v1_50/
scp -r test_data cix@<BOARD_IP>:/home/cix/onnx_resnet_v1_50/
```

开发板侧运行推理请参考：

```text
ai-modelhub-resnet50.md
```

## 11. 验证结果记录

建议记录以下信息：

```bash
python --version
pip list | grep -E "CixBuilder|tensorflow|numpy|onnx"
cixbuild -v
```

建议记录表：

| 项目                           | 结果                               |
| ---------------------------- | -------------------------------- |
| 主机系统                         | 待补充                              |
| Python 版本                    | 待补充                              |
| NOE Compiler / CixBuilder 版本 | 待补充                              |
| AI ModelHub 分支               | 待补充                              |
| 模型名称                         | `onnx_resnet_v1_50`              |
| 编译配置                         | `cfg/onnx_resnet_v1_50build.cfg` |
| 输出模型                         | `resnet_v1_50.cix`               |
| 编译是否成功                       | 待补充                              |
| 备注                           | 待补充                              |

## 12. 下一步

完成 NOE Compiler 安装和模型编译后，继续阅读：

```text
ai-modelhub-resnet50.md
```

如遇到 `cixbuild` 找不到、Python 版本不匹配、依赖安装失败、`.cix` 未生成等问题，请参考：

```text
troubleshooting.md
```

## 13. 参考资料

* CIX P1 NOE SDK 和 AI ModelHub 开发指导手册
* CIX P1 NPU 开发指导手册
