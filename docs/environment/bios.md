# 2.1 BIOS

本章节用于说明开发板需要更新、重刷或回退 BIOS 时，如何通过 U 盘进入 UEFI Shell 并执行 BIOS 更新。

不同开发板BIOS地址如下：

| **开发平台**   | **下载链接**                                                                                      |
|----------------|---------------------------------------------------------------------------------------------------|
| 瑞莎星睿 O6    | <https://dl.radxa.com/orion/o6/images/bios/orion-o6-bios-1.1.0-1.zip>                             |
| 瑞莎星睿 O6N   | <https://dl.radxa.com/orion/o6n/images/bios/orion-o6n-bios-1.2.4.zip>                             |
| 铭凡MS-R1      | <https://pc-file-web.oss-cn-shenzhen.aliyuncs.com/MS-R1/BIOS/cix_flash_all2_MGP1WSB_20260429.zip> |
| 香橙派 6 Plus  | <https://pan.baidu.com/s/1DLg8jvbddJNWj--SmZXnig?pwd=2jdm>                                        |
| 天数 TY1100-NX | 请不要自行刷写BIOS                                                                                |

正常参赛流程下，开发板通常已经完成 BIOS 刷写和系统镜像预装，开发者无需自行执行本章节。仅在赛事维护人员明确要求，或已确认当前 BIOS 版本与赛事指定版本不一致时，才需要进行更新。

> **WARNING：**
>
> 不同品牌、型号和硬件版本的开发板使用不同的 BIOS 固件。即使刷写流程相似，不同开发板的 BIOS 文件也不能混用。
>
> 刷入错误的 BIOS 可能导致设备无法启动，并且通常无法通过普通 U 盘方式自行恢复，需要由赛事维护人员使用专用工具处理。

## 一、更新前确认

执行 BIOS 更新前，应确认以下信息：

1.  当前开发板的型号及硬件版本；

2.  BIOS 固件适用于当前开发板，并符合赛事指定的 Release 基线；

3.  固件来自开发板官方资源页面、赛事资源包或赛事维护人员提供的可靠来源；

4.  已阅读固件包内的更新说明，并确认更新方式、文件名称及命令参数与当前固件包一致。

不要仅根据 BIOS 文件名判断固件是否可用。如果无法确认固件是否匹配，请停止操作并联系赛事维护人员。

## 二、制作 BIOS 更新 U 盘

准备以下硬件：

1.  待更新 BIOS 的开发板及匹配的电源适配器；

2.  显示器与HDMI 或 DP 连接线；

3.  FAT32 格式 U 盘；

4.  USB 键盘。

从赛事资源包中下载当前开发板对应的 BIOS 更新包。

将更新包解压后，按照原有目录结构复制到 FAT32 U 盘。不要只复制其中的 BIOS .bin 文件，也不要自行删除、移动或重命名更新包中的文件。

BIOS 更新包中通常包含以下文件：

- startup.nsh

- FlashUpdate.efi

- Shell.efi

- BIOS 固件 .bin 文件

- EFI 目录

- 平台专用目录

- 其他辅助工具和配置文件

其中，开发者通常只需要使用厂商指定的 BIOS 更新入口：

```bash
startup.nsh
```

或者：

```bash
FlashUpdate.efi -f <实际 BIOS 文件名>.bin
```

更新包中的其他文件通常不需要开发者手动执行，但必须按照原有目录结构完整保留。

## 三、进入 UEFI Shell

1.  将 BIOS 更新 U 盘插入开发板；

2.  连接显示器、键盘和电源并给设备上电；

3.  在启动 Logo 阶段连续短按 Esc 或 F2，进入 BIOS 设置界面；

4.  进入 Boot Manager；

5.  选择 UEFI Shell。

## 四、定位 BIOS 更新 U 盘

进入 UEFI Shell 后，屏幕通常会显示文件系统映射，例如：

```bash
FS0:
FS1:
FS2:
```

依次进入文件系统并查看目录内容：

```bash
FS0:
ls
```

如果没有看到 BIOS 更新文件，继续尝试：

```bash
FS1:
ls
```

或者：

```bash
FS2:
ls
```

如果 U 盘未出现在当前映射表中，可以执行：

```bash
map -r
```

重新扫描设备后，再检查各个 FS 目录。

当目录中出现以下任意内容时，通常说明已经定位到 BIOS 更新 U 盘：

