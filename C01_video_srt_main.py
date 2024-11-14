# -*- encoding: utf-8 -*-
"""
@File: B01_video_srt_main.py
@Modify Time: 2024/11/1 11:56       
@Author: Kevin-Chen
@Descriptions: 功能整合:英文视频加中英文字幕
"""

from A01_get_audio_from_video import extract_audio_from_video
from A02_whisper_to_srt import transcribe_and_generate_srt
from A03_srt_add_cn import translate_srt
from A06_srt_2_ass import convert_srt_to_ass_with_line_split
from A07_ass_in_video import embed_ass_subtitles
import os

if __name__ == '__main__':
    ''' 主要可选参数 '''
    # 主文件名称
    main_name = "ubc_words"
    # 音频的语音类型, 用于whisper识别语音
    language_code = "English"  # "japanese" or "Chinese" or "English"
    # 选择whisper模型
    whisper_model = 'whisper_models/large-v3.pt'  # small.pt, base.pt, large-v3.pt 三种类型模型可选
    # 输入视频路径
    the_video_path = f"{main_name}.mp4"
    # 输出视频路径
    the_output_video_path = f"{main_name}_output.mp4"
    # 中文字幕占屏幕高度的比率
    cn_fontsize_ratio = 0.018
    # 英文字幕占屏幕高度的比率
    eng_fontsize_ratio = 0.018

    ''' 临时文件 '''
    # 输出音频路径 (临时文件)
    the_audio_path = f"{main_name}.mp3"
    # 字幕srt文件路径 (临时文件)
    the_srt_path = f"{main_name}_subtitles.srt"
    # 翻译后的srt文件路径 (临时文件)
    the_srt_translated_path = f"{main_name}_translated_subtitles.srt"
    # 生成ass字幕文件路径 (临时文件)
    the_ass_path = f"{main_name}.ass"

    ''' 功能函数 '''
    # 提取音频
    extract_audio_from_video(the_video_path, the_audio_path)
    print(f"音频已提取: {the_audio_path}")

    # 音频识别文字
    transcribe_and_generate_srt(the_audio_path, the_srt_path, language_code,
                                whisper_model)
    print(f"原文字幕已生成: {the_srt_path}")

    # srt添加中文翻译
    translate_srt(the_srt_path, the_srt_translated_path, language_code)
    print(f"中英文字幕已生成: {the_srt_translated_path}")

    # 生成ASS字幕文件
    convert_srt_to_ass_with_line_split(the_srt_translated_path, the_ass_path, the_video_path,
                                       eng_fontsize_ratio=eng_fontsize_ratio,
                                       cn_fontsize_ratio=cn_fontsize_ratio)
    print(f"ASS字幕已生成: {the_ass_path}")

    # 嵌入字幕到视频中
    embed_ass_subtitles(the_video_path, the_ass_path, the_output_video_path)
    print(f"视频已生成: {the_output_video_path}")

    ''' 删除临时文件 '''
    os.remove(the_audio_path)
    os.remove(the_srt_path)
    os.remove(the_srt_translated_path)
    os.remove(the_ass_path)
    print("所有临时文件已删除")
