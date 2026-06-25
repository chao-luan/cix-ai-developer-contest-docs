# MNN CPU / KleidiAI

本文档介绍如何在 Armv9 开发板上使用 MNN 的 CPU 路径运行本地 LLM / VLM / 多模态模型，并尽可能利用 Arm CPU 优化能力。

本流程基于 Arm Learning Path 中的 MNN Omni 示例，优先验证 CPU-only 本地多模态推理路径。

## 1. 适用场景

* 在开发板本地运行 MNN 模型。
* 验证 MNN CPU 路径是否可用。
* 验证 `llm_demo` 是否可以加载 MNN Omni 模型。
* 验证文本、图像等多模态输入能力。
* 为后续 MNN OpenCL 或其他后端验证提供基线。

## 2. 前置条件

* 开发板已正常启动。
* 已完成网络配置。
* 可访问 GitHub / ModelScope。
* 磁盘空间充足。

建议至少预留：

```text
MNN 源码和编译空间：5 GB+
Qwen2.5-Omni-7B-MNN 模型：约 15 GB+
```

## 3. 安装基础依赖

```bash
sudo apt update
sudo apt install -y git build-essential gcc g++ cmake
```

安装 Git LFS，用于下载大模型权重：

```bash
sudo apt install -y git-lfs
git lfs install
```

## 4. 创建工作目录

```bash
mkdir -p ~/mnn
cd ~/mnn
```

## 5. 获取 MNN 源码

```bash
git clone https://github.com/alibaba/MNN.git
cd MNN
```

## 6. 编译 MNN CPU / KleidiAI 版本

```bash
mkdir -p build
cd build

cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DMNN_BUILD_SHARED=ON \
  -DMNN_BUILD_LLM=ON \
  -DMNN_BUILD_AUDIO=ON \
  -DMNN_BUILD_LLM_OMNI=ON \
  -DMNN_LOW_MEMORY=ON \
  -DMNN_KLEIDIAI=ON

make -j$(nproc)
```

参数说明：

| 参数                      | 说明                   |
| ----------------------- | -------------------- |
| `MNN_BUILD_SHARED=ON`   | 构建共享库                |
| `MNN_BUILD_LLM=ON`      | 启用 LLM 支持            |
| `MNN_BUILD_AUDIO=ON`    | 启用音频相关组件             |
| `MNN_BUILD_LLM_OMNI=ON` | 启用 Omni 多模态支持        |
| `MNN_LOW_MEMORY=ON`     | 启用较低内存占用配置           |
| `MNN_KLEIDIAI=ON`       | 启用 Arm KleidiAI 相关优化 |

## 7. 验证编译产物

```bash
ls -l ~/mnn/MNN/build/llm_demo
```

如果存在 `llm_demo`，说明 MNN LLM Demo 编译成功。

## 8. 配置运行时库路径

检查 `llm_demo` 链接到的 MNN 动态库：

```bash
cd ~/mnn/MNN/build
ldd ./llm_demo | grep -E "libMNN|Express|Audio|OpenCV" || true
```

如果发现 `libMNN.so` 指向系统中其他目录，而不是本次编译的 `~/mnn/MNN/build`，建议设置 `LD_LIBRARY_PATH`：

```bash
export LD_LIBRARY_PATH=$HOME/mnn/MNN/build:$HOME/mnn/MNN/build/express:$HOME/mnn/MNN/build/tools/audio:$HOME/mnn/MNN/build/tools/cv:${LD_LIBRARY_PATH:-}
```

如需长期生效：

```bash
echo 'export LD_LIBRARY_PATH=$HOME/mnn/MNN/build:$HOME/mnn/MNN/build/express:$HOME/mnn/MNN/build/tools/audio:$HOME/mnn/MNN/build/tools/cv:${LD_LIBRARY_PATH:-}' >> ~/.bashrc
source ~/.bashrc
```

再次检查：

```bash
ldd ./llm_demo | grep -E "libMNN|Express|Audio|OpenCV" || true
```

## 9. 下载验证模型

Arm Learning Path 使用预构建的 MNN Omni 模型包：

```bash
cd ~/mnn
git clone https://www.modelscope.cn/MNN/Qwen2.5-Omni-7B-MNN.git
cd ~/mnn/Qwen2.5-Omni-7B-MNN
git lfs pull
```

检查主要模型文件：

```bash
ls -lh ~/mnn/Qwen2.5-Omni-7B-MNN/config.json
ls -lh ~/mnn/Qwen2.5-Omni-7B-MNN/llm.mnn
ls -lh ~/mnn/Qwen2.5-Omni-7B-MNN/llm.mnn.weight
```

```{note}
如果 `llm.mnn` 或 `llm.mnn.weight` 只有几百字节，说明 Git LFS 权重没有完整下载，需要重新执行 `git lfs pull`。
```

## 10. 验证模型是否能加载

```bash
cd ~/mnn/MNN/build
./llm_demo ~/mnn/Qwen2.5-Omni-7B-MNN/config.json
```

如果进入交互模式，说明模型配置和运行时基本可用。

退出方式：

```text
Ctrl+C
```

或输入：

```text
exit
```

## 11. 文本推理验证

创建 prompt 文件：

