# 2.2 OS

本章节用于在系统无法启动、系统环境损坏或需要恢复赛事统一环境时，将赛事指定的系统镜像重新烧录至 NVMe SSD。

正常情况下，参赛设备已经预装赛事指定的 Debian 12 系统，无需重新烧录。仅在赛事维护人员明确要求，或设备系统无法正常恢复时执行本章节操作。

本章提供以下两种系统恢复方式：

1.  **通过 NVMe USB 硬盘盒恢复系统**：将 NVMe SSD 从开发板中拆下，通过硬盘盒连接至 Windows、Linux 或 macOS 电脑，使用 balenaEtcher 将解压后的磁盘镜像写入 NVMe SSD。该方式操作直观，推荐普通开发者使用。
2.  **通过 U 盘启动恢复或安装系统**：在不便拆卸 NVMe SSD 时，先从 U 盘启动开发板，再根据镜像类型完成系统恢复。对于 .img.xz 磁盘镜像，解压后使用 dd 写入板载 NVMe SSD；对于 .iso 安装镜像，从 U 盘启动安装程序，并按照界面提示将系统安装至 NVMe SSD。

两种方式任选其一，无需重复执行。

.img.xz 是经过压缩的完整磁盘镜像，使用前应先解压为 .img。解压后的 .img 既可以写入 U 盘作为可启动系统，也可以写入 NVMe SSD。本指南主要介绍将系统恢复至 NVMe SSD 的操作方法。

.iso 通常作为系统安装介质使用，应先写入 U 盘并从 U 盘启动安装程序，不应直接作为完整磁盘镜像写入 NVMe SSD。

```{warning}
系统镜像烧录会清除目标 SSD 中的全部数据。执行前请备份重要文件，并仔细确认目标磁盘的型号、容量及设备名称，避免误操作电脑本机硬盘、U 盘或其他存储设备。
```

## 2.2.1 准备工作

通用准备：

1.  当前开发平台对应的赛事系统镜像；
2.  待恢复系统的开发板及匹配的电源适配器；
3.  显示器和键盘，用于启动和烧录结果验证；
4.  提前备份 NVMe SSD 中的重要数据。

采用 NVMe USB 硬盘盒方式时，还需准备：

1.  NVMe USB 硬盘盒；
2.  Windows 或 Linux 电脑；
3.  从开发板中拆下的目标 NVMe SSD。

采用 U 盘启动方式时，还需准备：

1.  能够在当前开发板上正常启动的系统 U 盘；
2.  已安装在开发板上的目标 NVMe SSD。

Windows、Linux 和 macOS 环境均推荐使用 balenaEtcher 完成镜像写入。

对于 .img.xz 镜像，应先解压为 .img，再使用 balenaEtcher 写入 NVMe SSD，或者在开发板从 U 盘启动后使用 dd 写入板载 NVMe SSD。

对于 .iso 镜像，应使用 balenaEtcher 将其写入 U 盘，再从 U 盘启动系统安装程序。

不同开发板系统镜像地址如下：

<table>
<colgroup>
<col style="width: 22%" />
<col style="width: 77%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>开发平台</strong></th>
<th><strong>下载链接</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><p>瑞莎星睿 O6</p>
<p>铭凡MS-R1</p></td>
<td><a href="https://archive.cixtech.com/cdimage_debian/debian-12.13.0-arm64-DVD-cix-20260514.iso">https://archive.cixtech.com/cdimage_debian/debian-12.13.0-arm64-DVD-cix-20260514.iso</a></td>
</tr>
<tr class="even">
<td>瑞莎星睿 O6N</td>
<td><a href="https://github.com/radxa-build/radxa-orion-cix-p1/releases/download/rsdk-r1/radxa-orion-cix-p1_bookworm_gnome_r1.output_512.img.xz">https://github.com/radxa-build/radxa-orion-cix-p1/releases/download/rsdk-r1/radxa-orion-cix-p1_bookworm_gnome_r1.output_512.img.xz</a></td>
</tr>
<tr class="odd">
<td>香橙派 6 Plus</td>
<td><a href="https://pan.baidu.com/s/1rzAbpiAIy1XT2Xg6ztWk6Q?pwd=e5rv">https://pan.baidu.com/s/1rzAbpiAIy1XT2Xg6ztWk6Q?pwd=e5rv</a></td>
</tr>
<tr class="even">
<td>天数 TY1100-NX</td>
<td>已安装好官方镜像，不建议重刷</td>
</tr>
</tbody>
</table>

