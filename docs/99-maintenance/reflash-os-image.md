# Reflash OS Image

本文档用于在系统镜像损坏、NVMe SSD 需要重新制备或工作人员批量准备设备时，将统一 OS 镜像烧录至 NVMe SSD。

```{warning}
该操作会覆盖目标硬盘上的全部数据。请务必确认目标盘符，避免误写入电脑本机硬盘或其他存储设备。
```

## 1. 适用场景

- 系统无法正常启动。
- NVMe SSD 需要重新烧录统一镜像。
- 工作人员需要批量制备参赛设备。
- 需要恢复到指定 Release 基线。

正常参赛流程下，选手无需执行本操作。

## 2. 前置准备

- NVMe SSD
- NVMe 硬盘盒
- Linux 主机或可执行 `lsblk`、`dd`、`zstd` 的环境
- 统一发布的系统镜像文件

## 3. 确认目标盘符

连接 NVMe 硬盘前，先执行：

```bash
lsblk
```

连接 NVMe 硬盘盒后，再次执行：

```bash
lsblk
```

对比两次输出，确认新增设备节点，例如：

```text
/dev/sda
/dev/sdb
```

```{warning}
后续命令会直接覆盖目标设备。请务必将示例中的 `/dev/sdX` 替换为实际 NVMe 设备节点。
```

## 4. 下载系统镜像

从 Release 发布地址下载系统镜像文件。

```bash
wget <OS_IMAGE_URL>
```

示例镜像文件名：

```text
linux-fs.sdcard.zst
```

## 5. 烧录镜像

执行以下命令，将压缩镜像解压并写入 NVMe SSD：

```bash
zstd -d linux-fs.sdcard.zst -c | sudo dd of=/dev/sdX bs=4M conv=fsync status=progress
```

其中：

- `/dev/sdX`：目标 NVMe SSD 设备节点。
- `bs=4M`：每次写入块大小。
- `conv=fsync`：确保数据同步写入存储设备。
- `status=progress`：显示写入进度。

## 6. 同步并安全弹出

烧录完成后执行：

```bash
sync
sudo eject /dev/sdX
```

## 7. 安装 NVMe SSD

关闭设备电源，将 NVMe SSD 从硬盘盒中取出，并安装回开发板指定插槽。

## 8. 验证结果

重新上电启动设备，确认：

- 板卡可以进入系统。
- 显示器有正常输出。
- 默认账号可以登录。
- 系统版本符合 Release 基线。

可执行以下命令检查：

```bash
uname -a
cat /etc/os-release
```

## 9. 常见问题

### 9.1 写错盘符

现象：本机硬盘或其他移动硬盘数据被覆盖。

处理：该问题通常无法直接恢复，执行烧录前必须通过 `lsblk` 二次确认设备节点。

### 9.2 `zstd: command not found`

安装 zstd：

```bash
sudo apt update
sudo apt install zstd
```

### 9.3 烧录完成后无法启动

检查：

- 镜像版本是否正确。
- NVMe SSD 是否安装到位。
- BIOS 是否支持当前镜像。
- 电源规格是否满足要求。
