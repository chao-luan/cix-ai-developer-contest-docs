# AI ModelHub ResNet50 Example

本文档介绍如何使用 AI ModelHub 中的 `onnx_resnet_v1_50` 示例完成 CIX P1 NPU 的端到端验证。

该示例用于验证以下链路：

```text
ONNX Model
  -> NOE Compiler / cixbuild
  -> .cix Model
  -> NOE UMD / AI Engine
  -> CIX P1 NPU Inference
```

```{warning}
本文档默认 AI SDK 已在开发板侧安装完成，并且 `/dev/aipu`、`libnoe` 等运行时检查已通过。

如果尚未安装 AI SDK，请先完成 `ai-sdk-installation.md`。
```

## 1. 适用场景

* 验证 AI ModelHub 是否可用。
* 使用 ResNet50 图像分类示例验证 NPU 推理。
* 对比 ONNX Runtime CPU 推理和 NPU 推理。
* 检查 `.cix` 模型加载、NPU job 创建、输入输出 tensor 和推理结果。

## 2. 前置条件

### 2.1 开发板侧

开发板应满足：

* `/dev/aipu` 存在。
* `pip3 list | grep libnoe` 有输出。
* `cix-noe-umd`、`cix-npu-umd`、`cix-ai-engine` 已安装。
* 已获取 AI ModelHub 示例工程。
* 已有 `resnet_v1_50.cix`，或已经在主机侧完成编译。

检查：

```bash
ls -l /dev/aipu
pip3 list | grep libnoe
dpkg -l | grep -E "cix-npu-driver|cix-npu-umd|cix-noe-umd|cix-ai-engine"
```

### 2.2 主机侧

如果需要重新编译模型，主机侧应满足：

* x86_64 Linux。
* Python 3.10。
* 已安装 NOE Compiler / CixBuilder。
* `cixbuild -v` 可正常输出版本。

## 3. 获取 AI ModelHub

在有权限的环境中克隆 AI ModelHub：

```bash
git clone ssh://codereview.cixtech.com:29418/cix_opensource/ai_model_hub
cd ai_model_hub
```

切换到当前 Release 对应分支，例如：

```bash
git checkout cix_26_q1_dev
```

```{warning}
分支名称需要以当前 Release 或维护人员提供的信息为准。不要混用不同 Release 的 AI ModelHub、AI SDK 和系统镜像。
```

## 4. 进入 ResNet50 示例目录

```bash
cd ai_model_hub/models/ComputeVision/Image_Classification/onnx_resnet_v1_50
```

查看目录：

```bash
ls
```

典型目录结构如下：

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

主要文件说明：

| 文件 / 目录             | 说明                    |
| ------------------- | --------------------- |
| `cfg/`              | 模型编译配置文件              |
| `datasets/`         | 量化校准数据                |
| `test_data/`        | 推理测试图片                |
| `model/`            | 原始 ONNX 模型            |
| `resnet_v1_50.cix`  | 已编译的 NPU 可执行模型        |
| `inference_npu.py`  | NPU 推理脚本              |
| `inference_onnx.py` | ONNX Runtime CPU 推理脚本 |

## 5. 可选：ONNX Runtime CPU 推理

ONNX Runtime 推理用于作为 CPU baseline，不代表 NPU 推理。

安装依赖：

```bash
pip3 install onnxruntime numpy pillow
```

运行：

```bash
python3 inference_onnx.py
```

如果能正常输出分类结果，说明原始 ONNX 模型和测试数据基本可用。

```{note}
ONNX Runtime 跑通只能说明 CPU 推理链路正常，不能证明 NPU 可用。
```

## 6. 可选：重新编译 `.cix` 模型

如果目录中已经包含 `resnet_v1_50.cix`，可以跳过本节。

在 x86_64 Linux 主机侧执行：

```bash
cd ai_model_hub/models/ComputeVision/Image_Classification/onnx_resnet_v1_50
```

可选：简化 ONNX 模型：

```bash
pip install onnxsim
onnxsim model/resnet50-v1-12.onnx model/resnet50-v1-12-sim.onnx
```

执行编译：

```bash
cixbuild cfg/onnx_resnet_v1_50build.cfg
```

编译成功后，检查 `.cix` 文件：

```bash
ls -lh resnet_v1_50.cix
```

