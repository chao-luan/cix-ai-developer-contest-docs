# CIX AI Developer Contest Documentation

本项目用于沉淀开发者大赛相关文档，包括快速开始、本地大模型运行、NPU SDK、多媒体 SDK、外部加速卡 SDK、CDC 云端大模型接入、典型案例与问题排查。

参赛者收到的设备默认已完成 BIOS 刷写和统一系统镜像预装。正常参赛流程下，建议优先阅读“快速开始”章节。BIOS 更新和系统重刷相关内容放在维护章节，仅用于异常恢复或工作人员制备设备。

```{toctree}
:maxdepth: 2
:caption: 开始使用

00-overview/index
01-quick-start/index

:maxdepth: 2
:caption: 模型运行与 SDK

02-local-llm-vlm/index
03-npu-sdk/index
04-multimedia-sdk/index

:maxdepth: 2
:caption: 外部加速与云端接入

05-external-accelerators/index
06-cdc-cloud-llm/index

:maxdepth: 2
:caption: 示例与问题排查

07-examples/index
08-faq/index
99-maintenance/index