# Update BIOS

本文档用于在 BIOS 需要升级、系统启动异常或工作人员制备设备时，通过 U 盘更新 BIOS 固件。

```{warning}
BIOS 更新属于高风险操作。请确认硬件型号和 BIOS 固件版本匹配。错误固件可能导致设备无法启动。
```

## 1. 适用场景

- BIOS 版本需要升级。
- 设备启动异常，需要恢复 BIOS。
- 工作人员批量制备开发板。
- Release 要求 BIOS 与 OS 版本匹配。

正常参赛流程下，选手无需执行本操作。

## 2. 前置准备

- FAT32 格式 U 盘
- BIOS 更新工具，例如 `FlashUpdate.efi`
- 对应硬件型号的 BIOS 固件文件
- 显示器、键盘、电源适配器

## 3. 制作 BIOS 更新 U 盘

将 U 盘格式化为 FAT32，然后将以下文件复制到 U 盘根目录：

```text
FlashUpdate.efi
<BIOS_FIRMWARE_FILE>.bin
```

示例：

```text
FlashUpdate.efi
cix_flash_all_rsa_pr.bin
```

```{danger}
严禁随意刷写 BIOS。

不同品牌、不同型号、不同硬件版本的开发板所使用的 BIOS 固件并不相同，例如 O6、O6N、MS-R1、EVB 等平台可能对应不同的 BIOS 文件。刷写前必须确认开发板型号、硬件版本以及 BIOS 固件文件完全匹配。

如果刷入错误 BIOS，设备可能无法启动，开发者通常无法自行恢复，需要使用专用烧录工具或由维护人员进行救砖处理，恢复过程较麻烦且存在风险。

正常参赛流程下，设备出厂或发放前已经完成 BIOS 刷写。除非维护人员明确要求，或确认为 BIOS 故障恢复场景，否则不要自行刷写 BIOS。
```

## 4. 进入 UEFI Shell

1. 插入 BIOS 更新 U 盘。
2. 接入显示器、键盘和电源。
3. 设备上电。
4. 启动过程中连续按 `Esc` 进入 UEFI 设置界面。
5. 选择 `Boot Manager`。
6. 选择 `UEFI Shell`。

## 5. 定位 U 盘

进入 UEFI Shell 后，查看设备映射表。通常带有 USB 标识的条目为 U 盘。

在 Shell 提示符下输入对应设备名，例如：

```text
FS1:
```

进入后执行：

```text
ls
```

确认可以看到：

```text
FlashUpdate.efi
<BIOS_FIRMWARE_FILE>.bin
```

## 6. 执行 BIOS 更新

执行以下命令：

```text
FlashUpdate.efi -f <BIOS_FIRMWARE_FILE>.bin
```

示例：

```text
FlashUpdate.efi -f cix_flash_all_rsa_pr.bin
```

等待更新完成，看到类似成功提示后再继续操作。

## 7. 重启设备

BIOS 更新完成后：

1. 断电。
2. 等待数秒。
3. 重新上电启动。
4. 进入系统。

## 8. 验证结果

确认：

- 设备可以正常启动。
- 显示器有输出。
- 可以进入系统。
- BIOS 版本符合 Release 要求。

## 9. 常见问题

### 9.1 UEFI Shell 中找不到 U 盘

检查：

- U 盘是否为 FAT32。
- 文件是否放在 U 盘根目录。
- 是否更换 USB 接口。
- 是否重新插拔 U 盘后进入 Shell。

### 9.2 执行命令提示找不到文件

先执行：

```text
ls
```

确认文件名是否完全一致，包括大小写和后缀名。

### 9.3 BIOS 更新后无法启动

检查：

- BIOS 固件是否匹配硬件版本。
- 是否使用了错误的 `_pr.bin` 或 `_proto.bin`。
- OS 镜像是否与 BIOS / Release 基线匹配。