不同平台的系统镜像格式和用途不同：

- .img.xz：压缩的完整磁盘镜像，使用前先解压为 .img；
- .img：可以写入 U 盘或 NVMe SSD；
- .iso：系统安装介质，通常写入 U 盘后启动安装程序。

请勿将镜像文件作为普通文件复制到 U 盘或 SSD。必须使用 balenaEtcher 或 dd 将镜像内容写入整个目标设备。

## 2.2.2 方式一：通过 NVMe USB 硬盘盒烧录

### 2.2.2.1 准备 balenaEtcher

从 balenaEtcher 官方页面下载并安装适用于当前电脑操作系统的版本。

balenaEtcher 支持 Windows、Linux 和 macOS，后续操作基本一致。

### 2.2.2.2 解压 .img.xz 镜像

如果下载的镜像后缀为 .img.xz，应先将其解压为 .img。

Windows 环境可以使用 7-Zip 等解压工具。

Linux 环境可以执行：

```bash
sudo apt update
sudo apt install -y xz-utils
```

解压镜像：

```text
unxz <系统镜像文件>.img.xz
```

例如：

```text
unxz \
radxa-orion-cix-p1_bookworm_gnome_r1.output_512.img.xz
```

解压完成后应得到：

```text
radxa-orion-cix-p1_bookworm_gnome_r1.output_512.img
```

检查镜像文件：

```bash
ls -lh \
radxa-orion-cix-p1_bookworm_gnome_r1.output_512.img
```

如果镜像本身已经是 .img，可以跳过解压步骤。

.iso 镜像不适用于本节的 NVMe 硬盘盒直接恢复方式，应按照 2.2.3 节制作系统安装 U 盘。

### 2.2.2.3 连接目标 SSD

将 NVMe SSD 安装到 NVMe USB 硬盘盒中，并连接至电脑。

如果 Windows 弹出初始化磁盘、格式化磁盘或修复磁盘提示，请选择取消。写入前不需要初始化、分区或格式化 SSD。

### 2.2.2.4 写入系统镜像

启动 balenaEtcher：

1.  单击 Flash from file；
2.  选择解压后的 .img 系统镜像；
3.  单击 Select target；
4.  选择 NVMe USB 硬盘盒中的目标 SSD；
5.  根据 SSD 容量和型号再次确认目标设备；
6.  单击 Flash；
7.  等待镜像写入和校验完成。

```{warning}
写入操作会清除目标 SSD 中的全部数据。不要选择电脑本机系统盘、其他硬盘或 U 盘。

写入过程中请勿：

1.  断开 NVMe USB 硬盘盒；
2.  关闭电脑或 balenaEtcher；
3.  使电脑进入睡眠或休眠状态；
4.  对目标 SSD 执行其他磁盘操作。
```

### 2.2.2.5 安全移除并安装 SSD

写入完成后：

1.  使用操作系统的安全弹出功能移除 NVMe USB 硬盘盒；
2.  关闭开发板电源；
3.  将 NVMe SSD 安装回开发板；
4.  确认 SSD 已正确插入并固定；
5.  连接显示器和键盘；
6.  给开发板上电。

首次启动时，系统可能执行初始化或自动扩展分区，启动时间可能比平时更长。请等待系统完成启动，不要中途断电。

## 2.2.3 方式二：通过 U 盘启动恢复或安装系统

如果不便拆卸 NVMe SSD，可以先制作系统启动 U 盘，再从 U 盘启动开发板。后续操作取决于系统镜像格式。

### 2.2.3.1 制作启动 U 盘

使用 balenaEtcher 制作启动 U 盘：

1.  将 U 盘连接至电脑；
2.  启动 balenaEtcher；
3.  单击 Flash from file；
4.  选择系统镜像；
5.  单击 Select target；
6.  选择目标 U 盘；
7.  单击 Flash；
8.  等待写入和校验完成；
9.  安全移除 U 盘。

