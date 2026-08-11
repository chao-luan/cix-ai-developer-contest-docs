# 3.2 CV

本节介绍如何使用 CIX AI Model Hub 中的计算机视觉模型，在 CIX P1 平台上完成模型编译、NPU 推理、输入输出适配及应用集成。

CIX AI Model Hub 中的完整视觉模型示例通常包括原始模型、量化配置、校准数据、测试数据、已编译的 .cix 模型，以及 ONNX 和 NPU 端到端推理脚本。对于首次验证，建议优先使用模型目录中已经提供的 .cix 文件和 inference_npu.py；仅在修改模型、量化参数、输入尺寸或编译配置时，才需要重新执行 cixbuild。

## 3.2.1 当前支持的视觉任务

当前 models/ComputeVision 目录包括以下方向：

| **任务方向** | **目录**              | **典型模型示例**                    | **主要输出**           |
|--------------|-----------------------|-------------------------------------|------------------------|
| 深度估计     | Depth_Estimation      | Depth Anything V2/V3、MiDaS V2      | 深度图或深度矩阵       |
| 人脸检测     | Face_Detection        | CenterFace、RetinaFace、YOLOv5-Face | 人脸框、关键点、置信度 |
| 人脸识别     | Face_Recognition      | SCRFD + ArcFace                     | 人脸特征和相似度       |
| 图像分类     | Image_Classification  | ResNet、MobileNet、ViT、Swin        | 类别和置信度           |
| 图像增强     | Image_Enhancement     | FLW-Net、PairLIE                    | 增强或去雾图像         |
| 车道线检测   | Lane_Detection        | LaneNet、LSTR、UFLD                 | 车道线位置             |
| OCR          | OCR                   | PP-OCRv4、Duguang OCR               | 文本框和识别文本       |
| 目标检测     | Object_Detection      | YOLOv8/9/11/12/13、YOLOX、SSD       | 检测框、类别、置信度   |
| 目标跟踪     | Object_Tracking       | ByteTrack、NanoTrack                | 目标轨迹和跟踪 ID      |
| 姿态估计     | Pose_Estimation       | HRNet、OpenPose、YOLOv8 Pose        | 人体或手部关键点       |
| 语义分割     | Semantic_Segmentation | DeepLab、FCN、SAM2、FastSAM         | 分割 Mask 或类别图     |
| 超分辨率     | Super_Resolution      | Real-ESRGAN、VDSR                   | 高分辨率图像           |

不同模型的输入尺寸、模型格式、后处理方法和输出内容不同，应以对应模型目录中的 ReadMe.md、推理脚本和实际模型文件为准。

## 3.2.2 CV 模型部署流程

完整部署流程分为宿主机编译和设备端推理两个阶段。

1. 获取 AI Model Hub
2. 选择 ComputeVision 模型目录
3. 检查原始模型、CFG、校准数据和测试数据
4. 【可选】在 x86_64 宿主机使用 cixbuild 生成 .cix
5. 将完整模型示例目录部署到 CIX P1
6. 在设备端运行 inference_npu.py
7. 检查模型输出并接入实际图片、视频或摄像头

如果模型目录已经提供与当前 Release 匹配的 .cix 文件，可以跳过编译，直接进行设备端推理。

NOE 编译器运行在 Ubuntu 20.04 或 Ubuntu 22.04 的 x86_64 主机环境中，环境要求 Python 3.10.2；生成的 .cix 文件在 CIX P1 设备端运行。设备端 Python 示例通过 cix-ai-engine 软件包提供的 NOE Engine 调用 NPU。

## 3.2.3 运行前检查

### 3.2.3.1 检查设备端 NOE 环境

在 CIX P1 开发板执行：

```bash
dpkg -l | grep -E "cix-npu|cix-noe|cix-ai"
```

检查 NOE Engine：

```bash
python3 -m pip list | grep -E "libnoe|noe_engine"
```

正常情况下应能看到 noe_engine 及其版本信息。

如果设备端软件包未安装，应先按照第 2.3.2 节完成 NPU Driver、NPU UMD、NOE Runtime 和 cix-ai-engine 安装，不建议混用不同 Release 的驱动、Runtime 和 .cix 文件。

### 3.2.3.2 检查 AI Model Hub

```bash
cd "$AI_MODEL_HUB_DIR”
ls models/ComputeVision
```

当前目录中应能够看到：

