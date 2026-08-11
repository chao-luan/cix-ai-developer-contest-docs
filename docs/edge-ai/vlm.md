# 3.4 VLM

本节介绍如何在 CIX P1 平台上运行图文特征模型和生成式 VLM（Vision-Language Model，视觉语言模型），并说明 AI Model Hub 中不同多模态资源的边界。

需要注意，AI Model Hub 中的 Image_to_Text 目录名称不能简单理解为“输入图片后生成自然语言描述”。当前该目录主要包含 CLIP、Chinese CLIP、RemoteCLIP、LongCLIP 和 SigLIP 等图文编码模型，它们通常输出图像和文本特征向量，用于跨模态检索、相似度计算或零样本分类。

真正能够根据图片生成自然语言答案的模型，主要通过 models/MultiModal 中的部署文档，结合 llama.cpp、MNN 或其他对应 Runtime 运行。

## 3.4.1 模型类型区别

| **类型**     | **输入**               | **输出**               | **典型任务**          |
|--------------|------------------------|------------------------|-----------------------|
| 普通 CV      | 图像或视频帧           | 类别、框、Mask、关键点 | 分类、检测、OCR、分割 |
| 图文编码模型 | 图像和文本             | 特征向量、相似度       | 图文检索、零样本分类  |
| 生成式 VLM   | 图像和文本指令         | 自然语言文本           | 图片描述、视觉问答    |
| Omni 模型    | 图像、文本、音频或视频 | 文本、音频等           | 多模态交互和智能体    |

普通 CV 模型通常可以整体编译为一个或多个 .cix 文件。生成式 VLM 通常包括视觉编码器、多模态投影模块、语言模型、Tokenizer 和采样模块，不能默认将完整模型编译成单个 .cix。

## 3.4.2 当前多模态资源

### 3.4.2.1 图文编码模型

当前目录：

models/Generative_AI/Image_to_Text

包含：

```text
onnx-Chinese-clip-vit-base-patch16
onnx_Chinese_clip
onnx_RemoteCLIP
onnx_clip
onnx_long_clip
onnx_siglip-so400m-patch14-384
```

这些模型目录均包含：

- 图像 Encoder .cix；
- 文本 Encoder .cix；
- CFG；
- 校准数据；
- inference_npu.py；
- inference_onnx.py；
- 测试数据。

例如：

```text
onnx_Chinese_clip/
├── clip_cn_img.cix
├── clip_cn_txt.cix
├── cfg/
├── datasets/
├── model/
├── test_data/
├── inference_npu.py
└── inference_onnx.py
```

### 3.4.2.2 文本检索模型

当前目录：

models/Generative_AI/Text_Image_Search/onnx_bge_small_zh

包含：

```text
bge-small-zh_256.cix
inference_npu.py
inference_onnx.py
cfg/
model/
scripts/
```

BGE 是文本向量模型，主要用于文本检索和向量化，不是完整的图片问答 VLM。

### 3.4.2.3 生成式多模态模型部署文档

当前 models/MultiModal 目录中的模型资源分为以下两种形式。

#### 3.4.2.3.1 完整模型目录

部分模型以完整目录形式提供，例如：

```text
Qwen2.5-VL-3B-Instruct
Qwen3-VL-2B-Instruct
Qwen3-VL-4B-Instruct
```

此类目录通常包含模型配置、测试数据、推理脚本和已经编译好的 .cix 文件，部署时必须保留完整目录结构，并按照目录内的 ReadMe.md 执行。通常可使用 inference_npu.py 调用已提供的 .cix 模型，在 NPU 上完成视觉编码或相关推理。

#### 3.4.2.3.2 Markdown 部署指导文档

部分模型仅提供独立的 Markdown 部署文档，例如：

```text
gemma-3-4b-it.md
gemma-4-E2B-it.md
gemma-4-E4B-it.md
GLM-OCR.md
InternVL2_5-4B.md
PaddleOCR-VL-1.5.md
Qwen2-VL-2B-Instruct.md
Qwen2.5-Omni-3B.md
Qwen2.5-Omni-7B.md
Qwen2.5-VL-3B-Instruct.md
Qwen3-Omni-30B-A3B-Instruct.md
Qwen3-VL-2B-Instruct.md
Qwen3-VL-4B-Instruct.md
Qwen3.5-0.8B.md
Qwen3.5-2B.md
Qwen3.5-35B-A3B.md
Qwen3.5-4B.md
Qwen3.5-9B.md
Qwen3.6-35B-A3B.md
```

此类 .md 文件是模型部署说明，本身不包含完整模型文件、.cix 文件或 inference_npu.py。部署前必须打开对应文档，并按照其中指定的模型下载地址、模型格式、推理框架、运行程序及依赖要求完成部署。

同一模型可能同时提供完整目录和独立部署文档。此时应优先查看完整模型目录中的 ReadMe.md，并结合对应的独立 Markdown 文档确认模型版本、运行方式和依赖要求。

### 3.4.2.4 不属于 VLM 的目录

以下目录虽然属于 Generative AI，但不属于视觉语言问答模型：

Generative_AI/Text_to_Image

