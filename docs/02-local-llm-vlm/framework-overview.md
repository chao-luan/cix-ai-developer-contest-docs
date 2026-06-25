# Framework Overview

本文档介绍本章节涉及的本地大模型运行框架、后端类型和推荐使用场景。

## 1. 背景

开发者大赛中的部分场景需要在开发板本地运行 LLM / VLM 模型，例如：

* 本地文本生成。
* 本地图像理解。
* 本地 OCR / 多模态问答。
* 边缘端隐私计算。
* 离线 AI 应用。
* 云边协同场景中的端侧模型推理。

本章节主要覆盖两类本地推理框架：

* llama.cpp
* MNN

## 2. llama.cpp

llama.cpp 是常用的轻量级大模型推理框架，适合在本地 CPU 或 GPU 上运行量化后的 LLM / VLM 模型。

常见特点：

* 支持 GGUF 模型格式。
* 适合边缘端和个人设备部署。
* 支持 CPU 推理。
* 支持多种硬件加速后端。
* 适合快速验证本地 LLM / VLM 能力。

在本项目中，llama.cpp 主要用于：

* 本地 LLM 推理。
* 本地 VLM 推理。
* CPU / GPU 后端对比。
* 端侧大模型 Demo 验证。

## 3. MNN

MNN 是面向端侧部署的轻量级推理引擎，适合移动端、嵌入式设备和边缘设备上的 AI 推理任务。

在本项目中，MNN 主要用于：

* 本地多模态模型推理。
* 图像、文本、语音等多输入场景。
* 端侧 AI 应用开发。
* CPU / GPU 后端对比。

## 4. KleidiAI

KleidiAI 是 Arm 面向 Arm CPU 的 AI 性能优化组件，用于提升 Arm CPU 上 AI 工作负载的执行效率。

```{note}
KleidiAI 不是独立的大模型推理框架，而是底层性能优化组件。开发者通常通过 llama.cpp、MNN 等上层框架间接使用相关优化能力。
```

## 5. Vulkan

Vulkan 是跨平台图形和计算 API。在本项目中，Vulkan 主要用于 llama.cpp 的 GPU 后端，尝试利用开发板 GPU 进行大模型推理加速。

适用场景：

* 希望对比 CPU 与 GPU 推理性能。
* 模型和框架已支持 Vulkan 后端。
* GPU 驱动和 Vulkan Runtime 已正确安装。

## 6. OpenCL

OpenCL 是跨平台并行计算 API。在本项目中，OpenCL 主要用于 MNN 的 GPU 后端，尝试利用开发板 GPU 进行端侧推理加速。

适用场景：

* MNN 模型支持 OpenCL 后端。
* GPU 驱动和 OpenCL Runtime 已正确安装。
* 希望验证 GPU 加速效果。

## 7. How to Choose

| 目标                  | 推荐路径                    |
| ------------------- | ----------------------- |
| 快速跑通本地 LLM          | llama.cpp CPU           |
| 跑 GGUF 模型           | llama.cpp               |
| 尝试 GPU 加速 LLM / VLM | llama.cpp Vulkan        |
| 运行端侧多模态应用           | MNN                     |
| 尝试 MNN GPU 加速       | MNN OpenCL              |
| 跑 NPU 模型            | NPU SDK 章节              |
| 接云端大模型              | CDC Cloud LLM Access 章节 |

## 8. 与 NPU SDK 的区别

本章节关注的是通过通用本地推理框架运行 LLM / VLM：

```text
llama.cpp / MNN
→ CPU 或 GPU
→ 本地模型推理
```

NPU SDK 章节关注的是通过 CIX-P1 NPU / NOE SDK 运行模型：

```text
NOE SDK / AI ModelHub
→ NPU
→ 典型算法 Demo，例如 YOLOv8n、Whisper
```

二者不是替代关系，而是不同推理路径。
