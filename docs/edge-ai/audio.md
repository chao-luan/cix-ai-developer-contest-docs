# 3.3 Audio

本节介绍如何使用 CIX AI Model Hub 中的音频模型，在 CIX P1 平台上完成说话人验证、语音识别和语音合成。

## 3.3.1 当前 Audio 模型

### 3.3.1.1 说话人验证

| **模型目录**                         | **主要文件**                                   |
|--------------------------------------|------------------------------------------------|
| Speaker_Verification/onnx_campplus   | CAMPPlus ONNX、.cix、CFG、测试音频和推理脚本   |
| Speaker_Verification/onnx_eres2netv2 | ERes2NetV2 ONNX、.cix、CFG、测试音频和推理脚本 |

说话人验证模型用于提取语音中的说话人特征，并计算两段语音是否来自同一说话人。

### 3.3.1.2 语音识别

| **模型目录**                                         | **说明**                  |
|------------------------------------------------------|---------------------------|
| Speech_Recognition/onnx_sensevoice                   | SenseVoice 语音识别示例   |
| Speech_Recognition/onnx_whisper_tiny_multi_language  | Whisper Tiny 多语言示例   |
| Speech_Recognition/onnx_whisper_small_multi_language | Whisper Small 多语言示例  |
| Speech_Recognition/onnx_whisper_medium_multilingual  | Whisper Medium 多语言示例 |

其中：

- Whisper Tiny 和 Small 目录主要提供 Encoder .cix；
- Whisper Medium 目录同时提供 Encoder 和 Decoder .cix；
- SenseVoice 目录提供 sense_voice_mask256.cix。

不同模型的 NPU 加速范围并不完全相同，应根据模型目录中的实际 .cix 文件判断哪些子模型运行在 NPU 上。

### 3.3.1.3 语音合成

当前 TTS 目录提供：

TTS/onnx_kokoro

该目录包括：

```text
bert2.cix
text_encoder.cix
predictor.cix
decoder00.cix
decoder01.cix
decoder1_int8.mnn
voices/af_heart.pt
voices/zf_xiaoyi.pt
inference_npu.py
inference_onnx.py
```

由此可见，Kokoro 示例是一个由多个子模型组成的混合 Pipeline，并不是将整个 TTS 模型编译为单个 .cix。部分子模型使用 NPU .cix，另一个 Decoder 使用 MNN 模型。

## 3.3.2 Audio 推理流程

不同 Audio 任务的流程如下。

### 3.3.2.1 说话人验证

1. 两段音频
2. 重采样和声学特征提取
3. NPU 提取说话人向量
4. 计算向量相似度
5. 判断是否为同一说话人

### 3.3.2.2 语音识别

1. 音频
2. 重采样、分帧和声学特征提取
3. NPU Encoder 或完整声学模型推理
4. Decoder 和 Tokenizer
5. 识别文本

### 3.3.2.3 TTS

1. 输入文本
2. Tokenizer / BERT
3. Text Encoder
4. 时长或特征预测
5. Decoder
6. 生成音频波形

Audio 示例中的音频读取、特征提取、Tokenizer 和部分 Decoder 可能仍在 CPU 或其他 Runtime 上运行。因此，端到端耗时不等于单个 .cix 的 NPU 推理时间。

## 3.3.3 运行前检查

检查 NOE Engine：

```bash
python3 -m pip list | grep -E "libnoe|noe_engine"
```

检查 Audio 目录：

```bash
cd "$AI_MODEL_HUB_DIR”
find models/Audio \
-mindepth 1 \
-maxdepth 2 \
-type d \
| sort
```

安装公共依赖：

进入 AI Model Hub 根目录后，应先阅读根目录中的 ReadMe.md 或 ReadMe_EN.md，并按照其中“二、环境与依赖”的说明安装当前版本所需依赖。

不同模型和不同任务所需的 Python 依赖可能不同，不要默认直接执行根目录中的 requirements.txt，也不要仅根据脚本导入内容自行升级系统已有软件包。

检查系统音频和转换工具：

```bash
sudo apt update
sudo apt install -y ffmpeg
```

不同模型可能依赖：

- NumPy；
- PyTorch；
- Transformers；
- SentencePiece；
- FunASR；
- 音频读取库；
- MNN Runtime。

具体依赖应以模型 ReadMe.md 和脚本导入内容为准。