其中的 SDXL-Turbo 和 Stable Diffusion V1.4 用于文生图，不应写入 VLM 图片问答流程。

## 3.4.3 部署路径选择

| **路径**                                | **模型要求**                        | **适用场景**                     |
|-----------------------------------------|-------------------------------------|----------------------------------|
| AI Model Hub 完整模型目录或图文编码示例 | 配套模型、.cix 文件、推理脚本及配置 | 快速验证图文编码或已有多模态模型 |
| llama.cpp                               | 主模型 GGUF、视觉模型或投影文件     | 图片描述和视觉问答               |
| MNN                                     | 完整 MNN 多模态模型目录             | CPU/OpenCL 多模态推理            |
| NPU + CPU/GPU 混合                      | 可拆分并适配的子模型                | 高级优化和定制部署               |
| 预构建多模态 Demo                       | 对应 ARM64 DEB 和资源               | 快速展示和二次开发               |

推荐顺序：

1. 检查对应模型提供的是完整目录还是独立 Markdown
2. 按照目录内 ReadMe.md 或独立部署文档准备环境
3. 使用指定模型和框架完成基础验证
4. 确认图像输入真正生效
5. 验证 Vulkan、OpenCL 或 NPU
6. 最后考虑自定义 NPU 子模型拆分

不要在首次验证时同时修改模型版本、量化方式、推理框架和硬件后端。

## 3.4.4 运行 Chinese CLIP 图文匹配示例

进入目录：

```bash
cd "$AI_MODEL_HUB_DIR/models/Generative_AI/Image_to_Text/onnx_Chinese_clip”
```

检查模型：

```bash
ls -lh clip_cn_img.cix
ls -lh clip_cn_txt.cix
ls -lh inference_npu.py
ls -lh test_data
```

执行：

```bash
python3 inference_npu.py
```

脚本通常会完成：

1. 读取图片和候选文本
2. NPU 图像 Encoder
3. NPU 文本 Encoder
4. 特征归一化
5. 计算相似度
6. 输出匹配结果

正常输出可能是特征相似度、候选文本排序或分类结果，而不是一段自然语言图片描述。

其他图文模型也可以采用相同的验证方式：

```bash
cd "$AI_MODEL_HUB_DIR/models/Generative_AI/Image_to_Text/onnx_clip”
python3 inference_npu.py
cd "$AI_MODEL_HUB_DIR/models/Generative_AI/Image_to_Text/onnx_siglip-so400m-patch14-384”
python3 inference_npu.py
```

不同模型的文本 Tokenizer、图片尺寸和输出维度不同，图像 Encoder 与文本 Encoder 必须使用同一模型版本配套的文件。

## 3.4.5 运行生成式 VLM

首先检查目标模型在 models/MultiModal 目录中的资源形式。

部分模型提供完整模型目录，例如：

```text
Qwen2.5-VL-3B-Instruct/
Qwen3-VL-2B-Instruct/
Qwen3-VL-4B-Instruct/
```

此类模型应保留完整目录结构，并优先按照目录内的 ReadMe.md、推理脚本和配置文件运行。

查看示例：

```bash
cd "$AI_MODEL_HUB_DIR/models/MultiModal/Qwen2.5-VL-3B-Instruct”
sed -n '1,260p' ReadMe.md
ls -lh
```

其他模型可能仅提供独立的 Markdown 部署文档，例如：

```text
Qwen2-VL-2B-Instruct.md
```

查看对应文档：

```bash
cd "$AI_MODEL_HUB_DIR”
sed -n '1,260p' \
models/MultiModal/Qwen2-VL-2B-Instruct.md
```

如果同一模型同时存在完整目录和同名 Markdown，应先阅读完整目录中的 ReadMe.md，再结合独立 Markdown 确认模型版本、依赖和运行方式。

部署文档中通常会明确：

- 使用 llama.cpp、MNN 或其他框架；
- 需要下载的原始模型；
- 模型转换方式；
- 量化格式；
- 主模型文件；
- 视觉模型或投影文件；
- 图片和 Prompt 的传入方式；
- 运行程序名称；
- 推荐的线程和后端参数。

**llama.cpp 通用形式**

对于 llama.cpp 多模态路径，常见运行形式为：

```bash
<VLM_CLI> \
-m <MAIN_MODEL.gguf> \
--mmproj <VISION_MODEL.gguf> \
--image <IMAGE_PATH> \
-p "<PROMPT>"
```

其中：

| **参数**    | **说明**                      |
|-------------|-------------------------------|
| \<VLM_CLI\> | 当前 Release 提供的多模态程序 |
| -m          | 语言模型主体                  |
| --mmproj    | 视觉编码器或多模态投影模型    |
| --image     | 输入图片                      |
| -p          | 文本问题                      |

实际程序名称和参数必须以对应 Markdown 和当前软件包的 --help 为准。

**MNN 通用形式**

对于 MNN 多模态路径，通常需要完整的 MNN 模型目录：

```text
<llm_demo> \
<MODEL_DIR>/config.json \
<PROMPT_FILE>
```

图片路径可能写在 Prompt、配置文件或模型专用输入格式中，应以对应模型文档为准，不能直接套用普通文本 LLM 的运行方式。

