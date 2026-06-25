# Troubleshooting

本文档整理开发板在启动、显示、网络、系统服务、SDK 环境和 AI Demo 运行过程中的常见问题与排查方法。

正常参赛流程下，选手收到的设备应已完成 BIOS 刷写、OS 镜像预装和基础环境配置。出现问题时，应优先按照本文档从低风险操作开始排查，不要直接重刷系统或 BIOS。

## 1. 排查原则

建议按照从低风险到高风险的顺序排查：

```text
检查供电和外设
→ 检查显示输出
→ 检查网络服务和系统服务
→ 检查启动盘和系统状态
→ 重启相关服务
→ 重启系统
→ 重刷 OS 镜像
→ BIOS 刷写
→ 更换硬件交叉验证
```

```{warning}
不要把所有异常都直接归因于 BIOS。

Wi-Fi 异常、图形界面异常、SDK 依赖异常、Demo 启动失败、端口占用等问题，大多数情况下与 BIOS 无关，应优先从系统服务、驱动、配置和软件环境排查。
```

## 2. 快速检查清单

遇到设备异常时，先确认以下项目：

| 检查项  | 说明                          |
| ---- | --------------------------- |
| 电源   | 电源适配器规格是否满足要求，供电线是否稳定       |
| 显示   | HDMI / DP 线是否正常，显示器输入源是否正确  |
| 外设   | 键盘、鼠标、U 盘是否识别               |
| 启动盘  | NVMe SSD 是否安装到位             |
| 网络   | 有线或无线网络是否可用                 |
| 系统   | 是否能进入系统或通过 SSH 登录           |
| 服务   | NetworkManager、gdm3 等服务是否正常 |
| SDK  | NPU / AI SDK 组件是否安装完整       |
| Demo | Demo 端口是否被占用，依赖是否安装完整       |

## 3. 设备无法启动

### 3.1 现象

* 上电后无系统画面。
* 无法进入操作系统。
* 停留在启动界面。
* 反复重启。
* 无法识别启动盘。

### 3.2 可能原因

* 电源不稳定。
* 显示器或显示线异常。
* NVMe SSD 未安装到位。
* OS 镜像损坏。
* BIOS 启动项异常。
* BIOS 与 OS Release 不匹配。

### 3.3 排查步骤

1. 断电后重新上电。
2. 检查电源适配器和供电线。
3. 更换 HDMI / DP 线。
4. 更换显示器或切换显示器输入源。
5. 尝试进入 UEFI 设置界面。
6. 检查 NVMe SSD 是否安装到位。
7. 使用硬盘盒连接电脑，确认 SSD 是否可识别。
8. 必要时重刷 OS 镜像。

系统镜像重刷请参考：

[Reflash OS Image](reflash-os-image.md)

如果 OS 重刷后仍无法启动，再联系维护人员判断是否需要 BIOS 刷写。

## 4. 黑屏或无显示输出

### 4.1 现象

* 板卡上电后屏幕无信号。
* 系统可能已经启动，但桌面不显示。
* 显示器一直黑屏。
* 图形界面无法进入。

### 4.2 排查步骤

先确认是否只是显示问题：

1. 检查 HDMI / DP 线。
2. 检查显示器输入源。
3. 更换显示器。
4. 尝试进入 UEFI。
5. 尝试通过 SSH 登录设备。

如果可以 SSH 登录，说明系统可能仍在运行。可尝试重启图形界面服务：

```bash
sudo systemctl restart gdm3
```

查看服务状态：

```bash
systemctl status gdm3
```

查看近期错误日志：

```bash
journalctl -xe
```

```{note}
如果系统可以通过 SSH 登录，通常不需要直接重刷 BIOS。优先排查显示服务、桌面环境、GPU / 显示驱动和线缆问题。
```

## 5. 能检测到网卡但没有 Wi-Fi

### 5.1 现象

* 系统能检测到无线网卡。
* 图形界面没有 Wi-Fi 开关。
* Wi-Fi 列表为空。
* Wi-Fi 无法连接。
* 重启后 Wi-Fi 消失或异常。

### 5.2 排查步骤

查看网络设备状态：

```bash
nmcli device status
```

查看 Wi-Fi 开关状态：

```bash
nmcli radio wifi
```

查看是否被软/硬开关禁用：

```bash
rfkill list
```

如果 Wi-Fi 被 block，执行：

```bash
sudo rfkill unblock wifi
```

重启 NetworkManager：

```bash
sudo systemctl restart NetworkManager
```

重新扫描 Wi-Fi：

```bash
nmcli device wifi list
```

也可以使用文本界面配置网络：

```bash
nmtui
```

### 5.3 仍无法恢复

如果仍没有 Wi-Fi，建议：

1. 重启系统。
2. 检查是否可以使用有线网络。
3. 检查 NetworkManager 状态。
4. 保存以下命令输出并反馈维护人员：

```bash
nmcli device status
nmcli radio wifi
rfkill list
ip addr
journalctl -u NetworkManager --no-pager | tail -100
```

```{warning}
Wi-Fi 异常通常不需要刷 BIOS。除非维护人员明确确认问题与 BIOS 或固件版本相关，否则不要因为 Wi-Fi 问题自行刷写 BIOS。
```

## 6. 有线网络异常

### 6.1 现象

* 插入网线后无法联网。
* 无法获取 IP。
* 可以 ping IP，但无法访问域名。
* SSH 无法连接。

### 6.2 排查步骤

检查网口状态：

```bash
ip link
nmcli device status
```