```text
Depth_Estimation
Face_Detection
Face_Recognition
Image_Classification
Image_Enhancement
Lane_Detection
Object_Detection
Object_Tracking
OCR
Pose_Estimation
Semantic_Segmentation
Super_Resolution
```

### 3.2.3.3 安装环境与依赖

进入 AI Model Hub 根目录后，应先阅读根目录中的 ReadMe.md 或 ReadMe_EN.md，并按照其中“二、环境与依赖”的说明安装当前版本所需依赖。

不同模型和不同任务所需的 Python 依赖可能不同，不要默认直接执行根目录中的 requirements.txt，也不要仅根据脚本导入内容自行升级系统已有软件包。

## 3.2.4 运行 ResNet50 图像分类示例

本节以以下模型为例：

models/ComputeVision/Image_Classification/onnx_resnet_v1_50

当前目录包含：

cfg/

cpp_example/

datasets/

model/

test_data/

```text
inference_npu.py
inference_onnx.py
resnet_v1_50.cix
ReadMe.md
Tutorials.ipynb
```

进入模型目录：

```bash
cd "$AI_MODEL_HUB_DIR/models/ComputeVision/Image_Classification/onnx_resnet_v1_50”
```

检查关键文件：

```bash
ls -lh resnet_v1_50.cix
ls -lh inference_npu.py
ls -lh test_data
```

执行 NPU 推理：

```bash
python3 inference_npu.py
```

正常运行时，终端会出现类似日志：

```text
npu: noe_init_context success
npu: noe_load_graph success
Input tensor count is 1.
Output tensor count is 1.
npu: noe_create_job success
image path : test_data/...
<class name>
npu: noe_clean_job success
npu: noe_unload_graph success
npu: noe_deinit_context success
```

如果能够完成 Runtime 初始化、模型加载、推理任务创建、分类结果输出和资源释放，说明 ResNet50 NPU 推理链路基本正常。

模型示例包含预处理、推理和后处理三个阶段，示例设计重点是易于理解，并不代表已经达到最短端到端耗时。

## 3.2.5 可选：重新编译模型

如果当前模型目录已经提供可直接使用的 resnet_v1_50.cix，且其与当前 NOE Runtime 版本匹配，可以跳过本节。

以下操作在安装了 NOE 编译器的 x86_64 Linux 宿主机执行。

检查编译器：

```text
cixbuild -v
```

进入模型目录：

```bash
cd "$AI_MODEL_HUB_DIR/models/ComputeVision/Image_Classification/onnx_resnet_v1_50”
```

检查编译文件：

```bash
ls cfg
ls datasets
ls model
```

如需要对 ONNX 模型进行简化：

```bash
python3 -m pip install onnxsim
onnxsim \
model/resnet50-v1-12.onnx \
model/resnet50-v1-12-sim.onnx
```

执行编译：

```text
cixbuild cfg/onnx_resnet_v1_50build.cfg
```

编译成功后通常会显示：

```text
Serialization Model: ...
build success.......
Total errors: 0
```

检查生成文件：

```bash
find . -maxdepth 2 -type f -name "*.cix" -ls
```

cixbuild 配置文件采用 INI 格式，通常包括：

| **配置段**    | **作用**                                   |
|---------------|--------------------------------------------|
| \[Common\]    | 设置编译模式                               |
| \[Parser\]    | 设置模型格式、模型文件、输入输出和模型领域 |
| \[Optimizer\] | 设置校准数据、量化和精度评估参数           |
| \[GBuilder\]  | 设置目标硬件、输出文件、性能分析和自动分片 |

NOE 编译器当前公开的 model_domain 包括：

```text
image_classification
object_detection
keyword_spotting
speech_recognition
image_segmentation
```

OCR、深度估计、姿态估计、图像增强等模型应优先使用对应模型目录中已经验证的 CFG，不应只根据任务名称自行编造新的 model_domain。

如果需要启用自动分片，可在 \[GBuilder\] 中使用：

```text
tiling=fps
```

自动分片会根据模型结构、NPU 核心数和片上内存尝试优化 FPS。手动分片需要逐层分析，配置不当可能产生负优化，普通开发者不建议优先使用。

## 3.2.6 替换输入和处理输出

不同视觉模型通常均包含：

1. 图片或视频帧
2. 输入预处理
3. NPU 推理
4. 输出后处理
5. 分类、检测、分割或可视化结果

替换自定义输入前，应重点确认：