## 3.4.6 验证图片输入是否生效

模型能够输出文字，不代表视觉输入已经生效。

至少进行以下验证：

1.  对同一图片提出两个不同问题；
2.  使用两张内容明显不同的图片；
3.  有图和无图分别运行；
4.  检查日志中是否加载视觉模型；
5.  检查是否产生 Image Embedding 或 Image Token；
6.  检查回答是否与图片内容相关。

如果模型只能普通聊天，应检查：

- 是否误用了纯文本 LLM；
- 视觉模型或 mmproj 是否加载；
- 图片路径是否正确；
- 主模型和视觉模型是否匹配；
- Prompt 模板是否符合当前 VLM；
- 当前 CLI 是否真正支持多模态。

## 3.4.7 NPU 混合部署说明

当前 NOE 编译器没有通用的：

```text
model_domain=vlm
model_domain=image_to_text
model_domain=multimodal_chat
```

因此不能将任意完整 VLM 直接执行：

1. 完整 VLM
2. cixbuild
3. 单个 vlm.cix

NOE 当前公开的 model_domain 仍为图像分类、目标检测、关键词识别、语音识别和图像分割。

VLM 混合部署通常采用：

| **组件**           | **可选后端**         |
|--------------------|----------------------|
| 图片解码和 Resize  | CPU、CME、多媒体组件 |
| Vision Encoder     | NPU、GPU 或 CPU      |
| 多模态投影层       | CPU、GPU 或 NPU      |
| LLM Prefill/Decode | CPU、Vulkan、OpenCL  |
| Tokenizer 和采样   | CPU                  |

如需将 Vision Encoder 单独部署至 NPU，应完成：

1.  从完整 VLM 中拆分 Vision Encoder；
2.  导出固定输入 Shape 的 ONNX；
3.  准备校准数据；
4.  使用经过验证的 CFG 编译；
5.  对比原始模型和 NPU 输出；
6.  检查特征维度、数据类型和布局；
7.  将特征接入投影层和 LLM；
8.  验证端到端图片问答结果。

该路径属于高级适配工作。赛事基础项目应优先使用已有 llama.cpp、MNN 或多模态 Demo。

## 3.4.8 多模态应用 Demo

当前 AI Model Hub 提供以下相关 Demo：

```text
image-multichat-gradio
image-multichat-streamlit
picquery-cn-gradio
videoquery-streamlit
ai-album-streamlit
```

这些 Demo 可以作为参赛作品界面和 Pipeline 的参考，但最终作品仍需体现 Agent 的多步骤规划、工具调用和状态推进能力，不能仅提交模型展示页面。

## 3.4.9 性能和资源观察

VLM 端到端耗时通常包括：

| **阶段**       | **说明**                 |
|----------------|--------------------------|
| 图片加载       | 文件读取和图片解码       |
| 图片预处理     | Resize、裁剪、归一化     |
| Vision Encoder | 生成图像特征             |
| 多模态投影     | 转换为 LLM 可接收的特征  |
| Prefill        | 处理图像 Token 和 Prompt |
| Decode         | 逐 Token 生成答案        |
| 输出处理       | Tokenizer 解码和格式化   |

建议记录：

- 模型名称和参数规模；
- 主模型量化格式；
- 视觉模型格式；
- 图片分辨率；
- 上下文长度；
- CPU、Vulkan、OpenCL 或混合后端；
- 视觉编码时间；
- 首 Token 延迟；
- Prefill 速度；
- Decode 速度；
- 峰值内存；
- 是否发生后端回退。

不同模型、量化格式、图片分辨率和上下文长度的结果不能直接横向比较。

## 3.4.10 常见问题

| **问题现象**                | **处理建议**                                                                    |
|-----------------------------|---------------------------------------------------------------------------------|
| MultiModal 目录只有 .md     | 当前目录主要提供部署指导，应按照 Markdown 准备模型                              |
| Chinese CLIP 不输出自然语言 | 该模型是图文编码模型，不是生成式 VLM                                            |
| 模型能聊天但看不懂图片      | 检查视觉模型、图片参数和 Prompt 模板                                            |
| 主模型和视觉模型加载失败    | 确保二者来自同一模型版本                                                        |
| 图片问答结果与图片无关      | 检查图片是否成功读取并编码                                                      |
| MNN 只能文本推理            | 检查是否使用完整多模态模型目录                                                  |
| Vulkan/OpenCL 未生效        | 检查 Runtime、构建选项和运行日志                                                |
| 完整 VLM 无法直接 cixbuild  | NOE 没有通用 VLM 模型领域，应拆分子模型                                         |
| 内存不足                    | 使用更小模型、更低量化或降低图片和上下文规模                                    |
| 推理速度慢                  | 分别统计 Vision Encoder、Prefill 和 Decode                                      |
| 多模态 Demo 无法启动        | 检查对应 Demo 目录中的 ARM64 DEB 软件包是否已正确安装，并核对模型资源和端口配置 |
| 模型产生错误描述            | 对关键操作增加规则校验、置信度判断或人工确认                                    |
