# Known Boot Issues

本文档整理设备启动、显示、系统进入和恢复过程中的常见问题。

## 1. 绿灯亮但屏幕无信号

### 可能原因

- 显示器输入源选择错误。
- HDMI / DP 线连接异常。
- 系统未正常启动。
- BIOS 或 OS 镜像版本不匹配。
- 启动盘异常。

### 排查步骤

1. 更换 HDMI / DP 线。
2. 更换显示器或切换输入源。
3. 断电后重新上电。
4. 尝试进入 UEFI 设置界面。
5. 检查 NVMe SSD 是否安装到位。
6. 必要时重刷 OS 镜像或更新 BIOS。

## 2. 无法进入系统

### 可能原因

- NVMe SSD 未识别。
- 系统镜像损坏。
- BIOS 启动项配置异常。
- BIOS 与 OS Release 不匹配。

### 排查步骤

1. 进入 BIOS / UEFI，确认是否能看到启动盘。
2. 检查 NVMe SSD 是否松动。
3. 使用硬盘盒连接电脑，确认 SSD 是否可识别。
4. 重新烧录系统镜像。
5. 如仍无法启动，更新 BIOS。

## 3. U 盘在 UEFI Shell 中不可见

### 可能原因

- U 盘未格式化为 FAT32。
- U 盘未插好。
- 文件未放在 U 盘根目录。
- U 盘兼容性问题。

### 排查步骤

1. 将 U 盘重新格式化为 FAT32。
2. 将 BIOS 更新文件放到 U 盘根目录。
3. 更换 USB 接口。
4. 更换 U 盘。
5. 重新进入 UEFI Shell。

## 4. BIOS 更新命令无法执行

### 可能原因

- 当前目录不是 U 盘目录。
- `FlashUpdate.efi` 文件名不一致。
- BIOS 固件文件名不一致。
- 固件文件缺失或损坏。

### 排查步骤

先执行：

```text
ls
```

确认当前目录下存在：

```text
FlashUpdate.efi
<BIOS_FIRMWARE_FILE>.bin
```

然后再执行：

```text
FlashUpdate.efi -f <BIOS_FIRMWARE_FILE>.bin
```

## 5. 重刷系统后仍无法启动

### 可能原因

- OS 镜像版本不正确。
- BIOS 版本不匹配。
- NVMe SSD 异常。
- 烧录时目标盘符选择错误。
- 写入过程未完整完成。

### 排查步骤

1. 重新确认镜像来源和版本。
2. 重新执行 `sync` 后再弹出硬盘。
3. 更换 NVMe SSD 交叉验证。
4. 检查 BIOS 版本。
5. 重新刷 BIOS 后再启动。

## 6. 端口占用导致 Demo 无法启动

虽然该问题不属于启动问题，但在恢复环境后进行 Demo 验证时较常见。

### 现象

AI Demo Manager 启动某个 Demo 失败，或者页面无法访问。

### 可能原因

该 Demo 已经被手动启动，占用了对应端口。

### 处理方法

先停止手动启动的进程，再通过 AI Demo Manager 启动。必要时可以查找端口占用：

```bash
sudo lsof -i:<PORT>
```

结束对应进程：

```bash
sudo kill -9 <PID>
```

然后重新启动 AI Demo Manager。