## 3.3.4 运行说话人验证示例

以下以 CAMPPlus 为例。

进入模型目录：

```bash
cd "$AI_MODEL_HUB_DIR/models/Audio/Speaker_Verification/onnx_campplus”
```

检查关键文件：

```bash
ls -lh speech_campplus_sv_zh_en_16k-common_advanced-10s.cix
ls -lh inference_npu.py
ls -lh test_data
```

测试数据中包含不同说话人、不同语言的 16 kHz WAV 文件和测试列表。

执行：

```bash
python3 inference_npu.py
```

正常运行时，脚本应完成：

1.  读取测试列表；
2.  加载两段语音；
3.  执行特征提取；
4.  使用 NPU 生成说话人向量；
5.  输出相似度或验证结果。

替换自定义语音前，应确认：

- 采样率符合模型要求；
- 音频为有效 WAV；
- 音频长度满足模型输入要求；
- 测试列表格式与原示例一致。

ERes2NetV2 示例使用方式相同，但模型文件名和 CFG 不同：

```bash
cd "$AI_MODEL_HUB_DIR/models/Audio/Speaker_Verification/onnx_eres2netv2”
python3 inference_npu.py
```

## 3.3.5 运行语音识别示例

### 3.3.5.1 SenseVoice

```bash
cd "$AI_MODEL_HUB_DIR/models/Audio/Speech_Recognition/onnx_sensevoice”
```

检查文件：

```bash
ls -lh sense_voice_mask256.cix
ls -lh inference_npu.py
ls -lh test_data
```

测试数据目录包含中文、英文、日文、韩文和粤语音频。

执行：

```bash
python3 inference_npu.py
```

### 3.3.5.2 Whisper Tiny

```bash
cd "$AI_MODEL_HUB_DIR/models/Audio/Speech_Recognition/onnx_whisper_tiny_multi_language”
```

检查关键文件：

```bash
ls -lh whisper_tiny_encoder.cix
ls -lh inference_npu.py
ls -lh test_data
ls -ld whisper-tiny-multi
```

执行：

```bash
python3 inference_npu.py
```

该目录同时包含：

scripts/

whisper-tiny-multi/

test_data/

因此不要只复制 whisper_tiny_encoder.cix。完整推理还依赖模型配置、Tokenizer、音频预处理和解码代码。

### 3.3.5.3 Whisper Medium

Whisper Medium 与 Tiny 不同，其目录中同时包含：

```text
whisper_medium_multilingual_encoder.cix
whisper_medium_multilingual_decoder.cix
```

并分别提供 Encoder 和 Decoder 的 CFG：

cfg/whisper_medium_multilingual_encoder/

cfg/whisper_medium_multilingual_decoder/

运行时必须同时保留两个 .cix 文件和完整目录结构：

```bash
cd "$AI_MODEL_HUB_DIR/models/Audio/Speech_Recognition/onnx_whisper_medium_multilingual”
python3 inference_npu.py
```

不能把 Whisper Tiny 的单 Encoder 部署方式直接套用到 Whisper Medium。

## 3.3.6 运行 Kokoro TTS 示例

进入目录：

```bash
cd "$AI_MODEL_HUB_DIR/models/Audio/TTS/onnx_kokoro”
```

检查关键文件：

```bash
ls -lh *.cix
ls -lh decoder1_int8.mnn
ls -lh voices
ls -lh inference_npu.py
```

应至少看到：

```text
bert2.cix
text_encoder.cix
predictor.cix
decoder00.cix
decoder01.cix
decoder1_int8.mnn
voices/af_heart.pt
voices/zf_xiaoyi.pt
```

执行：

```bash
python3 inference_npu.py
```

如果脚本支持参数，可先查看：

```bash
python3 inference_npu.py --help
```

否则应查看：

```text
sed -n '1,260p' ReadMe.md
sed -n '1,260p' inference_npu.py
```

Kokoro 目录包含多个 CFG：

```text
bert_build.cfg
text_encoder_build.cfg
predictor_build.cfg
decoder00_build.cfg
decoder01_build.cfg
```

如需重新编译，应分别编译对应子模型，例如：

```text
cixbuild cfg/bert_build.cfg
cixbuild cfg/text_encoder_build.cfg
cixbuild cfg/predictor_build.cfg
cixbuild cfg/decoder00_build.cfg
cixbuild cfg/decoder01_build.cfg
```

