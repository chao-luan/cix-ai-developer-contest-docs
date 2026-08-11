# 3. 此芯P1端侧AI

此芯P1提供强大的CPU/GPU/NPU异构计算，综合AI算力可达45 TOPS，能满足不同场景的AI算法需求。基于Linux的推理框架和硬件加速方式推荐如下：

<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 32%" />
<col style="width: 21%" />
<col style="width: 31%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>模型类别</strong></th>
<th><strong>框架</strong></th>
<th><strong>硬件加速</strong></th>
<th><strong>备注</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td rowspan="2">LLM</td>
<td>llama.cpp</td>
<td>CPU – KleidiAI<br>
GPU – Vulkan</td>
<td rowspan="2">支持Qwen, MiniCPM, Ernie等大语言模型</td>
</tr>
<tr class="even">
<td>MNN</td>
<td>CPU – KleidiAI<br>
GPU – OpenCL</td>
</tr>
<tr class="odd">
<td>CV</td>
<td>CIX NOE</td>
<td>NPU</td>
<td>支持Yolo, ResNet, MobileNet, OCR, Embedding等模型</td>
</tr>
<tr class="even">
<td>Audio</td>
<td>CIX NOE</td>
<td>NPU</td>
<td>支持ASR, TTS等模型</td>
</tr>
<tr class="odd">
<td>SD</td>
<td>CIX NOE</td>
<td>NPU</td>
<td>支持SD 1.4, SDXL等模型</td>
</tr>
<tr class="even">
<td>VLM</td>
<td>CIX NOE + llama.cpp/MNN</td>
<td>NPU + CPU/GPU</td>
<td>Embedding &amp; ViT部分可以用NPU加速，LLM部分可以用CPU/GPU加速</td>
</tr>
</tbody>
</table>

此芯AI Model Hub提供适配优化好的主流模型下载，开发者可以直接部署使用，链接如下：

```text
ai_model_hub_26_Q2 · 模型库
```

```{toctree}
:maxdepth: 2
:hidden:

llm
cv
audio
vlm
```