```bash
cat > ~/mnn/text_baseline_prompt.txt <<'EOF'
You are an on-device inference assistant. In one short sentence, describe the benefits of multimodal on-device inference.
EOF
```

运行文本推理：

```bash
cd ~/mnn/MNN/build
./llm_demo ~/mnn/Qwen2.5-Omni-7B-MNN/config.json ~/mnn/text_baseline_prompt.txt
```

如果可以看到模型输出文本，说明 MNN CPU 文本推理路径已跑通。

## 12. 图像多模态验证

准备图片目录：

```bash
mkdir -p ~/mnn/assets
```

下载测试图片：

```bash
wget -P ~/mnn/assets https://upload.wikimedia.org/wikipedia/commons/e/e6/Pet_Food_Aisle.jpg
```

检查图片：

```bash
file ~/mnn/assets/Pet_Food_Aisle.jpg
```

创建图像 prompt：

```bash
cat > ~/mnn/prompt_picture_coverage.txt <<EOF
<img>$HOME/mnn/assets/Pet_Food_Aisle.jpg</img> You are an on-device retail shelf auditing assistant. Audit ONLY the main left shelf. Do NOT count every item. Estimate facing coverage for top/middle/bottom as high|medium|low and identify the sparsest zone. Output ONE line only using bullet-style segments separated by semicolons: Shelf audit; - Coverage: top=<high|medium|low>, middle=<high|medium|low>, bottom=<high|medium|low>; - Priority zone: <top|middle|bottom>-<left|center|right>; - Reason: <one short sentence>; - Notes: <NOT_SURE if unclear>.
EOF
```

运行图像推理：

```bash
cd ~/mnn/MNN/build
./llm_demo ~/mnn/Qwen2.5-Omni-7B-MNN/config.json ~/mnn/prompt_picture_coverage.txt
```

```{note}
图像推理通常比文本推理更慢，因为模型需要先编码图像。终端长时间没有输出不一定代表卡死，请等待一段时间再判断。
```

## 13. 验证结果记录

建议记录：

```bash
uname -a
cat /etc/os-release
lscpu
free -h
```

以及以下结果：

| 项目                  | 结果  |
| ------------------- | --- |
| 开发板型号               | 待补充 |
| OS / Kernel         | 待补充 |
| MNN commit          | 待补充 |
| 是否启用 `MNN_KLEIDIAI` | 待补充 |
| `llm_demo` 是否生成     | 待补充 |
| 模型是否下载完整            | 待补充 |
| 文本推理是否成功            | 待补充 |
| 图像推理是否成功            | 待补充 |
| 首次加载耗时              | 待补充 |
| 备注                  | 待补充 |

## 14. 常见问题

### 14.1 编译失败

检查：

* `cmake` 是否安装。
* `gcc/g++` 是否安装。
* 磁盘空间是否充足。
* 是否缺少 MNN 编译依赖。
* 是否使用了不支持当前平台的编译选项。

### 14.2 找不到 `llm_demo`

检查是否启用了：

```text
-DMNN_BUILD_LLM=ON
-DMNN_BUILD_LLM_OMNI=ON
```

重新编译：

```bash
cd ~/mnn/MNN
rm -rf build
mkdir build && cd build

cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DMNN_BUILD_SHARED=ON \
  -DMNN_BUILD_LLM=ON \
  -DMNN_BUILD_AUDIO=ON \
  -DMNN_BUILD_LLM_OMNI=ON \
  -DMNN_LOW_MEMORY=ON \
  -DMNN_KLEIDIAI=ON

make -j$(nproc)
```

### 14.3 运行时报 `undefined symbol`

通常是动态库路径混乱导致 `llm_demo` 加载了系统里的旧版 `libMNN.so`。

执行：

```bash
ldd ./llm_demo | grep -E "libMNN|Express|Audio|OpenCV" || true
```

然后设置：

```bash
export LD_LIBRARY_PATH=$HOME/mnn/MNN/build:$HOME/mnn/MNN/build/express:$HOME/mnn/MNN/build/tools/audio:$HOME/mnn/MNN/build/tools/cv:${LD_LIBRARY_PATH:-}
```

### 14.4 模型文件没有完整下载

检查：

```bash
ls -lh ~/mnn/Qwen2.5-Omni-7B-MNN/llm.mnn ~/mnn/Qwen2.5-Omni-7B-MNN/llm.mnn.weight
```

如果文件很小，重新执行：

```bash
cd ~/mnn/Qwen2.5-Omni-7B-MNN
git lfs pull
```

### 14.5 图像推理很慢

图像推理需要额外编码图片，在 CPU-only 路径上可能需要较长时间。建议先完成文本推理，再验证图像推理。

## 15. 参考资料

* [Arm Learning Path: Build a Multimodal Retail Restocking Assistant on Armv9 With MNN](https://learn.arm.com/learning-paths/cross-platform/multimodel_mnn_v9/)
* [Arm Learning Path: Build MNN and prepare an Omni model on Armv9](https://learn.arm.com/learning-paths/cross-platform/multimodel_mnn_v9/2_mnn_build/)
* [MNN GitHub Repository](https://github.com/alibaba/MNN)
* [Qwen2.5-Omni-7B-MNN ModelScope Repository](https://www.modelscope.cn/MNN/Qwen2.5-Omni-7B-MNN)