不要执行：

```text
model_domain=tts
```

NOE 编译器公开的 model_domain 列表中没有 tts。Kokoro 应使用目录中已经验证的 CFG，不应根据上层任务名称自行修改 model_domain。

## 3.3.7 替换自定义音频或文本

### 3.3.7.1 自定义音频

先使用 FFmpeg 查看音频信息：

```bash
ffprobe input_audio.wav
```

需要时进行格式转换：

```bash
ffmpeg \
-i input_audio \
-ar 16000 \
-ac 1 \
output_16k_mono.wav
```

16000 Hz、单声道 仅适用于明确要求该格式的模型，例如当前说话人验证目录中的 16 kHz 模型。其他模型应以其 README 和预处理脚本为准。

重点检查：

| **检查项** | **说明**                       |
|------------|--------------------------------|
| 采样率     | 是否与模型一致                 |
| 声道       | 单声道或多声道                 |
| 音频时长   | 是否需要裁剪、补齐或分段       |
| 数据格式   | WAV、MP3、FLAC 等              |
| 归一化     | PCM 幅值是否正确               |
| Tokenizer  | 必须与模型版本匹配             |
| 测试列表   | 说话人验证可能要求特定列表格式 |

### 3.3.7.2 自定义 TTS 文本

替换 TTS 文本时，应确认：

- 当前模型支持的语言；
- 使用的 Voice 文件；
- 文本编码和标点格式；
- 输出采样率；
- 输出文件路径；
- 中英文 Voice 与文本语言是否匹配。

不要直接删除 voices、kokoro 或 decoder1_int8.mnn，这些都是完整 TTS Pipeline 的组成部分。

## 3.3.8 接入麦克风和 Agent

完成文件推理后，再接入麦克风。

推荐流程：

1. 麦克风
2. 录音或音频分段
3. 格式转换和特征提取
4. 语音识别
5. 文本输入 LLM / Agent
6. 工具调用
7. TTS 生成回复
8. 扬声器播放

建议按以下顺序开发：

1.  使用模型自带测试音频跑通；
2.  使用自定义音频文件验证；
3.  单独验证麦克风录音；
4.  将录音文件送入识别脚本；
5.  接入 LLM 或 Agent；
6.  最后接入 Kokoro TTS 和扬声器。

当前 AI Model Hub 还提供：

demos/audio-chat-gradio

## 3.3.9 性能观察

Audio 应分阶段记录耗时：

| **阶段**         | **说明**               |
|------------------|------------------------|
| 音频读取         | 文件或麦克风获取数据   |
| 重采样与特征提取 | PCM 转换和声学特征计算 |
| NPU 推理         | .cix 子模型执行时间    |
| Decoder          | Token 或声学特征解码   |
| Tokenizer        | Token 与文本转换       |
| TTS 波形生成     | 声学模型和 Decoder     |
| 音频保存或播放   | 文件写入和音频输出     |

正式比较时，应固定：

- 输入音频或文本；
- 音频长度；
- 模型版本；
- .cix 和 Runtime 版本；
- Decoder 参数；
- Voice 文件；
- 系统负载和温度。

## 3.3.10 常见问题

| **问题现象**               | **处理建议**                               |
|----------------------------|--------------------------------------------|
| 只看到 Whisper，找不到 TTS | 使用当前 Audio/TTS/onnx_kokoro 目录        |
| 说话人验证结果异常         | 检查采样率、音频长度和测试列表             |
| 识别结果为空               | 检查音频格式、Tokenizer 和模型目录是否完整 |
| Whisper 找不到 Tokenizer   | 不要只复制 .cix，应复制完整目录            |
| Whisper Medium 加载失败    | 同时检查 Encoder 和 Decoder .cix           |
| SenseVoice 无法解析音频    | 检查 MP3 解码依赖和音频路径                |
| Kokoro 找不到模型          | 检查多个 .cix、MNN Decoder 和 Voice 文件   |
| Kokoro 能运行但无音频      | 检查输出路径、音频写入和声卡播放           |
| noe_load_graph 失败        | 检查 .cix 与 NOE Runtime 版本              |
| 端到端耗时较高             | 分离特征提取、NPU、Decoder 和音频输出耗时  |