如果镜像为 .img.xz，应先按照 2.2.2 节的方法解压为 .img，再写入 U 盘。

如果镜像为 .iso，可以直接选择 .iso 文件制作系统安装 U 盘。

### 2.2.3.2 从 U 盘启动

1.  确认目标 NVMe SSD 已安装在开发板中；
2.  将启动 U 盘插入开发板；
3.  连接显示器、键盘和电源；
4.  给设备上电；
5.  在启动 Logo 阶段连续短按 Esc 或 F2，进入 Boot Manager；
6.  选择对应的 USB 存储设备启动。

进入系统后执行：

```text
findmnt /
lsblk -o NAME,SIZE,MODEL,TRAN,TYPE,MOUNTPOINTS
```

应确认：

1.  当前根文件系统运行在 U 盘中；
2.  板载 NVMe SSD 可以正常识别；
3.  已明确区分启动 U 盘和目标 NVMe SSD。

### 2.2.3.3 使用 .img.xz 镜像写入 NVMe SSD

本步骤适用于 .img.xz 磁盘镜像。

将系统镜像复制或下载到当前 U 盘系统中。安装解压工具：

```bash
sudo apt update
sudo apt install -y xz-utils
```

解压镜像：

```text
unxz <系统镜像文件>.img.xz
```

确认板载 NVMe SSD：

```text
lsblk -o NAME,SIZE,MODEL,TYPE,MOUNTPOINTS
```

板载 NVMe SSD 通常显示为：

```bash
/dev/nvme0n1
```

如果 NVMe SSD 分区被自动挂载，应根据实际分区名称卸载，例如：

```bash
sudo umount /dev/nvme0n1p1 2>/dev/null || true
sudo umount /dev/nvme0n1p2 2>/dev/null || true
```

使用 dd 将解压后的 .img 写入整个 NVMe SSD：

```bash
sudo dd \
if=<解压后的系统镜像>.img \
of=/dev/nvme0n1 \
bs=4M \
conv=fsync \
status=progress
```

```{warning}
of 必须填写整个 NVMe 磁盘设备：

/dev/nvme0n1

不要填写分区设备：

/dev/nvme0n1p1

也不要将启动 U 盘误选为目标设备。

写入完成后执行：

sync

sudo poweroff

等待设备完全关机后拔出 U 盘，再重新上电，使设备从 NVMe SSD 启动。
```

### 2.2.3.4 使用 .iso 镜像安装系统

本步骤适用于 .iso 系统安装镜像。

从 .iso 安装 U 盘启动后，按照系统安装界面的提示完成安装。

安装过程中应确认：

1.  安装目标为开发板中的 NVMe SSD；
2.  不要选择系统安装 U 盘作为目标磁盘；
3.  已备份目标 NVMe SSD 中的重要数据；
4.  分区和格式化操作针对的是目标 NVMe SSD；
5.  安装过程中保持设备持续供电。

安装完成后：

1.  按照安装程序提示关闭或重新启动设备；
2.  等待设备完全关机；
3.  拔出系统安装 U 盘；
4.  重新给设备上电；
5.  确认设备从 NVMe SSD 启动。

如果设备仍然进入安装界面，应检查 U 盘是否已拔出，或者在 Boot Manager 中调整启动顺序。

## 2.2.4 验证烧录结果

系统启动后，执行以下命令检查系统和磁盘信息：

```bash
uname -a
```

用于查看当前内核及系统架构信息。

```bash
cat /etc/os-release
```

用于查看当前操作系统版本。

```bash
lsblk
```

用于查看 SSD、磁盘分区及挂载关系。

```bash
df -h
```

用于查看系统分区的容量和使用情况。

应确认以下项目：

1.  开发板可以正常上电和启动，进入 Debian 12系统；
2.  系统版本符合赛事指定的 Release 基线；
3.  NVMe SSD 可以正常识别；
4.  系统根分区可以正常挂载，根分区容量显示正常；
5.  网络和基础外设可以正常使用。
6.  执行 findmnt /，确认系统根目录实际挂载在目标 NVMe SSD 分区，而不是启动 U 盘。