| **检查项** | **说明**                         |
|------------|----------------------------------|
| 输入尺寸   | 必须与模型输入 Shape 一致        |
| 色彩空间   | RGB、BGR 或灰度                  |
| 张量布局   | NCHW 或 NHWC                     |
| 数据类型   | uint8、float32、量化整数等       |
| 归一化     | 缩放、均值、标准差               |
| 标签文件   | 分类标签或字符表                 |
| 后处理     | NMS、Anchor、阈值、Mask 解析     |
| 模型组合   | OCR、人脸识别等可能包含多个 .cix |

运行前可先查看脚本：

```bash
python3 inference_npu.py --help
```

如果脚本未实现帮助参数，应直接查看：

```text
sed -n '1,240p' ReadMe.md
sed -n '1,240p' inference_npu.py
```

不要假定所有模型都使用相同的图片参数名称。部分脚本直接读取固定的 test_data 目录，部分脚本支持命令行指定输入路径。

## 3.2.7 视频、摄像头和应用 Demo

目标跟踪、人脸识别和目标检测等模型目录中已经包含视频测试数据或 C++ 示例，例如：

```text
Object_Tracking/onnx_bytetrack_s/test_data/palace.mp4
Face_Recognition/onnx_scrfd_arcface/datasets/in_video.mp4
部分模型目录/cpp_example
```

接入摄像头或视频时，推荐采用以下处理流程：

1. 摄像头或视频文件
2. V4L2 / GStreamer / FFmpeg / VPU 解码
3. 获取图像帧
4. 图像预处理
5. NOE Engine NPU 推理
6. 结果叠加、显示或 Agent 工具调用

开发时应依次跑通以下环节：

1.  单张图片 NPU 推理；
2.  摄像头取流或视频解码；
3.  将取流、解码与 NPU 推理串接为实时 Pipeline。

当前 AI Model Hub 还提供多种预构建应用 Demo，例如：

```text
face-recognition-gradio
pp-ocrv4-gradio
real-esrgan-gradio
yolox-depth-gradio
yolox-gradio
```

## 3.2.8 性能和精度验证

可从以下维度评估 CV 模型：

| **指标**     | **说明**                             |
|--------------|--------------------------------------|
| NPU 推理时间 | 仅模型计算耗时                       |
| 端到端延迟   | 预处理、数据复制、推理和后处理总耗时 |
| FPS          | 单位时间处理帧数                     |
| 吞吐量       | 不同 Batch Size 下单位时间处理样本数 |
| 稳定性       | 长时间运行是否异常                   |
| 精度         | 与原模型或标注数据的结果差异         |

模型目录的脚本如果支持 Benchmark，可执行：

```bash
python3 inference_npu.py --benchmark True
```

典型指标包括：

| **任务** | **指标**                      |
|----------|-------------------------------|
| 图像分类 | Top-1、Top-5                  |
| 目标检测 | mAP                           |
| 语义分割 | mIoU                          |
| 人脸识别 | FAR、FRR、Identification Rate |
| 超分辨率 | PSNR                          |

AI Model Hub 的 utils/evaluate 中提供了 ImageNet、COCO 等评估工具。完整 Python 示例包含输入输出处理，因此其总耗时不能直接等同于 NPU 核心推理耗时。

## 3.2.9 常见问题

| **问题现象**          | **处理建议**                                                |
|-----------------------|-------------------------------------------------------------|
| 找不到 .cix 文件      | 检查当前模型目录是否提供预编译模型，或在宿主机执行 cixbuild |
| noe_init_context 失败 | 检查 NPU Driver、UMD、NOE Runtime 和系统版本                |
| noe_load_graph 失败   | 检查 .cix 是否损坏，或是否与当前 Runtime 匹配               |
| 找不到 utils          | 保持 AI Model Hub 原始目录结构                              |
| 输出类别明显错误      | 检查输入尺寸、颜色通道、归一化和标签文件                    |
| 检测框位置异常        | 检查 Resize、Letterbox、Anchor 和坐标缩放                   |
| 模型可运行但速度较慢  | 区分预处理、推理和后处理耗时                                |
| 视频推理失败          | 先分别验证视频解码和单张图片推理                            |
| 重新编译精度下降      | 检查校准数据、量化参数和输入预处理                          |
| 编译出现算子错误      | 检查模型格式、opset、输入输出节点及当前编译器支持范围       |
