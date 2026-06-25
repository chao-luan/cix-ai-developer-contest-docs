# Local LLM and VLM Runtime

本章节介绍如何在开发板本地使用 llama.cpp 和 MNN 运行 LLM / VLM 模型，覆盖 CPU 与 GPU 两类运行路径。

本章节主要面向以下场景：

* 在开发板本地运行大语言模型。
* 在开发板本地运行视觉语言模型。
* 对比 CPU、GPU 后端的运行方式和适用场景。
* 为开发者大赛中的端侧 AI 应用提供基础模型运行能力。

```{note}
本章节关注本地模型推理。NPU SDK、NOE SDK 和 AI ModelHub 相关内容请参考 NPU SDK 章节；云端大模型接入请参考 CDC Cloud LLM Access 章节。
```

## Runtime Matrix and Reference

| 框架        | CPU 后端         | GPU 后端 | 主要用途                        | 参考资料                                                                                                                 |
| --------- | -------------- | ------ | --------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| llama.cpp | CPU / KleidiAI | Vulkan | 本地 LLM / VLM 推理，常用于 GGUF 模型 | [Arm Learning Path: llama.cpp on Armv9](https://learn.arm.com/learning-paths/cross-platform/ernie_moe_v9/)           |
| MNN       | CPU / Arm 优化路径 | OpenCL | 本地多模态推理、端侧 AI 应用            | [Arm Learning Path: MNN Multimodal on Armv9](https://learn.arm.com/learning-paths/cross-platform/multimodel_mnn_v9/) |

```{warning}
Arm 官方 Learning Path 是上游参考教程。开发者大赛实际使用的模型文件、编译参数、运行命令、SDK 版本和硬件平台，应以本项目文档及维护人员提供的信息为准。
```

## Recommended Validation Order

建议按照以下顺序验证：

```text
llama.cpp CPU
→ llama.cpp Vulkan
→ MNN CPU
→ MNN OpenCL
```

其中 `llama.cpp CPU` 依赖最少，最适合作为本地大模型运行的第一条验证路径。

```{toctree}
:maxdepth: 1

framework-overview
llama-cpp-cpu-kleidiai
llama-cpp-gpu-vulkan
mnn-cpu-kleidiai
mnn-gpu-opencl
```
