# Maintenance and Recovery

本章节用于系统异常、镜像损坏、BIOS 需要刷写或工作人员重新制备设备时参考。

正常参赛流程下，选手收到的设备已经完成 BIOS 刷写和统一系统镜像预装，无需执行本章节操作。

```{warning}
本章节包含系统镜像重刷和 BIOS 刷写等高风险操作。执行前请确认硬件型号、系统镜像版本和 BIOS 固件版本，避免因误操作导致设备无法启动。

尤其是 BIOS 刷写，不同品牌、不同型号、不同硬件版本的开发板所使用的 BIOS 固件并不相同。刷错 BIOS 后，开发者通常无法自行恢复，需要使用专用工具或由维护人员救砖处理。
```

```{toctree}
:maxdepth: 1

reflash-os-image
bios-flashing
troubleshooting
```
