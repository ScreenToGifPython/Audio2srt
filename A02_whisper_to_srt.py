# -*- encoding: utf-8 -*-
"""
@File: test_3.py
@Modify Time: 2024/10/30 14:25       
@Author: Kevin-Chen
@Descriptions: 
"""
import whisper
import sys
import os
import srt
from datetime import timedelta


def transcribe_and_generate_srt(audio_file, srt_output_file, language='en', whisper_model='median.pt'):
    # 检查是否是打包后的可执行文件
    if getattr(sys, 'frozen', False):
        # 获取当前文件目录（针对 Nuitka 的打包环境）
        current_dir = os.path.dirname(sys.executable)
    else:
        # 开发环境中，使用当前文件路径
        current_file_path = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file_path)

    model_path = os.path.join(current_dir, whisper_model)
    # 加载 Whisper 模型
    model = whisper.load_model(model_path)

    # 转录音频并获取时间戳
    result = model.transcribe(audio_file, verbose=True, language=language)

    # 准备 SRT 片段列表
    subtitles = []
    for segment in result['segments']:
        start = timedelta(seconds=segment['start'])
        end = timedelta(seconds=segment['end'])
        content = segment['text'].strip()

        # 创建一个 SRT 的 subtitle 对象
        subtitle = srt.Subtitle(index=len(subtitles) + 1, start=start, end=end, content=content)
        subtitles.append(subtitle)

    # 生成 SRT 文件
    srt_content = srt.compose(subtitles)
    with open(srt_output_file, "w", encoding="utf-8") as f:
        f.write(srt_content)


if __name__ == '__main__':
    pass