- startup.nsh

- FlashUpdate.efi

- BIOS 固件 .bin 文件

- 平台专用更新目录

## 五、执行 BIOS 更新

进入 BIOS 更新 U 盘目录后，根据当前开发板官方说明或赛事资源包选择对应的更新方式。

> **WARNING：**
>
> BIOS 更新过程中，请保持设备持续供电，不要拔出 U 盘、按下电源键、强制重启设备或执行其他 UEFI Shell 命令，以免更新中断并导致设备无法正常启动。
>
> 部分开发板进入 UEFI Shell 后会自动检测并执行 startup.nsh。如果更新程序已经自动启动，请勿重复输入命令。

### 方式一：执行 startup.nsh

如果更新包提供 startup.nsh，且官方说明要求通过该脚本进行更新，输入以下命令并按 Enter 键：

```bash
startup.nsh
```

startup.nsh 通常会自动调用 BIOS 更新工具和对应的固件文件。开发者不需要再手动执行更新包中的其他 .efi 工具。

### 方式二：执行 FlashUpdate.efi

如果更新包未提供 startup.nsh，或官方说明明确要求使用 FlashUpdate.efi，执行：

```bash
FlashUpdate.efi -f <实际 BIOS 文件名>.bin
```

例如，实际 BIOS 文件名为：

```text
board_bios_general.bin
```

则执行：

```bash
FlashUpdate.efi -f board_bios_general.bin
```

注意：startup.nsh 和 FlashUpdate.efi 不是任选其一，如不确定应以当前开发板官方说明或赛事资源包中的更新步骤为准。

## 六、平台示例

**示例一：Radxa Orion O6**

从 Radxa 官方资源页面[资源汇总下载 \| Radxa Docs](https://docs.radxa.com/orion/download#bios-%E5%9B%BA%E4%BB%B6)下载<https://dl.radxa.com/orion/o6/images/bios/orion-o6-bios-1.1.0-1.zip>或赛事资源包中找到与当前设备匹配的 BIOS 更新包。

将解压后的全部文件按照原有目录结构复制到 FAT32 U 盘根目录。

进入 UEFI Shell 并定位到 BIOS 更新 U 盘后，执行：

```bash
startup.nsh
```

更新脚本会自动调用对应的更新工具和 BIOS 固件文件。开发者不需要手动执行 FlashUpdate.efi、BurnImage.efi 或其他辅助程序。

**示例二：Orange Pi 6 Plus**

从 Orange Pi 官方资源页面[OrangePi 6 Plus-Orange Pi官网](http://www.orangepi.cn/html/hardWare/computerAndMicrocontrollers/service-and-support/Orange-Pi-6-Plus.html)或赛事资源包中下载与当前设备匹配的 General BIOS 更新包。

将解压后的全部文件按照原有目录结构复制到 FAT32 U 盘。

进入 UEFI Shell 并定位到 BIOS 更新 U 盘，并确认目录中存在 FlashUpdate.efi 和对应的 General BIOS 固件文件后，执行：

```bash
FlashUpdate.efi -f OPI6PLUS_BIOS_1.4_General.bin
```

其中，OPI6PLUS_BIOS_1.4_General.bin 可以替换为当前赛事资源包或官方 BIOS 更新包中的实际文件名。

## 七、重启与验证

看到 BIOS 更新成功提示后：

1.  按照屏幕提示等待设备自动重启或关闭设备；

2.  如果设备自动重启，请在确认更新完成后正常关闭设备；

3.  等待数秒，确保设备完全断电；

4.  拔出 BIOS 更新 U 盘；

5.  重新给设备上电；

6.  检查设备能否正常进入 BIOS 和操作系统。

更新完成后，建议确认以下项目：

1.  设备可以正常上电；

2.  显示器可以正常输出；

3.  可以进入 BIOS 设置界面；

4.  BIOS 可以识别启动盘；

5.  可以正常进入操作系统；

6.  BIOS 版本与赛事指定版本一致；

7.  系统和外设运行正常。

BIOS 版本应优先在 BIOS 设置界面中查看，常见字段包括：

```text
BIOS Version
Build Date
Firmware Version
Hardware Information
```

进入操作系统后，也可以执行：

```bash
uname -a
cat /etc/os-release
```

以上命令用于确认当前内核和操作系统环境，不能直接用于判断 BIOS 固件版本。
