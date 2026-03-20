# 12 高仿真 TTS 配音

## 1. 模块定位

将脚本文本转成可用于成片的高自然度音频，并产出时间戳字幕（SRT）。

对应代码目录：
- `app/modules/tts/chattts_engine.py`
- `app/modules/tts/cosyvoice_engine.py`
- `app/modules/tts/voice_clone.py`
- `app/modules/tts/tts_manager.py`

## 2. 输入与输出

- 输入：脚本文本、音色、语速、情感参数
- 输出：`wav/mp3`、`srt`、音频时长、生成日志

## 3. 引擎路由策略

- 默认：ChatTTS
- 备选：CosyVoice
- 声音克隆：GPT-SoVITS（单独训练流程）

## 4. 核心流程

1. 文本分段并插入停顿标记。
2. 按段生成音频并拼接。
3. 记录时间戳生成字幕。
4. 返回试听地址供人工确认。

## 5. 接口设计

- `POST /api/tts/generate`
- `POST /api/tts/preview`
- `POST /api/tts/clone/train`

## 6. 异常策略

- 引擎超时：自动切换备选引擎重试。
- 发音异常：定位段落后局部重合成。
- 长文本失败：自动分批并行生成。

## 7. 监控指标

- 合成成功率
- 平均生成时长
- 重生成率
- 音色满意度（人工打分）

## 8. MVP 验收标准

- 单条 60-120 秒脚本可稳定生成音频+SRT。
- 用户可在 2 次以内拿到可用配音版本。