查看 IP 地址：

```bash
ip addr
```

重启网络服务：

```bash
sudo systemctl restart NetworkManager
```

测试网络连通性：

```bash
ping -c 4 8.8.8.8
```

测试 DNS：

```bash
ping -c 4 www.baidu.com
```

如果可以 ping IP，但无法 ping 域名，检查 DNS：

```bash
resolvectl status
```

## 7. 图形界面异常

### 7.1 现象

* 可以进入命令行，但无法进入桌面。
* 桌面卡死。
* 登录后黑屏。
* 图形应用无法启动。

### 7.2 排查步骤

重启显示管理服务：

```bash
sudo systemctl restart gdm3
```

查看状态：

```bash
systemctl status gdm3
```

查看日志：

```bash
journalctl -u gdm3 --no-pager | tail -100
journalctl -xe
```

如果远程 SSH 可用，可以先通过 SSH 备份日志，再进一步处理。

## 8. SDK 环境异常

### 8.1 现象

* NPU 设备节点不存在。
* Python 推理库找不到。
* AI Demo 启动时报缺少依赖。
* 模型推理失败。

### 8.2 检查 NPU 设备

执行：

```bash
ls -l /dev/aipu
```

如果设备节点不存在，检查驱动是否安装、模块是否加载、系统是否需要重启。

### 8.3 检查 Python 依赖

执行：

```bash
pip3 list | grep libnoe
```

如果缺少相关包，需要重新确认 AI SDK 安装步骤。

### 8.4 检查系统版本

执行：

```bash
uname -a
cat /etc/os-release
```

确认系统版本是否符合当前 Release 基线。

```{note}
SDK 环境异常一般优先检查驱动包、用户态运行时库、Python 包和环境变量，不应直接刷 BIOS。
```

## 9. AI Demo Manager 或 Demo 启动异常

### 9.1 AI Demo Manager 无法访问

进入安装目录：

```bash
cd /opt/ai-demo-manager/
```

启动服务：

```bash
python3 manager.py
```

默认访问地址通常为：

```text
http://localhost:7860
```

远程访问时，应将 `localhost` 替换为开发板实际 IP 地址，例如：

```text
http://<BOARD_IP>:7860
```

### 9.2 Demo 页面打不开

检查：

* Demo 是否已经启动。
* 访问 IP 是否正确。
* 端口是否正确。
* 防火墙或网络是否阻断。
* Demo 进程是否异常退出。

### 9.3 端口占用

如果某个 Demo 已经被手动启动，再通过 AI Demo Manager 启动同一个 Demo，可能会因为端口冲突导致失败。

查看端口占用：

```bash
sudo lsof -i:<PORT>
```

结束对应进程：

```bash
sudo kill -9 <PID>
```

然后重新启动 AI Demo Manager。

```{warning}
通过命令行手动启动的 Demo 进程不一定受 AI Demo Manager 管控。通过 AI Demo Manager 启动前，请确认对应端口没有被其他进程占用。
```

## 10. 系统镜像疑似损坏

### 10.1 现象

* 系统无法启动。
* 分区异常。
* 大量系统文件缺失。
* 多个基础服务异常。
* 重启服务无法恢复。
* 环境与统一参赛基线明显不一致。

### 10.2 处理方法

如果确认 OS 镜像损坏，或需要恢复统一参赛环境，可以重刷 OS 镜像。

请参考：

[Reflash OS Image](reflash-os-image.md)

```{warning}
重刷 OS 镜像会覆盖目标硬盘数据。执行前请确认目标盘符和镜像版本。
```

## 11. BIOS 相关问题

只有在以下情况才考虑 BIOS 刷写：

* 维护人员明确要求。
* 当前 BIOS 版本与 Release 基线不匹配。
* 设备无法启动，且已排除电源、显示器、启动盘和 OS 镜像问题。
* 已确认当前问题与 BIOS 固件相关。

请参考：

[BIOS Flashing and Recovery](bios-flashing.md)

```{danger}
不同品牌、不同型号、不同硬件版本的开发板所使用的 BIOS 固件并不相同。刷错 BIOS 可能导致设备无法启动，开发者通常无法自行恢复，需要专用工具或维护人员救砖。

除非维护人员明确要求，否则不要自行刷写 BIOS。
```

## 12. 重刷系统或 BIOS 后仍无法恢复

如果完成常规排查后仍无法恢复，建议：

* 更换 NVMe SSD 交叉验证。
* 更换电源适配器。
* 更换显示器或显示线。
* 更换 U 盘重新制作启动盘或 BIOS 更新盘。
* 检查是否使用了错误的 OS 镜像。
* 检查是否使用了错误的 BIOS 固件。
* 记录状态灯、屏幕现象、串口日志、系统日志或照片。
* 将问题反馈给维护人员。

## 13. 反馈问题时需要提供的信息

反馈问题时建议提供以下信息：

```text
硬件型号：
硬件版本：
OS 版本：
Release 基线：
BIOS 版本：
问题现象：
是否能进入 UEFI：
是否能进入系统：
是否能 SSH 登录：
是否能识别 NVMe：
是否能识别网卡：
是否有 Wi-Fi：
是否能使用有线网络：
是否重启过 NetworkManager：
是否重启过 gdm3：
是否重刷过 OS：
是否刷写过 BIOS：
已尝试操作：
相关日志或截图：
```

常用日志采集命令：

```bash
uname -a
cat /etc/os-release
lsblk
ip addr
nmcli device status
rfkill list
journalctl -xe
```
