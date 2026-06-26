# NPU SDK

本章节介绍如何在 CIX P1 / Radxa Orion O6 类开发板上安装、检查和使用 NPU SDK。

CIX P1 的 NPU 软件栈以 NOE SDK 为核心，用于完成模型编译、量化、NPU 运行时调用和性能分析。开发者通常需要同时理解以下两部分：

* **板端运行环境**：NPU 内核态驱动、用户态运行时库、NOE Python 推理组件。
* **主机编译环境**：NOE 编译器、AI ModelHub、模型转换、量化和 `.cix` 模型生成。

```{warning}
NPU SDK 与普通 CPU / GPU 推理框架不同。  
NPU 推理通常不是直接加载原始 ONNX / PyTorch / GGUF 模型运行，而是需要先通过 NOE 编译器将模型转换、量化并生成 CIX P1 NPU 可执行的模型文件，再在板端调用 NOE UMD / AI Engine 执行推理。
```

## 文档结构

```{toctree}
:maxdepth: 1

ai-sdk-installation
noe-compiler
ai-modelhub-resnet50
troubleshooting
```

## Runtime Overview

| 组件                        | 安装位置            | 作用                           |
| ------------------------- | --------------- | ---------------------------- |
| NPU KMD                   | 开发板             | NPU 内核态驱动，负责设备节点、内存、任务调度、中断等 |
| NPU UMD                   | 开发板             | 用户态运行时库，向应用提供 NPU 调用接口       |
| NOE UMD                   | 开发板             | CIX NOE 统一运行时接口              |
| AI Engine                 | 开发板             | Python 推理引擎和上层封装             |
| NOE Compiler / CixBuilder | x86_64 Linux 主机 | 模型解析、量化、编译，生成 `.cix` 模型      |
| AI ModelHub               | 主机 + 开发板        | 模型、配置、测试数据、推理脚本和示例工程         |

## 推荐阅读顺序

1. 先完成 [AI SDK Installation](ai-sdk-installation.md)，确保板端 NPU 驱动和运行时可用。
2. 再阅读 [NOE Compiler](noe-compiler.md)，了解如何在 x86_64 Linux 主机上安装编译器并生成 NPU 模型。
3. 最后阅读 [AI ModelHub ResNet50 Example](ai-modelhub-resnet50.md)，使用 ResNet50 示例完成端到端编译和 NPU 推理验证。
4. 如果遇到 `/dev/aipu` 不存在、`libnoe` 不可用、模型无法加载等问题，参考 [Troubleshooting](troubleshooting.md)。

## 参考资料

* Radxa Orion O6 Artificial Intelligence Documentation
* CIX P1 NPU 开发指导手册
* CIX P1 NOE SDK 和 AI ModelHub 开发指导手册