如果看到类似：

```text
resnet_v1_50.cix
```

说明模型编译产物已生成。

## 7. 将示例复制到开发板

如果 AI ModelHub 在主机侧，需要复制示例到开发板：

```bash
scp -r ai_model_hub/models/ComputeVision/Image_Classification/onnx_resnet_v1_50 \
  cix@<BOARD_IP>:/home/cix/
```

登录开发板：

```bash
ssh cix@<BOARD_IP>
```

进入目录：

```bash
cd ~/onnx_resnet_v1_50
```

检查必要文件：

```bash
ls -lh resnet_v1_50.cix
ls -lh inference_npu.py
ls -lh test_data
```

## 8. 运行 NPU 推理

在开发板侧执行：

```bash
cd ~/onnx_resnet_v1_50
python3 inference_npu.py
```

正常情况下，日志中应出现类似内容：

```text
npu: noe_init_context success
npu: noe_load_graph success
Input tensor count is 1.
Output tensor count is 1.
npu: noe_create_job success
```

随后会打印测试图片路径和分类结果，例如：

```text
image path : test_data/ILSVRC2012_val_00037133.JPEG
ice bear, polar bear, Ursus Maritimus, Thalarctos maritimus
```

推理结束时应看到：

```text
npu: noe_clean_job success
npu: noe_unload_graph success
npu: noe_deinit_context success
```

如果可以看到上述 `success` 日志和分类结果，说明 NPU 推理流程基本跑通。

## 9. 结果截图

建议将成功运行截图保存到：

```text
docs/_static/images/npu-resnet50-result.jpg
```

然后在本文档中引用：

```md
![NPU ResNet50 result](../_static/images/npu-resnet50-result.jpg)
```

示例：

![NPU ResNet50 result](../_static/images/npu-resnet50-result.jpg)

## 10. 验证结果记录

建议记录以下信息：

```bash
uname -a
cat /etc/os-release
ls -l /dev/aipu
pip3 list | grep libnoe
dpkg -l | grep -E "cix-npu-driver|cix-npu-umd|cix-noe-umd|cix-ai-engine"
```

结果记录表：

| 项目             | 结果                  |
| -------------- | ------------------- |
| 开发板型号          | 待补充                 |
| OS / Kernel    | 待补充                 |
| AI SDK Release | 待补充                 |
| `libnoe`       | 待补充                 |
| `/dev/aipu`    | 待补充                 |
| 示例模型           | `onnx_resnet_v1_50` |
| NPU 模型文件       | `resnet_v1_50.cix`  |
| 推理脚本           | `inference_npu.py`  |
| NPU 推理是否成功     | 待补充                 |
| 输出类别是否正常       | 待补充                 |
| 截图             | 待补充                 |

## 11. 成功标准

可以按以下标准判断 ResNet50 示例是否通过：

| 检查项        | 通过标准                                                                               |                  |
| ---------- | ---------------------------------------------------------------------------------- | ---------------- |
| 设备节点       | `/dev/aipu` 存在                                                                     |                  |
| Python 运行时 | `pip3 list                                                                         | grep libnoe` 有输出 |
| 模型文件       | `resnet_v1_50.cix` 存在                                                              |                  |
| 上下文初始化     | 出现 `noe_init_context success`                                                      |                  |
| 模型加载       | 出现 `noe_load_graph success`                                                        |                  |
| Job 创建     | 出现 `noe_create_job success`                                                        |                  |
| 推理结果       | 输出图片分类结果                                                                           |                  |
| 资源释放       | 出现 `noe_clean_job success`、`noe_unload_graph success`、`noe_deinit_context success` |                  |

## 12. 下一步

完成 ResNet50 示例后，可以继续尝试：

* 更换 AI ModelHub 中的其他 CV 模型。
* 使用 `noe_benchmark` 进行稳定性测试。
* 使用 `noe_profiler` 进行性能分析。
* 对比 CPU ONNX Runtime 与 NPU 推理耗时。

如果遇到模型加载失败、`libnoe` 不存在、`/dev/aipu` 不存在、推理结果异常等问题，请参考：

```text
troubleshooting.md
```

## 13. 参考资料

* CIX P1 NOE SDK 和 AI ModelHub 开发指导手册
* CIX P1 NPU 开发指导手册
